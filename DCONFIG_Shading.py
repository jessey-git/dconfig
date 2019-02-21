# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Shading paramters and setup
#

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_OT_setup_shading(bpy.types.Operator):
    bl_idname = "dconfig.setup_shading"
    bl_label = "DC Setup Shading"
    bl_description = "Set common shading and overlay parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        context.space_data.clip_end = 100
        context.space_data.clip_start = 0.025

        context.space_data.shading.light = 'MATCAP'
        context.space_data.shading.show_shadows = False
        context.space_data.shading.show_cavity = True
        context.space_data.shading.cavity_type = 'WORLD'
        context.space_data.shading.cavity_ridge_factor = 0
        context.space_data.shading.cavity_valley_factor = 1
        context.space_data.shading.curvature_ridge_factor = 0
        context.space_data.shading.curvature_valley_factor = 0.8
        context.space_data.shading.xray_alpha_wireframe = 0

        context.space_data.overlay.wireframe_threshold = 1.0

        context.scene.display.matcap_ssao_distance = 1

        return dc.trace_exit(self)


def menu_func(self, context):
    self.layout.operator("dconfig.setup_shading", text="DC Setup Shading")
    self.layout.separator()


def register():
    bpy.types.VIEW3D_MT_view.prepend(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
