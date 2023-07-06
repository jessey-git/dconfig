# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Mesh modeling helper ops
#

import bpy
import itertools
from . import DCONFIG_Utils as dc


class DCONFIG_MT_node_quick(bpy.types.Menu):
    bl_label = "Quick"

    def draw(self, context):
        layout = self.layout

        dc.setup_op(layout, "dconfig.nodegroup_center", text="Center Node Group")
        dc.setup_op(layout, "dconfig.nodegroup_center_all", text="Center All Node Groups")


class UnparentedContext():
    def __init__(self, nodes):
        self.parent_dict = {}
        for node in nodes:
            if node.parent is not None:
                self.parent_dict[node] = node.parent
            node.parent = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for node, parent in self.parent_dict.items():
            node.parent = parent


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
        with UnparentedContext(nodes):
            bbox_min, bbox_max = dc.calculate_bbox(map(lambda n: n.location.to_3d(), nodes))
            box_center = (((bbox_min) + (bbox_max)) / 2).to_2d()

            dc.trace(1, "Adjusting '{}' nodes by {}", name, -box_center)

            for node in nodes:
                node.location -= box_center

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

        material_nodes = ((material.name, material.node_tree.nodes) for material
            in bpy.data.materials if (material.node_tree is not None))

        geometry_nodes = ((group.name, group.nodes) for group
            in bpy.data.node_groups)

        compositor_nodes = ((scene.name, scene.node_tree.nodes) for scene
            in bpy.data.scenes if (scene.node_tree is not None))

        all_node_trees = itertools.chain(material_nodes, geometry_nodes, compositor_nodes)
        for node_tree in all_node_trees:
            name, nodes = node_tree
            DCONFIG_OT_nodegroup_center.center_nodes(name, nodes)

        return dc.trace_exit(self)
