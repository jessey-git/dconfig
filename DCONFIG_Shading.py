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


def set_viewport_defaults(space_data):
    # space_data.show_region_tool_header = False

    space_data.clip_end = 2000
    space_data.clip_start = 0.02

    space_data.lock_camera = True

    space_data.shading.type = 'MATERIAL'
    space_data.shading.studio_light = 'city.exr'

    space_data.shading.type = 'SOLID'
    space_data.shading.light = 'MATCAP'
    space_data.shading.show_shadows = False
    space_data.shading.show_cavity = True
    space_data.shading.cavity_type = 'WORLD'
    space_data.shading.cavity_ridge_factor = 0
    space_data.shading.cavity_valley_factor = 1.25
    space_data.shading.curvature_ridge_factor = 0
    space_data.shading.curvature_valley_factor = 0.8
    space_data.shading.xray_alpha_wireframe = 0

    space_data.overlay.display_handle = 'SELECTED'
    space_data.overlay.show_curve_normals = False
    if bpy.app.version >= (2, 90, 0):
        space_data.overlay.show_stats = False
        space_data.overlay.show_fade_inactive = False

    space_data.overlay.wireframe_threshold = 1.0
    space_data.overlay.show_edges = True


def set_scene_defaults(scene):
    scene.display.matcap_ssao_distance = 0.15

    scene.tool_settings.snap_elements = {'VERTEX'}
    scene.tool_settings.snap_target = 'ACTIVE'
    scene.tool_settings.statvis.type = 'DISTORT'
    scene.tool_settings.statvis.distort_min = 0
    scene.tool_settings.statvis.distort_max = math.radians(40)

    scene.tool_settings.use_mesh_automerge = True


def set_engine_defaults(scene):
    # Workbench
    scene.display.render_aa = '11'
    scene.display.viewport_aa = '5'

    # Eevee
    scene.eevee.use_ssr = True
    scene.eevee.use_ssr_halfres = False
    scene.eevee.use_ssr_refraction = True

    scene.eevee.use_gtao = True
    scene.eevee.gtao_distance = 0.4

    scene.eevee.use_volumetric_shadows = True
    scene.eevee.volumetric_tile_size = '2'

    scene.eevee.use_shadow_high_bitdepth = True
    scene.eevee.use_soft_shadows = True

    scene.render.use_high_quality_normals = True

    # Cycles
    if bpy.app.version < (3, 0, 0):
        scene.cycles.samples = 20
        scene.cycles.preview_samples = 6
        scene.cycles.use_square_samples = True
        scene.cycles.tile_order = 'CENTER'

        scene.cycles.max_bounces = 180
        scene.cycles.diffuse_bounces = 10
        scene.cycles.glossy_bounces = 100
        scene.cycles.transmission_bounces = 36
        scene.cycles.volume_bounces = 2
        scene.cycles.transparent_max_bounces = 19

        scene.cycles.sample_clamp_indirect = 0

        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.preview_denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.preview_denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        scene.cycles.preview_denoising_start_sample = 10000

        scene.render.tile_x = 160
        scene.render.tile_y = 90
    else:
        scene.cycles.max_bounces = 180
        scene.cycles.diffuse_bounces = 10
        scene.cycles.glossy_bounces = 100
        scene.cycles.transmission_bounces = 36
        scene.cycles.volume_bounces = 2
        scene.cycles.transparent_max_bounces = 19

        scene.cycles.sample_clamp_indirect = 0

        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.preview_denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.preview_denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        scene.cycles.preview_denoising_prefilter = 'ACCURATE'
        scene.cycles.preview_denoising_start_sample = 10000

        scene.cycles.blur_glossy = 0.1

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'

    # General View
    scene.view_settings.look = 'Medium High Contrast'

class DCONFIG_OT_viewport_defaults(bpy.types.Operator):
    bl_idname = "dconfig.viewport_defaults"
    bl_label = "DC Viewport Defaults"
    bl_description = "Set common viewport parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        set_viewport_defaults(context.space_data)
        set_scene_defaults(context.scene)

        return dc.trace_exit(self)


class DCONFIG_OT_engine_defaults(bpy.types.Operator):
    bl_idname = "dconfig.engine_defaults"
    bl_label = "DC Engine Defaults"
    bl_description = "Set common rendering engine parameters"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dc.trace_enter(self)

        set_engine_defaults(context.scene)

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
def load_handler(filepath):
    # Only apply settings when the file being loaded is from startup.blend (aka. '')
    is_startup_file = (bpy.data.filepath == '') or (filepath == '')
    if is_startup_file and not bpy.app.background:
        scene = bpy.data.scenes[0]

        set_engine_defaults(scene)
        set_scene_defaults(scene)

        window = bpy.data.window_managers[0].windows[0]
        for screen in bpy.data.screens:
            for area in (a for a in screen.areas if a.type == 'OUTLINER'):
                area.spaces.active.show_restrict_column_select = True
                area.spaces.active.show_restrict_column_hide = True
                area.spaces.active.show_restrict_column_viewport = True
                area.spaces.active.show_restrict_column_render = True

            for area in (a for a in screen.areas if a.type == 'VIEW_3D'):
                set_viewport_defaults(area.spaces.active)


def register():
    bpy.types.VIEW3D_MT_view.prepend(menu_func)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
    bpy.app.handlers.load_post.remove(load_handler)
