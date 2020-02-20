# ------------------------------------------------------------
# Copyright(c) 2020 Jesse Yurkovich
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
            dc.setup_op(layout, "dconfig.subd_bevel", text="Sub-D Bevel")


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
        bpy.ops.mesh.bevel(offset_type='PERCENT', offset_pct=25, vertex_only=False)

        return dc.trace_exit(self)


class DCONFIG_OT_subd_bevel(bpy.types.Operator):
    bl_idname = "dconfig.subd_bevel"
    bl_label = "DC Sub-D friendly Bevel"
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

        bpy.ops.mesh.bevel('INVOKE_DEFAULT', offset_type='OFFSET', offset=0.01, segments=2, profile=1, clamp_overlap=True, miter_outer='ARC')

        return dc.trace_exit(self)


class DCONFIG_OT_subd_toggle(bpy.types.Operator):
    bl_idname = "dconfig.subd_toggle"
    bl_label = "DC Sub-D Toggle"
    bl_description = "Toggle subdivision surface modifier"
    bl_options = {'REGISTER', 'UNDO'}

    levels: bpy.props.IntProperty(name="Levels", default=1, min=1, max=5)

    @classmethod
    def poll(cls, context):
        return dc.active_object_available(context, {'MESH', 'CURVE', 'FONT'})

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        mod_subd = next((mod for mod in reversed(target.modifiers) if mod.type == 'SUBSURF'), None)
        if mod_subd is None:
            mod_subd = target.modifiers.new("Subdivision", 'SUBSURF')
            mod_subd.levels = self.levels
            mod_subd.show_only_control_edges = True
        else:
            if self.levels != mod_subd.levels:
                mod_subd.levels = self.levels
                mod_subd.show_viewport = True
            else:
                mod_subd.show_viewport = not mod_subd.show_viewport

        return dc.trace_exit(self)


class DCONFIG_OT_quick_panel(bpy.types.Operator):
    bl_idname = "dconfig.quick_panel"
    bl_label = "DC Quick Panel"
    bl_description = "Panel macro"
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.FloatProperty(name="Offset", default=0.0100, step=1, min=0.0001, max=1, precision=4)
    offset2: bpy.props.FloatProperty(name="Offset (secondary)", default=0.0033, step=1, min=0.0001, max=1, precision=4)
    inset: bpy.props.FloatProperty(name="Inset", default=0.0067, step=1, min=0.0001, max=1, precision=4)
    depth: bpy.props.FloatProperty(name="Depth", default=0.0100, step=1, min=0.0001, max=1, precision=4)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_object_available(context, {'MESH'})

    def execute(self, context):
        dc.trace_enter(self)

        bpy.ops.mesh.bevel(offset_type='OFFSET', offset=self.offset, offset_pct=0, segments=2, vertex_only=False)
        bpy.ops.mesh.inset(thickness=self.inset, depth=-self.depth)
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset_type='OFFSET', offset=self.offset2, segments=2, profile=1, clamp_overlap=True, miter_outer='ARC')

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
