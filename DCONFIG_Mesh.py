# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import bpy
from . import DCONFIG_Utils as dc


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
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        if "dc_bevel" not in target.modifiers:
            if context.mode == 'EDIT_MESH':
                dc.trace(1, "Selecting initial set of sharp edges")
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

                bpy.ops.mesh.edges_select_sharp()
                bpy.ops.transform.edge_bevelweight(value=1)

            dc.trace(1, "Creating bevel modifier")
            self.create_bevel_mod(target)
        else:
            return dc.warn_canceled(self, "Mesh already beveled")

        return dc.trace_exit(self)

    def create_bevel_mod(self, target):
        mod = target.modifiers.new("dc_bevel", 'BEVEL')
        mod.offset_type = 'PERCENT'
        mod.limit_method = 'WEIGHT'
        mod.miter_outer = 'MITER_ARC'
        mod.width_pct = 5
        mod.segments = 2
        mod.profile = 1
