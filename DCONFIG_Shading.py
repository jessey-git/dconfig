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
    bl_description = "Set common shading and overlay parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        DC.trace_enter("DC_OT_setup_shading")

        context.space_data.shading.light = 'MATCAP'
        context.space_data.shading.show_shadows = True
        context.space_data.shading.show_cavity = True
        context.space_data.shading.cavity_ridge_factor = 0
        context.space_data.shading.cavity_valley_factor = 2
        context.space_data.shading.curvature_ridge_factor = 0
        context.space_data.shading.curvature_valley_factor = 2
        context.space_data.shading.xray_alpha_wireframe = 0

        context.space_data.overlay.wireframe_threshold = 0.86

        return DC.trace_exit("DC_OT_setup_shading")


def menu_func(self, context):
    self.layout.operator("view3d.dc_setup_shading", text="DC Setup Shading")
    self.layout.separator()


def register():
    bpy.types.VIEW3D_MT_view.prepend(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
