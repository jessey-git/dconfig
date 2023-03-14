# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import bpy
from . import DCONFIG_Utils as dc


class DCONFIG_MT_node_quick(bpy.types.Menu):
    bl_label = "Quick"

    def draw(self, context):
        layout = self.layout

        dc.setup_op(layout, "dconfig.nodegroup_center", text="Center Node Group")
        dc.setup_op(layout, "dconfig.nodegroup_center_all", text="Center All Node Groups")


class DCONFIG_OT_nodegroup_center(bpy.types.Operator):
    bl_idname = "dconfig.nodegroup_center"
    bl_label = "DC Center Node Group"
    bl_description = "Center the current node group"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.node_tree

    @classmethod
    def center_nodes(cls, name, nodes):
        bbox_min, bbox_max = dc.calculate_bbox(map(lambda n: n.location.copy().to_3d(), nodes))
        box_center = ((bbox_min) + (bbox_max)) / 2

        dc.trace(1, "Adjusting '{}' nodes by {} {}", name, -box_center.x, -box_center.y)

        for node in nodes:
            node.location = node.location - box_center.to_2d()

    def execute(self, context):
        dc.trace_enter(self)

        DCONFIG_OT_nodegroup_center.center_nodes(context.space_data.node_tree.name, context.space_data.node_tree.nodes)

        return dc.trace_exit(self)


class DCONFIG_OT_nodegroup_center_all(bpy.types.Operator):
    bl_idname = "dconfig.nodegroup_center_all"
    bl_label = "DC Center All Node Groups"
    bl_description = "Center all node groups"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dc.trace_enter(self)

        for material in bpy.data.materials:
            if material.node_tree:
                DCONFIG_OT_nodegroup_center.center_nodes(material.name, material.node_tree.nodes)
        for group in bpy.data.node_groups:
            DCONFIG_OT_nodegroup_center.center_nodes(group.name, group.nodes)
        for scene in bpy.data.scenes:
            if scene.node_tree:
                DCONFIG_OT_nodegroup_center.center_nodes(scene.name, scene.node_tree.nodes)

        return dc.trace_exit(self)
