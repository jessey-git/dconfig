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

        col.separator()

        col.prop(context.tool_settings, "use_transform_data_origin", text="Origins")
        col.prop(context.tool_settings, "use_transform_pivot_point_align", text="Locations")
        col.prop(context.tool_settings, "use_transform_skip_children", text="Parents")

        # Right
        split = pie.split()
        col = split.column()

        orient_slot = context.scene.transform_orientation_slots[0]
        orientation = orient_slot.custom_orientation

        sub = col.column(align=True)
        sub.scale_x = 1.75
        sub.scale_y = 1.25
        sub.prop(orient_slot, "type", expand=True)

        sub = col.column(align=True)
        row = sub.row(align=True)
        row.scale_y = 1.25
        row.operator("transform.create_orientation", text="New", icon='ADD', emboss=False).use = True

        if orientation:
            row = sub.row(align=True)
            row.scale_y = 1.25
            row.prop(orientation, "name", text="")
            row.operator("transform.delete_orientation", text="", icon="X", emboss=True)

        # Bottom
        split = pie.split()

        col = split.column(align=True)
        col.scale_y = 1.25
        dc.setup_op(col, "dconfig.set_snap_settings", "SNAP_VERTEX", "Vert snap", element='VERTEX', target='ACTIVE', align_rotation=False)
        dc.setup_op(col, "dconfig.set_snap_settings", "SNAP_FACE", "Face snap", element='FACE', target='MEDIAN', align_rotation=True)


class DCONFIG_MT_image_pivot(bpy.types.Menu):
    bl_label = "Pivot"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.space_data, "pivot_point", expand=True)


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


class DCONFIG_OT_set_snap_settings(bpy.types.Operator):
    bl_idname = "dconfig.set_snap_settings"
    bl_label = "DC Set Snap Settings"
    bl_description = "Set snapping settings"
    bl_options = {'REGISTER', 'UNDO'}

    element: bpy.props.StringProperty(name="Snap Element")
    target: bpy.props.StringProperty(name="Snap Target")
    align_rotation: bpy.props.BoolProperty(name="Align Rotation")

    def execute(self, context):
        dc.trace_enter(self)

        context.scene.tool_settings.snap_elements = {self.element}
        context.scene.tool_settings.snap_target = self.target
        context.scene.tool_settings.use_snap_align_rotation = self.align_rotation

        return dc.trace_exit(self)


def DCONFIG_FN_ui_origin_set(self, context):
    layout = self.layout

    layout.separator()

    if context.mode == 'EDIT_MESH':
        layout.operator("dconfig.set_pivot", text="Origin to Selected")
    else:
        dc.setup_op(layout, "object.origin_set", icon=None, text="Origin to Cursor", type='ORIGIN_CURSOR', center='MEDIAN')
        dc.setup_op(layout, "object.origin_set", icon=None, text="Origin to Geometry", type='ORIGIN_GEOMETRY', center='MEDIAN')


def register():
    bpy.types.VIEW3D_MT_snap.append(DCONFIG_FN_ui_origin_set)


def unregister():
    bpy.types.VIEW3D_MT_snap.remove(DCONFIG_FN_ui_origin_set)
