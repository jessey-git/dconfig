# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Setup User Preferences
#

import os
import shutil

import bpy
import addon_utils

addon_keymaps = []


def setup_hotkeys():
    # pylint: disable=C0326
    kc = bpy.context.window_manager.keyconfigs

    if kc.active.preferences is not None:
        kc.active.preferences.select_mouse = "LEFT"
        kc.active.preferences.spacebar_action = "SEARCH"
        kc.active.preferences.use_select_all_toggle = True

    new_keymap = (
        # Keymap Name           Space       Region      Modal   Type                        Key                 Action      SHIFT   CTRL    ALT     Properties
        ("Screen",              "EMPTY",    "WINDOW",   False,  "ed.undo_history",          "BUTTON4MOUSE",     "PRESS",    False,  True,   False,  ()),
        ("Screen",              "EMPTY",    "WINDOW",   False,  "screen.repeat_history",    "BUTTON5MOUSE",     "PRESS",    False,  True,   False,  ()),
        ("Screen",              "EMPTY",    "WINDOW",   False,  "screen.redo_last",         "BUTTON5MOUSE",     "PRESS",    False,  False,  False,  ()),
        ("Screen",              "EMPTY",    "WINDOW",   False,  "script.reload",            "F8",               "PRESS",    False,  False,  False,  ()),

        ("Object Non-modal",    "EMPTY",    "WINDOW",   False,  "wm.call_menu",             "S",                "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_snap"),)),
        ("Object Non-modal",    "EMPTY",    "WINDOW",   False,  "wm.call_menu_pie",         "BUTTON4MOUSE",     "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_transforms_pie"),)),
        ("Object Non-modal",    "EMPTY",    "WINDOW",   False,  "object.origin_set",        "BUTTON5MOUSE",     "PRESS",    True,   False,  False,  ()),

        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "view3d.view_center_cursor",    "HOME",         "PRESS",    False,  False,  True,   ()),
        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "view3d.toggle_shading",        "Z",            "PRESS",    False,  False,  False,  (("type", "WIREFRAME"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "wm.call_menu_pie",             "Z",            "PRESS",    True,   False,  False,  (("name", "VIEW3D_MT_shading_ex_pie"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "wm.call_menu_pie",             "Q",            "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_boolean_pie"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "wm.call_menu_pie",             "Q",            "PRESS",    False,  True,   False,  (("name", "DCONFIG_MT_symmetry_pie"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   False,  "wm.call_menu_pie",             "W",            "PRESS",    False,  False,  False,  (("name", "DCONFIG_MT_add_primitive_pie"),)),

        ("Mesh",                "EMPTY",    "WINDOW",   False,  "mesh.select_linked",       "LEFTMOUSE",        "DOUBLE_CLICK", False,  False,  False,  (("delimit", {'SEAM'}),)),
        ("Mesh",                "EMPTY",    "WINDOW",   False,  "mesh.select_linked",       "LEFTMOUSE",        "DOUBLE_CLICK", True,   False,  False,  (("delimit", {'SEAM'}),)),
        ("Mesh",                "EMPTY",    "WINDOW",   False,  "mesh.delete_edgeloop",     "X",                "PRESS",        False,  True,   False,  (("use_face_split", False),)),
        ("Mesh",                "EMPTY",    "WINDOW",   False,  "wm.call_menu",             "BUTTON4MOUSE",     "PRESS",        False,  False,  False,  (("name", "VIEW3D_MT_edit_mesh_select_mode"),)),

        ("View3D Gesture Circle",   "EMPTY",    "WINDOW",   True,   "CANCEL",               "C",                "RELEASE",  False,  False,  False,   ()),
    )

    addon_keymaps.clear()
    for (name, space, region, modal, idname, key, action, SHIFT, CTRL, ALT, props) in new_keymap:
        km = kc.addon.keymaps.new(name=name, space_type=space, region_type=region, modal=modal)
        if not modal:
            kmi = km.keymap_items.new(idname, key, action, shift=SHIFT, ctrl=CTRL, alt=ALT)
        else:
            kmi = km.keymap_items.new_modal(idname, key, action, shift=SHIFT, ctrl=CTRL, alt=ALT)
        for prop, value in props:
            setattr(kmi.properties, prop, value)

        addon_keymaps.append((km, kmi))

    print('Added {} keymaps'.format(len(addon_keymaps)))


def remove_hotkeys():
    print('Removing {} keymaps'.format(len(addon_keymaps)))
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def setup_userpreferences():
    user_prefs = bpy.context.preferences

    if user_prefs.edit.undo_steps < 100:
        user_prefs.edit.undo_steps = 100

    user_prefs.view.show_tooltips_python = True
    user_prefs.view.show_developer_ui = True

    user_prefs.view.mini_axis_type = 'MINIMAL'
    user_prefs.view.mini_axis_size = 40

    user_prefs.system.anisotropic_filter = 'FILTER_8'
    user_prefs.system.multi_sample = '4'
    user_prefs.system.gpu_viewport_quality = 1


def setup_addons():
    addon_utils.enable("mesh_looptools", default_set=True, persistent=True)
    addon_utils.enable("node_wrangler", default_set=True, persistent=True)


class DCONFIG_OT_install_theme(bpy.types.Operator):
    bl_idname = "dconfig.install_theme"
    bl_label = "DC Install Theme"
    bl_description = "Installs custom dconfig theme"
    bl_options = {'REGISTER'}

    def execute(self, context):
        script_path = bpy.utils.user_resource('SCRIPTS')
        source_path = os.path.join(script_path, "addons", "dconfig", "dconfig.xml")
        target_path = os.path.join(script_path, "presets", "interface_theme")

        self.makedir(target_path)
        filepath = shutil.copy(source_path, target_path)
        bpy.ops.script.execute_preset(filepath=filepath, menu_idname="USERPREF_MT_interface_theme_presets")

        return {'FINISHED'}

    def makedir(self, target):
        if not os.path.exists(target):
            os.makedirs(target)


def register():
    setup_hotkeys()
    setup_userpreferences()
    setup_addons()


def unregister():
    remove_hotkeys()
