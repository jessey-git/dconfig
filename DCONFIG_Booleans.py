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


def create_collection_name(base):
    return "DC_boolean_" + base.name


class DC_MT_boolean_pie(bpy.types.Menu):
    bl_label = "Booleans"

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

    def rename_boolean_obj(self, base, boolean_obj):
        new_name = base.name + "_" + self.bool_operation.lower()
        if self.cutline:
            new_name += "_cutline"

        old_name = DC.full_name(boolean_obj)
        boolean_obj.name = new_name
        DC.trace(2, "Renamed {} to {}", old_name, DC.full_name(boolean_obj))

    def make_inset_name(self, base):
        return base.name + "_inset"

    def create_cutter(self, base, boolean_obj, boolean_move_list, inset_move_list):
        self.rename_boolean_obj(base, boolean_obj)

        if self.cutline:
            boolean_obj.modifiers.new('Cutline', "SOLIDIFY").thickness = 0.02

        if self.insetted:
            bpy.context.view_layer.objects.active = boolean_obj
            base.select_set(state=False)
            boolean_obj.select_set(state=True)

            bpy.ops.object.duplicate()
            inset = bpy.context.active_object
            inset.name = self.make_inset_name(base)

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

    def create_bool(self, base, boolean_obj):
        DC.trace(2, "Adding boolean modifier to {}", DC.full_name(base))
        mod = base.modifiers.new(boolean_obj.name, "BOOLEAN")
        mod.object = boolean_obj
        mod.operation = self.bool_operation

    def prepare_collections(self, base):
        col_orig = None
        col_bool = None

        for collection in bpy.data.collections:
            if base.name in collection.all_objects and collection.name not in collection.objects:
                col_orig = collection
                break

        if col_orig is None:
            col_orig = bpy.context.scene.collection

        collection_name = create_collection_name(base)
        if collection_name in bpy.data.collections.keys():
            col_bool = bpy.data.collections[collection_name]
        else:
            col_bool = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(col_bool)

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

        # Grab our main active object and validate it's actually a mesh...
        base = bpy.context.active_object
        if base.type != "MESH":
            return DC.trace_exit("DC_OT_boolean_live.execute")

        DC.trace(1, "Base: {}", DC.full_name(base))

        # Prepare the boolean geometry and our collections...
        self.prepare_objects()
        col_orig, col_bool = self.prepare_collections(base)

        bpy.ops.object.editmode_toggle()
        selected = bpy.context.selected_objects

        DC.trace(1, "Current selection: {}", selected)

        # Perform actual boolean operations (keeping track of the final set of geometry to move)...
        boolean_move_list = []
        inset_move_list = []
        for obj in selected:
            if obj != base:
                DC.trace(1, "Found boolean obj: {}", DC.full_name(obj))
                self.create_cutter(base, obj, boolean_move_list, inset_move_list)
                self.create_bool(base, obj)

        # Place everything in the right collection...
        DC.trace(1, "Boolean Move list: {}", boolean_move_list)
        DC.trace(1, "Inset Move list: {}", inset_move_list)
        base.select_set(state=False)
        for item in boolean_move_list:
            item.select_set(state=False)
            if item.name not in col_bool.objects:
                col_bool.objects.link(item)
            col_orig.objects.unlink(item)

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

        # Grab our main active object and validate it's actually a mesh...
        base = bpy.context.active_object
        if base.type != "MESH":
            return DC.trace_exit("DC_OT_toggle_cutters.execute")

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

        # Grab our main active object and validate it's actually a mesh...
        base = bpy.context.active_object
        if base.type != "MESH":
            return DC.trace_exit("DC_OT_boolean_apply.execute")

        DC.trace(1, "Base: {}", DC.full_name(base))

        orphaned_objects = []

        mod_count = len(base.modifiers)
        mod_apply_count = 0
        if len(base.modifiers) > 0:
            for i in range(mod_count - 1, -1, -1):
                if base.modifiers[i].type == "BOOLEAN":
                    mod_apply_count = i + 1
                    break

        DC.trace(1, "Applying {} of {} modifiers", mod_apply_count, mod_count)

        for i in range(mod_apply_count):
            modifier = base.modifiers[0]
            DC.trace(2, "Applying {}", modifier.type)
            if modifier.type == "BOOLEAN":
                orphaned_objects.append(modifier.object)
            bpy.ops.object.modifier_apply(apply_as="DATA", modifier=modifier.name)

        DC.trace(1, "Processing {} orphaned objects", len(orphaned_objects))

        collection_name = create_collection_name(base)
        for col in bpy.data.collections:
            if col.name != collection_name:
                for i in range(len(orphaned_objects) - 1, -1, -1):
                    if orphaned_objects[i].name in col.all_objects:
                        DC.trace(2, "Object {} belongs to another collection called {}. Skipping...", orphaned_objects[i].name, col.name)
                        orphaned_objects.remove(orphaned_objects[i])

        DC.trace(1, "Removing {} orphaned objects", len(orphaned_objects))
        if len(orphaned_objects) > 0:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in orphaned_objects:
                obj.select_set(True)

            bpy.ops.object.delete(use_global=False, confirm=False)

        if collection_name in bpy.data.collections:
            col = bpy.data.collections[collection_name]
            if len(col.all_objects) == 0:
                DC.trace(1, "Removing collection: {}", collection_name)
                context.scene.collection.children.unlink(col)
                bpy.data.collections.remove(col)
            else:
                DC.trace(1, "Collection still contains objects; not removing: {}", collection_name)

        base.select_set(True)
        return DC.trace_exit("DC_OT_boolean_apply.execute")
