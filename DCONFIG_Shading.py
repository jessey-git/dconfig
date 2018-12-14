# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Shading paramters and setup
#

import bpy
from . import DCONFIG_Utils as DC


class DC_OT_setup_shading(bpy.types.Operator):
    bl_idname = "view3d.dc_setup_shading"
    bl_label = "DC Setup Shading"
    bl_options = {'REGISTER'}

    def execute(self, context):
        DC.trace_enter("DC_OT_setup_shading.execute")

        bpy.context.space_data.shading.light = 'MATCAP'
        bpy.context.space_data.shading.show_shadows = True
        bpy.context.space_data.shading.show_cavity = True
        bpy.context.space_data.shading.cavity_ridge_factor = 0
        bpy.context.space_data.shading.cavity_valley_factor = 2
        bpy.context.space_data.shading.curvature_ridge_factor = 0
        bpy.context.space_data.shading.curvature_valley_factor = 2
        bpy.context.space_data.shading.xray_alpha_wireframe = 0

        bpy.context.space_data.overlay.wireframe_threshold = 0.86

        return DC.trace_exit("DC_OT_setup_shading.execute")
