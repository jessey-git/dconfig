# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better booleans
#

from collections import namedtuple

import bpy
from . import DCONFIG_Utils as dc


TargetData = namedtuple('TargetData', ["object", "collection", "bool_collection"])
SourceData = namedtuple("SourceData", ["object", "collection"])


class Details:
    COLLECTION_PREFIX = "DC_boolean_"
    BOOLEAN_OBJECT_NAME = "dc_bool_obj"

    @classmethod
    def create_collection_name(cls, obj):
        return cls.COLLECTION_PREFIX + obj.name

    @classmethod
    def get_selected_meshes(cls, context):
        return [obj for obj in context.selected_objects if obj.type == "MESH"]


class DC_MT_boolean_pie(bpy.types.Menu):
    bl_label = "Booleans"

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        pie.operator("view3d.dc_boolean_apply", text="Apply")

        # RIGHT
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.5

        prop = col.operator("view3d.dc_boolean_live", text="Live Add")
        prop.bool_operation = 'UNION'
        prop.cutline = False
        prop.insetted = False

        prop = col.operator("view3d.dc_boolean_live", text="Live Intersect")
        prop.bool_operation = 'INTERSECT'
        prop.cutline = False
        prop.insetted = False

        prop = col.operator("view3d.dc_boolean_live", text="Live Subtract")
        prop.bool_operation = 'DIFFERENCE'
        prop.cutline = False
        prop.insetted = False

        prop = col.operator("view3d.dc_boolean_live", text="Live Subtract Inset")
        prop.bool_operation = 'DIFFERENCE'
        prop.cutline = False
        prop.insetted = True

        prop = col.operator("view3d.dc_boolean_live", text="Live Cutline")
        prop.bool_operation = 'DIFFERENCE'
        prop.cutline = True
        prop.insetted = False

        # BOTTOM
        pie.operator("view3d.dc_boolean_toggle", text="Toggle Live Booleans")


class DC_OT_boolean_live(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_live"
    bl_label = "DC Live Booleans"
    bl_description = "Add selected geometry as a boolean to the active objects"
    bl_options = {'REGISTER'}

    cutline: bpy.props.BoolProperty(name='Cutline', default=False)
    insetted: bpy.props.BoolProperty(name='Insetted', default=False)
    bool_operation: bpy.props.StringProperty(name="Boolean Operation")

    def create_bool_obj(self, context, source, inset_move_list):
        def rename_boolean_obj(source):
            old_name = dc.full_name(source.object)
            dc.rename(source.object, Details.BOOLEAN_OBJECT_NAME)
            dc.trace(2, "Renamed {} to {}", old_name, dc.full_name(source.object))

        if not source.object.name.startswith(Details.BOOLEAN_OBJECT_NAME):
            rename_boolean_obj(source)

            if self.cutline:
                mod = source.object.modifiers.new('Cutline', "SOLIDIFY")
                mod.thickness = 0.02

            if self.insetted:
                context.view_layer.objects.active = source.object
                source.object.select_set(state=True)

                bpy.ops.object.duplicate()
                inset = context.active_object
                dc.rename(inset, "DC_bool_inset")

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.ops.transform.resize(value=(0.92, 0.92, 0.92), constraint_axis=(False, False, False), mirror=False, proportional='DISABLED')
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                context.view_layer.objects.active = source.object
                bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                context.object.constraints["Copy Transforms"].target = inset
                inset_move_list.append(inset)

        source.object.display_type = 'WIRE'

    def create_bool_mod(self, target, source):
        dc.trace(2, "Adding boolean modifier to {}", dc.full_name(target.object))
        mod = target.object.modifiers.new(source.object.name, 'BOOLEAN')
        mod.object = source.object
        mod.operation = self.bool_operation
        mod.show_expanded = False

        # Booleans go at top of stack...
        mod_index = len(target.object.modifiers) - 1
        while mod_index > 0 and target.object.modifiers[mod_index - 1].type != 'BOOLEAN':
            bpy.ops.object.modifier_move_up(modifier=mod.name)
            mod_index -= 1

    def prepare_objects(self, context):
        if context.mode == 'EDIT_MESH':
            if context.object.data.total_vert_sel > 0:
                bpy.ops.mesh.select_linked()
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.separate(type='SELECTED')
        else:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all()
            bpy.ops.mesh.normals_make_consistent(inside=False)

    def prepare_data(self, context):
        bool_targets = []

        # Cleanup and separate if necessary...
        self.prepare_objects(context)

        # We should have at least 2 mesh objects (1 target, 1 source) at this point now...
        selected = Details.get_selected_meshes(context)
        if len(selected) < 2:
            return None, None

        # Place the bool_collection at the scene level to unclutter the object's own collection
        for obj in selected[:-1]:
            own_collection = dc.find_collection(context, obj)
            bool_collection = dc.make_collection(context.scene.collection, Details.create_collection_name(obj))
            bool_collection.hide_render = True
            bool_targets.append(TargetData(obj, own_collection, bool_collection))

        # Last object is the boolean source; remove any modifiers present on it...
        source = selected[-1]
        source_collection = dc.find_collection(context, source)

        active = context.view_layer.objects.active
        context.view_layer.objects.active = source
        while source.modifiers:
            modifier = source.modifiers[0]
            bpy.ops.object.modifier_remove(modifier=modifier.name)
        context.view_layer.objects.active = active

        bool_source = SourceData(source, source_collection)

        return bool_targets, bool_source

    def execute(self, context):
        dc.trace_enter("DC_OT_boolean_live")

        # Process and prepare all necessary data for the later operations
        # This supports multi-object editing by preparing data for every selected
        # object as best as possible. There is always just 1 boolean source object
        # to apply to 1 or more targets...
        bool_targets, bool_source = self.prepare_data(context)
        if bool_targets is None or bool_source is None:
            return dc.trace_exit("DC_OT_boolean_live", 'CANCELLED')

        dc.trace(1, "Data:")
        for target in bool_targets:
            dc.trace(2, "Target {}|{}|{}", dc.full_name(target.object), target.collection.name, target.bool_collection.name)
        dc.trace(2, "Source {}|{}", dc.full_name(bool_source.object), bool_source.collection.name)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        # Perform actual boolean operations (keeping track of the final set of geometry to move)...
        dc.trace(1, "Processing:")

        inset_move_list = []
        self.create_bool_obj(context, bool_source, inset_move_list)
        for target in bool_targets:
            self.create_bool_mod(target, bool_source)

        # Place everything in the right collection...

        # Link the source into each target's boolean collection...
        for target in bool_targets:
            if bool_source.object.name not in target.bool_collection.objects:
                target.bool_collection.objects.link(bool_source.object)

        # Remove it from its existing location IFF it's not already in a boolean collection
        if not bool_source.collection.name.startswith(Details.COLLECTION_PREFIX):
            bool_source.collection.objects.unlink(bool_source.object)

        # Pick the first target as the place to move the new inset geometry
        first_target = bool_targets[0]
        for obj in inset_move_list:
            if obj.name not in first_target.collection.objects:
                first_target.collection.objects.link(obj)

        bpy.ops.object.select_all(action='DESELECT')
        first_target.object.select_set(state=True)

        return dc.trace_exit("DC_OT_boolean_live")


class DC_OT_boolean_toggle(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_toggle"
    bl_label = "DC Toggle Cutters"
    bl_description = "Toggle boolean viewport visability for the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dc.trace_enter("DC_OT_boolean_toggle")

        # Grab our main active object...
        active = context.active_object
        dc.trace(1, "Active: {}", dc.full_name(active))

        # Toggle viewport visibility on our special boolean collection for this object...
        collection_name = Details.create_collection_name(active)
        if collection_name in bpy.data.collections:
            dc.trace(1, "Toggling visibility: {}", collection_name)
            bpy.data.collections[collection_name].hide_viewport = not bpy.data.collections[collection_name].hide_viewport

        return dc.trace_exit("DC_OT_boolean_toggle")


class DC_OT_boolean_apply(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_apply"
    bl_label = "DC Apply Booleans"
    bl_description = "Apply all boolean modifiers for the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dc.trace_enter("DC_OT_boolean_apply")

        if context.mode != "OBJECT":
            return dc.trace_exit("DC_OT_boolean_apply", result='CANCELLED')

        # Process all selected objects...
        for current_object in Details.get_selected_meshes(context):
            dc.trace(1, "Processing: {}", dc.full_name(current_object))

            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = current_object

            # We need to apply everything up until the last boolean modifier
            mod_count = len(current_object.modifiers)
            mod_apply_count = 0
            for i in range(mod_count - 1, -1, -1):
                if current_object.modifiers[i].type == 'BOOLEAN':
                    mod_apply_count = i + 1
                    break

            dc.trace(2, "Applying {} of {} modifiers", mod_apply_count, mod_count)

            orphaned_objects = []
            for i in range(mod_apply_count):
                modifier = current_object.modifiers[0]
                dc.trace(3, "Applying {}", modifier.type)

                if modifier.type == 'BOOLEAN' and modifier.object is not None:
                    orphaned_objects.append(modifier.object)

                try:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)
                except RuntimeError:
                    bpy.ops.object.modifier_remove(modifier=modifier.name)

            # Only delete boolean objects that are not linked anywhere else...
            dc.trace(2, "Processing orphaned objects: {}", dc.full_names(orphaned_objects))
            orphans_to_delete = [o for o in orphaned_objects if len(o.users_collection) < 2]
            orphans_to_unlink = [o for o in orphaned_objects if len(o.users_collection) > 1]

            # The collection must be visible for delete to work...
            collection_name = Details.create_collection_name(current_object)
            if collection_name in bpy.data.collections:
                bpy.data.collections[collection_name].hide_viewport = False

            if orphans_to_delete:
                dc.trace(2, "Removing {} orphaned objects", len(orphans_to_delete))
                for obj in orphans_to_delete:
                    obj.select_set(True)

                bpy.ops.object.delete(use_global=False, confirm=False)

            # Now remove the collection...
            if collection_name in bpy.data.collections:
                col_bool = bpy.data.collections[collection_name]

                # Unlink orphans who actually have a home somewhere else...
                if orphans_to_unlink:
                    dc.trace(2, "Unlinking {} orphaned objects", len(orphans_to_unlink))
                    for orphan in orphans_to_unlink:
                        col_bool.objects.unlink(orphan)

                # The user may have inserted their own objects
                if not col_bool.all_objects:
                    dc.trace(2, "Removing collection: {}", collection_name)

                    # Find correct parent collection to delete from...
                    parent_col = None
                    for col in bpy.data.collections:
                        if collection_name in col.children:
                            parent_col = col
                            break

                    if parent_col is None:
                        parent_col = context.scene.collection

                    parent_col.children.unlink(col_bool)
                    bpy.data.collections.remove(col_bool)
                else:
                    dc.trace(2, "Collection still contains objects; not removing: {}", collection_name)

        return dc.trace_exit("DC_OT_boolean_apply")
