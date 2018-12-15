# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better booleans
#

import bpy
import bmesh
from collections import namedtuple
from . import DCONFIG_Utils as DC


TargetData = namedtuple('TargetData', ["object", "collection", "bool_collection"])
SourceData = namedtuple("SourceData", ["object", "collection"])


class Constants:
    COLLECTION_PREFIX = "DC_boolean_"
    BOOLEAN_OBJECT_NAME = "dc_bool_obj"

    @classmethod
    def create_collection_name(cls, item):
        return cls.COLLECTION_PREFIX + item.name


class DC_MT_boolean_pie(bpy.types.Menu):
    bl_label = "Booleans"

    @classmethod
    def poll(self, context):
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
        pie.operator("view3d.dc_boolean_toggle_cutters", text="Toggle Cutters")


class DC_OT_boolean_live(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_live"
    bl_label = "DC Live Booleans"
    bl_description = "Add selected geometry as a boolean to the active objects"
    bl_options = {'REGISTER'}

    cutline: bpy.props.BoolProperty(name='Cutline', default=False)
    insetted: bpy.props.BoolProperty(name='Insetted', default=False)
    bool_operation: bpy.props.StringProperty(name="Boolean Operation")

    def find_collection(self, context, item):
        collections = item.users_collection
        if len(collections) > 0:
            return collections[0]
        return context.scene.collection

    def make_bool_collection(self, item, parent_collection):
        collection_name = Constants.create_collection_name(item)
        if collection_name in bpy.data.collections.keys():
            return bpy.data.collections[collection_name]
        else:
            bool_collection = bpy.data.collections.new(collection_name)
            bool_collection.hide_render = True
            parent_collection.children.link(bool_collection)
            return bool_collection

    def create_bool_obj(self, context, source, inset_move_list):
        def rename_boolean_obj(source):
            old_name = DC.full_name(source.object)
            DC.rename(source.object, Constants.BOOLEAN_OBJECT_NAME)
            DC.trace(2, "Renamed {} to {}", old_name, DC.full_name(source.object))

        if not source.object.name.startswith(Constants.BOOLEAN_OBJECT_NAME):
            rename_boolean_obj(source)

            if self.cutline:
                mod = source.object.modifiers.new('Cutline', "SOLIDIFY")
                mod.thickness = 0.02

            if self.insetted:
                context.view_layer.objects.active = source.object
                source.object.select_set(state=True)

                bpy.ops.object.duplicate()
                inset = context.active_object
                DC.rename(inset, "DC_bool_inset")

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
        DC.trace(2, "Adding boolean modifier to {}", DC.full_name(target.object))
        mod = target.object.modifiers.new(source.object.name, 'BOOLEAN')
        mod.object = source.object
        mod.operation = self.bool_operation

    def prepare_objects(self, context):
        if context.active_object.mode == 'EDIT':
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

        # We should have at least 2 objects (1 target, 1 source) at this point now...
        selected = context.selected_objects
        if len(selected) < 2:
            return None, None

        for item in selected[:-1]:
            own_collection = self.find_collection(context, item)
            bool_collection = self.make_bool_collection(item, own_collection)
            bool_targets.append(TargetData(item, own_collection, bool_collection))

        source = context.selected_objects[-1]
        source_collection = self.find_collection(context, source)
        bool_source = SourceData(source, source_collection)

        return bool_targets, bool_source

    def execute(self, context):
        DC.trace_enter("DC_OT_boolean_live.execute")

        # Process and prepare all necessary data for the later operations
        # This supports multi-object editing by preparing data for every selected
        # object as best as possible. There is always just 1 boolean source object
        # to apply to 1 or more targets...
        bool_targets, bool_source = self.prepare_data(context)
        if bool_targets is None or bool_source is None:
            return DC.trace_exit("DC_OT_boolean_live.execute", 'CANCELLED')

        DC.trace(1, "Data:")
        for target in bool_targets:
            DC.trace(2, "Target {}|{}|{}", DC.full_name(target.object), target.collection.name, target.bool_collection.name)
        DC.trace(2, "Source {}|{}", DC.full_name(bool_source.object), bool_source.collection.name)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        # Perform actual boolean operations (keeping track of the final set of geometry to move)...
        DC.trace(1, "Processing:")

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
        if not bool_source.collection.name.startswith(Constants.COLLECTION_PREFIX):
            bool_source.collection.objects.unlink(bool_source.object)

        # Pick the first target as the place to move the new inset geometry
        first_target = bool_targets[0]
        for item in inset_move_list:
            if item.name not in first_target.collection.objects:
                first_target.collection.objects.link(item)

        bpy.ops.object.select_all(action='DESELECT')
        first_target.object.select_set(state=True)

        return DC.trace_exit("DC_OT_boolean_live.execute")


class DC_OT_toggle_cutters(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_toggle_cutters"
    bl_label = "DC Toggle Cutters"
    bl_description = "Toggle boolean viewport visability for the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        DC.trace_enter("DC_OT_toggle_cutters.execute")

        # Grab our main active object...
        active = context.active_object
        DC.trace(1, "Active: {}", DC.full_name(active))

        # Toggle viewport visibility on our special boolean collection for this object...
        collection_name = Constants.create_collection_name(active)
        if collection_name in bpy.data.collections.keys():
            DC.trace(1, "Toggling visibility: {}", collection_name)
            bpy.data.collections[collection_name].hide_viewport = not bpy.data.collections[collection_name].hide_viewport

        return DC.trace_exit("DC_OT_toggle_cutters.execute")


class DC_OT_boolean_apply(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_apply"
    bl_label = "DC Apply Booleans"
    bl_description = "Apply all boolean modifiers for the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        DC.trace_enter("DC_OT_boolean_apply.execute")

        if context.mode != "OBJECT":
            return DC.trace_exit("DC_OT_boolean_apply.execute", result='CANCELLED')

        # Process all selected objects...
        for current_object in context.selected_objects:
            DC.trace(1, "Processing: {}", DC.full_name(current_object))

            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = current_object

            # We need to apply everything up until the last boolean modifier
            mod_count = len(current_object.modifiers)
            mod_apply_count = 0
            if len(current_object.modifiers) > 0:
                for i in range(mod_count - 1, -1, -1):
                    if current_object.modifiers[i].type == 'BOOLEAN':
                        mod_apply_count = i + 1
                        break

            DC.trace(2, "Applying {} of {} modifiers", mod_apply_count, mod_count)

            orphaned_objects = []
            for i in range(mod_apply_count):
                modifier = current_object.modifiers[0]
                DC.trace(3, "Applying {}", modifier.type)

                if modifier.type == 'BOOLEAN' and modifier.object is not None:
                    orphaned_objects.append(modifier.object)

                try:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)
                except RuntimeError:
                    bpy.ops.object.modifier_remove(modifier=modifier.name)

            # Only delete boolean objects that are not linked anywhere else...
            DC.trace(2, "Processing orphaned objects: {}", DC.full_names(orphaned_objects))
            orphans_to_delete = [o for o in orphaned_objects if len(o.users_collection) < 2]
            orphans_to_unlink = [o for o in orphaned_objects if len(o.users_collection) > 1]

            if len(orphans_to_delete) > 0:
                DC.trace(2, "Removing {} orphaned objects", len(orphans_to_delete))
                for obj in orphans_to_delete:
                    obj.select_set(True)

                bpy.ops.object.delete(use_global=False, confirm=False)

            # Now remove the collection
            collection_name = Constants.create_collection_name(current_object)
            if collection_name in bpy.data.collections:
                col_bool = bpy.data.collections[collection_name]

                # Unlink orphans who actually have a home somewhere else...
                if len(orphans_to_unlink) > 0:
                    DC.trace(2, "Unlinking {} orphaned objects", len(orphans_to_unlink))
                    for orphan in orphans_to_unlink:
                        col_bool.objects.unlink(orphan)

                # The user may have inserted their own objects
                if len(col_bool.all_objects) == 0:
                    DC.trace(2, "Removing collection: {}", collection_name)

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
                    DC.trace(2, "Collection still contains objects; not removing: {}", collection_name)

        return DC.trace_exit("DC_OT_boolean_apply.execute")
