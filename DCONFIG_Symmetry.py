# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better symmetry
#

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_MT_symmetry_pie(bpy.types.Menu):
    bl_label = "Symmetry"

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_available(context)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        pie.operator("dconfig.mesh_symmetry", text="+X to -X", icon='TRIA_LEFT').direction = 'POSITIVE_X'

        # Right
        pie.operator("dconfig.mesh_symmetry", text="-X to +X", icon='TRIA_RIGHT').direction = 'NEGATIVE_X'

        # Bottom
        pie.operator("dconfig.mesh_symmetry", text="+Z to -Z", icon='TRIA_DOWN').direction = 'POSITIVE_Z'

        # Top
        pie.operator("dconfig.mesh_symmetry", text="-Z to +Z", icon='TRIA_UP').direction = 'NEGATIVE_Z'

        # Top Left
        pie.operator("dconfig.mirror", text="Mirror Local", icon='MOD_MIRROR').local = True

        # Top Right
        pie.operator("dconfig.mirror", text="Mirror World", icon='MOD_MIRROR').local = False

        # Bottom Left
        pie.operator("dconfig.mesh_symmetry", text="+Y to -Y", icon='DOT').direction = 'POSITIVE_Y'

        # Bottom Right
        pie.operator("dconfig.mesh_symmetry", text="-Y to +Y", icon='DOT').direction = 'NEGATIVE_Y'


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

        return dc.trace_exit(self)


class DCONFIG_OT_mirror(bpy.types.Operator):
    bl_idname = "dconfig.mirror"
    bl_label = "DC Mirror"
    bl_description = "Mirrow mesh across an axis"
    bl_options = {'REGISTER', 'UNDO'}

    local: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        target = context.active_object
        mirror_object = self.create_mirror_obj(context)
        self.create_mirror_mod(target, mirror_object)

        return dc.trace_exit(self)

    def create_mirror_obj(self, context):
        mirror_object = None
        if not self.local:
            # Use a special collection
            helpers_collection = dc.make_helpers_collection(context)

            if "DC_World_Origin" in helpers_collection.all_objects:
                dc.trace(1, "Using existing world-origin empty")
                mirror_object = helpers_collection.objects["DC_World_Origin"]
            else:
                dc.trace(1, "Creating new world-origin empty")
                original_object = context.view_layer.objects.active
                original_mode = context.object.mode

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
                mirror_object = bpy.context.object
                mirror_object.name = "DC_World_Origin"
                mirror_object.select_set(state=False)
                mirror_object.hide_viewport = True

                mirror_object_collection = dc.find_collection(context, mirror_object)
                helpers_collection.objects.link(mirror_object)
                mirror_object_collection.objects.unlink(mirror_object)

                context.view_layer.objects.active = original_object
                context.view_layer.objects.active.select_set(True)
                bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        return mirror_object

    def create_mirror_mod(self, target, mirror_object):
        dc.trace(1, "Adding {} mirror modifier to {}", "local" if self.local else "world", dc.full_name(target))

        if self.local:
            mod = target.modifiers.new("dc_local", "MIRROR")
            mod.use_axis[0] = True
            mod.use_bisect_axis[0] = True
            mod.use_clip = True
        else:
            mod = target.modifiers.new("dc_world", "MIRROR")
            mod.use_axis[0] = True
            mod.use_bisect_axis[0] = False
            mod.mirror_object = mirror_object

        mod.show_on_cage = True
        mod.show_expanded = False

        # Local mirrors go before World and after Booleans...
        if self.local:
            mod_index = len(target.modifiers) - 1
            while mod_index > 0 and target.modifiers[mod_index - 1].type != 'BOOLEAN':
                bpy.ops.object.modifier_move_up(modifier=mod.name)
                mod_index -= 1
