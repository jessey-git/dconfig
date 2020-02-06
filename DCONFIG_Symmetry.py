# ------------------------------------------------------------
# Copyright(c) 2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better symmetry
#

import bpy

from mathutils import (Vector, Matrix)
from . import DCONFIG_Utils as dc


class DCONFIG_OT_mesh_symmetry(bpy.types.Operator):
    bl_idname = "dconfig.mesh_symmetry"
    bl_label = "DC Mesh Symmetry"
    bl_description = "Symmetrize mesh along an axis"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=(
            ('POSITIVE_X', "+X to -X", "+X to -X", 0),
            ('NEGATIVE_X', "-X to +X", "-X to +X", 1),
            ('POSITIVE_Y', "+Y to -Y", "+Y to -Y", 2),
            ('NEGATIVE_Y', "-Y to +Y", "-Y to +Y", 3),
            ('POSITIVE_Z', "+Z to -Z", "+Z to -Z", 4),
            ('NEGATIVE_Z', "-Z to +Z", "-Z to +Z", 5),
        ),
        name="Direction",
        description="which side to copy from",
        default='POSITIVE_X',
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)

    dc_uses_symmetry_gizmo = True

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        if context.mode == 'EDIT_MESH':
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.symmetrize(direction=self.direction)
        else:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.symmetrize(direction=self.direction)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        DCONFIG_GGT_symmetry_gizmo.destroy(context)

        return dc.trace_exit(self)

    def invoke(self, context, event):
        dc.trace_enter(self)

        if context.space_data.type == 'VIEW_3D':
            DCONFIG_GGT_symmetry_gizmo.create(context)

        return dc.trace_exit(self)


class DCONFIG_GT_symmetry_gizmo(bpy.types.Gizmo):
    __slots__ = (
        "custom_shape",
        "op",
        "direction",
        "draw_offset",
    )

    cube_tri_verts = (
        (-0.5, -0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5),
        (-0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (0.5, 0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5),
        (0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
        (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5),
        (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5),
        (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5),
        (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5),
        (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', self.cube_tri_verts)

    def update(self, mat_target):
        self.matrix_basis = mat_target
        self.matrix_offset = Matrix.Translation(self.draw_offset * 3)

    def invoke(self, context, event):
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        if event.value == 'PRESS':
            self.op.direction = self.direction
            self.op.execute(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


class DCONFIG_GGT_symmetry_gizmo(bpy.types.GizmoGroup):
    bl_label = "Symmetry Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    gizmo_state = {}

    @staticmethod
    def my_target_operator(context):
        wm = context.window_manager
        op = wm.operators[-1] if wm.operators else None
        return op if getattr(op, "dc_uses_symmetry_gizmo", False) else None

    @classmethod
    def poll(cls, context):
        op = cls.my_target_operator(context)
        if op is None:
            DCONFIG_GGT_symmetry_gizmo.destroy(context)
            return False
        return True

    @classmethod
    def create(cls, context):
        cls.gizmo_state['show_gizmo_object_translate'] = context.space_data.show_gizmo_object_translate
        cls.gizmo_state['show_gizmo_object_rotate'] = context.space_data.show_gizmo_object_rotate
        cls.gizmo_state['show_gizmo_object_scale'] = context.space_data.show_gizmo_object_scale
        cls.gizmo_state['show_gizmo'] = context.space_data.show_gizmo

        context.space_data.show_gizmo_object_translate = False
        context.space_data.show_gizmo_object_rotate = False
        context.space_data.show_gizmo_object_scale = False
        context.space_data.show_gizmo = True

        wm = context.window_manager
        wm.gizmo_group_type_ensure("DCONFIG_GGT_symmetry_gizmo")

    @classmethod
    def destroy(cls, context):
        wm = context.window_manager
        wm.gizmo_group_type_unlink_delayed("DCONFIG_GGT_symmetry_gizmo")

        if cls.gizmo_state:
            context.space_data.show_gizmo_object_translate = cls.gizmo_state['show_gizmo_object_translate']
            context.space_data.show_gizmo_object_rotate = cls.gizmo_state['show_gizmo_object_rotate']
            context.space_data.show_gizmo_object_scale = cls.gizmo_state['show_gizmo_object_scale']
            context.space_data.show_gizmo = cls.gizmo_state['show_gizmo']
            cls.gizmo_state.clear()

    def setup(self, context):
        def setup_widget(direction, draw_offset, color):
            mpr = self.gizmos.new("DCONFIG_GT_symmetry_gizmo")
            mpr.op = DCONFIG_GGT_symmetry_gizmo.my_target_operator(context)
            mpr.direction = direction
            mpr.draw_offset = draw_offset

            mpr.color = color
            mpr.alpha = 0.3
            mpr.color_highlight = color
            mpr.alpha_highlight = 0.5

            mpr.select_bias = 0
            mpr.scale_basis = 0.2

            mpr.use_draw_offset_scale = True
            mpr.use_select_background = True
            mpr.use_event_handle_all = False

        ui_theme_prefs = context.preferences.themes[0].user_interface
        setup_widget("POSITIVE_X", Vector((-1, 0, 0)), ui_theme_prefs.axis_x)
        setup_widget("NEGATIVE_X", Vector((1, 0, 0)), ui_theme_prefs.axis_x)
        setup_widget("POSITIVE_Y", Vector((0, -1, 0)), ui_theme_prefs.axis_y)
        setup_widget("NEGATIVE_Y", Vector((0, 1, 0)), ui_theme_prefs.axis_y)
        setup_widget("POSITIVE_Z", Vector((0, 0, -1)), ui_theme_prefs.axis_z)
        setup_widget("NEGATIVE_Z", Vector((0, 0, 1)), ui_theme_prefs.axis_z)

    def refresh(self, context):
        target = context.active_object

        mat_target = target.matrix_world.normalized()
        for mpr in self.gizmos:
            mpr.update(mat_target)
