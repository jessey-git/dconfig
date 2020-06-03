# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Adds primitives at center of selected elements
#

import math
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
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "6", prim_type='Cylinder', radius=0.25, depth=0.25, vertices=6, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "8", prim_type='Cylinder', radius=0.25, depth=0.25, vertices=8, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "16", prim_type='Cylinder', radius=0.50, depth=0.50, vertices=16, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CYLINDER', "32", prim_type='Cylinder', radius=0.50, depth=0.50, vertices=32, align=align)

        col.separator()
        dc.setup_op(col, "dconfig.add_primitive", 'CURVE_BEZCURVE', "Bezier", prim_type='B_Curve', radius=0.50, align=align)
        dc.setup_op(col, "dconfig.add_edge_curve", 'CURVE_NCIRCLE', "Edge Curve")

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "6", prim_type='Circle', radius=0.25, vertices=6, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "8", prim_type='Circle', radius=0.25, vertices=8, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "16", prim_type='Circle', radius=0.50, vertices=16, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CIRCLE', "32", prim_type='Circle', radius=0.50, vertices=32, align=align)

        col.separator()
        dc.setup_op(col, "dconfig.add_primitive", 'CURVE_BEZCIRCLE', "Circle", prim_type='B_Circle', radius=0.50, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_CAPSULE', "Capsule", prim_type='Oval', radius=0.125, length=0.5, vertices_2=8, align=align)

        # Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "12", prim_type='Sphere', radius=0.25, segments=12, ring_count=6, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "24", prim_type='Sphere', radius=0.50, segments=24, ring_count=12, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "32", prim_type='Sphere', radius=0.50, segments=32, ring_count=16, align=align)

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.1
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 1", prim_type='Quad_Sphere', radius=0.50, levels=1, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 2", prim_type='Quad_Sphere', radius=0.50, levels=2, align=align)
        dc.setup_op(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 3", prim_type='Quad_Sphere', radius=0.50, levels=3, align=align)

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
    depth: bpy.props.FloatProperty(name="Depth", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    length: bpy.props.FloatProperty(name="Length", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    size: bpy.props.FloatProperty(name="Size", default=1.0, step=1, min=0.01, precision=3, unit='LENGTH')
    segments: bpy.props.IntProperty(name="Segments", default=12, min=3, max=40)
    ring_count: bpy.props.IntProperty(name="Rings", default=6, min=3, max=20)
    vertices: bpy.props.IntProperty(name="Vertices", default=8, min=3, max=150)
    vertices_2: bpy.props.IntProperty(name="Vertices", default=4, step=2, min=6, max=32)
    levels: bpy.props.IntProperty(name="Levels", default=1, min=1, max=5)
    align: bpy.props.StringProperty(name="Align", default='WORLD')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, "prim_type")
        layout.separator()
        if self.prim_type == 'Cube' or self.prim_type == 'Plane':
            layout.prop(self, "size")
        elif self.prim_type == 'Circle':
            layout.prop(self, "radius")
            layout.prop(self, "vertices")
        elif self.prim_type == 'Oval':
            layout.prop(self, "radius")
            layout.prop(self, "length")
            layout.prop(self, "vertices_2")
        elif self.prim_type == 'Cylinder':
            layout.prop(self, "radius")
            layout.prop(self, "depth")
            layout.prop(self, "vertices")
        elif self.prim_type == 'Sphere':
            layout.prop(self, "radius")
            layout.prop(self, "segments")
            layout.prop(self, "ring_count")
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

        elif self.prim_type == 'Cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=self.radius, depth=self.depth, vertices=self.vertices, align=self.align)

        elif self.prim_type == 'Sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, segments=self.segments, ring_count=self.ring_count, align=self.align)

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

        def prepare_geo(bm_mod, verts):
            new_geo = bmesh.ops.contextual_create(bm_mod, geom=verts, mat_nr=0, use_smooth=False)

            grid_fill_edges = []
            for e in new_geo['faces'][0].edges:
                v1_y = e.verts[0].co.y
                v2_y = e.verts[1].co.y
                if v1_y * v2_y > 0.0001:
                    grid_fill_edges.append(e)

            grid_faces = bmesh.ops.grid_fill(bm_mod, edges=grid_fill_edges)
            bmesh.ops.delete(bm_mod, geom=new_geo['faces'], context='FACES_ONLY')
            return grid_faces['faces']

        if context.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')

            prepare_geo(bm, bm.verts)

            me = bpy.data.meshes.new("Oval")
            bm.to_mesh(me)
            bm.free()

            obj = bpy.data.objects.new("Oval", me)
            if align == 'CURSOR':
                obj.matrix_world = context.scene.cursor.matrix.copy()
            elif align == 'VIEW':
                mat = context.space_data.region_3d.view_matrix.transposed().to_4x4()
                mat.translation = context.scene.cursor.location
                obj.matrix_world = mat
            else:
                obj.matrix_world.translation = context.scene.cursor.location

            context.collection.objects.link(obj)
            dc.make_active_object(context, obj)
        else:
            bpy.ops.mesh.select_all(action='DESELECT')

            bm_orig = bmesh.from_edit_mesh(context.active_object.data)
            new_verts = [bm_orig.verts.new(v.co) for v in bm.verts]
            new_faces = prepare_geo(bm_orig, new_verts)

            new_face_verts = set()
            for f in new_faces:
                for v in f.verts:
                    new_face_verts.add(v)

            if align == 'CURSOR':
                bmesh.ops.transform(bm_orig, verts=list(new_face_verts), matrix=context.scene.cursor.matrix)
            elif align == 'VIEW':
                mat = context.space_data.region_3d.view_matrix.transposed().to_4x4()
                mat.translation = context.scene.cursor.location
                bmesh.ops.transform(bm_orig, verts=list(new_face_verts), matrix=mat)
            else:
                new_location = context.active_object.matrix_world.inverted() @ context.scene.cursor.location
                bmesh.ops.translate(bm_orig, verts=list(new_face_verts), vec=new_location)

            bmesh.update_edit_mesh(context.active_object.data)

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
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_subd.name)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_sphere.name)

        if was_edit:
            dc.make_active_object(context, prev_active)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

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

            # Extract transformation matrix only if 1 face is selected
            if context.active_object.data.total_face_sel == 1:
                bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
                context.scene.cursor.matrix = context.scene.transform_orientation_slots[0].custom_orientation.matrix.to_4x4()

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
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', offset_type='OFFSET', vertex_only=True, clamp_overlap=True)

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
