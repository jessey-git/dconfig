# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

import bpy
from . import auto_load


bl_info = {
    "name": "dconfig",
    "author": "deadpin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Custom settings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene"}


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    bl_option = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        layout.operator("dconfig.install_theme", text="Load Theme")
        layout.operator("dconfig.setup_addons", text="Setup Addons")


#
# Addon registration
#

auto_load.init()


def register():
    print('DCONFIG :: register')

    bpy.utils.register_class(Preferences)
    auto_load.register()


def unregister():
    print('DCONFIG :: unregister')

    auto_load.unregister()
    bpy.utils.unregister_class(Preferences)


if __name__ == '__main__':
    register()
