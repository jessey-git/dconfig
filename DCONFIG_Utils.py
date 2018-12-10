# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Common utilities
#

DebugTraceEnabled = True


def full_name(obj):
    return "{}({})".format(obj.name, obj.data.name)


def trace(level, message, *args):
    if DebugTraceEnabled:
        indent = "" if level == 0 else "  " * int(level)
        print(indent + message.format(*args))


def trace_enter(message):
    trace(0, "")
    trace(0, "ENTER " + message)


def trace_exit(message):
    trace(0, "EXIT  " + message)
    trace(0, "")
    return {"FINISHED"}
