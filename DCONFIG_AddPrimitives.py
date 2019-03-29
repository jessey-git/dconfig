# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
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

        def setop(layout, name, icon, text, prim_type, props):
            op = layout.operator(name, icon=icon, text=text)
            op.prim_type = prim_type
            for prop, value in props:
                setattr(op, prop, value)

        # Left
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        setop(col, "dconfig.add_primitive", 'MESH_CYLINDER', "6", prim_type='Cylinder', props=(("radius", 0.25), ("depth", 0.25), ("vertices", 6)))
        setop(col, "dconfig.add_primitive", 'MESH_CYLINDER', "8", prim_type='Cylinder', props=(("radius", 0.25), ("depth", 0.25), ("vertices", 8)))
        setop(col, "dconfig.add_primitive", 'MESH_CYLINDER', "16", prim_type='Cylinder', props=(("radius", 0.50), ("depth", 0.50), ("vertices", 16)))
        setop(col, "dconfig.add_primitive", 'MESH_CYLINDER', "32", prim_type='Cylinder', props=(("radius", 0.50), ("depth", 0.50), ("vertices", 32)))

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        setop(col, "dconfig.add_primitive", 'MESH_CIRCLE', "6", prim_type='Circle', props=(("radius", 0.25), ("vertices", 6)))
        setop(col, "dconfig.add_primitive", 'MESH_CIRCLE', "8", prim_type='Circle', props=(("radius", 0.25), ("vertices", 8)))
        setop(col, "dconfig.add_primitive", 'MESH_CIRCLE', "16", prim_type='Circle', props=(("radius", 0.50), ("vertices", 16)))
        setop(col, "dconfig.add_primitive", 'MESH_CIRCLE', "32", prim_type='Circle', props=(("radius", 0.50), ("vertices", 32)))

        # Right
        split = pie.split(align=True)
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "12", prim_type='Sphere', props=(("radius", 0.25), ("segments", 12), ("ring_count", 6)))
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "24", prim_type='Sphere', props=(("radius", 0.50), ("segments", 24), ("ring_count", 12)))
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "32", prim_type='Sphere', props=(("radius", 0.50), ("segments", 32), ("ring_count", 16)))

        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 1", prim_type='Quad_Sphere', props=(("levels", 1),))
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 2", prim_type='Quad_Sphere', props=(("levels", 2),))
        setop(col, "dconfig.add_primitive", 'MESH_UVSPHERE', "Quad 3", prim_type='Quad_Sphere', props=(("levels", 3),))

        # Bottom
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_edge_curve", icon='CURVE_NCIRCLE', text="Edge Curve")
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 2x2x2").resolution = 2
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 3x3x3").resolution = 3
        col.operator("dconfig.add_lattice", icon='LATTICE_DATA', text="FFD 4x4x4").resolution = 4

        # Top
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.scale_x = 1.25
        col.operator("dconfig.add_primitive", icon='MESH_PLANE', text="Plane").prim_type = 'Plane'
        col.operator("dconfig.add_primitive", icon='MESH_CUBE', text="Cube").prim_type = 'Cube'

        # Top Left
        # Top Right
        # Bottom Left
        # Bottom Right


class DCONFIG_OT_add_primitive(bpy.types.Operator):
    bl_idname = "dconfig.add_primitive"
    bl_label = "DC Add Primitive"
    bl_description = "Add pre-configured primitives and align to currently selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    prim_type: bpy.props.StringProperty(name="Type")
    radius: bpy.props.FloatProperty(name="Radius", default=1.0, step=1, min=0.01)
    depth: bpy.props.FloatProperty(name="Depth", default=1.0, step=1, min=0.01)
    size: bpy.props.FloatProperty(name="Size", default=1.0, step=1, min=0.01)
    segments: bpy.props.IntProperty(name="Segments", default=12, min=3, max=40)
    ring_count: bpy.props.IntProperty(name="Rings", default=6, min=3, max=20)
    vertices: bpy.props.IntProperty(name="Vertices", default=8, min=3, max=96)
    levels: bpy.props.IntProperty(name="Levels", default=1, min=1, max=5)

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
        is_ortho = not context.space_data.region_3d.is_perspective

        if self.prim_type == 'Cube':
            bpy.ops.mesh.primitive_cube_add(size=self.size)

        elif self.prim_type == 'Plane':
            bpy.ops.mesh.primitive_plane_add(size=self.size, view_align=is_ortho)

        elif self.prim_type == 'Circle':
            bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=self.radius, vertices=self.vertices, view_align=is_ortho)

        elif self.prim_type == 'Cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=self.radius, depth=self.depth, vertices=self.vertices)

        elif self.prim_type == 'Sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, segments=self.segments, ring_count=self.ring_count)

        elif self.prim_type == 'Quad_Sphere':
            self.add_quad_sphere(context, self.radius, self.levels)

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
        prev_cursor_location = tuple(context.scene.cursor.location)
        is_edit_mode = context.mode == 'EDIT_MESH'

        if context.active_object is None or (not context.selected_objects) or (is_edit_mode and context.active_object.data.total_vert_sel == 0):
            dc.trace(1, "Adding {} at cursor", self.prim_type)
            self.add_primitive(context)
        elif context.active_object.type == 'MESH' and is_edit_mode and tuple(context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            dc.trace(1, "Adding {} aligned to selected faces", self.prim_type)
            prev_active = context.active_object
            prev_orientation = context.scene.transform_orientation_slots[0].type

            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self.add_primitive(context)
            bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), constraint_axis=(False, False, False))

            context.view_layer.objects.active = prev_active
            context.view_layer.objects.active.select_set(True)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            context.scene.transform_orientation_slots[0].type = prev_orientation
        else:
            dc.trace(1, "Adding {} at selection", self.prim_type)
            bpy.ops.view3d.snap_cursor_to_selected()
            self.add_primitive(context)

        context.scene.cursor.location = prev_cursor_location
        return dc.trace_exit(self)


class DCONFIG_OT_add_lattice(bpy.types.Operator):
    bl_idname = "dconfig.add_lattice"
    bl_label = "DC Add Lattice"
    bl_description = "Add pre-configured lattice surrounding the selected geometry"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.IntProperty(name="Resolution", default=2, min=2, max=4)

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

        lattice.points_u = self.resolution
        lattice.points_v = self.resolution
        lattice.points_w = self.resolution

        lattice.interpolation_type_u = 'KEY_BSPLINE'
        lattice.interpolation_type_v = 'KEY_BSPLINE'
        lattice.interpolation_type_w = 'KEY_BSPLINE'
        lattice.use_outside = False

        # Position + Orientation
        self.set_transforms(target, lattice_object)

        # Place in a special collection
        helpers_collection = dc.get_helpers_collection(context)
        helpers_collection.objects.link(lattice_object)

        # Ensure the lattice is added to local view...
        if context.space_data.local_view is not None:
            lattice_object.local_view_set(context.space_data, True)

        return lattice_object

    def create_lattice_mod(self, target, lattice):
        mod = target.modifiers.new(lattice.name, "LATTICE")
        mod.object = lattice
        mod.show_expanded = False

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
