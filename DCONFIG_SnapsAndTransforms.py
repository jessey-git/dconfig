# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Better snap and transform menus
#

import bpy
from mathutils import (Vector)
from . import DCONFIG_Utils as dc


class DCONFIG_MT_snap(bpy.types.Menu):
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


class DCONFIG_OT_center_collection(bpy.types.Operator):
    bl_idname = "dconfig.center_collection"
    bl_label = "DC Center Meshes"
    bl_description = "Center all meshes within the collection at the world origin"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.bbox_min = None
        self.bbox_max = None

    @classmethod
    def poll(cls, context):
        collection = context.collection
        return collection is not None and len(collection.all_objects) > 0

    def execute(self, context):
        dc.trace_enter(self)

        # Ensure an object from the current collection is active...
        collection = context.collection
        context.view_layer.objects.active = collection.all_objects[0]

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        # Process all objects to determine the collection's bounding box
        all_meshes = dc.get_meshes(collection.all_objects)
        for obj in all_meshes:
            if obj.modifiers:
                # It's too risky to move the object's origin if there are modifiers present...
                return dc.warn_canceled(self, "Object {} has {} unapplied modifiers", dc.full_name(obj), len(obj.modifiers))

            obj.select_set(True)
            bbox_min, bbox_max = dc.find_world_bbox(obj.matrix_world, [Vector(v) for v in obj.bound_box])
            self.merge_bbox(bbox_min, bbox_max)

        dc.trace(1, "Bounding box min:{}  max:{}", self.bbox_min, self.bbox_max)
        bottom_min = self.bbox_min
        bottom_max = Vector((self.bbox_max.x, self.bbox_max.y, self.bbox_min.z))
        bottom_center = (bottom_min + bottom_max) / 2
        dc.trace(1, "Bounding box bottom center: {}", bottom_center)

        # Move each object origin to the bbox bottom center...
        prev_cursor_location = Vector(context.scene.cursor_location)
        context.scene.cursor_location = bottom_center
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor_location = prev_cursor_location

        # Move each object to the world-center...
        for obj in all_meshes:
            obj.location = (0, 0, 0)

        return dc.trace_exit(self)

    def merge_bbox(self, bbox_min, bbox_max):
        if self.bbox_min is None:
            self.bbox_min = bbox_min
            self.bbox_max = bbox_max
        else:
            if bbox_min.x < self.bbox_min.x:
                self.bbox_min.x = bbox_min.x
            if bbox_min.y < self.bbox_min.y:
                self.bbox_min.y = bbox_min.y
            if bbox_min.z < self.bbox_min.z:
                self.bbox_min.z = bbox_min.z

            if bbox_max.x > self.bbox_max.x:
                self.bbox_max.x = bbox_max.x
            if bbox_max.y > self.bbox_max.y:
                self.bbox_max.y = bbox_max.y
            if bbox_max.z > self.bbox_max.z:
                self.bbox_max.z = bbox_max.z


def menu_func(self, context):
    self.layout.operator("dconfig.center_collection", text="DC Center Meshes")


def register():
    bpy.types.OUTLINER_MT_collection.append(menu_func)


def unregister():
    bpy.types.OUTLINER_MT_collection.remove(menu_func)
