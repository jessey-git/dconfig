# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_MT_quick(bpy.types.Menu):
    bl_label = "Quick"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.remove_doubles", text="Weld vertices")

        layout.separator()
        op = layout.operator("mesh.select_face_by_sides", text="Select N-Gons")
        op.type = 'GREATER'
        op.number = 4
        op.extend = False

        layout.separator()
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.fill_grid", text="Fill Grid")
        layout.operator("dconfig.subdivide_cylinder", text="Subdivide Cylinder")
        layout.operator("dconfig.subd_bevel", text="Sub-D Bevel")


class DCONFIG_OT_subdivide_cylinder(bpy.types.Operator):
    bl_idname = "dconfig.subdivide_cylinder"
    bl_label = "DC Subdivide Cylinder"
    bl_description = "Subdivide cyclinder to increase curvature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and dc.active_mesh_available(context)

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
        return dc.active_mesh_available(context) and context.mode == 'EDIT_MESH'

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


focus_settings = {
    "EDIT_MESH": True,
    "OBJECT": True
}


class DCONFIG_OT_mesh_focus(bpy.types.Operator):
    bl_idname = "dconfig.mesh_focus"
    bl_label = "DC Mesh Focus"
    bl_description = "Focus on selected mesh elements and hide everything else"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        current_focus = focus_settings[context.mode]

        if current_focus:
            dc.trace(1, "Focus")
            if context.mode == 'EDIT_MESH':
                bpy.ops.mesh.hide(unselected=True)

            bpy.ops.view3d.view_selected()
            bpy.ops.view3d.zoom(delta=-1, use_cursor_init=True)
        else:
            dc.trace(1, "Unfocus")
            if context.mode == 'EDIT_MESH':
                bpy.ops.mesh.reveal(select=False)
            else:
                bpy.ops.view3d.view_all()

        focus_settings[context.mode] = not current_focus

        return dc.trace_exit(self)
