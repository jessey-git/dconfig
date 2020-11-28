# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better snap and transform menus
#

import bpy

from . import DCONFIG_Utils as dc


class DCONFIG_MT_transforms_pie(bpy.types.Menu):
    bl_label = "Transforms"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.prop(context.scene.tool_settings, "transform_pivot_point", expand=True)

        # Right
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25
        col.prop(context.scene.transform_orientation_slots[0], "type", expand=True)

        # Bottom
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25

        col.prop(context.tool_settings, "use_transform_data_origin", text="Origins")
        col.prop(context.tool_settings, "use_transform_pivot_point_align", text="Locations")
        col.prop(context.tool_settings, "use_transform_skip_children", text="Parents")


class DCONFIG_MT_image_pivot(bpy.types.Menu):
    bl_label = "Pivot"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.space_data, "pivot_point", expand=True)


class DCONFIG_MT_origin_set(bpy.types.Menu):
    bl_label = "Set Origin"

    def draw(self, context):
        layout = self.layout

        layout.operator_enum("object.origin_set", property="type")

        layout.separator()

        layout.operator("dconfig.set_pivot", text="Origin to Selection")


class DCONFIG_OT_set_pivot(bpy.types.Operator):
    bl_idname = "dconfig.set_pivot"
    bl_label = "DC Set Pivot"
    bl_description = "Set object pivot while in edit mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.active_object.data.total_vert_sel > 0

    def execute(self, context):
        dc.trace_enter(self)

        prev_cursor_location = context.scene.cursor.location.copy()
        prev_cursor_matrix = context.scene.cursor.matrix.copy()

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        context.scene.cursor.matrix = prev_cursor_matrix
        context.scene.cursor.location = prev_cursor_location

        return dc.trace_exit(self)
