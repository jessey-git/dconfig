# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Adds primitives at center of selected elements
#

import bpy


class DC_MT_add_primitive_pie(bpy.types.Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1.5
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="6").type = 'Circle_6'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="8").type = 'Circle_8'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="16").type = 'Circle_16'
        col.operator("view3d.dc_add_primitive", icon='MESH_CIRCLE', text="32").type = 'Circle_32'

        # Right
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1.5
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="6").type = 'Cylinder_6'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="8").type = 'Cylinder_8'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="16").type = 'Cylinder_16'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="32").type = 'Cylinder_32'
        col.operator("view3d.dc_add_primitive", icon='MESH_CYLINDER', text="64").type = 'Cylinder_64'

        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1.5
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="12").type = 'Sphere_12'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="24").type = 'Sphere_24'
        col.operator("view3d.dc_add_primitive", icon='MESH_UVSPHERE', text="32").type = 'Sphere_32'

        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1.5
        col.operator("view3d.dc_add_primitive", icon='MESH_PLANE', text="Plane").type = 'Plane'
        col.operator("view3d.dc_add_primitive", icon='MESH_CUBE', text="Cube").type = 'Cube'


class DC_OT_add_primitive(bpy.types.Operator):
    bl_idname = "view3d.dc_add_primitive"
    bl_label = "DC Add Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(name="Type")

    def add_primitive(self):
        if self.type == 'Cube':
            bpy.ops.mesh.primitive_cube_add(size=1.0)

        elif self.type == 'Plane':
            bpy.ops.mesh.primitive_plane_add()
        elif self.type == 'Circle_6':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.25, vertices=6)
        elif self.type == 'Circle_8':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.25, vertices=8)
        elif self.type == 'Circle_16':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.50, vertices=16)
        elif self.type == 'Circle_32':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.50, vertices=32)

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

    def invoke(self, context, event):
        cur = bpy.context.scene.cursor_location
        cur = list(cur)

        t_axis = bpy.context.scene.transform_orientation

        if bpy.context.object.data.total_vert_sel == 0:
            self.add_primitive()
        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            active = bpy.context.view_layer.objects.active
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()

            self.add_primitive()

            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0, 0, 0), constraint_axis=(
                False, False, False), constraint_orientation='AddAxis', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.0)
            active.select_set(state=True)
            bpy.context.view_layer.objects.active = active
            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.view3d.snap_cursor_to_selected()
            self.add_primitive()

        bpy.context.scene.cursor_location = cur
        bpy.data.scenes[0].transform_orientation = t_axis
        return {'FINISHED'}
