# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Adds primitives at center of selected elements
#

import bpy
from mathutils import (Matrix, Vector)
from . import DCONFIG_Utils as utils


class DC_MT_add_primitive_pie(bpy.types.Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="6").type = 'Cylinder_6'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="8").type = 'Cylinder_8'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="16").type = 'Cylinder_16'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="32").type = 'Cylinder_32'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="64").type = 'Cylinder_64'

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="6").type = 'Circle_6'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="8").type = 'Circle_8'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="16").type = 'Circle_16'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="32").type = 'Circle_32'

        # Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="12").type = 'Sphere_12'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="24").type = 'Sphere_24'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="32").type = 'Sphere_32'
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="Quad 1").type = 'Quad_Sphere_1'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="Quad 2").type = 'Quad_Sphere_2'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="Quad 3").type = 'Quad_Sphere_3'

        # Bottom
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.00
        col.scale_x = 1.00
        col.operator("view3d.dc_add_edge_curve", icon='CURVE_NCIRCLE', text="Edge Curve")
        col.operator("view3d.dc_add_lattice", icon='LATTICE_DATA', text="3 x 3 x 3").type = '3x3x3'
        col.operator("view3d.dc_add_lattice", icon='LATTICE_DATA', text="4 x 4 x 4").type = '4x4x4'

        # Top
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("view3d.dc_add_primitive", icon='MESH_PLANE', text="Plane").type = 'Plane'
        col.operator("view3d.dc_add_primitive", icon='MESH_CUBE', text="Cube").type = 'Cube'

        # Top Left
        # Top Right
        # Bottom Left
        # Bottom Right


class DC_OT_add_primitive(bpy.types.Operator):
    bl_idname = "view3d.dc_add_primitive"
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
            bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.50, vertices=64)

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
        active = None
        if context.mode == 'EDIT_MESH':
            was_edit = True
            active = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.mesh.primitive_cube_add(size=radius * 2)

        cube = context.active_object
        mod_subd = cube.modifiers.new("dc_temp_subd", 'SUBSURF')
        mod_subd.levels = levels
        mod_sphere = cube.modifiers.new("dc_temp_cast", 'CAST')
        mod_sphere.factor = 1
        mod_sphere.radius = radius
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_subd.name)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_sphere.name)

        if was_edit:
            active.select_set(True)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    def execute(self, context):
        cursor_location = tuple(context.scene.cursor_location)

        if context.object is None or (context.object.type == 'MESH' and context.object.data.total_vert_sel == 0):
            self.add_primitive(context)
        elif context.object.type == 'MESH' and tuple(context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            active = context.view_layer.objects.active
            saved_orientation = context.scene.transform_orientation_slots[0].type

            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self.add_primitive(context)

            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0, 0, 0), constraint_axis=(
                False, False, False), constraint_orientation='AddAxis', mirror=False, proportional='DISABLED')
            active.select_set(state=True)
            context.view_layer.objects.active = active
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            context.scene.transform_orientation_slots[0].type = saved_orientation
        else:
            bpy.ops.view3d.snap_cursor_to_selected()
            self.add_primitive(context)

        context.scene.cursor_location = cursor_location
        return {'FINISHED'}


class DC_OT_add_lattice(bpy.types.Operator):
    bl_idname = "view3d.dc_add_lattice"
    bl_label = "DC Add Lattice"
    bl_description = "Add pre-configured lattice surrounding the selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(name="Type")

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == "MESH" and active_object.select_get()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        target = context.active_object
        lattice = self.create_lattice_obj(context, target)
        self.create_lattice_mod(target, lattice)

        bpy.ops.object.select_all(action='DESELECT')

        helpers_collection = utils.make_collection(context.scene.collection, "DC_helpers")
        helpers_collection.objects.link(lattice)
        context.view_layer.objects.active = lattice
        lattice.select_set(True)

        return {'FINISHED'}

    def create_lattice_obj(self, context, target):
        # Create lattice
        lattice = bpy.data.lattices.new('DC_lattice')
        lattice_object = bpy.data.objects.new('DC_lattice', lattice)

        if self.type == "3x3x3":
            lattice.points_u = 3
            lattice.points_v = 3
            lattice.points_w = 3
        elif self.type == "4x4x4":
            lattice.points_u = 4
            lattice.points_v = 4
            lattice.points_w = 4

        lattice.interpolation_type_u = 'KEY_BSPLINE'
        lattice.interpolation_type_v = 'KEY_BSPLINE'
        lattice.interpolation_type_w = 'KEY_BSPLINE'
        lattice.use_outside = False

        # Position + Orientation
        lattice_object.location = self.find_world_center(target)
        lattice_object.scale = target.dimensions * 1.1
        lattice_object.rotation_euler = target.rotation_euler

        return lattice_object

    def create_lattice_mod(self, target, lattice):
        mod = target.modifiers.new(lattice.name, "LATTICE")
        mod.object = lattice

    def find_world_center(self, target):
        local_bbox = [Vector(v) for v in target.bound_box]
        world_bbox = [target.matrix_world @ v for v in local_bbox]

        min_vec = Vector(world_bbox[0])
        max_vec = Vector(world_bbox[0])

        for v in world_bbox:
            if v.x < min_vec.x:
                min_vec.x = v.x
            if v.y < min_vec.y:
                min_vec.y = v.y
            if v.z < min_vec.z:
                min_vec.z = v.z

            if v.x > max_vec.x:
                max_vec.x = v.x
            if v.y > max_vec.y:
                max_vec.y = v.y
            if v.z > max_vec.z:
                max_vec.z = v.z

        # Return center
        return ((min_vec + max_vec) / 2)


class DC_OT_add_edge_curve(bpy.types.Operator):
    bl_idname = "view3d.dc_add_edge_curve"
    bl_label = "DC Add Edge Curve"
    bl_description = "Add curve following a path of connected edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == "MESH" and active_object.select_get()

    def invoke(self, context, event):
        if context.mode == 'EDIT_MESH':
            if context.object.data.total_edge_sel > 0:
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                context.view_layer.objects.active = context.selected_objects[-1]
            else:
                return {'CANCELLED'}

        bpy.ops.object.convert(target='CURVE')
        if context.active_object.type != 'CURVE':
            return {'CANCELLED'}

        curve = context.active_object
        curve.data.dimensions = '3D'
        curve.data.fill_mode = 'FULL'
        curve.data.resolution_u = 3
        curve.data.bevel_depth = 0.0
        curve.data.bevel_resolution = 2
        curve.data.splines[0].use_smooth = True

        self.mouse_x = event.mouse_x
        self.original_depth = curve.data.bevel_depth
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        curve = context.active_object

        if event.type == 'MOUSEMOVE':
            delta = event.mouse_x - self.mouse_x
            curve.data.bevel_depth = self.original_depth + delta * 0.01
        elif event.type == 'WHEELUPMOUSE':
            if curve.data.bevel_resolution < 6:
                curve.data.bevel_resolution += 1
        elif event.type == 'WHEELDOWNMOUSE':
            if curve.data.bevel_resolution > 0:
                curve.data.bevel_resolution -= 1

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
