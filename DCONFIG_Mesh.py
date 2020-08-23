# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import math

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_MT_quick(bpy.types.Menu):
    bl_label = "Quick"

    def draw(self, context):
        layout = self.layout

        if context.mode != 'EDIT_MESH':
            layout.menu_contents("DCONFIG_MT_modifiers")

        else:
            layout.menu("DCONFIG_MT_modifiers", icon='MODIFIER')
            layout.separator()

            dc.setup_op(layout, "mesh.remove_doubles", text="Weld vertices")

            layout.separator()
            dc.setup_op(layout, "mesh.select_face_by_sides", text="Select N-Gons", type='NOTEQUAL', number=4, extend=False)
            dc.setup_op(layout, "mesh.region_to_loop", text="Select Boundary Loop")

            layout.separator()
            layout.operator_context = 'INVOKE_REGION_WIN'
            dc.setup_op(layout, "mesh.fill_grid", text="Fill Grid")
            dc.setup_op(layout, "dconfig.make_quads", text="Make Quads")
            dc.setup_op(layout, "dconfig.subdivide_cylinder", text="Subdivide Cylinder")
            dc.setup_op(layout, "dconfig.quick_panel", text="Quick Panel")
            dc.setup_op(layout, "dconfig.subd_bevel", text="SubD Bevel")


class DCONFIG_OT_make_quads(bpy.types.Operator):
    bl_idname = "dconfig.make_quads"
    bl_label = "DC Make Quads"
    bl_description = "Triangulate and then convert to Quads"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_object_available(context, {'MESH'})

    def execute(self, context):
        dc.trace_enter(self)

        angle = math.radians(60)
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads(face_threshold=angle, shape_threshold=angle)

        return dc.trace_exit(self)


class DCONFIG_OT_subdivide_cylinder(bpy.types.Operator):
    bl_idname = "dconfig.subdivide_cylinder"
    bl_label = "DC Subdivide Cylinder"
    bl_description = "Subdivide cyclinder to increase curvature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_object_available(context, {'MESH'})

    def execute(self, context):
        dc.trace_enter(self)

        bpy.ops.mesh.edgering_select('INVOKE_DEFAULT')
        bpy.ops.mesh.loop_multi_select()

        if bpy.app.version >= (2, 90, 0):
            bpy.ops.mesh.bevel(offset_type='PERCENT', offset_pct=25, affect='EDGES')
        else:
            bpy.ops.mesh.bevel(offset_type='PERCENT', offset_pct=25, vertex_only=False)

        return dc.trace_exit(self)


class DCONFIG_OT_subd_bevel(bpy.types.Operator):
    bl_idname = "dconfig.subd_bevel"
    bl_label = "DC SubD friendly Bevel"
    bl_description = "Create a subdivision friendly bevel"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_object_available(context, {'MESH'})

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        target.update_from_editmode()

        if target.data.total_edge_sel > 0:
            dc.trace(1, "Using existing set of {} selected edges", target.data.total_edge_sel)
        else:
            dc.trace(1, "Selecting set of sharp edges")
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.edges_select_sharp()

        bpy.ops.mesh.bevel('INVOKE_DEFAULT', offset_type='ABSOLUTE', offset=0.01, segments=2, profile=1, clamp_overlap=True, miter_outer='ARC')

        return dc.trace_exit(self)


class DCONFIG_OT_subd_toggle(bpy.types.Operator):
    bl_idname = "dconfig.subd_toggle"
    bl_label = "DC SubD Toggle"
    bl_description = "Toggle subdivision surface modifier"
    bl_options = {'REGISTER'}

    levels: bpy.props.IntProperty(name="Levels", default=1, min=1, max=5)

    @classmethod
    def poll(cls, context):
        return dc.active_object_available(context, {'MESH', 'CURVE', 'FONT'})

    def execute(self, context):
        dc.trace_enter(self)

        objects = dc.get_objects(context.selected_objects, {'MESH', 'CURVE', 'FONT'})
        if not objects:
            objects = [context.active_object]
        subd_visible = False
        subd_invisible = False

        # Track visibility states for all required objects...
        for obj in objects:
            mod_subd = next((mod for mod in reversed(obj.modifiers) if mod.type == 'SUBSURF'), None)
            if mod_subd is None:
                subd_invisible = True
            else:
                if mod_subd.show_viewport:
                    subd_visible = True
                else:
                    subd_invisible = True

        # If there's a mix, then push them towards visible, otherwise just toggle...
        show_viewport_toggle = False
        if subd_invisible and subd_visible:
            show_viewport_toggle = True

        for obj in objects:
            mod_subd = next((mod for mod in reversed(obj.modifiers) if mod.type == 'SUBSURF'), None)
            if mod_subd is None:
                mod_subd = obj.modifiers.new("Subdivision", 'SUBSURF')
                mod_subd.levels = self.levels
                mod_subd.show_only_control_edges = True
            else:
                if self.levels != mod_subd.levels:
                    mod_subd.levels = self.levels
                    mod_subd.show_viewport = True
                else:
                    mod_subd.show_viewport = show_viewport_toggle if show_viewport_toggle else not mod_subd.show_viewport

        return dc.trace_exit(self)


class DCONFIG_OT_quick_panel(bpy.types.Operator):
    bl_idname = "dconfig.quick_panel"
    bl_label = "DC Quick Panel"
    bl_description = "Panel macro"
    bl_options = {'REGISTER', 'UNDO'}

    scale: bpy.props.FloatProperty(name="Scale", default=1, step=1, min=0, max=2)
    offset: bpy.props.FloatProperty(name="Offset", default=1, step=1, min=0, max=2)
    inset: bpy.props.FloatProperty(name="Inset", default=0.5, step=1, min=0, max=1)
    depth: bpy.props.FloatProperty(name="Depth", default=0.5, step=1, min=0, max=1)
    invert: bpy.props.BoolProperty(name="Invert", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_object_available(context, {'MESH'})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, "scale", slider=True)
        layout.separator()
        layout.prop(self, "offset", slider=True)
        layout.prop(self, "inset", slider=True)
        layout.prop(self, "depth", slider=True)
        layout.prop(self, "invert")

    def execute(self, context):
        dc.trace_enter(self)

        bevel_offset1 = (0.01 / 4) * self.offset * self.scale
        inset_thickness = bevel_offset1 * self.inset
        inset_depth = 0.02 * self.depth * self.scale * (-1 if self.invert else 1)
        bevel_offset2 = math.fabs(inset_depth) / 3

        bpy.ops.object.vertex_group_assign_new()
        vgroup = context.active_object.vertex_groups.active

        bpy.ops.mesh.bevel(offset_type='OFFSET', offset=bevel_offset1, offset_pct=0, segments=2)
        bpy.ops.mesh.inset(thickness=inset_thickness, depth=-inset_depth, use_boundary=False)
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset_type='OFFSET', offset=bevel_offset2, segments=2, profile=1, clamp_overlap=True, miter_outer='ARC')

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group=vgroup.name)
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

        for _ in range(4):
            bpy.ops.mesh.select_less()

        return dc.trace_exit(self)


focus_settings = {
    "EDIT_CURVE": True,
    "EDIT_MESH": True,
}


class DCONFIG_OT_mesh_focus(bpy.types.Operator):
    bl_idname = "dconfig.mesh_focus"
    bl_label = "DC Mesh Focus"
    bl_description = "Focus on selected mesh elements and hide everything else"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        if context.mode == 'OBJECT':
            dc.trace(1, "View selected")
            bpy.ops.view3d.view_selected()
            bpy.ops.view3d.zoom(delta=-1, use_cursor_init=True)
        elif context.mode == 'SCULPT':
            dc.trace(1, "View selected")
            bpy.ops.view3d.view_selected()
        else:
            current_focus = focus_settings[context.mode]
            if current_focus:
                dc.trace(1, "Focus")
                if context.mode == 'EDIT_MESH':
                    bpy.ops.mesh.hide(unselected=True)
                elif context.mode == 'EDIT_CURVE':
                    bpy.ops.curve.hide(unselected=True)

                bpy.ops.view3d.view_selected()
                bpy.ops.view3d.zoom(delta=-1, use_cursor_init=True)
            else:
                dc.trace(1, "Unfocus")
                if context.mode == 'EDIT_MESH':
                    bpy.ops.mesh.reveal(select=False)
                elif context.mode == 'EDIT_CURVE':
                    bpy.ops.curve.reveal(select=False)

            focus_settings[context.mode] = not current_focus

        return dc.trace_exit(self)
