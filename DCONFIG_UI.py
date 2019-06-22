# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Misc UI
#

from ctypes import windll
import re
import blf
import bpy


def draw_stats(font_id, line_height, final_scale):
    view_layer = bpy.context.view_layer

    # Gather up stats...
    stats = bpy.context.scene.statistics(view_layer).split("|")
    if bpy.context.mode == 'OBJECT':
        stats = stats[2:4]
    elif bpy.context.mode == 'EDIT_MESH':
        stats = stats[1:4]
    elif bpy.context.mode == 'EDIT_CURVE':
        stats = stats[1:2]
    elif bpy.context.mode == 'SCULPT':
        stats = stats[1:3]
    else:
        return

    # Initial positions and offsets to handle tool region and top text...
    toolbar_width = next((region.width for region in bpy.context.area.regions if region.type == 'TOOLS'), 100)
    top_offset = line_height * 10
    x_pos = (20 * final_scale) + toolbar_width
    y_pos = bpy.context.area.height - top_offset

    digit_width = blf.dimensions(font_id, "0")[0]
    longest_title = blf.dimensions(font_id, "Edges")[0]  # Known longest title
    longest_digits = digit_width * 10

    # Calculate dimensions for each piece of data...
    lines = []
    for value in stats:
        line_data = [[val, 0] for val in filter(None, re.split("[ :/]", value))]
        for data in line_data:
            data[1] = blf.dimensions(font_id, data[0])[0]

        lines.append(line_data)

    # Aligned layout using dimensions above (special case first piece of data for the title)...
    for line in lines:
        x = x_pos + longest_title
        for index, data in enumerate(line):
            if index > 0:
                x += longest_digits
            blf.position(font_id, x - data[1], y_pos, 0)
            blf.draw(font_id, data[0])

        y_pos -= line_height


def draw_func(ignore):
    # Only draw when allowed...
    space_data = bpy.context.space_data
    if not (space_data.overlay.show_overlays and space_data.overlay.show_text):
        return

    # Setup font and scaling parameters...
    font_id = draw_settings["font_id"]
    font_size = draw_settings["font_size"]
    dpi_scale = draw_settings["dpi_scale"]

    ui_scale = bpy.context.preferences.view.ui_scale
    final_scale = ui_scale * dpi_scale

    blf.size(font_id, int(font_size * ui_scale), int(72 * dpi_scale))
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.9)
    blf.shadow_offset(font_id, 1, -1)

    line_height = blf.dimensions(font_id, "M")[1] * 1.55

    # Draw all the things...
    draw_stats(font_id, line_height, final_scale)


def get_ppi_win32():
    LOGPIXELSX = 88
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    return pix_per_inch


draw_settings = {
    "font_id": 0,
    "font_size": 11,
    "dpi_scale": None,
    "handler": None
}


def register():
    draw_settings["dpi_scale"] = get_ppi_win32() / 96
    draw_settings["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_func, (None, ), 'WINDOW', 'POST_PIXEL')


def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(draw_settings["handler"], 'WINDOW')
