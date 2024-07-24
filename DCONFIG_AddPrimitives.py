# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Adds primitives at center of selected elements
#

import math
import random
from itertools import zip_longest

import bpy
import bmesh
from mathutils import (Vector, Matrix)

from . import DCONFIG_Utils as dc


class DCONFIG_MT_add_primitive_pie(bpy.types.Menu):
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        align = 'WORLD' if context.space_data.region_3d.is_perspective else 'VIEW'

        # Left
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        if context.mode == 'OBJECT':
            dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "Dynamic", prim_type='Geo-Cylinder', radius=0.50, depth=0.25, vertices=8, align=align)
            col.separator(factor=0.25)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "8", prim_type='Cylinder', radius=0.50, depth=0.25, vertices=8, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "16", prim_type='Cylinder', radius=0.50, depth=0.50, vertices=16, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "32", prim_type='Cylinder', radius=0.50, depth=0.50, vertices=32, align=align)

        col.separator()
        dc.setup_op(col, "dconfig.add_primitive", 'CURVE_BEZCURVE', "Bezier", prim_type='B_Curve', radius=0.50, align=align)
        dc.setup_op(col, "dconfig.add_edge_curve", 'CURVE_NCIRCLE', "Edge Curve")
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Dish-1", prim_type='Dish-1', radius=1, segments=24, ring_count=8, focal_point=0.75, align=align)
        if context.mode == 'OBJECT':
            col.separator(factor=0.25)
            dc.setup_op(col, "dconfig.add_techring", 'DISC', "Tech Ring", align=align)

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        if context.mode == 'OBJECT':
            dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "Dynamic", prim_type='Geo-Circle', radius=0.50, vertices=8, align=align)
            col.separator(factor=0.25)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "8", prim_type='Circle', radius=0.50, vertices=8, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "16", prim_type='Circle', radius=0.50, vertices=16, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "32", prim_type='Circle', radius=0.50, vertices=32, align=align)

        col.separator()
        dc.setup_op(col, "dconfig.add_primitive", 'CURVE_BEZCIRCLE', "Circle", prim_type='B_Circle', radius=0.50, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CAPSULE', "Capsule", prim_type='Oval', radius=0.125, length=0.5, vertices_2=10, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Dish-2", prim_type='Dish-2', radius=1, vertices_2=24, focal_point=0.75, align=align)

        # Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "12", prim_type='Sphere', radius=0.50, segments=12, ring_count=6, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "24", prim_type='Sphere', radius=0.50, segments=24, ring_count=12, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "32", prim_type='Sphere', radius=0.50, segments=32, ring_count=16, align=align)

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 2", prim_type='Quad_Sphere', radius=0.50, levels=2, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 3", prim_type='Quad_Sphere', radius=0.50, levels=3, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 4", prim_type='Quad_Sphere', radius=0.50, levels=4, align=align)

        # Bottom
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.2

        has_collections = bool(bpy.data.collections)
        if has_collections:
            if len(bpy.data.collections) > 10:
                col.operator_context = 'INVOKE_REGION_WIN'
                dc.setup_op(col, "object.collection_instance_add", 'OUTLINER_OB_GROUP_INSTANCE', "Collections...")
            else:
                col.operator_context = 'EXEC_REGION_WIN'
                col.operator_menu_enum(
                    "object.collection_instance_add",
                    "collection",
                    text="Collections",
                    icon='OUTLINER_OB_GROUP_INSTANCE',
                )

        # Top
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_PLANE', "Plane", prim_type='Plane', size=1, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CUBE', "Cube", prim_type='Cube', size=1, align=align)

        # Top Left
        split = pie.split()

        # Top Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        dc.setup_op(col, "dconfig.add_primitive", 'VIEW_CAMERA', "", prim_type='Camera', align=align)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        dc.setup_op(col, "dconfig.add_primitive", 'EMPTY_DATA', "", prim_type='Empty', radius=0.25, align=align)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        dc.setup_op(col, "dconfig.add_primitive", 'LIGHT_POINT', "", prim_type='Light', light_type='POINT', radius=1, align=align)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        dc.setup_op(col, "dconfig.add_primitive", 'LIGHT_SUN', "", prim_type='Light', light_type='SUN', radius=1, align=align)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        dc.setup_op(col, "dconfig.add_primitive", 'LIGHT_AREA', "", prim_type='Light', light_type='AREA', radius=1, align=align)

        # Bottom Left
        split = pie.split()

        # Bottom Right
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25

        menu_name = 'VIEW3D_MT_add'
        if context.mode == 'EDIT':
            menu_name = 'VIEW3D_MT_mesh_add'
        elif context.mode == 'EDIT_CURVE':
            menu_name = 'VIEW3D_MT_curve_add'

        dc.setup_op(col, "wm.call_menu", 'DOT', "All", name=menu_name)


class DCONFIG_OT_add_primitive(bpy.types.Operator):
    bl_idname = "dconfig.add_primitive"
    bl_label = "DC Add Primitive"
    bl_description = "Add pre-configured primitives and align to currently selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    prim_type: bpy.props.StringProperty(name="Type")
    light_type: bpy.props.StringProperty(name="Light Type")
    radius: bpy.props.FloatProperty(name="Radius", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    focal_point: bpy.props.FloatProperty(name="Focal Point", default=0.5, step=1, min=0.01, precision=3, unit='LENGTH')
    depth: bpy.props.FloatProperty(name="Depth", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    length: bpy.props.FloatProperty(name="Length", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    size: bpy.props.FloatProperty(name="Size", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    segments: bpy.props.IntProperty(name="Segments", default=12, min=3, max=40)
    ring_count: bpy.props.IntProperty(name="Rings", default=6, min=3, max=20)
    vertices: bpy.props.IntProperty(name="Vertices", default=8, min=3, max=150)
    vertices_2: bpy.props.IntProperty(name="Vertices", default=4, step=2, min=6, max=48)
    levels: bpy.props.IntProperty(name="Levels", default=1, min=1, max=5)
    align: bpy.props.StringProperty(name="Align", default='WORLD')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, "prim_type")
        layout.separator()
        if self.prim_type in ('Cube', 'Plane'):
            layout.prop(self, "size")
        elif self.prim_type in ('Circle', 'Geo-Circle'):
            layout.prop(self, "vertices")
            layout.prop(self, "radius")
        elif self.prim_type == 'Oval':
            layout.prop(self, "vertices_2")
            layout.prop(self, "radius")
            layout.prop(self, "length")
        elif self.prim_type in ('Cylinder', 'Geo-Cylinder'):
            layout.prop(self, "vertices")
            layout.prop(self, "radius")
            layout.prop(self, "depth")
        elif self.prim_type == 'Sphere':
            layout.prop(self, "radius")
            layout.prop(self, "segments")
            layout.prop(self, "ring_count")
        elif self.prim_type == 'Dish-1':
            layout.prop(self, "radius")
            layout.prop(self, "focal_point")
            layout.prop(self, "segments")
            layout.prop(self, "ring_count")
        elif self.prim_type == 'Dish-2':
            layout.prop(self, "vertices_2")
            layout.prop(self, "radius")
            layout.prop(self, "focal_point")
        elif self.prim_type == 'Quad_Sphere':
            layout.prop(self, "radius")
            layout.prop(self, "levels")

    def add_primitive(self, context):
        if self.prim_type == 'Cube':
            bpy.ops.mesh.primitive_cube_add(size=self.size, align=self.align)

        elif self.prim_type == 'Plane':
            bpy.ops.mesh.primitive_plane_add(size=self.size, align=self.align)

        elif self.prim_type == 'Circle':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=self.radius, vertices=self.vertices, align=self.align)

        elif self.prim_type == 'Geo-Circle':
            self.add_geo_circle(context, self.radius, self.vertices, self.align)

        elif self.prim_type == 'Cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=self.radius, depth=self.depth, vertices=self.vertices, align=self.align)

        elif self.prim_type == 'Geo-Cylinder':
            self.add_geo_cylinder(context, self.radius, self.depth, self.vertices, self.align)

        elif self.prim_type == 'Sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, segments=self.segments, ring_count=self.ring_count, align=self.align)

        elif self.prim_type == 'Dish-1':
            self.add_dish(context, self.radius, self.focal_point, self.segments, self.ring_count, self.align)
        elif self.prim_type == 'Dish-2':
            self.add_quad_dish(context, self.radius, self.focal_point, self.vertices_2, self.align)

        elif self.prim_type == 'Oval':
            self.add_oval(context, self.radius, self.length, self.vertices_2, self.align)

        elif self.prim_type == 'Quad_Sphere':
            self.add_quad_sphere(context, self.radius, self.levels, self.align)

        elif self.prim_type == 'B_Curve':
            bpy.ops.curve.primitive_bezier_curve_add(radius=self.radius, enter_editmode=False, align=self.align)

        elif self.prim_type == 'B_Circle':
            bpy.ops.curve.primitive_bezier_circle_add(radius=self.radius, enter_editmode=False, align=self.align)

        elif self.prim_type == 'Light':
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.light_add(type=self.light_type, radius=self.radius, align=self.align)

        elif self.prim_type == 'Camera':
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.camera_add(align=self.align)

        elif self.prim_type == 'Empty':
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius=self.radius, align=self.align)

        if self.align != 'WORLD' and context.mode == 'OBJECT' and context.active_object.type == 'MESH':
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    def add_oval(self, context, radius, length, vertices, align):
        bm = bmesh.new()

        bmesh.ops.create_circle(bm, cap_ends=False, radius=radius, segments=vertices - 2)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x < -0.0001], context='VERTS')
        bmesh.ops.translate(bm, verts=bm.verts, vec=(length / 2, 0.0, 0.0))
        bmesh.ops.mirror(bm, geom=bm.verts, axis='X', merge_dist=0.0001)

        new_geo = bmesh.ops.contextual_create(bm, geom=bm.verts, mat_nr=0, use_smooth=False)

        grid_fill_edges = []
        for e in new_geo['faces'][0].edges:
            v1_y = e.verts[0].co.y
            v2_y = e.verts[1].co.y
            if v1_y * v2_y > 0.0001:
                grid_fill_edges.append(e)

        bmesh.ops.grid_fill(bm, edges=grid_fill_edges)
        bmesh.ops.delete(bm, geom=new_geo['faces'], context='FACES_ONLY')

        dc.add_new_bmesh(context, "Oval", bm, align)

    def add_dish(self, context, radius, focal_point, segments, ring_count, align):
        bm = bmesh.new()

        prev_z = 0
        orig_face = None
        step = radius / ring_count
        for r in reversed(range(ring_count)):
            x = (r + 1) * step
            z = (x**2) / (4 * self.focal_point)

            if orig_face is None:
                new_geo = bmesh.ops.create_circle(bm, cap_ends=True, radius=x, segments=segments)
                bmesh.ops.translate(bm, verts=new_geo['verts'], vec=(0.0, 0.0, z))
                orig_face = bm.faces[:]
            else:
                bmesh.ops.inset_individual(bm, faces=orig_face, use_even_offset=False, thickness=step, depth=z - prev_z)

            prev_z = z

        new_geo = bmesh.ops.poke(bm, faces=orig_face)
        new_geo['verts'][0].co.z = 0

        dc.add_new_bmesh(context, "Dish", bm, align)

    def add_quad_dish(self, context, radius, focal_point, vertices, align):
        bm = bmesh.new()

        bmesh.ops.create_circle(bm, cap_ends=False, radius=radius, segments=vertices)

        grid_fill_edges = []
        span = vertices / 4
        mid = vertices / 2
        for e in bm.edges:
            index = e.index
            if (index < mid and index >= span) or (index >= mid and index >= (mid + span)):
                grid_fill_edges.append(e)

        bmesh.ops.grid_fill(bm, edges=grid_fill_edges)

        for v in bm.verts:
            z = (v.co.x**2 + v.co.y**2) / (4 * focal_point)
            v.co = (v.co.x, v.co.y, z)

        bm.normal_update()
        dc.add_new_bmesh(context, "QuadDish", bm, align)

    def add_quad_sphere(self, context, radius, levels, align):
        was_edit = False
        prev_active = None
        if context.mode == 'EDIT_MESH':
            was_edit = True
            prev_active = context.active_object
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.mesh.primitive_cube_add(size=radius * 2, align=align)

        quad_sphere = context.active_object
        dc.rename(quad_sphere, "QuadSphere")

        mod_subd = quad_sphere.modifiers.new("dc_temp_subd", 'SUBSURF')
        mod_subd.levels = levels
        mod_sphere = quad_sphere.modifiers.new("dc_temp_cast", 'CAST')
        mod_sphere.factor = 1
        mod_sphere.radius = radius

        bpy.ops.object.modifier_apply(modifier=mod_subd.name)
        bpy.ops.object.modifier_apply(modifier=mod_sphere.name)

        if was_edit:
            dc.make_active_object(context, prev_active)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    def add_geo_circle(self, context, radius, vertices, align):
        bm = bmesh.new()
        dc.add_new_bmesh(context, "geo-circle", bm, align)

        mod = context.active_object.modifiers.new(name="dc_circle", type="NODES")

        node_group = next((ng for ng in bpy.data.node_groups if ng.name == "dc_circle"), None)
        if node_group is None:
            node_group = bpy.data.node_groups.new("dc_circle", 'GeometryNodeTree')

            if bpy.app.version_file <= (4, 0, 22):
                node_group.inputs.new('NodeSocketGeometry', "Geometry")
                node_group.outputs.new('NodeSocketGeometry', "Geometry")
                self.new_input_link_pre4(node_group, 'NodeSocketInt', "Vertices", "vertices")
                self.new_input_link_pre4(node_group, 'NodeSocketFloatDistance', "Radius", "radius")
            else:
                node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
                self.new_input_link(node_group, 'NodeSocketInt', 'NONE', "Vertices", "vertices")
                self.new_input_link(node_group, 'NodeSocketFloat', 'DISTANCE', "Radius", "radius")

            node_input = node_group.nodes.new('NodeGroupInput')
            node_output = node_group.nodes.new('NodeGroupOutput')
            node_circle = node_group.nodes.new("GeometryNodeMeshCircle")
            node_circle.fill_type = 'TRIANGLE_FAN'

            node_group.links.new(node_input.outputs["Vertices"], node_circle.inputs.get("Vertices"))
            node_group.links.new(node_input.outputs["Radius"], node_circle.inputs.get("Radius"))
            node_group.links.new(node_circle.outputs.get("Mesh"), node_output.inputs.get("Geometry"))

            self.finalize_node_io(node_input, node_output)
        else:
            node_input = node_group.nodes.get("Group Input")

        mod.node_group = node_group
        mod[node_input.outputs["Vertices"].identifier] = vertices
        mod[node_input.outputs["Radius"].identifier] = radius

    def add_geo_cylinder(self, context, radius, depth, vertices, align):
        bm = bmesh.new()
        dc.add_new_bmesh(context, "geo-cylinder", bm, align)

        mod = context.active_object.modifiers.new(name="dc_cylinder", type="NODES")

        node_group = next((ng for ng in bpy.data.node_groups if ng.name == "dc_cylinder"), None)
        if node_group is None:
            node_group = bpy.data.node_groups.new("dc_cylinder", 'GeometryNodeTree')
            if bpy.app.version_file <= (4, 0, 22):
                node_group.inputs.new('NodeSocketGeometry', "Geometry")
                node_group.outputs.new('NodeSocketGeometry', "Geometry")
                self.new_input_link_pre4(node_group, 'NodeSocketInt', "Vertices", "vertices")
                self.new_input_link_pre4(node_group, 'NodeSocketFloatDistance', "Radius", "radius")
                self.new_input_link_pre4(node_group, 'NodeSocketFloatDistance', "Depth", "depth")
            else:
                node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
                self.new_input_link(node_group, 'NodeSocketInt', 'NONE', "Vertices", "vertices")
                self.new_input_link(node_group, 'NodeSocketFloat', 'DISTANCE', "Radius", "radius")
                self.new_input_link(node_group, 'NodeSocketFloat', 'DISTANCE', "Depth", "depth")

            node_input = node_group.nodes.new('NodeGroupInput')
            node_output = node_group.nodes.new('NodeGroupOutput')
            node_cylinder = node_group.nodes.new("GeometryNodeMeshCylinder")

            node_group.links.new(node_input.outputs["Vertices"], node_cylinder.inputs.get("Vertices"))
            node_group.links.new(node_input.outputs["Radius"], node_cylinder.inputs.get("Radius"))
            node_group.links.new(node_input.outputs["Depth"], node_cylinder.inputs.get("Depth"))
            node_group.links.new(node_cylinder.outputs.get("Mesh"), node_output.inputs.get("Geometry"))

            self.finalize_node_io(node_input, node_output)
        else:
            node_input = node_group.nodes.get("Group Input")

        mod.node_group = node_group
        mod[node_input.outputs["Vertices"].identifier] = vertices
        mod[node_input.outputs["Radius"].identifier] = radius
        mod[node_input.outputs["Depth"].identifier] = depth

    def finalize_node_io(self, node_input, node_output):
        node_output.is_active_output = True
        node_input.select = False
        node_output.select = False

        node_input.location.x = -200 - node_input.width
        node_output.location.x = 200

    def new_input_link(self, node_group, socket_type, socket_subtype, socket_name, prop_name):
        prop = self.rna_type.properties[prop_name]

        s_in = node_group.interface.new_socket(socket_name, in_out='INPUT', socket_type=socket_type)
        s_in.subtype = socket_subtype
        s_in.default_value = prop.default
        s_in.min_value = prop.hard_min
        s_in.max_value = prop.hard_max


    def new_input_link_pre4(self, node_group, socket_type, socket_name, prop_name):
        prop = self.rna_type.properties[prop_name]

        s_in = node_group.inputs.new(socket_type, socket_name)
        s_in.default_value = prop.default
        s_in.min_value = prop.hard_min
        s_in.max_value = prop.hard_max

    def execute(self, context):
        dc.trace_enter(self)
        prev_cursor_location = context.scene.cursor.location.copy()
        prev_cursor_matrix = context.scene.cursor.matrix.copy()
        is_edit_mode = context.mode == 'EDIT_MESH'

        if context.active_object is None or (not context.selected_objects) or (is_edit_mode and context.active_object.data.total_vert_sel == 0):
            dc.trace(1, "Adding {} at cursor", self.prim_type)
            self.add_primitive(context)
        elif context.active_object.type == 'MESH' and is_edit_mode and tuple(context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            dc.trace(1, "Adding {} aligned to selected faces", self.prim_type)
            prev_active = context.active_object

            try:
                bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
                context.scene.cursor.matrix = context.scene.transform_orientation_slots[0].custom_orientation.matrix.to_4x4()
            except RuntimeError:
                pass

            bpy.ops.view3d.snap_cursor_to_selected()

            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            self.align = 'CURSOR'
            self.add_primitive(context)

            new_object = context.active_object
            if new_object.type == 'MESH':
                dc.make_active_object(context, prev_active)
                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        else:
            dc.trace(1, "Adding {} at selection", self.prim_type)
            bpy.ops.view3d.snap_cursor_to_selected()
            self.add_primitive(context)

        context.scene.cursor.matrix = prev_cursor_matrix
        context.scene.cursor.location = prev_cursor_location
        return dc.trace_exit(self)


class DCONFIG_OT_add_techring(bpy.types.Operator):
    bl_idname = "dconfig.add_techring"
    bl_label = "DC Add Tech-Ring"
    bl_description = "Adds a tech-ring mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def sanitize_inputs(self, context):
        if self.ring_count_max < self.ring_count_min:
            self.ring_count_max = self.ring_count_min

        if self.track_width_max < self.track_width_min:
            self.track_width_max = self.track_width_min

        if self.arc_max < self.arc_min:
            self.arc_max = self.arc_min

    seed: bpy.props.IntProperty(name="Seed", default=0, min=0)
    align: bpy.props.StringProperty(name="Align", default='WORLD')

    arc_count: bpy.props.IntProperty(name="Arc count", default=36, min=8, max=128, step=4)
    track_count: bpy.props.IntProperty(name="Track count", default=20, min=8, max=32)

    ring_count_min: bpy.props.IntProperty(name="Ring count min", default=2,  min=1, max=32, update=sanitize_inputs)
    ring_count_max: bpy.props.IntProperty(name="Ring count max", default=10,  min=1, max=32, update=sanitize_inputs)
    ring_count_bonus: bpy.props.IntProperty(name="Ring count bonus", default=0,  min=0, max=2)

    track_width_min: bpy.props.IntProperty(name="Track width min", default=1, min=1, max=32, update=sanitize_inputs)
    track_width_max: bpy.props.IntProperty(name="Track width max", default=4, min=1, max=32, update=sanitize_inputs)

    arc_min: bpy.props.FloatProperty(name="Arc min", default=math.radians(90), min=math.radians(30), max=128, step=1000, subtype='ANGLE', update=sanitize_inputs)
    arc_max: bpy.props.FloatProperty(name="Arc max", default=math.radians(340), min=math.radians(30), max=128, step=1000, subtype='ANGLE', update=sanitize_inputs)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, "seed")

        layout.separator()
        layout.prop(self, "arc_count")
        layout.prop(self, "track_count")

        layout.separator()
        layout.prop(self, "ring_count_min")
        layout.prop(self, "ring_count_max")
        layout.prop(self, "ring_count_bonus")

        layout.separator()
        layout.prop(self, "track_width_min")
        layout.prop(self, "track_width_max")

        layout.separator()
        layout.prop(self, "arc_min")
        layout.prop(self, "arc_max")

    def execute(self, context):
        dc.trace_enter(self)

        def random_arc_to_span(min_angle_rad, max_angle_rad):
            rand_deg = random.randrange(int(math.degrees(min_angle_rad)), int(math.degrees(max_angle_rad)) + 1, 10)
            return int(self.arc_count * (rand_deg / 360.0))

        def mark_faces(bm, track_start, track_end, span_start, span_end, material_index):
            track_end = min(track_end, self.track_count)
            for track in range(track_start, track_end):
                track_offset = track * self.arc_count
                for span in range(span_start, span_end):
                    face_offset = track_offset + (span % self.arc_count)
                    bm.faces[face_offset].material_index = material_index

        aspect_x = math.pi / 2
        aspect_y = (math.pi * 0.14) / 2
        mat = Matrix.Scale(aspect_x, 4, (1.0, 0.0, 0.0)) @ Matrix.Scale(aspect_y, 4, (0.0, 1.0, 0.0))
        mat = Matrix.Translation((0.0, aspect_y, 0.0)) @ mat

        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=self.arc_count, y_segments=self.track_count, size=1, matrix=mat, calc_uvs=True)
        bm.faces.ensure_lookup_table()

        random.seed(self.seed)

        ringCount = random.randrange(self.ring_count_min, self.ring_count_max + 1)
        for _ in range(ringCount):
            track_start = random.randrange(0, self.track_count + 1)
            track_end = track_start + random.randrange(self.track_width_min, self.track_width_max + 1)
            span_start = random_arc_to_span(0, math.pi * 2)
            span_end = span_start + random_arc_to_span(self.arc_min, self.arc_max)

            mark_faces(bm, track_start, track_end, span_start, span_end, 1)

        for _ in range(self.ring_count_bonus):
            track_start = random.randrange(0, self.track_count + 1)
            track_end = track_start + 1
            span_start = 0
            span_end = self.arc_count

            mark_faces(bm, track_start, track_end, span_start, span_end, random.randrange(0, 2))

        bm.normal_update()
        dc.add_new_bmesh(context, "TechRing", bm, self.align)

        self.create_mods(context.active_object)
        self.ensure_materials(context.active_object)

        return dc.trace_exit(self)

    def create_mods(self, target):
        bend_mod = target.modifiers.new("dc_bend", 'SIMPLE_DEFORM')
        bend_mod.deform_method = 'BEND'
        bend_mod.deform_axis = 'Z'
        bend_mod.angle = math.radians(360)

        target.modifiers.new("dc_weld", 'WELD')

    def ensure_materials(self, target):
        bpy.ops.object.material_slot_add()
        bpy.ops.object.material_slot_add()

        material = bpy.data.materials.get("dc_viewport_black")
        if material is None:
            material = bpy.data.materials.new("dc_viewport_black")
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.0, 0.0, 1)
            material.diffuse_color = (0.0, 0.0, 0.0, 1)

        target.data.materials[1] = material


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
            context.active_object.update_from_editmode()
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

            bpy.ops.mesh.bevel('INVOKE_DEFAULT', offset_type='OFFSET', affect='VERTICES', clamp_overlap=True)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # Modal
    # Mouse move: Adjust size of bevel
    # Mouse wheel: Adjust resolution of bevel
    def modal(self, context, event):
        if self.step == 0:
            return self.continue_or_finish(context, event)

        if self.step == 1:
            curve = context.active_object

            if event.type == 'MOUSEMOVE':
                delta_x = event.mouse_x - self.mouse_start_x
                curve.data.bevel_depth = self.original_depth + delta_x * 0.01
            elif event.type == 'WHEELUPMOUSE':
                if curve.data.bevel_resolution < 6:
                    curve.data.bevel_resolution += 1
            elif event.type == 'WHEELDOWNMOUSE':
                if curve.data.bevel_resolution > 0:
                    curve.data.bevel_resolution -= 1

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
        obj = context.selected_objects[-1]
        bpy.ops.object.select_all(action='DESELECT')
        dc.make_active_object(context, obj)

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

        self.mouse_start_x = event.mouse_x
        self.original_depth = curve.data.bevel_depth

    def make_even(self, context):
        def group_items(items, n):
            args = [iter(items)] * n
            return zip_longest(*args)

        curve = context.active_object
        points = curve.data.splines.active.points

        # Check if we need to do work...
        if len(points) < 3:
            bpy.ops.object.convert(target='MESH')
            return

        # Save previous pivot and orientation and set to desired values...
        prev_transform_pivot_point = context.scene.tool_settings.transform_pivot_point
        prev_orientation_type = context.scene.transform_orientation_slots[0].type
        context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        context.scene.transform_orientation_slots[0].type = 'GLOBAL'

        radius_adjustments = [None]
        normals = [None]

        # Calculate radius adjustments and axis for all points except the ends...
        for i in range(1, len(points) - 1):
            a = points[i - 1]
            b = points[i]
            c = points[i + 1]

            ba = a.co.to_3d() - b.co.to_3d()
            bc = c.co.to_3d() - b.co.to_3d()

            alpha = ba.angle(bc)
            beta = math.pi - alpha

            radius_adjustments.insert(i, abs(1 / math.cos(beta / 2)))
            normals.insert(i, ba.cross(bc).normalized())

        ring_size = 4 + 2 * curve.data.bevel_resolution

        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(curve.data)

        # Group Edge Loops (Assumes that vertices are created ring after ring)
        rings = list(group_items(bm.verts, ring_size))
        z_axis = Vector((0, 0, 1))

        for i in range(1, len(rings) - 1):
            for vertex in rings[i]:
                vertex.select = True

            if normals[i].length >= 0.001:
                # Create Rotation Matrices
                rotation_axis = normals[i].cross(z_axis)
                rotation_angle = normals[i].angle(z_axis)
                rotation_matrix = Matrix.Rotation(rotation_angle, 4, rotation_axis)
                backrotation_matrix = Matrix.Rotation(-rotation_angle, 4, rotation_axis)

                # Rotate, Scale, Rotate Back
                bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=rotation_matrix, verts=rings[i])
                bpy.ops.transform.resize(value=(radius_adjustments[i], radius_adjustments[i], 1), constraint_axis=(True, True, False))
                bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=backrotation_matrix, verts=rings[i])

            for vertex in rings[i]:
                vertex.select = False

        # Reset previous pivot and orientation
        context.scene.tool_settings.transform_pivot_point = prev_transform_pivot_point
        context.scene.transform_orientation_slots[0].type = prev_orientation_type

    def continue_or_finish(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            dc.trace(1, "Ending step {}", self.step)

            if self.step == 0:
                self.prepare(context)
                self.create_curve(context, event)

            self.step += 1
            if self.step == 2:
                self.make_even(context)
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
