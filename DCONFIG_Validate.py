# ------------------------------------------------------------
# Copyright(c) 2020 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Model validator
#

from collections import (namedtuple, defaultdict)
import math
import re

import bpy
import bmesh
from . import DCONFIG_Utils as dc

#
# Rules
#


Rule = namedtuple('Rule', ['category', 'label'])
ObjectRuleData = namedtuple('ObjectRuleData', ['obj', 'bm'])
CollectionRuleData = namedtuple('CollectionRuleData', ['collection'])
RuleResult = namedtuple('RuleResult', ['rule', 'is_error', 'detail'])


class BaseObjectRule:
    BAD_NAMES = [
        'BezierCircle', 'BezierCurve',
        'Circle', 'Cone', 'Cube', 'CurvePath', 'Cylinder',
        'Grid',
        'Icosphere',
        'Material', 'Mball',
        'NurbsCircle', 'NurbsCurve', 'NurbsPath',
        'Plane',
        'Sphere', 'Surface', 'SurfCircle', 'SurfCurve', 'SurfCylinder', 'SurfPatch', 'SurfSphere', 'SurfTorus', 'Suzanne',
        'Text', 'Torus'
    ]

    def is_bad_name(self, name):
        pattern = r"({})\.?\d*$".format("|".join(self.BAD_NAMES))
        return re.match(pattern, name, re.IGNORECASE) is not None

    def ready_selection(self, select_mode):
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type=select_mode)


class BaseCollectionRule:
    pass


class ObjectNameRule(BaseObjectRule):
    rule = Rule('Organization', 'Object name')

    def execute(self, data):
        is_error = self.is_bad_name(data.obj.name)
        return RuleResult(self.rule, is_error, "Object '{}' is named poorly".format(data.obj.name))


class ObjectDataNameRule(BaseObjectRule):
    rule = Rule('Organization', 'Object data name')

    def execute(self, data):
        if data.obj.data.users < 2:
            is_error = data.obj.name != data.obj.data.name
            message = "Object '{}' uses data name '{}' which does not match".format(data.obj.name, data.obj.data.name)
        else:
            is_error = self.is_bad_name(data.obj.data.name)
            message = "Object '{}' uses data name '{}' which is named poorly".format(data.obj.name, data.obj.data.name)

        return RuleResult(self.rule, is_error, message)


class GeometryIsolatedVertRule(BaseObjectRule):
    rule = Rule('Geometry', 'Isolated vertices')

    def execute(self, data):
        self.ready_selection('VERT')
        bpy.ops.mesh.select_loose(extend=False)

        isolated_count = sum(1 for v in data.bm.verts if v.select)
        is_error = isolated_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} isolated vertices".format(data.obj.name, isolated_count))


class GeometryCoincidentVertRule(BaseObjectRule):
    rule = Rule('Geometry', 'Coincident vertices')

    def execute(self, data):
        doubles = bmesh.ops.find_doubles(data.bm, verts=data.bm.verts, dist=0.0001)

        doubles_count = len(doubles['targetmap'])
        is_error = doubles_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} doubled vertices".format(data.obj.name, doubles_count))


class GeometryInteriorFaceRule(BaseObjectRule):
    rule = Rule('Geometry', 'Interior faces')

    def execute(self, data):
        self.ready_selection('FACE')
        bpy.ops.mesh.select_interior_faces()

        interior_count = sum(1 for f in data.bm.faces if f.select)
        is_error = interior_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} interior faces".format(data.obj.name, interior_count))


class GeometryNonManifoldRule(BaseObjectRule):
    rule = Rule('Geometry', 'Manifold geometry')

    def execute(self, data):
        self.ready_selection('VERT')
        bpy.ops.mesh.select_non_manifold(extend=False, use_boundary=False)

        non_manifold_count = sum(1 for v in data.bm.verts if v.select)
        is_error = non_manifold_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} non-manifold vertices".format(data.obj.name, non_manifold_count))


class GeometryDistortionRule(BaseObjectRule):
    rule = Rule('Geometry', 'Distortion')
    Max_Distortion = math.radians(40)

    def is_face_distorted(self, face):
        face_no = face.normal
        max_angle = 0.0

        for loop in face.loops:
            loop_no = loop.calc_normal()
            if loop_no.dot(face_no) < 0.0:
                loop_no.negate()

            max_angle = max(max_angle, face_no.angle(loop_no, math.pi))

        return (2 * max_angle) >= self.Max_Distortion

    def execute(self, data):
        distored_faces = sum(1 for f in data.bm.faces if self.is_face_distorted(f))
        is_error = distored_faces > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} distorted faces".format(data.obj.name, distored_faces))


class TopologyTrianglesRule(BaseObjectRule):
    rule = Rule('Topology', 'Triangles')

    def execute(self, data):
        self.ready_selection('FACE')
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL', extend=False)

        face_count = len(data.bm.faces)
        triangle_count = sum(1 for f in data.bm.faces if f.select)
        percentage = float(triangle_count) / face_count
        is_error = percentage > 0.10
        return RuleResult(self.rule, is_error, "Object '{}' is composed of {:.1f}% triangles".format(data.obj.name, percentage * 100))


class TopologyNGonRule(BaseObjectRule):
    rule = Rule('Topology', 'Ngons')

    def execute(self, data):
        self.ready_selection('FACE')
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)

        face_count = len(data.bm.faces)
        ngon_count = sum(1 for f in data.bm.faces if f.select)
        percentage = float(ngon_count) / face_count
        is_error = percentage > 0.10
        return RuleResult(self.rule, is_error, "Object '{}' is composed of {:.1f}% ngons".format(data.obj.name, percentage * 100))


class TopologyPoleRule(BaseObjectRule):
    rule = Rule('Topology', 'Large poles')

    def execute(self, data):
        large_pole_count = sum(1 for v in data.bm.verts if len(v.link_edges) > 5)
        is_error = large_pole_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} poles with 6+ edges".format(data.obj.name, large_pole_count))


class TopologySubDivCreaseRule(BaseObjectRule):
    rule = Rule('Topology', 'Edge creases')

    def execute(self, data):
        crease = data.bm.edges.layers.crease.verify()

        edge_count = sum(1 for e in data.bm.edges if e[crease] > 0.0)
        is_error = edge_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} edges with creases set".format(data.obj.name, edge_count))


class OrientationTransformRule(BaseObjectRule):
    rule = Rule('Orientation', 'Unapplied transforms')

    def execute(self, data):
        loc_applied = all(c == 0.0 for c in data.obj.location)
        scale_applied = all(c == 1.0 for c in data.obj.scale)
        rotation_applied = all(c == 0.0 for c in data.obj.rotation_euler)

        is_error = not (loc_applied and scale_applied and rotation_applied)
        return RuleResult(self.rule, is_error, "Object '{}' has unapplied location, rotation, or scale".format(data.obj.name))


class MaterialRule(BaseObjectRule):
    rule = Rule('Material', 'Material missing')

    def execute(self, data):
        is_error = data.obj.active_material is None
        return RuleResult(self.rule, is_error, "Object '{}' does not have an assigned material".format(data.obj.name))


class MaterialNameRule(BaseObjectRule):
    rule = Rule('Material', 'Material name')

    def execute(self, data):
        if data.obj.active_material is None:
            is_error = False
            message = "No material found"
        else:
            is_error = self.is_bad_name(data.obj.active_material.name)
            message = "Material '{}' is named poorly for object '{}'".format(data.obj.active_material.name, data.obj.name)

        return RuleResult(self.rule, is_error, message)


class MaterialUVRule(BaseObjectRule):
    rule = Rule('Material', 'UVs missing')

    def execute(self, data):
        is_error = len(data.obj.data.uv_layers) == 0
        return RuleResult(self.rule, is_error, "Object '{}' is missing UVs".format(data.obj.name))


class AllMeshRule(BaseCollectionRule):
    rule = Rule('Organization', 'Mesh Collection')

    def execute(self, data):
        number_non_mesh = sum(1 for obj in data.collection.all_objects if obj.type != 'MESH')
        is_error = number_non_mesh > 0
        return RuleResult(self.rule, is_error, "Collection '{}' contains {} non-mesh objects".format(data.collection.name, number_non_mesh))


class MaterialUVOverlapRule(BaseCollectionRule):
    rule = Rule('Material', 'UVs overlap')

    def execute(self, data):
        return RuleResult(self.rule, False, "")
        # if len(data.obj.data.uv_layers) > 0:
        #     self.ready_selection('FACE')
        #     bpy.ops.uv.select_overlapping(extend=False)
        #     overlap_count = sum(1 for f in data.bm.faces if f.select)
        #     is_error = overlap_count > 0
        #     message = "Object '{}' has {} overlapping UVs".format(data.obj.name, overlap_count)
        # else:
        #     is_error = False
        #     message = 'No UVs found'
        # return RuleResult(self.rule, is_error, message)

#
# Analyzer Processing
#


class ObjectAnalyzer:
    Rules = [
        ObjectNameRule(),
        ObjectDataNameRule(),
        GeometryIsolatedVertRule(),
        GeometryCoincidentVertRule(),
        GeometryInteriorFaceRule(),
        GeometryNonManifoldRule(),
        GeometryDistortionRule(),
        TopologyTrianglesRule(),
        TopologyNGonRule(),
        TopologyPoleRule(),
        TopologySubDivCreaseRule(),
        OrientationTransformRule(),
        MaterialRule(),
        MaterialNameRule(),
        MaterialUVRule(),
    ]

    def __init__(self, obj):
        self.rule_data = ObjectRuleData(obj, bmesh.from_edit_mesh(obj.data))
        self.rule_data.bm.select_mode = {'VERT', 'EDGE', 'FACE'}

    def find_problems(self):
        analysis = []
        for rule in ObjectAnalyzer.Rules:
            result = rule.execute(self.rule_data)
            analysis.append(result)

        return analysis


class CollectionAnalyzer:
    Rules = [
        AllMeshRule(),
        MaterialUVOverlapRule()
    ]

    def __init__(self, collection):
        self.rule_data = CollectionRuleData(collection)

    def find_problems(self):
        analysis = []
        for rule in CollectionAnalyzer.Rules:
            result = rule.execute(self.rule_data)
            analysis.append(result)

        return analysis


class Validator:
    def __init__(self, collection):
        self.collection = collection
        self.results = defaultdict(list)

    def run(self, context):
        print("--------------------------------")

        self.results.clear()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        print('Checking collection : ', self.collection.name)
        context.scene.dc_validation_collection = self.collection.name
        self.examine_collection()

        for obj in dc.get_objects(self.collection.all_objects, {'MESH'}):
            print('Checking object : ', obj.name)
            self.examine_object(context, obj)

        self.post_results(context.scene)
        print("--------------------------------")

    def examine_collection(self):
        analyzer = CollectionAnalyzer(self.collection)
        analysis_results = analyzer.find_problems()
        self.process(analysis_results)

    def examine_object(self, context, obj):
        prev_hide_viewport = obj.hide_viewport
        obj.hide_viewport = False

        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')

        analyzer = ObjectAnalyzer(obj)
        analysis_results = analyzer.find_problems()
        self.process(analysis_results)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        obj.select_set(False)
        obj.hide_viewport = prev_hide_viewport

    def process(self, analysis_results):
        for result in analysis_results:
            if result.rule not in self.results:
                self.results[result.rule] = []
            if result.is_error:
                self.results[result.rule].append(result.detail)

    def post_results(self, scene):
        scene.dc_validation_results_index = 0
        scene.dc_validation_results.clear()

        for key in self.results:
            errors = self.results[key]
            print('{} errors: {}'.format(len(errors), key))
            for err in errors:
                print('  {}'.format(err))

                item = scene.dc_validation_results.add()
                item.name = key.label
                item.rule_category = key.category
                item.rule_label = key.label
                item.result_detail = err
                scene.dc_validation_results_index += 1


#
# Operators and UI
#

class DCONFIG_OT_validate(bpy.types.Operator):
    bl_idname = "dconfig.validate"
    bl_label = "DC Validate"
    bl_description = "Validate Model"

    @classmethod
    def poll(cls, context):
        return context.collection is not None

    def execute(self, context):
        validator = Validator(context.collection)
        validator.run(context)

        return {'FINISHED'}


class DCONFIG_UL_validation_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.15, align=True)
        split.alignment = 'LEFT'
        split.label(text=item.rule_category)
        split = split.split(factor=0.30, align=True)
        split.alignment = 'LEFT'
        split.label(text=item.rule_label)
        split.label(text=item.result_detail)

    def invoke(self, context, event):
        pass


class DCONFIG_PT_validate_results(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DC"
    bl_label = "DC Validation Report"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene

        layout.label(text="Collection: " + scene.dc_validation_collection)
        layout.template_list("DCONFIG_UL_validation_items", "", scene, "dc_validation_results", scene, "dc_validation_results_index", rows=5)


class DCONFIG_ValidationResultCollection(bpy.types.PropertyGroup):
    rule_category: bpy.props.StringProperty()
    rule_label: bpy.props.StringProperty()
    result_detail: bpy.props.StringProperty()


def menu_func(self, context):
    self.layout.operator("dconfig.validate")


def register():
    bpy.types.OUTLINER_MT_collection.append(menu_func)
    bpy.types.Scene.dc_validation_collection = bpy.props.StringProperty()
    bpy.types.Scene.dc_validation_results = bpy.props.CollectionProperty(type=DCONFIG_ValidationResultCollection)
    bpy.types.Scene.dc_validation_results_index = bpy.props.IntProperty()


def unregister():
    bpy.types.OUTLINER_MT_collection.remove(menu_func)
    del bpy.types.Scene.dc_validation_results
    del bpy.types.Scene.dc_validation_results_index
