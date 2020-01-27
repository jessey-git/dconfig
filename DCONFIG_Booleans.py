# ------------------------------------------------------------
# Copyright(c) 2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better booleans
#

from collections import namedtuple

import bpy
from . import DCONFIG_Utils as dc


BoolData = namedtuple('BoolData', ["object", "collection"])


class Details:
    BOOLEAN_OBJECT_NAME = "dc_bool_obj"


class DCONFIG_MT_boolean_pie(bpy.types.Menu):
    bl_label = "Booleans"

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_available(context)

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25

        dc.setup_op(col, "dconfig.boolean_immediate", 'DOT', "Add", bool_operation='UNION')
        dc.setup_op(col, "dconfig.boolean_immediate", 'DOT', "Intersect", bool_operation='INTERSECT')
        dc.setup_op(col, "dconfig.boolean_immediate", 'DOT', "Subtract", bool_operation='DIFFERENCE')

        # Right
        split = pie.split()
        col = split.column(align=True)
        col.scale_y = 1.25

        dc.setup_op(col, "dconfig.boolean_live", 'MOD_BOOLEAN', "Live Add", bool_operation='UNION', cutline=False, insetted=False)
        dc.setup_op(col, "dconfig.boolean_live", 'MOD_BOOLEAN', "Live Intersect", bool_operation='INTERSECT', cutline=False, insetted=False)
        dc.setup_op(col, "dconfig.boolean_live", 'MOD_BOOLEAN', "Live Subtract", bool_operation='DIFFERENCE', cutline=False, insetted=False)

        dc.setup_op(col, "dconfig.boolean_live", 'MOD_BOOLEAN', "Live Subtract Inset", bool_operation='DIFFERENCE', cutline=False, insetted=True)
        dc.setup_op(col, "dconfig.boolean_live", 'MOD_BOOLEAN', "Live Cutline", bool_operation='DIFFERENCE', cutline=True, insetted=False)

        # Bottom
        dc.setup_op(pie, "dconfig.boolean_toggle", 'HIDE_OFF', "Toggle Live Booleans")

        # Top
        dc.setup_op(pie, "dconfig.boolean_apply", text="Apply")


class DCONFIG_OT_boolean_live(bpy.types.Operator):
    bl_idname = "dconfig.boolean_live"
    bl_label = "DC Live Booleans"
    bl_description = "Add selected geometry as a boolean to the active objects"
    bl_options = {'REGISTER'}

    cutline: bpy.props.BoolProperty(name='Cutline', default=False)
    insetted: bpy.props.BoolProperty(name='Insetted', default=False)
    bool_operation: bpy.props.StringProperty(name="Boolean Operation")

    @classmethod
    def poll(cls, context):
        return dc.active_mesh_selected(context)

    def create_bool_obj(self, context, source, inset_move_list):
        def rename_boolean_obj(source):
            old_name = dc.full_name(source.object)
            dc.rename(source.object, Details.BOOLEAN_OBJECT_NAME)
            dc.trace(2, "Renamed {} to {}", old_name, dc.full_name(source.object))

        if not source.object.name.startswith(Details.BOOLEAN_OBJECT_NAME):
            rename_boolean_obj(source)

            if self.cutline:
                mod = source.object.modifiers.new('Cutline', "SOLIDIFY")
                mod.thickness = 0.007

            if self.insetted:
                context.view_layer.objects.active = source.object
                source.object.select_set(state=True)

                bpy.ops.object.duplicate()
                inset = context.active_object
                dc.rename(inset, "dc_bool_inset")

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.ops.transform.resize(value=(0.95, 0.95, 0.95), constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False)
                context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

                context.view_layer.objects.active = source.object
                bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                context.active_object.constraints["Copy Transforms"].target = inset
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
            if context.active_object.data.total_vert_sel > 0:
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
        selected_meshes = dc.get_sorted_meshes(context.selected_objects, context.active_object)
        if len(selected_meshes) < 2:
            return None, None

        # Track the target data
        for obj in selected_meshes[:-1]:
            own_collection = dc.find_collection(context, obj)
            bool_targets.append(BoolData(obj, own_collection))

        # Last object is the boolean source
        source = selected_meshes[-1]
        source_collection = dc.find_collection(context, source)
        bool_source = BoolData(source, source_collection)

        return bool_targets, bool_source

    def execute(self, context):
        dc.trace_enter(self)

        # Process and prepare all necessary data for the later operations
        # This supports multi-object editing by preparing data for every selected
        # object as best as possible. There is always just 1 boolean source object
        # to apply to 1 or more targets...
        bool_targets, bool_source = self.prepare_data(context)
        if bool_targets is None or bool_source is None:
            return dc.warn_canceled(self, "At least 2 mesh objects must be selected")

        dc.trace(1, "Data:")
        for target in bool_targets:
            dc.trace(2, "Target {}|{}", dc.full_name(target.object), target.collection.name)
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
        bool_collection = dc.get_boolean_collection(context, True)

        # Link the source into the boolean collection...
        if bool_source.object.name not in bool_collection.objects:
            bool_collection.objects.link(bool_source.object)
            bool_source.collection.objects.unlink(bool_source.object)

        # Pick the first target as the place to move the new inset geometry
        first_target = bool_targets[0]
        for obj in inset_move_list:
            if obj.name not in first_target.collection.objects:
                first_target.collection.objects.link(obj)

        bpy.ops.object.select_all(action='DESELECT')
        first_target.object.select_set(state=True)

        return dc.trace_exit(self)


class DCONFIG_OT_boolean_immediate(bpy.types.Operator):
    bl_idname = "dconfig.boolean_immediate"
    bl_label = "DC Booleans"
    bl_description = "Add selected geometry as a boolean to the active objects"
    bl_options = {'REGISTER', 'UNDO'}

    bool_operation: bpy.props.StringProperty(name="Boolean Operation")

    @classmethod
    def poll(cls, context):
        ok_edit = context.mode == 'EDIT_MESH' and context.active_object.data.total_face_sel > 0
        ok_object = context.mode == 'OBJECT' and len(context.selected_objects) > 1
        return ok_edit or ok_object

    def execute(self, context):
        dc.trace_enter(self)

        if context.mode == 'EDIT_MESH':
            dc.trace(1, "Performing direct mesh boolean from selected geometry")
            bpy.ops.mesh.select_linked()

            context.active_object.update_from_editmode()
            if context.active_object.data.total_vert_sel == len(context.active_object.data.vertices):
                return dc.warn_canceled(self, "All vertices of object became selected")

            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.intersect_boolean(operation=self.bool_operation)
        else:
            # Process and prepare all necessary data for the later operations
            # This supports multi-object editing by preparing data for every selected
            # object as best as possible. There is always just 1 boolean source object
            # to apply to 1 or more targets...
            bool_targets, bool_source = self.prepare_data(context)
            if bool_targets is None or bool_source is None:
                return dc.warn_canceled(self, "At least 2 mesh objects must be selected")

            dc.trace(1, "Data:")
            for target in bool_targets:
                dc.trace(2, "Target {}", dc.full_name(target.object))
            dc.trace(2, "Source {}", dc.full_name(bool_source.object))

            # Perform actual boolean operations...
            dc.trace(1, "Processing:")

            for target in bool_targets:
                context.view_layer.objects.active = target.object
                target.object.select_set(True)

                self.apply_bool_mod(target, bool_source)

            dc.trace(1, "Cleanup:")
            bpy.ops.object.select_all(action='DESELECT')

            source_name = dc.full_name(bool_source.object)
            bool_source.object.select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)
            dc.trace(2, "Deleted {}", source_name)

        return dc.trace_exit(self)

    def prepare_source(self, context, source):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.objects.active = source
        source.select_set(True)

        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.normals_make_consistent(inside=False)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

    def prepare_data(self, context):
        bool_targets = []

        # We should have at least 2 mesh objects (1 target, 1 source) at this point now...
        selected_meshes = dc.get_meshes(context.selected_objects)
        if len(selected_meshes) < 2:
            return None, None

        # Track each target
        for obj in selected_meshes[:-1]:
            bool_targets.append(BoolData(obj, None))

        # Last object is the boolean source; make sure all modifiers are applied and cleanup...
        source = selected_meshes[-1]
        self.prepare_source(context, source)
        bool_source = BoolData(source, None)

        return bool_targets, bool_source

    def apply_bool_mod(self, target, source):
        dc.trace(2, "Applying boolean modifier to {}", dc.full_name(target.object))
        mod = target.object.modifiers.new(source.object.name, 'BOOLEAN')
        mod.object = source.object
        mod.operation = self.bool_operation

        # Non-Live Booleans go to top-most location in the stack...
        mod_index = len(target.object.modifiers) - 1
        while mod_index > 0:
            bpy.ops.object.modifier_move_up(modifier=mod.name)
            mod_index -= 1

        try:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        except RuntimeError as e:
            dc.trace(2, "Failed! Applying failed with {}", e)


class DCONFIG_OT_boolean_toggle(bpy.types.Operator):
    bl_idname = "dconfig.boolean_toggle"
    bl_label = "DC Toggle Cutters"
    bl_description = "Toggle boolean viewport visability for the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dc.trace_enter(self)

        bool_collection = dc.get_boolean_collection(context, False)
        if bool_collection is not None:
            hide_viewport = not bool_collection.hide_viewport
            dc.trace(1, "Setting visibility to {}", hide_viewport)
            bool_collection.hide_viewport = hide_viewport

        return dc.trace_exit(self)


class DCONFIG_OT_boolean_apply(bpy.types.Operator):
    bl_idname = "dconfig.boolean_apply"
    bl_label = "DC Apply Booleans"
    bl_description = "Apply all boolean modifiers for the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and dc.active_mesh_selected(context)

    def execute(self, context):
        dc.trace_enter(self)

        # Process all selected objects...
        for current_object in dc.get_meshes(context.selected_objects):
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
            orphans_to_delete = []
            for orphan in orphaned_objects:
                ok_to_delete = True
                for obj in bpy.data.objects:
                    if obj not in orphaned_objects:
                        for modifier in obj.modifiers:
                            if modifier.type == 'BOOLEAN' and modifier.object is not None and modifier.object.name == orphan.name:
                                ok_to_delete = False
                                break

                    if not ok_to_delete:
                        break

                if ok_to_delete:
                    orphans_to_delete.append(orphan)

            # The collection must be visible for delete to work...
            bool_collection = dc.get_boolean_collection(context, False)
            if bool_collection is not None:
                prev_hide_viewport = bool_collection.hide_viewport
                bool_collection.hide_viewport = False

            dc.trace(2, "Removing {} orphaned objects", len(orphans_to_delete))
            if orphans_to_delete:
                for obj in orphans_to_delete:
                    obj.select_set(True)

                bpy.ops.object.delete(use_global=False, confirm=False)

            # Now remove the collection...
            if bool_collection is not None:
                # The user may have inserted their own objects
                if not bool_collection.all_objects:
                    dc.trace(2, "Removing collection: {}", bool_collection.name)

                    # Find correct parent collection to delete from...
                    parent_collection = None
                    for collection in bpy.data.collections:
                        if bool_collection.name in collection.children:
                            parent_collection = collection
                            break

                    if parent_collection is None:
                        parent_collection = context.scene.collection

                    parent_collection.children.unlink(bool_collection)
                    bpy.data.collections.remove(bool_collection)
                else:
                    dc.trace(2, "Collection still contains objects; not removing: {}", bool_collection.name)
                    bool_collection.hide_viewport = prev_hide_viewport

        return dc.trace_exit(self)
