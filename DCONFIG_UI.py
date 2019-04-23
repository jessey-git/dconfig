# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Misc UI
#

from ctypes import windll
import blf
import bpy


def draw_func(ignore):
    # Only draw our text when allowed...
    space_data = bpy.context.space_data
    if not (space_data.overlay.show_overlays and space_data.overlay.show_text):
        return

    # Gather statistics...
    view_layer = bpy.context.view_layer
    stats = bpy.context.scene.statistics(view_layer).split("|")

    if bpy.context.mode == 'OBJECT':
        stats = stats[2:5]
    elif bpy.context.mode == 'EDIT_MESH':
        stats = stats[1:5]
    elif bpy.context.mode == 'SCULPT':
        stats = stats[1:4]
    else:
        stats = []

    # Setup font and scaling parameters...
    font_id = 0
    font_size = 11  # In points

    dpi_scale = int(draw_info["dpi"] / 96)
    ui_scale = bpy.context.preferences.view.ui_scale
    final_scale = ui_scale * dpi_scale

    blf.size(font_id, font_size, 72 * dpi_scale)
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.9)
    blf.shadow_offset(font_id, 1, -1)
    line_height = blf.dimensions(font_id, "M")[1] * 1.55

    # Start drawing a few lines down from the top and shifted away
    # from the Tools panel...
    top_offset = line_height * 10
    if bpy.context.scene.render.engine == 'CYCLES':
        if bpy.context.space_data.shading.type == 'RENDERED':
            top_offset += line_height

    toolbar_width = next((region.width for region in bpy.context.area.regions if region.type == 'TOOLS'), 100)
    x_pos = (20 * final_scale) + toolbar_width
    y_pos = bpy.context.area.height - top_offset

    for value in stats:
        line_text = value.replace(":", ": ").replace("/", " / ").strip()
        blf.position(font_id, x_pos, y_pos, 0)
        blf.draw(font_id, line_text)

        y_pos -= line_height


def get_ppi():
    LOGPIXELSX = 88
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    return pix_per_inch


draw_info = {
    "dpi": None,
    "handler": None
}


def register():
    draw_info["dpi"] = get_ppi()
    draw_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_func, (None, ), 'WINDOW', 'POST_PIXEL')


def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(draw_info["handler"], 'WINDOW')
