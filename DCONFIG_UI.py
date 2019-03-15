# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# UI Menus and Panels
#

import bpy


class DCONFIG_MT_quick(bpy.types.Menu):
    bl_label = "Quick"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.fill_grid", text="Fill Grid")
        layout.operator("dconfig.subdivide_cylinder", text="Subdivide Cylinder")
        layout.operator("dconfig.subd_bevel", text="Sub-D Bevel")

        layout.separator()
        layout.operator("mesh.remove_doubles", text="Remove Doubles")
