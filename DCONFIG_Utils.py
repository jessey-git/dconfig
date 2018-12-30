# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

import bpy

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

#
# Collection utilities
#


def find_collection(context, obj):
    collections = obj.users_collection
    if collections:
        return collections[0]
    return context.scene.collection


def make_collection(parent_collection, collection_name):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection)
        return new_collection


def make_helpers_collection(context):
    return make_collection(context.scene.collection, "DC_helpers")


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


def warn_canceled(op, message):
    op.report(type={'WARNING'}, message=message)
    return trace_exit(op, 'CANCELLED')
