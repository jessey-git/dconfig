# ------------------------------------------------------------
# Copyright(c) 2018-2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Playground
#

import bpy
import itertools
import MaterialX as mx
from dataclasses import dataclass
from . import DCONFIG_Utils as dc

class UINode:
    def __init__(self):
        self.node = None
        self.input = None
        self.output = None
        self.name = None
        self.category = None
        self.bnode = None

socket_map = {
    "mix": { "mix": 0, "bg": 1, "fg": 2 },
    "oren_nayar_diffuse_bsdf": { },
    "dielectric_bsdf": { },
}

def load_input_values(mtlx_node, bnode, input_map):
    for input in mtlx_node.getInputs():
        input_value = input.getValue()

        socket = input_map.get(input.getName())
        if socket is not None and input_value is not None:
            bnode.inputs[socket].default_value = input_value


# NOTE: Need to completely fill out each node as much as possible here in case Edges are not added later but the socket still needs its value set (e.g. The factor on the mix node)
def getBlenderNode(mtlx_node, bnodes):
    category = mtlx_node.getCategory()
    print("Found '{}'".format(category))

    if category == "oren_nayar_diffuse_bsdf":
        bnode = bnodes.new('ShaderNodeBsdfDiffuse')
        load_input_values(mtlx_node, bnode, socket_map["oren_nayar_diffuse_bsdf"])
        return bnode

    elif category == "dielectric_bsdf":
        bnode = bnodes.new('ShaderNodeBsdfGlass')
        load_input_values(mtlx_node, bnode, socket_map["dielectric_bsdf"])
        return bnode

    elif category == "mix":
        bnode = bnodes.new('ShaderNodeMixShader')
        load_input_values(mtlx_node, bnode, socket_map["mix"])
        return bnode

    elif category == "surface":
        bnode = bnodes.new('NodeReroute')
        bnode.label = "surface:" + mtlx_node.getName()
        return bnode
    elif category == "surfacematerial":
        bnode = bnodes.get("Material Output")
        return bnode
    return None


def createEdge(mtlx_up, output, mtlx_down, input, bnode_tree):
    # FIXME: We need a mapping between MaterialX input/output names to our sockets just like for Export. Need to centralize this per-node somehow...
    if output:
        out = output.getName()
    else:
        out = ""
    print("Edge between {}({})[{}] and {}({})[{}]".format(mtlx_up.name, mtlx_up.category, out, mtlx_down.name, mtlx_down.category, input.getName()))

    if mtlx_down.bnode and mtlx_up.bnode:
        category_mapping = socket_map.get(mtlx_down.category)

        b_in_index = 0 if not category_mapping else category_mapping[input.getName()]
        b_out_index = 0 if out == "" else 0
        bnode_tree.links.new(mtlx_down.bnode.inputs[b_in_index], mtlx_up.bnode.outputs[b_out_index])


class DCONFIG_OT_node_sandbox(bpy.types.Operator):
    bl_idname = "dconfig.node_sandbox"
    bl_label = "DC Node Sandbox"
    bl_description = "Sandbox"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dc.trace_enter(self)

        # Graph::Graph
        #   buildUiBaseGraph
        #     setUiNodeInfo -- adds to _graphNodes

        _graphNodes = []

        doc = mx.createDocument()
        mx.readFromXmlFile(doc, "t:/mtlx-playground.mtlx")

        mat_name = "TEST"
        mat = (bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name))
        mat.use_nodes = True
        bnodes = mat.node_tree.nodes

        for node in doc.getNodes():
            uinode = UINode()
            uinode.node = node
            uinode.name = node.getName()
            uinode.category = node.getCategory()
            uinode.bnode = getBlenderNode(node, bnodes)

            _graphNodes.append(uinode)

        for node in doc.getActiveInputs():
            uinode = UINode()
            uinode.input = node
            uinode.category = node.getCategory()
            uinode.name = node.getName()

            _graphNodes.append(uinode)

        for node in doc.getActiveOutputs():
            uinode = UINode()
            uinode.output = node
            uinode.category = node.getCategory()
            uinode.name = node.getName()

            _graphNodes.append(uinode)

        print("------------------------------")
        print("Nodes:")
        for node in _graphNodes:
            print("  {}({})".format(node.name, node.category))
        print()

        def findNode(name, type):
            pos = 0
            for node in _graphNodes:
                if node.name == name:
                    if type == "node" and node.node:
                        return pos
                    elif type == "input" and node.input:
                        return pos
                    elif type == "output" and node.output:
                        return pos
                pos += 1

            return -1


        for node in doc.getNodes():
            nD = node.getNodeDef(node.getName())

            for input in node.getActiveInputs():
                nodeGraphName = input.getNodeGraphString()
                connectedNode = input.getConnectedNode()
                connectedOutput = input.getConnectedOutput()

                upNum = -1
                downNum = -1

                # print("{} | {} | {}".format(nodeGraphName, connectedNode, connectedOutput))
                if connectedNode:
                    upNum = findNode(connectedNode.getName(), "node")
                    downNum = findNode(node.getName(), "node")
                elif connectedOutput:
                    upNum = findNode(connectedOutput.getName(), "output");
                    downNum = findNode(node.getName(), "node");

                if upNum != -1:
                    createEdge(_graphNodes[upNum], connectedOutput, _graphNodes[downNum], input, mat.node_tree)

        return dc.trace_exit(self)
