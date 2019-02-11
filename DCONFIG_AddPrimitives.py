# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Adds primitives at center of selected elements
#

import bpy
from mathutils import (Vector)
from . import DCONFIG_Utils as dc


class DCONFIG_MT_add_primitive_pie(bpy.types.Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_CYLINDER', text="6").type = 'Cylinder_6'
        col.operator("dconfig.add_primitive", icon='MESH_CYLINDER', text="8").type = 'Cylinder_8'
        col.operator("dconfig.add_primitive", icon='MESH_CYLINDER', text="16").type = 'Cylinder_16'
        col.operator("dconfig.add_primitive", icon='MESH_CYLINDER', text="32").type = 'Cylinder_32'
        col.operator("dconfig.add_primitive", icon='MESH_CYLINDER', text="64").type = 'Cylinder_64'

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_CIRCLE', text="6").type = 'Circle_6'
        col.operator("dconfig.add_primitive", icon='MESH_CIRCLE', text="8").type = 'Circle_8'
        col.operator("dconfig.add_primitive", icon='MESH_CIRCLE', text="16").type = 'Circle_16'
        col.operator("dconfig.add_primitive", icon='MESH_CIRCLE', text="32").type = 'Circle_32'

        # Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="12").type = 'Sphere_12'
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="24").type = 'Sphere_24'
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="32").type = 'Sphere_32'
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="Quad 1").type = 'Quad_Sphere_1'
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="Quad 2").type = 'Quad_Sphere_2'
        col.operator("dconfig.add_primitive", icon='MESH_UVSPHERE', text="Quad 3").type = 'Quad_Sphere_3'

        # Bottom
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_edge_curve", icon='CURVE_NCIRCLE', text="Edge Curve")
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 2x2x2").resolution = '2x2x2'
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 3x3x3").resolution = '3x3x3'
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 4x4x4").resolution = '4x4x4'

        # Top
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_PLANE', text="Plane").type = 'Plane'
        col.operator("dconfig.add_primitive", icon='MESH_CUBE', text="Cube").type = 'Cube'

        # Top Left
        # Top Right
        # Bottom Left
        # Bottom Right


class DCONFIG_OT_add_primitive(bpy.types.Operator):
    bl_idname = "dconfig.add_primitive"
    bl_label = "DC Add Primitive"
    bl_description = "Add pre-configured primitives and align to currently selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(name="Type")

    def add_primitive(self, context):
        is_ortho = not context.space_data.region_3d.is_perspective

        if self.type == 'Cube':
            bpy.ops.mesh.primitive_cube_add(size=1.0)
        elif self.type == 'Plane':
            bpy.ops.mesh.primitive_plane_add(view_align=is_ortho)

        elif self.type == 'Circle_6':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.25, vertices=6, view_align=is_ortho)
        elif self.type == 'Circle_8':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.25, vertices=8, view_align=is_ortho)
        elif self.type == 'Circle_16':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.50, vertices=16, view_align=is_ortho)
        elif self.type == 'Circle_32':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.50, vertices=32, view_align=is_ortho)

        elif self.type == 'Cylinder_6':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.25, vertices=6)
        elif self.type == 'Cylinder_8':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.25, vertices=8)
        elif self.type == 'Cylinder_16':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.50, vertices=16)
        elif self.type == 'Cylinder_32':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.50, vertices=32)
        elif self.type == 'Cylinder_64':
            bpy.ops.mesh.primitive_cylinder_add(radius=1.00, depth=1.00, vertices=64)

        elif self.type == 'Sphere_12':
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.25)
        elif self.type == 'Sphere_24':
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.50)
        elif self.type == 'Sphere_32':
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.50)

        elif self.type == 'Quad_Sphere_1':
            self.add_quad_sphere(context, 0.5, 1)
        elif self.type == 'Quad_Sphere_2':
            self.add_quad_sphere(context, 0.5, 2)
        elif self.type == 'Quad_Sphere_3':
            self.add_quad_sphere(context, 0.5, 3)

    def add_quad_sphere(self, context, radius, levels):
        was_edit = False
        prev_active = None
        if context.mode == 'EDIT_MESH':
            was_edit = True
            prev_active = context.active_object
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.mesh.primitive_cube_add(size=radius * 2)

        quad_sphere = context.active_object
        dc.rename(quad_sphere, "QuadSphere")

        mod_subd = quad_sphere.modifiers.new("dc_temp_subd", 'SUBSURF')
        mod_subd.levels = levels
        mod_sphere = quad_sphere.modifiers.new("dc_temp_cast", 'CAST')
        mod_sphere.factor = 1
        mod_sphere.radius = radius
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_subd.name)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_sphere.name)

        if was_edit:
            context.view_layer.objects.active = prev_active
            prev_active.select_set(True)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    def execute(self, context):
        dc.trace_enter(self)
        prev_cursor_location = tuple(context.scene.cursor_location)
        is_edit_mode = context.mode == 'EDIT_MESH'

        if context.active_object is None or (not context.selected_objects) or (is_edit_mode and context.active_object.data.total_vert_sel == 0):
            self.add_primitive(context)
        elif context.active_object.type == 'MESH' and is_edit_mode and tuple(context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            prev_active = context.active_object
            prev_orientation = context.scene.transform_orientation_slots[0].type

            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self.add_primitive(context)
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0, 0, 0), constraint_axis=(
                False, False, False), constraint_orientation='AddAxis', mirror=False, proportional='DISABLED')

            context.view_layer.objects.active = prev_active
            context.view_layer.objects.active.select_set(True)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            context.scene.transform_orientation_slots[0].type = prev_orientation
        else:
            bpy.ops.view3d.snap_cursor_to_selected()
            self.add_primitive(context)

        context.scene.cursor_location = prev_cursor_location
        return dc.trace_exit(self)


class DCONFIG_OT_add_lattice(bpy.types.Operator):
    bl_idname = "dconfig.add_lattice"
    bl_label = "DC Add Lattice"
    bl_description = "Add pre-configured lattice surrounding the selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty(name="Resolution")

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        target = context.active_object
        lattice = self.create_lattice_obj(context, target)
        self.create_lattice_mod(target, lattice)

        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = lattice
        lattice.select_set(True)

        return dc.trace_exit(self)

    def create_lattice_obj(self, context, target):
        # Create lattice
        lattice = bpy.data.lattices.new('dc_lattice')
        lattice_object = bpy.data.objects.new('dc_lattice', lattice)

        if self.resolution == "2x2x2":
            lattice.points_u = 2
            lattice.points_v = 2
            lattice.points_w = 2
        elif self.resolution == "3x3x3":
            lattice.points_u = 3
            lattice.points_v = 3
            lattice.points_w = 3
        elif self.resolution == "4x4x4":
            lattice.points_u = 4
            lattice.points_v = 4
            lattice.points_w = 4

        lattice.interpolation_type_u = 'KEY_BSPLINE'
        lattice.interpolation_type_v = 'KEY_BSPLINE'
        lattice.interpolation_type_w = 'KEY_BSPLINE'
        lattice.use_outside = False

        # Position + Orientation
        self.set_transforms(target, lattice_object)

        # Place in a special collection
        helpers_collection = dc.get_helpers_collection(context)
        helpers_collection.objects.link(lattice_object)

        # Toggle out of local-view mode and re-enter to ensure lattice shows up
        if context.space_data.local_view is not None:
            bpy.ops.view3d.localview()
            lattice_object.select_set(True)
            bpy.ops.view3d.localview()

        return lattice_object

    def create_lattice_mod(self, target, lattice):
        mod = target.modifiers.new(lattice.name, "LATTICE")
        mod.object = lattice

    def set_transforms(self, target, lattice):
        bbox_min, bbox_max = dc.find_world_bbox(target.matrix_world, [v.co for v in target.data.vertices])
        size = bbox_max - bbox_min

        lattice.location = (bbox_min + bbox_max) / 2
        lattice.scale = Vector([max(0.1, c) for c in size]) * 1.1
        lattice.rotation_euler = target.rotation_euler


class DCONFIG_OT_add_edge_curve(bpy.types.Operator):
    bl_idname = "dconfig.add_edge_curve"
    bl_label = "DC Add Edge Curve"
    bl_description = "Add curve following a path of connected edges"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.step = 0
        self.should_separate = False
        self.mouse_start_x = 0
        self.original_depth = 0.0

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def invoke(self, context, event):
        dc.trace_enter(self)

        if context.mode == 'OBJECT':
            # Object mode means we can skip to creating/manipulating the curve object
            self.create_curve(context, event)
            self.step = 1
        elif context.mode == 'EDIT_MESH' and context.active_object.data.total_edge_sel > 0:
            self.should_separate = context.active_object.data.total_edge_sel != len(context.active_object.data.edges)
            if self.should_separate:
                bpy.ops.mesh.duplicate_move()

            # Create a vertex group to be used later
            bpy.ops.object.vertex_group_assign_new()
            context.active_object.vertex_groups.active.name = "dc_temp_vgroup"
        else:
            return dc.warn_canceled(self, "No edges selected")

        dc.trace(1, "Starting step {}", self.step)
        if self.step == 0:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', offset_type='OFFSET', vertex_only=True, clamp_overlap=True)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # Modal
    # Mouse move: Adjust size of bevel
    # Mouse wheel: Adjust resolution of bevel
    # Shift Mouse wheel: Adjust sub-d level
    def modal(self, context, event):
        if self.step == 0:
            return self.continue_or_finish(context, event)

        if self.step == 1:
            curve = context.active_object

            if event.type == 'MOUSEMOVE':
                delta_x = event.mouse_x - self.mouse_start_x
                curve.data.bevel_depth = self.original_depth + delta_x * 0.01
            elif event.type == 'WHEELUPMOUSE':
                if not event.shift and curve.data.bevel_resolution < 6:
                    curve.data.bevel_resolution += 1
                elif event.shift and curve.modifiers[0].levels < 3:
                    curve.modifiers[0].levels += 1
            elif event.type == 'WHEELDOWNMOUSE':
                if not event.shift and curve.data.bevel_resolution > 0:
                    curve.data.bevel_resolution -= 1
                elif event.shift and curve.modifiers[0].levels > 0:
                    curve.modifiers[0].levels -= 1

        return self.continue_or_finish(context, event)

    def prepare(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.object.vertex_group_set_active(group="dc_temp_vgroup")
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

        if self.should_separate:
            dc.trace(2, "Separating due to subset of edges being selected")
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        context.view_layer.objects.active = context.selected_objects[-1]
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active.select_set(True)

    def create_curve(self, context, event):
        bpy.ops.object.convert(target='CURVE')
        if context.active_object.type != 'CURVE':
            return dc.warn_canceled(self, "Converting to curve failed")

        curve = context.active_object
        curve.data.dimensions = '3D'
        curve.data.fill_mode = 'FULL'
        curve.data.resolution_u = 3
        curve.data.bevel_depth = 0.0
        curve.data.bevel_resolution = 2
        curve.data.splines[0].use_smooth = True

        mod_subd = curve.modifiers.new("dc_subd", 'SUBSURF')
        mod_subd.levels = 0

        self.mouse_start_x = event.mouse_x
        self.original_depth = curve.data.bevel_depth

    def continue_or_finish(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            dc.trace(1, "Ending step {}", self.step)

            if self.step == 0:
                self.prepare(context)
                self.create_curve(context, event)

            self.step += 1
            if self.step == 2:
                return dc.trace_exit(self)

            dc.trace(1, "Starting step {}", self.step)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            vgroup = context.active_object.vertex_groups.active
            if vgroup is not None and vgroup.name == "dc_temp_vgroup":
                bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

            return dc.user_canceled(self)

        if self.step == 0:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}
