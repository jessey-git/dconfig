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


def draw_stats(context, space_data, font_id, longest_digits, line_height, ui_scale):
    # Gather up stats...
    mode = context.mode
    stats = {}
    for stat in context.scene.statistics(context.view_layer).split("|"):
        data = [val for val in filter(None, re.split("[ :/]", stat))]
        if len(data):
            stats[data[0]] = data
    if "Objects" not in stats:
        stats["Objects"] = ["Objects", "0", "0"]
    if "Verts" not in stats:
        stats["Verts"] = ["Verts", "0", "0"]
    if "Faces" not in stats:
        stats["Faces"] = ["Faces", "0", "0"]

    if mode == 'OBJECT':
        stats = [stats["Objects"], stats["Verts"], stats["Faces"]]
    elif mode == 'EDIT_MESH':
        stats = [stats["Objects"], stats["Verts"], stats["Edges"], stats["Faces"]]
    elif mode == 'EDIT_CURVE':
        stats = [stats["Objects"], stats["Verts"]]
    elif mode == 'EDIT_LATTICE':
        stats = [stats["Objects"], stats["Verts"]]
    elif mode == 'EDIT_ARMATURE':
        stats = [stats["Objects"], stats["Joints"], stats["Bones"]]
    elif mode == 'SCULPT':
        stats = [stats["Objects"], stats["Verts"], stats["Faces"]]
    else:
        return

    # Initial positions and offsets to handle tool region and top text...
    area = context.area
    toolbar_width = next((region.width for region in area.regions if region.type == 'TOOLS'), 100)
    top_offset = line_height * 8
    x_pos = (10 * ui_scale) + toolbar_width
    y_pos = area.height - ((26 * ui_scale) if space_data.show_region_tool_header else 0) - top_offset

    longest_title = 0

    # Calculate dimensions for each piece of data...
    class Item:
        def __init__(self, text, font_id):
            self.text = text.replace(",", "\u2009")
            self.dim_x = blf.dimensions(font_id, self.text)[0]

    lines = []
    for stat in stats:
        line_data = [Item(val, font_id) for val in stat]

        longest_title = max(longest_title, line_data[0].dim_x)
        lines.append(line_data)

    # Aligned layout using dimensions above (special case first piece of data for the title)...
    blf.color(font_id, 1, 1, 1, 1)
    for line_index, line in enumerate(lines):
        x = x_pos + longest_title
        for item_index, item in enumerate(line):
            if item_index > 0:
                x += longest_digits
            blf.position(font_id, x - item.dim_x, y_pos, 0)
            blf.draw(font_id, item.text)

        if line_index == 0:
            y_pos -= line_height / 2
        y_pos -= line_height


def draw_func(ignore):
    context = bpy.context
    space_data = context.space_data

    # Only draw when allowed...
    if not (space_data.overlay.show_overlays and space_data.overlay.show_text):
        return

    # Disable the built-in stats...
    if space_data.overlay.show_stats:
        space_data.overlay.show_stats = False

    # Setup font and scaling parameters...
    font_id = draw_settings["font_id"]
    font_size = draw_settings["font_size"]
    ui_scale = context.preferences.system.ui_scale

    if bpy.app.version < (3, 4, 0):
        blf.size(font_id, round(font_size * ui_scale), 72)
    else:
        blf.size(font_id, round(font_size * ui_scale))
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.9)
    blf.shadow_offset(font_id, 1, -1)

    # Draw all the things...
    longest_digits = draw_settings["longest_digits"]
    line_height = draw_settings["line_height"]
    if longest_digits == 0:
        digit_width = blf.dimensions(font_id, "0")[0] * 10
        space_width = blf.dimensions(font_id, "\u2009")[0] * 2
        longest_digits = draw_settings["longest_digits"] = digit_width + space_width
        line_height = draw_settings["line_height"] = blf.dimensions(font_id, "M")[1] * 1.55
    draw_stats(context, space_data, font_id, longest_digits, line_height, ui_scale)


draw_settings = {
    "font_id": 0,
    "font_size": 11,
    "longest_digits": 0,
    "line_height": 0,
    "handler": None
}


def register():
    draw_settings["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_func, (None, ), 'WINDOW', 'POST_PIXEL')


def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(draw_settings["handler"], 'WINDOW')
