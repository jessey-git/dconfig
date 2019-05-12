# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Viewport paramters and setup
#

import bpy
from bpy.app.handlers import persistent
from . import DCONFIG_Utils as dc


class DCONFIG_OT_viewport_defaults(bpy.types.Operator):
    bl_idname = "dconfig.viewport_defaults"
    bl_label = "DC Viewport Defaults"
    bl_description = "Set common viewport parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        context.scene.tool_settings.snap_elements = {'VERTEX'}

        context.scene.tool_settings.statvis.type = 'DISTORT'
        context.scene.tool_settings.statvis.distort_min = 0
        context.scene.tool_settings.statvis.distort_max = 0.698132

        context.space_data.clip_end = 100
        context.space_data.clip_start = 0.02

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


class DCONFIG_OT_toggle_wireframe(bpy.types.Operator):
    bl_idname = "dconfig.toggle_wireframe"
    bl_label = "DC Toggle Wireframe"
    bl_description = "Toggle wireframe overlay"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        context.space_data.overlay.show_wireframes = not context.space_data.overlay.show_wireframes

        return dc.trace_exit(self)


def menu_func(self, context):
    self.layout.operator("dconfig.viewport_defaults", text="DC Viewport Defaults")
    self.layout.separator()


@persistent
def load_handler(ignore):
    area = next((area for area in bpy.context.screen.areas if area.type == 'VIEW_3D'), None)
    if area is not None:
        region = next((region for region in area.regions if region.type == 'WINDOW'), None)

    if region is not None:
        override = {'area': area, 'region': region}
        bpy.ops.dconfig.viewport_defaults(override)


def register():
    bpy.types.VIEW3D_MT_view.prepend(menu_func)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
    bpy.app.handlers.load_post.remove(load_handler)
