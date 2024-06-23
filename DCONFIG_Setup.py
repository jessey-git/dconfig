# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Setup User Preferences
#

import os
import shutil
import threading
import time

import bpy

addon_keymaps = []


def setup_hotkeys():
    kc = bpy.context.window_manager.keyconfigs

    if kc.active.preferences is not None:
        kc.active.preferences.select_mouse = 'LEFT'
        kc.active.preferences.spacebar_action = 'TOOL'
        kc.active.preferences.gizmo_action = 'DRAG'
        kc.active.preferences.v3d_tilde_action = 'GIZMO'
        kc.active.preferences.use_select_all_toggle = True
        kc.active.preferences.use_pie_click_drag = True
        kc.active.preferences.use_v3d_shade_ex_pie = True

    new_keymap = (
        # Keymap Name           Space       Region      ID                          Key             Action      SHIFT   CTRL    ALT     Properties
        ("Screen",              "EMPTY",    "WINDOW",   "screen.redo_last",         "BUTTON5MOUSE", "PRESS",    False,  False,  False,  ()),

        ("Object Non-modal",    "EMPTY",    "WINDOW",   "wm.call_menu",             "S",            "PRESS",    True,   False,  False,  (("name", "VIEW3D_MT_snap"),)),
        ("Object Non-modal",    "EMPTY",    "WINDOW",   "wm.call_menu_pie",         "BUTTON4MOUSE", "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_transforms_pie"),)),

        ("Object Mode",         "EMPTY",    "WINDOW",   "wm.call_menu_pie",         "A",            "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_add_primitive_pie"),)),
        ("Mesh",                "EMPTY",    "WINDOW",   "wm.call_menu_pie",         "A",            "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_add_primitive_pie"),)),
        ("Curve",               "EMPTY",    "WINDOW",   "wm.call_menu_pie",         "A",            "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_add_primitive_pie"),)),

        ("Object Mode",         "EMPTY",    "WINDOW",   "dconfig.subd_toggle",      "ONE",          "PRESS",    False,  False,  True,   (("levels", 1),)),
        ("Object Mode",         "EMPTY",    "WINDOW",   "dconfig.subd_toggle",      "TWO",          "PRESS",    False,  False,  True,   (("levels", 2),)),
        ("Object Mode",         "EMPTY",    "WINDOW",   "dconfig.subd_toggle",      "THREE",        "PRESS",    False,  False,  True,   (("levels", 3),)),
        ("Object Mode",         "EMPTY",    "WINDOW",   "dconfig.subd_toggle",      "FOUR",         "PRESS",    False,  False,  True,   (("levels", 4),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.subd_toggle",      "ONE",          "PRESS",    False,  False,  True,   (("levels", 1),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.subd_toggle",      "TWO",          "PRESS",    False,  False,  True,   (("levels", 2),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.subd_toggle",      "THREE",        "PRESS",    False,  False,  True,   (("levels", 3),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.subd_toggle",      "FOUR",         "PRESS",    False,  False,  True,   (("levels", 4),)),

        ("3D View",             "VIEW_3D",  "WINDOW",   "view3d.view_center_cursor",    "HOME",     "PRESS",    False,  False,  True,   ()),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.toggle_wireframe",     "Z",        "PRESS",    True,   False,  False,  ()),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.mesh_symmetry",        "T",        "PRESS",    True,   False,  False,  ()),
        ("3D View",             "VIEW_3D",  "WINDOW",   "wm.call_menu",                 "Q",        "PRESS",    False,  False,  False,  (("name", "DCONFIG_MT_quick"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "wm.call_menu_pie",             "Q",        "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_boolean_pie"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "wm.call_menu_pie",         "BUTTON4MOUSE", "PRESS",    False,  False,  False,  (("name", "VIEW3D_MT_transform_gizmo_pie"),)),
        ("3D View",             "VIEW_3D",  "WINDOW",   "dconfig.mesh_focus",       "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),
        ("3D View",             "VIEW_3D",  "WINDOW",   "view3d.localview",         "BUTTON5MOUSE", "PRESS",    False,  True,   False,  (("frame_selected", True),)),

        ("Mesh",                "EMPTY",    "WINDOW",   "mesh.select_linked",       "LEFTMOUSE",    "DOUBLE_CLICK", False,  False,  False,  (("delimit", set()),)),
        ("Mesh",                "EMPTY",    "WINDOW",   "mesh.select_linked",       "LEFTMOUSE",    "DOUBLE_CLICK", True,   False,  False,  (("delimit", set()),)),
        ("Mesh",                "EMPTY",    "WINDOW",   "dconfig.edge_crease",      "E",            "PRESS",        True,   False,  False,  (("value", 1),)),
        ("Mesh",                "EMPTY",    "WINDOW",   "dconfig.edge_crease",      "E",            "PRESS",        True,   False,  True,   (("value", -1),)),

        ("UV Editor",           "EMPTY",    "WINDOW",   "uv.select_linked_pick",    "LEFTMOUSE",    "DOUBLE_CLICK", False,  False,  False,  ()),
        ("UV Editor",           "EMPTY",    "WINDOW",   "uv.select_linked_pick",    "LEFTMOUSE",    "DOUBLE_CLICK", True,   False,  False,  (("extend", True),)),
        ("UV Editor",           "EMPTY",    "WINDOW",   "wm.call_menu",             "S",            "PRESS",        True,   False,  False,  (("name", "IMAGE_MT_uvs_snap"),)),

        ("Node Editor",         "NODE_EDITOR",      "WINDOW",   "node.view_selected",   "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),
        ("Node Editor",         "NODE_EDITOR",      "WINDOW",   "wm.call_menu",         "Q",            "PRESS",    False,  False,  False,  (("name", "DCONFIG_MT_node_quick"),)),

        ("Outliner",            "OUTLINER",         "WINDOW",   "outliner.show_active", "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),
        ("Dopesheet",           "DOPESHEET_EDITOR", "WINDOW",   "action.view_selected", "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),
        ("Graph Editor",        "GRAPH_EDITOR",     "WINDOW",   "graph.view_selected",  "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),
        ("Image",               "IMAGE_EDITOR",     "WINDOW",   "image.view_selected",  "BUTTON4MOUSE", "PRESS",    False,  True,   False,  ()),

        ("Image",               "IMAGE_EDITOR",     "WINDOW",   "wm.call_menu",         "BUTTON4MOUSE", "PRESS",    True,   False,  False,  (("name", "DCONFIG_MT_image_pivot"),)),
        ("Image",               "IMAGE_EDITOR",     "WINDOW",   "image.clipboard_copy", "C",            "PRESS",    False,  True,   False,  ()),
        ("Image",               "IMAGE_EDITOR",     "WINDOW",   "image.clipboard_paste","V",            "PRESS",    False,  True,   False,  ()),
    )

    addon_keymaps.clear()
    for (name, space, region, idname, key, action, SHIFT, CTRL, ALT, props) in new_keymap:
        km = kc.addon.keymaps.new(name=name, space_type=space, region_type=region)
        kmi = km.keymap_items.new(idname, key, action, shift=SHIFT, ctrl=CTRL, alt=ALT)
        for prop, value in props:
            setattr(kmi.properties, prop, value)

        addon_keymaps.append((km, kmi))

    print('Added {} keymaps'.format(len(addon_keymaps)))

    print("Starting keymap fixup thread")
    thread = threading.Thread(target=modal_fix)
    thread.start()


def remove_hotkeys():
    print('Removing {} keymaps'.format(len(addon_keymaps)))
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def setup_userpreferences():
    user_prefs = bpy.context.preferences

    user_prefs.edit.undo_steps = 100
    user_prefs.edit.grease_pencil_eraser_radius = 40

    if bpy.app.version >= (2, 90, 0):
        user_prefs.edit.collection_instance_empty_size = 0.25
        user_prefs.view.show_statusbar_version = False
        user_prefs.view.show_statusbar_stats = False
        user_prefs.view.show_statusbar_memory = True
        try:
            user_prefs.view.show_statusbar_vram = True
        except AttributeError:
            pass

    user_prefs.view.show_tooltips_python = True
    user_prefs.view.show_developer_ui = True
    user_prefs.view.show_navigate_ui = False
    user_prefs.view.show_splash = False

    user_prefs.view.mini_axis_type = 'MINIMAL'
    user_prefs.view.mini_axis_size = 45
    user_prefs.view.mini_axis_brightness = 10

    user_prefs.view.smooth_view = 0
    user_prefs.view.pie_animation_timeout = 0

    user_prefs.inputs.drag_threshold = 150

    user_prefs.filepaths.save_version = 0
    user_prefs.filepaths.use_auto_save_temporary_files = False

    user_prefs.system.anisotropic_filter = 'FILTER_8'
    user_prefs.system.viewport_aa = '5'
    user_prefs.system.use_overlay_smooth_wire = True

    user_prefs.use_preferences_save = False


class DCONFIG_OT_setup_addons(bpy.types.Operator):
    bl_idname = "dconfig.setup_addons"
    bl_label = "DC Setup Addons"
    bl_description = "Enables important addons"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if bpy.app.version < (4, 2, 0):
            import addon_utils
            addon_utils.enable("mesh_looptools", default_set=True, persistent=True)
            addon_utils.enable("node_wrangler", default_set=True, persistent=True)
            addon_utils.enable("space_view3d_copy_attributes", default_set=True, persistent=True)
        else:
            bpy.ops.extensions.package_install(repo_index=0, pkg_id="looptools")
            bpy.ops.extensions.package_install(repo_index=0, pkg_id="copy_attributes_menu")

            bpy.ops.preferences.addon_enable(module="node_wrangler")
        return {'FINISHED'}


class DCONFIG_OT_install_theme(bpy.types.Operator):
    bl_idname = "dconfig.install_theme"
    bl_label = "DC Install Theme"
    bl_description = "Installs custom dconfig theme"
    bl_options = {'REGISTER'}

    def execute(self, context):
        script_path = bpy.utils.user_resource('SCRIPTS')
        source_path = os.path.join(script_path, "addons", "dconfig", "DCONFIG.xml")
        target_path = os.path.join(script_path, "presets", "interface_theme")

        self.makedir(target_path)
        filepath = shutil.copy(source_path, target_path)
        bpy.ops.script.execute_preset(filepath=filepath, menu_idname="USERPREF_MT_interface_theme_presets")

        return {'FINISHED'}

    def makedir(self, target):
        if not os.path.exists(target):
            os.makedirs(target)


def modal_fix():
    kc = bpy.context.window_manager.keyconfigs
    kca = kc.active

    for _ in range(0, 5):
        km = kca.keymaps.find("View3D Gesture Circle")
        if km is not None and km.keymap_items:
            km.keymap_items[0].type = 'C'
            km.keymap_items[0].value = 'RELEASE'
            print("Keymap fixed")
            break
        else:
            time.sleep(0.5)


def register():
    if not bpy.app.background:
        setup_hotkeys()
        setup_userpreferences()


def unregister():
    remove_hotkeys()
