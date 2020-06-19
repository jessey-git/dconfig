# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Misc UI
#

import re
import blf
import bpy


def draw_stats(font_id, line_height, ui_scale):
    view_layer = bpy.context.view_layer

    # Gather up stats...
    stats = bpy.context.scene.statistics(view_layer).split("|")
    if bpy.context.mode == 'OBJECT':
        if len(stats) == 8:
            stats = stats[2:4]
        else:
            stats = stats[1:3]
    elif bpy.context.mode == 'EDIT_MESH':
        stats = stats[1:4]
    elif bpy.context.mode == 'EDIT_CURVE':
        stats = stats[1:2]
    elif bpy.context.mode == 'EDIT_LATTICE':
        stats = stats[1:2]
    elif bpy.context.mode == 'SCULPT':
        stats = stats[1:3]
    else:
        return

    # Initial positions and offsets to handle tool region and top text...
    toolbar_width = next((region.width for region in bpy.context.area.regions if region.type == 'TOOLS'), 100)
    top_offset = line_height * 10
    x_pos = (20 * ui_scale) + toolbar_width
    y_pos = bpy.context.area.height - top_offset

    digit_width = blf.dimensions(font_id, "0")[0]
    longest_title = blf.dimensions(font_id, "Edges")[0]  # Known longest title
    longest_digits = digit_width * 10

    # Calculate dimensions for each piece of data...
    lines = []
    for value in stats:
        line_data = [[val, 0] for val in filter(None, re.split("[ :/]", value))]
        if len(line_data) > 3:
            line_data = line_data[1:]
        for data in line_data:
            data[1] = blf.dimensions(font_id, data[0])[0]

        lines.append(line_data)

    # Aligned layout using dimensions above (special case first piece of data for the title)...
    blf.color(font_id, 1, 1, 1, 1)
    for line in lines:
        x = x_pos + longest_title
        for index, data in enumerate(line):
            if index > 0:
                x += longest_digits
            blf.position(font_id, x - data[1], y_pos, 0)
            blf.draw(font_id, data[0].replace(",", "\u2009"))

        y_pos -= line_height


def draw_func(ignore):
    # Only draw when allowed...
    space_data = bpy.context.space_data
    if not (space_data.overlay.show_overlays and space_data.overlay.show_text):
        return

    # Setup font and scaling parameters...
    font_id = draw_settings["font_id"]
    font_size = draw_settings["font_size"]

    ui_scale = bpy.context.preferences.system.ui_scale

    blf.size(font_id, round(font_size * ui_scale), 72)
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.9)
    blf.shadow_offset(font_id, 1, -1)

    line_height = blf.dimensions(font_id, "M")[1] * 1.55

    # Draw all the things...
    draw_stats(font_id, line_height, ui_scale)


draw_settings = {
    "font_id": 0,
    "font_size": 11,
    "handler": None
}


def register():
    if bpy.app.version < (2, 90, 0):
        draw_settings["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_func, (None, ), 'WINDOW', 'POST_PIXEL')


def unregister():
    if bpy.app.version < (2, 90, 0):
        bpy.types.SpaceView3D.draw_handler_remove(draw_settings["handler"], 'WINDOW')
