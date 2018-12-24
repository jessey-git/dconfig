# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better snap and transform menus
#

import bpy


class DC_MT_snap(bpy.types.Menu):
    bl_label = "Snap"

    def draw(self, context):
        layout = self.layout

        layout.operator("view3d.snap_selected_to_grid", text="Selection to Grid")
        layout.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor").use_offset = False
        layout.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor (Keep Offset)").use_offset = True
        layout.operator("view3d.snap_selected_to_active", text="Selection to Active")

        layout.separator()

        layout.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected")
        layout.operator("view3d.snap_cursor_to_center", text="Cursor to World Origin")
        layout.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid")
        layout.operator("view3d.snap_cursor_to_active", text="Cursor to Active")


class DC_MT_transforms_pie(bpy.types.Menu):
    bl_label = "Transforms"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.5
        col.prop(context.scene.tool_settings, "transform_pivot_point", expand=True)

        # Right
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.5
        col.prop(context.scene.transform_orientation_slots[0], "type", expand=True)
