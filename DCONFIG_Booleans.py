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
from . import DCONFIG_Utils as DC

CollectionPrefix = "DC_boolean"


def create_collection_name(base):
    return CollectionPrefix + base.name


class DC_MT_boolean_pie(bpy.types.Menu):
    bl_label = "Booleans"

    @classmethod
    def poll(self, context):
        return bpy.context.active_object.type == "MESH"

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
    bl_options = {'REGISTER'}

    cutline: bpy.props.BoolProperty(name='Cutline', default=False)
    insetted: bpy.props.BoolProperty(name='Insetted', default=False)
    bool_operation: bpy.props.StringProperty(name="Boolean Operation")

    def rename_boolean_obj(self, boolean_obj):
        old_name = DC.full_name(boolean_obj)
        new_name = "dc_bool_obj"

        boolean_obj.name = new_name
        boolean_obj.data.name = new_name
        DC.trace(2, "Renamed {} to {}", old_name, DC.full_name(boolean_obj))

    def rename_inset_obj(self, base, inset):
        new_name = base.name + "_inset"
        inset.name = new_name
        inset.data.name = new_name

    def create_bool_obj(self, base, boolean_obj, boolean_move_list, inset_move_list):
        if not boolean_obj.name.startswith("dc_"):
            self.rename_boolean_obj(boolean_obj)

            if self.cutline:
                mod = boolean_obj.modifiers.new('Cutline', "SOLIDIFY")
                mod.thickness = 0.02

            if self.insetted:
                bpy.context.view_layer.objects.active = boolean_obj
                base.select_set(state=False)
                boolean_obj.select_set(state=True)

                bpy.ops.object.duplicate()
                inset = bpy.context.active_object
                self.rename_inset_obj(base, inset)

                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.ops.transform.resize(value=(0.92, 0.92, 0.92), constraint_axis=(False, False, False), mirror=False, proportional='DISABLED')
                bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
                bpy.ops.object.editmode_toggle()

                bpy.context.view_layer.objects.active = boolean_obj
                bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                bpy.context.object.constraints["Copy Transforms"].target = inset
                inset_move_list.append(inset)

        boolean_obj.display_type = 'WIRE'
        boolean_move_list.append(boolean_obj)

    def create_bool_mod(self, base, boolean_obj):
        DC.trace(2, "Adding boolean modifier to {}", DC.full_name(base))
        mod = base.modifiers.new(boolean_obj.name, "BOOLEAN")
        mod.object = boolean_obj
        mod.operation = self.bool_operation

    def prepare_collections(self, base):
        col_orig = None
        col_bool = None

        base_collections = base.users_collection
        if len(base_collections) > 0:
            col_orig = base_collections[0]
        else:
            col_orig = bpy.context.scene.collection

        collection_name = create_collection_name(base)
        if collection_name in bpy.data.collections.keys():
            col_bool = bpy.data.collections[collection_name]
        else:
            col_bool = bpy.data.collections.new(collection_name)
            col_orig.children.link(col_bool)

        col_bool.hide_render = True

        DC.trace(1, "Original collection name: {}", col_orig.name)
        DC.trace(1, "Boolean collection name: {}", col_bool.name)
        return col_orig, col_bool

    def prepare_objects(self):
        if bpy.context.active_object.mode == "EDIT":
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.separate(type='SELECTED')
        else:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all()
            bpy.ops.mesh.normals_make_consistent(inside=False)

    def execute(self, context):
        DC.trace_enter("DC_OT_boolean_live.execute")

        # Grab our main active object...
        base = bpy.context.active_object
        DC.trace(1, "Base: {}", DC.full_name(base))

        # Prepare the boolean objects and our collections...
        self.prepare_objects()
        col_orig, col_bool = self.prepare_collections(base)

        bpy.ops.object.editmode_toggle()
        selected = bpy.context.selected_objects

        DC.trace(1, "Current selection: {}", DC.full_names(selected))

        # Perform actual boolean operations (keeping track of the final set of geometry to move)...
        boolean_move_list = []
        inset_move_list = []
        for obj in selected:
            if obj != base:
                DC.trace(1, "Found boolean obj: {}", DC.full_name(obj))
                self.create_bool_obj(base, obj, boolean_move_list, inset_move_list)
                self.create_bool_mod(base, obj)

        # Place everything in the right collection...
        DC.trace(1, "Boolean Move list: {}", DC.full_names(boolean_move_list))
        DC.trace(1, "Inset Move list: {}", DC.full_names(inset_move_list))
        base.select_set(state=False)
        for item in boolean_move_list:
            item.select_set(state=False)

            # Link it to the new boolean collection
            if item.name not in col_bool.objects:
                col_bool.objects.link(item)

            # Remove it from its existing location IFF it's not already in another boolean collection
            for col in item.users_collection:
                if not col.name.startswith(CollectionPrefix) and item.name in col.objects:
                    col.objects.unlink(item)

        for item in inset_move_list:
            if item.name not in col_orig.objects:
                col_orig.objects.link(item)

        base.select_set(state=True)

        return DC.trace_exit("DC_OT_boolean_live.execute")


class DC_OT_toggle_cutters(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_toggle_cutters"
    bl_label = "DC Toggle Cutters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        DC.trace_enter("DC_OT_toggle_cutters.execute")

        # Grab our main active object...
        base = bpy.context.active_object
        DC.trace(1, "Base: {}", DC.full_name(base))

        # Toggle viewport visibility on our special boolean collection for this object...
        collection_name = create_collection_name(base)
        if collection_name in bpy.data.collections.keys():
            DC.trace(1, "Toggling visibility: {}", collection_name)
            bpy.data.collections[collection_name].hide_viewport = not bpy.data.collections[collection_name].hide_viewport

        return DC.trace_exit("DC_OT_toggle_cutters.execute")


class DC_OT_boolean_apply(bpy.types.Operator):
    bl_idname = "view3d.dc_boolean_apply"
    bl_label = "DC Apply Booleans"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        DC.trace_enter("DC_OT_boolean_apply.execute")

        if bpy.context.mode != "OBJECT":
            return DC.trace_exit("DC_OT_boolean_apply.execute", result="CANCELLED")

        # Grab our main active object...
        base = bpy.context.active_object
        DC.trace(1, "Base: {}", DC.full_name(base))

        # We need to apply everything up until the last boolean modifier
        mod_count = len(base.modifiers)
        mod_apply_count = 0
        if len(base.modifiers) > 0:
            for i in range(mod_count - 1, -1, -1):
                if base.modifiers[i].type == "BOOLEAN":
                    mod_apply_count = i + 1
                    break

        DC.trace(1, "Applying {} of {} modifiers", mod_apply_count, mod_count)

        orphaned_objects = []
        for i in range(mod_apply_count):
            modifier = base.modifiers[0]
            DC.trace(2, "Applying {}", modifier.type)
            if modifier.type == "BOOLEAN":
                orphaned_objects.append(modifier.object)
            bpy.ops.object.modifier_apply(apply_as="DATA", modifier=modifier.name)

        DC.trace(1, "Processing {} orphaned objects", len(orphaned_objects))

        skip_count = 0
        collection_name = create_collection_name(base)
        for col in bpy.data.collections:
            if col.name != collection_name:
                for i in range(len(orphaned_objects) - 1, -1, -1):
                    if orphaned_objects[i].name in col.objects:
                        DC.trace(2, "Object {} belongs to another collection called {}. Skipping...", orphaned_objects[i].name, col.name)
                        orphaned_objects.remove(orphaned_objects[i])
                        skip_count = skip_count + 1

        if len(orphaned_objects) > 0:
            DC.trace(1, "Removing {} orphaned objects", len(orphaned_objects))
            bpy.ops.object.select_all(action='DESELECT')
            for obj in orphaned_objects:
                obj.select_set(True)

            bpy.ops.object.delete(use_global=False, confirm=False)

        if collection_name in bpy.data.collections:
            col_bool = bpy.data.collections[collection_name]
            if len(col_bool.all_objects) - skip_count == 0:
                DC.trace(1, "Removing collection: {}", collection_name)

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
                DC.trace(1, "Collection still contains objects; not removing: {}", collection_name)

        base.select_set(True)
        return DC.trace_exit("DC_OT_boolean_apply.execute")
