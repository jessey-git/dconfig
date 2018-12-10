# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

import bpy
bl_info = {
    "name": "deadpin config",
    "author": "deadpin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Custom settings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene"}

if "DCONFIG_Setup" in locals():
    import importlib

    importlib.reload(DCONFIG_Setup)
    importlib.reload(DCONFIG_AddPrimitives)
    importlib.reload(DCONFIG_Booleans)
    importlib.reload(DCONFIG_SnapsAndTransforms)
else:
    from . import DCONFIG_Setup
    from . import DCONFIG_AddPrimitives
    from . import DCONFIG_Booleans
    from . import DCONFIG_SnapsAndTransforms

#
# Addon registration
#


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    bl_option = {'REGISTER'}

    def draw(self, context):
        import os

        layout = self.layout
        layout.operator("dconfig.install_theme", text="Load Theme")


classes = (
    Preferences,

    DCONFIG_Setup.DC_OT_install_theme,

    DCONFIG_AddPrimitives.DC_MT_add_primitive_pie,
    DCONFIG_AddPrimitives.DC_OT_add_primitive,

    DCONFIG_Booleans.DC_MT_boolean_pie,
    DCONFIG_Booleans.DC_OT_toggle_cutters,
    DCONFIG_Booleans.DC_OT_boolean_live,
    DCONFIG_Booleans.DC_OT_boolean_apply,

    DCONFIG_SnapsAndTransforms.DC_MT_snap,
    DCONFIG_SnapsAndTransforms.DC_MT_transforms_pie,
)


def register():
    print('DCONFIG :: registration')
    DCONFIG_Setup.setup_hotkeys()
    DCONFIG_Setup.setup_userpreferences()
    DCONFIG_Setup.setup_addons()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    DCONFIG_Setup.remove_hotkeys()

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
