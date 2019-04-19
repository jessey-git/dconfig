# ------------------------------------------------------------
# Copyright(c) 2019 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Misc UI
#

import blf
import bpy


def draw_func(ignore):
    font_id = 0
    ui_scale = bpy.context.preferences.view.ui_scale

    top_offset = 100 * ui_scale
    font_size = round(8 * ui_scale)

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

    vertical_offset = 0
    if bpy.context.scene.render.engine == 'CYCLES':
        if bpy.context.space_data.shading.type == 'RENDERED':
            vertical_offset = font_size * ui_scale

    toolbar_width = bpy.context.area.regions[1].width
    x_offset = (20 * ui_scale) + toolbar_width
    y_offset = bpy.context.area.height - top_offset

    if bpy.context.space_data.overlay.show_overlays:
        if bpy.context.space_data.overlay.show_text:
            blf.size(font_id, font_size, 96)
            blf.enable(font_id, blf.SHADOW)
            blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.9)
            blf.shadow_offset(font_id, 1, -1)

            for counter, value in enumerate(stats):
                value = value.replace(":", ": ")
                increment = (font_size * counter * ui_scale * 2)
                blf.position(font_id, x_offset, y_offset - increment - vertical_offset, 0)
                blf.draw(font_id, value.strip())


draw_handler = []


def register():
    draw_handler.clear()
    draw_handler.append(bpy.types.SpaceView3D.draw_handler_add(draw_func, (None, ), 'WINDOW', 'POST_PIXEL'))


def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler[0], 'WINDOW')
