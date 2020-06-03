# ------------------------------------------------------------
# Copyright(c) 2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better modifiers
#

import math

import bpy
from mathutils import (Vector, Matrix)
from . import DCONFIG_Symmetry as symmetry
from . import DCONFIG_Utils as dc


class DCONFIG_MT_modifiers(bpy.types.Menu):
    bl_label = "Modifiers"

    @classmethod
    def poll(cls, context):
        return dc.active_object_available(context, {'MESH', 'LATTICE'})

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        dc.setup_op(layout, "dconfig.mirror", 'MOD_MIRROR', "Local Mirror", local=True)
        dc.setup_op(layout, "dconfig.mirror", 'MOD_MIRROR', "World Mirror", local=False)

        layout.separator()
        dc.setup_op(layout, "dconfig.radial_array", 'MOD_ARRAY', "Radial Array")
        dc.setup_op(layout, "dconfig.bend", 'MOD_SIMPLEDEFORM', "Bend")

        layout.separator()
        dc.setup_op(layout, "dconfig.add_lattice", 'MESH_GRID', "FFD", resolution=2, only_base=True)


class DCONFIG_OT_mirror(bpy.types.Operator):
    bl_idname = "dconfig.mirror"
    bl_label = "DC Mirror"
    bl_description = "Mirror mesh across an axis"
    bl_options = {'REGISTER', 'UNDO'}

    local: bpy.props.BoolProperty()
    direction: bpy.props.EnumProperty(
        items=(
            ('POSITIVE_X', "+X to -X", "+X to -X", 0),
            ('NEGATIVE_X', "-X to +X", "-X to +X", 1),
            ('POSITIVE_Y', "+Y to -Y", "+Y to -Y", 2),
            ('NEGATIVE_Y', "-Y to +Y", "-Y to +Y", 3),
            ('POSITIVE_Z', "+Z to -Z", "+Z to -Z", 4),
            ('NEGATIVE_Z', "-Z to +Z", "-Z to +Z", 5),
        ),
        name="Direction",
        description="which side to copy from",
        default='POSITIVE_X',
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)

    dc_uses_symmetry_gizmo = True

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        mirror_object = self.create_mirror_obj(context)
        self.create_mirror_mod(target, mirror_object)

        symmetry.DCONFIG_GGT_symmetry_gizmo.destroy(context)

        return dc.trace_exit(self)

    def invoke(self, context, event):
        dc.trace_enter(self)

        if context.space_data.type == 'VIEW_3D':
            symmetry.DCONFIG_GGT_symmetry_gizmo.create(context)

        return dc.trace_exit(self)

    def create_mirror_obj(self, context):
        mirror_object = None
        if not self.local:
            # Use a special collection
            helpers_collection = dc.get_helpers_collection(context)

            world_origin_name = "dc_world_origin"
            if world_origin_name in helpers_collection.all_objects:
                dc.trace(1, "Using existing world-origin empty")
                mirror_object = helpers_collection.objects[world_origin_name]
            else:
                dc.trace(1, "Creating new world-origin empty")
                original_object = context.active_object
                original_mode = context.active_object.mode

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.25, align='WORLD', location=(0, 0, 0))
                mirror_object = context.active_object
                mirror_object.name = world_origin_name
                mirror_object.select_set(state=False)
                mirror_object.hide_viewport = True

                mirror_object_collection = dc.find_collection(context, mirror_object)
                helpers_collection.objects.link(mirror_object)
                mirror_object_collection.objects.unlink(mirror_object)

                dc.make_active_object(context, original_object)
                bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        return mirror_object

    def create_mirror_mod(self, target, mirror_object):
        dc.trace(1, "Adding {} mirror modifier to {}", "local" if self.local else "world", dc.full_name(target))

        if self.local:
            mod = target.modifiers.new("dc_local_mirror", 'MIRROR')
            mod.use_clip = True
        else:
            mod = target.modifiers.new("dc_world_mirror", 'MIRROR')
            mod.use_clip = True
            mod.mirror_object = mirror_object

        axis = 0 if self.direction in {'POSITIVE_X', 'NEGATIVE_X'} else 1 if self.direction in {'POSITIVE_Y', 'NEGATIVE_Y'} else 2
        should_bisect = self.local
        should_flip = should_bisect and self.direction.startswith('NEGATIVE')

        mod.use_axis = (False, False, False)
        mod.use_axis[axis] = True
        mod.use_bisect_axis[axis] = should_bisect
        mod.use_bisect_flip_axis[axis] = should_flip
        mod.show_on_cage = True
        mod.show_expanded = False

        # Local mirrors go before World and after Booleans...
        if self.local:
            mod_index = len(target.modifiers) - 1
            while mod_index > 0 and target.modifiers[mod_index - 1].type != 'BOOLEAN' and not target.modifiers[mod_index - 1].name.startswith("dc_local_mirror"):
                bpy.ops.object.modifier_move_up(modifier=mod.name)
                mod_index -= 1


class DCONFIG_OT_radial_array(bpy.types.Operator):
    bl_idname = "dconfig.radial_array"
    bl_label = "DC Radial Array"
    bl_description = "Array mesh in a radial fashion"
    bl_options = {'REGISTER', 'UNDO'}

    count: bpy.props.IntProperty(name="count", default=3, min=1, max=360)

    def __init__(self):
        self.mouse_x = None
        self.offset_mod = None
        self.radial_mod = None
        self.radial_object = None
        self.existing_strength = None
        self.existing_direction = None
        self.existing_count = None

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def invoke(self, context, event):
        dc.trace_enter(self)

        self.execute_core(context, False)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        dc.trace_enter(self)

        self.execute_core(context, True)
        self.radial_object.hide_viewport = True

        return dc.trace_exit(self)

    def execute_core(self, context, is_execute):
        target = context.active_object
        if not self.init_from_existing(target):
            self.create_radial_obj(context, target)
            self.create_radial_mod(target)
            self.align_objects(context, target)
            self.adjust_radial_mod(0, init=True)
        elif is_execute and self.count != self.radial_mod.count:
            self.adjust_radial_mod(self.count - self.radial_mod.count)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE' and event.ctrl:
            if self.mouse_x is not None:
                scale = 100 if event.shift else 10
                displace_delta = (event.mouse_x - self.mouse_x) / scale
                self.offset_mod.strength += displace_delta
            self.mouse_x = event.mouse_x
        elif not event.ctrl:
            self.mouse_x = None

        if event.type == 'WHEELUPMOUSE':
            self.adjust_radial_mod(1)

        elif event.type == 'WHEELDOWNMOUSE':
            if self.radial_mod.count > 1:
                self.adjust_radial_mod(-1)

        elif event.type in {'X', 'Y', 'Z'} and event.value == 'RELEASE':
            self.offset_mod.direction = event.type

        elif event.type == 'LEFTMOUSE':
            self.radial_object.hide_viewport = True
            return dc.trace_exit(self)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.existing_strength is None:
                self.radial_object.parent.select_set(True)
                context.view_layer.objects.active = self.radial_object.parent
                bpy.ops.object.modifier_remove(modifier=self.radial_mod.name)
                bpy.ops.object.modifier_remove(modifier=self.offset_mod.name)
                bpy.data.objects.remove(self.radial_object)
            else:
                self.offset_mod.strength = self.existing_strength
                self.offset_mod.direction = self.existing_direction
                self.adjust_radial_mod(self.existing_count - self.radial_mod.count)
                self.radial_object.hide_viewport = True
            return dc.user_canceled(self)

        return {'RUNNING_MODAL'}

    def create_radial_obj(self, context, target):
        dc.trace(1, "Creating new radial empty")
        prev_cursor_location = tuple(context.scene.cursor.location)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.25, align='WORLD')
        self.radial_object = context.active_object
        self.radial_object.name = target.name + "_world_radial"
        self.radial_object.select_set(state=True)

        # Place empty in a helpers collection
        radial_object_collection = dc.find_collection(context, self.radial_object)
        helpers_collection = dc.get_helpers_collection(context)
        helpers_collection.objects.link(self.radial_object)
        radial_object_collection.objects.unlink(self.radial_object)

        # Parent empty to the target
        self.radial_object.parent = target
        self.radial_object.matrix_parent_inverse = target.matrix_world.inverted()

        context.scene.cursor.location = prev_cursor_location

    def create_radial_mod(self, target):
        dc.trace(1, "Adding array modifier to {}", dc.full_name(target))

        self.offset_mod = target.modifiers.new("dc_offset", 'DISPLACE')
        self.offset_mod.strength = 0
        self.offset_mod.direction = 'Y'
        self.offset_mod.show_in_editmode = True
        self.offset_mod.show_on_cage = False
        self.offset_mod.show_expanded = False

        self.radial_mod = target.modifiers.new("dc_radial", 'ARRAY')
        self.radial_mod.fit_type = 'FIXED_COUNT'
        self.radial_mod.count = self.count
        self.radial_mod.offset_object = self.radial_object
        self.radial_mod.use_relative_offset = False
        self.radial_mod.use_object_offset = True
        self.radial_mod.use_merge_vertices = True
        self.radial_mod.use_merge_vertices_cap = True
        self.radial_mod.merge_threshold = 0.001

        self.radial_mod.show_on_cage = False
        self.radial_mod.show_expanded = False

    def align_objects(self, context, target):
        is_ortho = not context.space_data.region_3d.is_perspective
        if is_ortho:
            view = dc.get_view_orientation_from_quaternion(context.space_data.region_3d.view_rotation)

            dc.trace(1, "Using Ortho axis: {}", view)

            if view == 'TOP' or view == 'BOTTOM':
                self.radial_object["dc_axis"] = 'Z'
            elif view == 'LEFT' or view == 'RIGHT':
                self.radial_object["dc_axis"] = 'X'
            elif view == 'FRONT' or view == 'BACK':
                self.radial_object["dc_axis"] = 'Y'
        else:
            dc.trace(1, "Using Global-Z axis")
            self.radial_object["dc_axis"] = None

        # Ensure the proper object is active/selected for further bpy.ops
        bpy.ops.object.select_all(action='DESELECT')
        dc.make_active_object(context, self.radial_object)

    def adjust_radial_mod(self, delta, init=False):
        dc.trace(1, "Delta: {}", delta)
        if init:
            current_rotation = 0
        else:
            current_rotation = math.radians(360 / self.radial_mod.count)

        self.radial_mod.count += delta

        required_rotation = math.radians(360 / self.radial_mod.count)
        actual_rotation = current_rotation - required_rotation

        if self.radial_object["dc_axis"] is None:
            bpy.ops.transform.rotate(value=actual_rotation, constraint_axis=(False, False, True), orient_type='LOCAL')
        else:
            bpy.ops.transform.rotate(value=actual_rotation, orient_axis=self.radial_object["dc_axis"], orient_type='GLOBAL',)

    def init_from_existing(self, target):
        self.offset_mod = next((mod for mod in reversed(target.modifiers) if mod.name.startswith("dc_offset")), None)
        self.radial_mod = next((mod for mod in reversed(target.modifiers) if mod.name.startswith("dc_radial")), None)
        if self.radial_mod is not None:
            dc.trace(1, "Found existing modifier: {}", self.radial_mod.name)
            self.radial_object = self.radial_mod.offset_object
            self.radial_object.hide_viewport = False

            self.existing_strength = self.offset_mod.strength
            self.existing_direction = self.offset_mod.direction
            self.existing_count = self.radial_mod.count

            target.select_set(state=False)
            self.radial_object.select_set(state=True)

        return self.radial_mod is not None


class DCONFIG_OT_add_lattice(bpy.types.Operator):
    bl_idname = "dconfig.add_lattice"
    bl_label = "DC Add Lattice"
    bl_description = "Add pre-configured lattice surrounding the selected geometry"
    bl_options = {'REGISTER'}

    resolution: bpy.props.IntProperty(name="Resolution", default=2, min=2, max=6)
    only_base: bpy.props.BoolProperty(name="Only Base Object", default=True)

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def __init__(self):
        self.target = None
        self.lattice = None
        self.mod = None

    def invoke(self, context, event):
        dc.trace_enter(self)

        self.execute_core(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        dc.trace_enter(self)

        self.target = context.active_object
        self.execute_core(context)
        self.make_lattice_active(context)

        return dc.trace_exit(self)

    def execute_core(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.target = context.active_object
        self.create_lattice_obj(context)
        self.create_lattice_mod()

    def modal(self, context, event):
        if event.type == 'WHEELUPMOUSE':
            self.resolution += 1
            self.execute_core(context)
        elif event.type == 'WHEELDOWNMOUSE':
            self.resolution -= 1
            self.execute_core(context)
        elif event.type in {'B'} and event.value == 'RELEASE':
            self.only_base = not self.only_base
            self.execute_core(context)

        elif event.type == 'LEFTMOUSE':
            self.make_lattice_active(context)
            return dc.trace_exit(self)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return dc.user_canceled(self)

        return {'RUNNING_MODAL'}

    def make_lattice_active(self, context):
        dc.make_active_object(context, self.lattice)
        self.target.select_set(False)

    def create_lattice_obj(self, context):
        # Create lattice
        if self.lattice is None:
            lattice_data = bpy.data.lattices.new('dc_lattice')
            self.lattice = bpy.data.objects.new('dc_lattice', lattice_data)

            self.lattice.data.interpolation_type_u = 'KEY_LINEAR'
            self.lattice.data.interpolation_type_v = 'KEY_LINEAR'
            self.lattice.data.interpolation_type_w = 'KEY_LINEAR'
            self.lattice.data.use_outside = False

            # Place in a special collection
            helpers_collection = dc.get_helpers_collection(context)
            helpers_collection.objects.link(self.lattice)

            # Ensure the lattice is added to local view...
            if context.space_data.local_view is not None:
                self.lattice.local_view_set(context.space_data, True)

            # Parent target to the lattice...
            context.view_layer.update()
            self.lattice.parent = self.target
            self.lattice.matrix_parent_inverse = self.target.matrix_world.inverted()

        # Position + Orientation (resolution is affected for 0 dimensions)
        self.set_transforms()

    def create_lattice_mod(self):
        if self.mod is None:
            self.mod = self.target.modifiers.new(self.lattice.name, "LATTICE")
            self.mod.object = self.lattice
            self.mod.show_expanded = False

        # Place just after Booleans (or at end)...
        if self.only_base:
            mod_index = next((i for i, v in enumerate(self.target.modifiers) if v.name == self.mod.name), -1)
            while mod_index > 0 and self.target.modifiers[mod_index - 1].type != 'BOOLEAN':
                bpy.ops.object.modifier_move_up(modifier=self.mod.name)
                mod_index -= 1
        else:
            while self.target.modifiers[-1].name != self.mod.name:
                bpy.ops.object.modifier_move_down(modifier=self.mod.name)

    def set_transforms(self):
        if self.only_base:
            bbox_min, bbox_max = dc.calculate_bbox(map(lambda v: v.co, self.target.data.vertices))
            vert_avg = sum(map(lambda v: v.co, self.target.data.vertices), Vector()) / len(self.target.data.vertices)
            box_center = ((bbox_min + vert_avg) + (bbox_max - vert_avg)) / 2
            box_dims = bbox_max - bbox_min
        else:
            box_center = sum(map(Vector, self.target.bound_box), Vector()) / 8
            box_dims = self.target.dimensions

        target_loc, target_rot, _ = self.target.matrix_world.decompose()
        self.lattice.matrix_world = (Matrix.Translation(target_loc) @ target_rot.to_matrix().to_4x4() @ Matrix.Translation(box_center))
        self.lattice.dimensions = [max(0.01, d * 1.01) for d in box_dims]

        safe_res = [self.resolution if d > 0.0 else 1 for d in box_dims]
        self.lattice.data.points_u = safe_res[0]
        self.lattice.data.points_v = safe_res[1]
        self.lattice.data.points_w = safe_res[2]


class DCONFIG_OT_bend(bpy.types.Operator):
    bl_idname = "dconfig.bend"
    bl_label = "DC Bend"
    bl_description = "Bend mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        bend_object = self.create_bend_obj(context, target)
        self.create_bend_mod(target, bend_object)

        bend_object.select_set(state=False)
        bend_object.hide_viewport = True

        dc.make_active_object(context, target)

        return dc.trace_exit(self)

    def create_bend_obj(self, context, target):
        dc.trace(1, "Creating new bend empty")
        prev_cursor_location = tuple(context.scene.cursor.location)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.25, align='WORLD')
        bend_object = context.active_object
        bend_object.name = target.name + "_bender"
        bend_object.select_set(state=True)

        # Place empty in a helpers collection
        bend_object_collection = dc.find_collection(context, bend_object)
        helpers_collection = dc.get_helpers_collection(context)
        helpers_collection.objects.link(bend_object)
        bend_object_collection.objects.unlink(bend_object)

        # Parent empty to the target
        bend_object.parent = target
        bend_object.matrix_parent_inverse = target.matrix_world.inverted()

        context.scene.cursor.location = prev_cursor_location
        return bend_object

    def create_bend_mod(self, target, bend_object):
        array_mod = target.modifiers.new("dc_array", 'ARRAY')
        array_mod.fit_type = 'FIXED_COUNT'
        array_mod.count = 4
        array_mod.use_merge_vertices = True
        array_mod.use_merge_vertices_cap = True
        array_mod.merge_threshold = 0.003

        bend_mod = target.modifiers.new("dc_bend", 'SIMPLE_DEFORM')
        bend_mod.deform_method = 'BEND'
        bend_mod.deform_axis = 'Z'
        bend_mod.angle = math.radians(120)
        bend_mod.origin = bend_object
