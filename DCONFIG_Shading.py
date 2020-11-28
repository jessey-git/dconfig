# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Viewport paramters and setup
#

import math
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

        context.space_data.show_region_tool_header = False

        context.space_data.clip_end = 100
        context.space_data.clip_start = 0.02

        context.space_data.lock_camera = True

        context.space_data.shading.type = 'MATERIAL'
        context.space_data.shading.studio_light = 'city.exr'

        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.light = 'MATCAP'
        context.space_data.shading.show_shadows = False
        context.space_data.shading.show_cavity = True
        context.space_data.shading.cavity_type = 'WORLD'
        context.space_data.shading.cavity_ridge_factor = 0
        context.space_data.shading.cavity_valley_factor = 1
        context.space_data.shading.curvature_ridge_factor = 0
        context.space_data.shading.curvature_valley_factor = 0.8
        context.space_data.shading.xray_alpha_wireframe = 0

        context.space_data.overlay.display_handle = 'SELECTED'
        context.space_data.overlay.show_curve_normals = False
        if bpy.app.version >= (2, 90, 0):
            context.space_data.overlay.show_stats = False
            context.space_data.overlay.show_fade_inactive = False

        context.space_data.overlay.wireframe_threshold = 1.0

        context.scene.display.matcap_ssao_distance = 1

        context.scene.tool_settings.snap_elements = {'VERTEX'}
        context.scene.tool_settings.snap_target = 'ACTIVE'
        context.scene.tool_settings.statvis.type = 'DISTORT'
        context.scene.tool_settings.statvis.distort_min = 0
        context.scene.tool_settings.statvis.distort_max = math.radians(40)

        context.scene.tool_settings.use_mesh_automerge = True

        return dc.trace_exit(self)


class DCONFIG_OT_engine_defaults(bpy.types.Operator):
    bl_idname = "dconfig.engine_defaults"
    bl_label = "DC Engine Defaults"
    bl_description = "Set common rendering engine parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        # Workbench
        context.scene.display.render_aa = '11'
        context.scene.display.viewport_aa = '5'

        # Eevee
        context.scene.eevee.use_ssr = True
        context.scene.eevee.use_ssr_halfres = False
        context.scene.eevee.use_ssr_refraction = True

        context.scene.eevee.use_gtao = True
        context.scene.eevee.gtao_distance = 0.4

        context.scene.eevee.use_volumetric_shadows = True
        context.scene.eevee.volumetric_tile_size = '2'

        context.scene.eevee.use_shadow_high_bitdepth = True
        context.scene.eevee.use_soft_shadows = True

        context.scene.render.use_high_quality_normals = True

        # Cycles
        context.scene.cycles.samples = 20
        context.scene.cycles.preview_samples = 6
        context.scene.cycles.use_square_samples = True
        context.scene.cycles.tile_order = 'CENTER'

        context.scene.cycles.preview_denoiser = 'OPENIMAGEDENOISE'
        context.scene.cycles.preview_denoising_start_sample = 400

        # General View
        context.scene.view_settings.look = 'Medium High Contrast'

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
    self.layout.operator("dconfig.viewport_defaults")
    self.layout.operator("dconfig.engine_defaults")
    self.layout.separator()


@persistent
def load_handler(ignore):
    # Only apply settings when the file being loaded is from startup.blend (aka. '')
    if bpy.data.filepath == '':
        bpy.ops.dconfig.engine_defaults()

        for screen in bpy.data.screens:
            for area in (a for a in screen.areas if a.type == 'OUTLINER'):
                area.spaces.active.show_restrict_column_select = True
                area.spaces.active.show_restrict_column_hide = True
                area.spaces.active.show_restrict_column_viewport = True
                area.spaces.active.show_restrict_column_render = True

            for area in (a for a in screen.areas if a.type == 'VIEW_3D'):
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
