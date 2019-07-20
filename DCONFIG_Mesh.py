# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import bpy
import bmesh
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
        if target.data.total_edge_sel > 0:
            dc.trace(1, "Using existing set of {} selected edges", target.data.total_edge_sel)
        else:
            dc.trace(1, "Selecting set of sharp edges")
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.edges_select_sharp()

        edge_min = 100
        bm = bmesh.from_edit_mesh(target.data)
        for edge in bm.edges:
            if edge.select:
                edge_min = min(edge_min, edge.calc_length())

        bevel_offset = max(0.02, edge_min * .02)
        bevel_offset = min(bevel_offset, edge_min / 3)

        dc.trace(1, "Creating bevel with offset {}", bevel_offset)
        bpy.ops.mesh.bevel(offset_type='OFFSET', offset=bevel_offset, segments=2, profile=1, clamp_overlap=True, miter_outer='ARC')

        return dc.trace_exit(self)


class DCONFIG_OT_mesh_focus(bpy.types.Operator):
    bl_idname = "dconfig.mesh_focus"
    bl_label = "DC Mesh Focus"
    bl_description = "Focus on selected mesh elements and hide everything else"
    bl_options = {'REGISTER'}

    focus: bpy.props.BoolProperty()

    def execute(self, context):
        dc.trace_enter(self)

        if self.focus:
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

        return dc.trace_exit(self)
