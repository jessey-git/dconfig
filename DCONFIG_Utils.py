# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

import bpy
from mathutils import (Vector)

DebugTraceEnabled = True


#
# Object utilities
#

def full_name(obj):
    return "{}({})".format(obj.name, obj.data.name)


def full_names(obj_list):
    name_list = []
    for obj in obj_list:
        name_list.append(full_name(obj))
    return name_list


def rename(obj, new_name):
    obj.name = new_name
    obj.data.name = new_name


def active_mesh_available(context):
    active_object = context.active_object
    return active_object is not None and active_object.type == 'MESH'


def active_mesh_selected(context):
    active_object = context.active_object
    return active_object is not None and active_object.type == 'MESH' and (context.mode == 'EDIT_MESH' or active_object.select_get())


def get_meshes(obj_list):
    return [obj for obj in obj_list if obj.type == 'MESH']


def get_sorted_meshes(obj_list, active_object):
    return sorted(get_meshes(obj_list), key=lambda x: 0 if x == active_object else 1)

#
# Math utilities
#


def find_world_bbox(matrix_world, verts):
    world_verts = [matrix_world @ v for v in verts]

    bbox_min = Vector(world_verts[0])
    bbox_max = Vector(world_verts[0])

    for v in world_verts:
        if v.x < bbox_min.x:
            bbox_min.x = v.x
        if v.y < bbox_min.y:
            bbox_min.y = v.y
        if v.z < bbox_min.z:
            bbox_min.z = v.z

        if v.x > bbox_max.x:
            bbox_max.x = v.x
        if v.y > bbox_max.y:
            bbox_max.y = v.y
        if v.z > bbox_max.z:
            bbox_max.z = v.z

    # Return bounding box verts
    return bbox_min, bbox_max

#
# Collection utilities
#


def find_collection(context, obj):
    collections = obj.users_collection
    if collections:
        return collections[0]
    return context.scene.collection


def make_collection(parent_collection, collection_name, force_create=True, hide_render=False):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    elif force_create:
        new_collection = bpy.data.collections.new(collection_name)
        new_collection.hide_render = hide_render
        parent_collection.children.link(new_collection)
        return new_collection
    else:
        return None


def get_helpers_collection(context):
    return make_collection(context.scene.collection, "DC_helpers", True, True)


def get_boolean_collection(context, force_create):
    return make_collection(context.scene.collection, "DC_booleans", force_create, True)


#
# Trace utilities
#

def trace(level, message, *args):
    if DebugTraceEnabled:
        indent = "" if level == 0 else "  " * int(level)
        print(indent + message.format(*args))


def trace_enter(op):
    trace(0, "")
    trace(0, "ENTER " + type(op).__name__)


def trace_exit(op, result='FINISHED'):
    trace(0, "EXIT  " + type(op).__name__ + " : " + result)
    trace(0, "")
    return {result}


def user_canceled(op):
    return trace_exit(op, 'CANCELLED')


def warn_canceled(op, message, *args):
    op.report(type={'WARNING'}, message=message.format(*args))
    return trace_exit(op, 'CANCELLED')
