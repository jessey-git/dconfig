# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better symmetry
#

import math

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_MT_symmetry_pie(bpy.types.Menu):
    bl_label = "Symmetry"

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_available(context)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        pie.operator("dconfig.mesh_symmetry", text="+X to -X", icon='TRIA_LEFT').direction = 'POSITIVE_X'

        # Right
        pie.operator("dconfig.mesh_symmetry", text="-X to +X", icon='TRIA_RIGHT').direction = 'NEGATIVE_X'

        # Bottom
        pie.operator("dconfig.mesh_symmetry", text="+Z to -Z", icon='TRIA_DOWN').direction = 'POSITIVE_Z'

        # Top
        pie.operator("dconfig.mesh_symmetry", text="-Z to +Z", icon='TRIA_UP').direction = 'NEGATIVE_Z'

        # Top Left
        pie.operator("dconfig.mirror", text="Mirror Local", icon='MOD_MIRROR').local = True

        # Top Right
        col = pie.column(align=True)
        col.operator("dconfig.mirror", text="Mirror World", icon='MOD_MIRROR').local = False
        col.operator("dconfig.mirror_radial", text="Mirror Radial", icon='MOD_ARRAY')

        # Bottom Left
        pie.operator("dconfig.mesh_symmetry", text="+Y to -Y", icon='DOT').direction = 'POSITIVE_Y'

        # Bottom Right
        pie.operator("dconfig.mesh_symmetry", text="-Y to +Y", icon='DOT').direction = 'NEGATIVE_Y'


class DCONFIG_OT_mesh_symmetry(bpy.types.Operator):
    bl_idname = "dconfig.mesh_symmetry"
    bl_label = "DC Mesh Symmetry"
    bl_description = "Symmetrize mesh along an axis"
    bl_options = {'REGISTER', 'UNDO'}

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

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        if context.mode == 'EDIT_MESH':
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.symmetrize(direction=self.direction)
        else:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.symmetrize(direction=self.direction)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return dc.trace_exit(self)


class DCONFIG_OT_mirror(bpy.types.Operator):
    bl_idname = "dconfig.mirror"
    bl_label = "DC Mirror"
    bl_description = "Mirror mesh across an axis"
    bl_options = {'REGISTER', 'UNDO'}

    local: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        mirror_object = self.create_mirror_obj(context)
        self.create_mirror_mod(target, mirror_object)

        return dc.trace_exit(self)

    def create_mirror_obj(self, context):
        mirror_object = None
        if not self.local:
            # Use a special collection
            helpers_collection = dc.get_helpers_collection(context)

            if "DC_World_Origin" in helpers_collection.all_objects:
                dc.trace(1, "Using existing world-origin empty")
                mirror_object = helpers_collection.objects["DC_World_Origin"]
            else:
                dc.trace(1, "Creating new world-origin empty")
                original_object = context.active_object
                original_mode = context.active_object.mode

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
                mirror_object = context.active_object
                mirror_object.name = "DC_World_Origin"
                mirror_object.select_set(state=False)
                mirror_object.hide_viewport = True

                mirror_object_collection = dc.find_collection(context, mirror_object)
                helpers_collection.objects.link(mirror_object)
                mirror_object_collection.objects.unlink(mirror_object)

                context.view_layer.objects.active = original_object
                context.view_layer.objects.active.select_set(True)
                bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        return mirror_object

    def create_mirror_mod(self, target, mirror_object):
        dc.trace(1, "Adding {} mirror modifier to {}", "local" if self.local else "world", dc.full_name(target))

        if self.local:
            mod = target.modifiers.new("dc_local", 'MIRROR')
            mod.use_axis[0] = True
            mod.use_bisect_axis[0] = True
            mod.use_clip = True
        else:
            mod = target.modifiers.new("dc_world", 'MIRROR')
            mod.use_axis[0] = True
            mod.use_bisect_axis[0] = False
            mod.use_clip = True
            mod.mirror_object = mirror_object

        mod.show_on_cage = True
        mod.show_expanded = False

        # Local mirrors go before World and after Booleans...
        if self.local:
            mod_index = len(target.modifiers) - 1
            while mod_index > 0 and target.modifiers[mod_index - 1].type != 'BOOLEAN':
                bpy.ops.object.modifier_move_up(modifier=mod.name)
                mod_index -= 1


class DCONFIG_OT_mirror_radial(bpy.types.Operator):
    bl_idname = "dconfig.mirror_radial"
    bl_label = "DC Mirror Radial"
    bl_description = "Mirror mesh in a radial fashion"
    bl_options = {'REGISTER', 'UNDO'}

    count: bpy.props.IntProperty(name="count", default=0)

    def __init__(self):
        self.radial_mod = None
        self.radial_object = None

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
            self.create_radial_obj(context)
            self.create_radial_mod(target)
            self.align_objects(context, target)
            self.adjust_radial_mod(0)
        elif is_execute and self.count != self.radial_mod.count:
            self.adjust_radial_mod(self.count - self.radial_mod.count)

    def modal(self, context, event):
        if event.type == 'WHEELUPMOUSE':
            self.adjust_radial_mod(1)

        elif event.type == 'WHEELDOWNMOUSE':
            self.adjust_radial_mod(-1)

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.radial_object.hide_viewport = True
            return dc.trace_exit(self)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.radial_object.hide_viewport = True
            return dc.user_canceled(self)

        return {'RUNNING_MODAL'}

    def create_radial_obj(self, context):
        dc.trace(1, "Creating new radial empty")
        prev_cursor_location = tuple(context.scene.cursor.location)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False)
        self.radial_object = context.active_object
        self.radial_object.name = "DC Radial"
        self.radial_object.select_set(state=True)

        # Place empty in a helpers collection
        radial_object_collection = dc.find_collection(context, self.radial_object)
        helpers_collection = dc.get_helpers_collection(context)
        helpers_collection.objects.link(self.radial_object)
        radial_object_collection.objects.unlink(self.radial_object)

        context.scene.cursor.location = prev_cursor_location

    def create_radial_mod(self, target):
        dc.trace(1, "Adding array modifier to {}", dc.full_name(target))
        self.count = 3 if self.count is 0 else self.count

        self.radial_mod = target.modifiers.new("dc_radial", 'ARRAY')
        self.radial_mod.fit_type = 'FIXED_COUNT'
        self.radial_mod.count = self.count
        self.radial_mod.offset_object = self.radial_object
        self.radial_mod.use_relative_offset = False
        self.radial_mod.use_object_offset = True
        self.radial_mod.use_merge_vertices = True
        self.radial_mod.use_merge_vertices_cap = True

        self.radial_mod.show_on_cage = True
        self.radial_mod.show_expanded = False

    def align_objects(self, context, target):
        if context.scene.transform_orientation_slots[0].type == 'Face':
            target.select_set(state=True)
            dc.trace(1, "Using Face axis alignment: {}", [o.name for o in context.selected_objects])

            self.radial_object["dc_axis"] = None
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), constraint_axis=(False, False, False), orient_type='Face')
        else:
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
        context.view_layer.objects.active = self.radial_object
        context.view_layer.objects.active.select_set(True)

    def adjust_radial_mod(self, delta):
        dc.trace(1, "Delta: {}", delta)
        current_rotation = math.radians(360 / self.radial_mod.count if delta != 0 else 0)

        self.count += delta
        self.radial_mod.count = self.count

        required_rotation = math.radians(360 / self.radial_mod.count)
        actual_rotation = current_rotation - required_rotation

        if self.radial_object["dc_axis"] is None:
            bpy.ops.transform.rotate(value=actual_rotation, constraint_axis=(False, False, True), orient_type='LOCAL')
        else:
            bpy.ops.transform.rotate(value=actual_rotation, orient_axis=self.radial_object["dc_axis"], orient_type='GLOBAL',)

    def init_from_existing(self, target):
        self.radial_mod = next((mod for mod in reversed(target.modifiers) if mod.name.startswith("dc_radial")), None)
        if self.radial_mod is not None:
            dc.trace(1, "Found existing modifier: {}", self.radial_mod.name)
            self.radial_object = self.radial_mod.offset_object
            self.radial_object.hide_viewport = False

            target.select_set(state=False)
            self.radial_object.select_set(state=True)

        return self.radial_mod is not None
