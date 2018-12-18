# ------------------------------------------------------------
# Copyright(c) 2018 Jesse Yurkovich
# Licensed under the MIT License <http://opensource.org/licenses/MIT>.
# See the LICENSE file in the repo root for full license information.
# ------------------------------------------------------------

#
# Model validator
#

import bpy
import bmesh
import time
import re

from mathutils import Vector
from collections import (namedtuple, defaultdict)

BadNames = [
    'BezierCircle',
    'BezierCurve',
    'Circle',
    'Cone',
    'Cube',
    'CurvePath',
    'Cylinder',
    'Grid',
    'Icosphere',
    'Material',
    'Mball',
    'NurbsCircle',
    'NurbsCurve',
    'NurbsPath',
    'Plane',
    'Sphere',
    'Surface',
    'SurfCircle',
    'SurfCurve',
    'SurfCylinder',
    'SurfPatch',
    'SurfSphere',
    'SurfTorus',
    'Suzanne',
    'Text',
    'Torus'
]

#
# Utilities
#


def activate(obj):
    pass
    #bpy.context.active_object = obj


def is_edit_mode():
    return bpy.context.mode == 'EDIT_MESH'


def ensure_edit_mode():
    if not is_edit_mode():
        bpy.ops.object.editmode_toggle()


def ensure_not_edit_mode():
    if is_edit_mode():
        bpy.ops.object.editmode_toggle()


def has_active_mesh(context):
    obj = context.active_object
    return obj and obj.type == 'MESH'


def ready_selection(select_mode):
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type=select_mode)


def is_bad_name(name):
    pattern = '(%s)\.?\d*$' % '|'.join(BadNames)
    return re.match(pattern, name) is not None

#
# Rules
#


Rule = namedtuple('Rule', ['id', 'category', 'label'])
RuleData = namedtuple('RuleData', ['obj', 'bm'])
RuleResult = namedtuple('RuleResult', ['rule', 'is_error', 'detail'])


class ObjectNameRule:
    rule = Rule(1000, 'Organization', 'Object name')

    def execute(self, data):
        is_error = is_bad_name(data.obj.name)
        return RuleResult(self.rule, is_error, "Object '{}' is named poorly".format(data.obj.name))


class ObjectDataNameRule:
    rule = Rule(1001, 'Organization', 'Object data name')

    def execute(self, data):
        is_error = data.obj.name != data.obj.data.name
        return RuleResult(self.rule, is_error, "Object '{}' uses data name '{}' which does not match".format(data.obj.name, data.obj.data.name))


class GeometryTrianglesRule:
    rule = Rule(2000, 'Geometry', 'Triangles')

    def execute(self, data):
        ready_selection('FACE')
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL', extend=False)

        face_count = len(data.bm.faces)
        triangle_count = sum(1 for f in data.bm.faces if f.select)
        percentage = float(triangle_count) / face_count
        is_error = percentage > 0.15
        return RuleResult(self.rule, is_error, "Object '{0}' is composed of {1:.2f}% triangles".format(data.obj.name, percentage * 100))


class GeometryNGonRule:
    rule = Rule(2001, 'Geometry', 'Ngons')

    def execute(self, data):
        ready_selection('FACE')
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)

        ngon_count = sum(1 for f in data.bm.faces if f.select)
        is_error = ngon_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' is composed of {} ngons".format(data.obj.name, ngon_count))


class GeometryIsolatedVertRule:
    rule = Rule(2002, 'Geometry', 'Isolated vertices')

    def execute(self, data):
        ready_selection('VERT')
        bpy.ops.mesh.select_loose(extend=False)

        isolated_count = sum(1 for v in data.bm.verts if v.select)
        is_error = isolated_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} isolated vertices".format(data.obj.name, isolated_count))


class GeometryCoincidentVertRule:
    rule = Rule(2003, 'Geometry', 'Coincident vertices')

    def execute(self, data):
        doubles = bmesh.ops.find_doubles(data.bm, verts=data.bm.verts, dist=0.0001)

        doubles_count = len(doubles['targetmap'])
        is_error = doubles_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} doubled vertices".format(data.obj.name, doubles_count))


class GeometryInteriorFaceRule:
    rule = Rule(2004, 'Geometry', 'Interior faces')

    def execute(self, data):
        ready_selection('FACE')
        bpy.ops.mesh.select_interior_faces()

        interior_count = sum(1 for f in data.bm.faces if f.select)
        is_error = interior_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} interior faces".format(data.obj.name, interior_count))


class GeometryPoleRule:
    rule = Rule(2005, 'Geometry', 'Large poles')

    def execute(self, data):
        large_pole_count = sum(1 for v in data.bm.verts if len(v.link_edges) > 5)
        is_error = large_pole_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} poles with 6+ edges".format(data.obj.name, large_pole_count))


class GeometryOpenSubDivCreaseRule:
    rule = Rule(2006, 'Geometry', 'Edge creases')

    def execute(self, data):
        crease = data.bm.edges.layers.crease.verify()

        edge_count = sum(1 for e in data.bm.edges if e[crease] > 0.0)
        is_error = edge_count > 0
        return RuleResult(self.rule, is_error, "Object '{}' contains {} edges with creases set".format(data.obj.name, edge_count))


class OrientationTransformRule:
    rule = Rule(3000, 'Orientation', 'Unapplied transforms')

    def execute(self, data):
        loc_applied = all(c == 0.0 for c in data.obj.location)
        scale_applied = all(c == 1.0 for c in data.obj.scale)
        rotation_applied = all(c == 0.0 for c in data.obj.rotation_euler)

        is_error = not (loc_applied and scale_applied and rotation_applied)
        return RuleResult(self.rule, is_error, "Object '{}' has unapplied location, rotation, or scale".format(data.obj.name))


class MaterialRule:
    rule = Rule(4000, 'Material', 'Material missing')

    def execute(self, data):
        is_error = data.obj.active_material is None
        return RuleResult(self.rule, is_error, "Object '{}' does not have an assigned material".format(data.obj.name))


class MaterialNameRule:
    rule = Rule(4001, 'Material', 'Material name')

    def execute(self, data):
        if data.obj.active_material is None:
            is_error = False
            message = "No material found"
        else:
            is_error = is_bad_name(data.obj.active_material.name)
            message = "Material '{}' is named poorly for object '{}'".format(data.obj.active_material.name, data.obj.name)

        return RuleResult(self.rule, is_error, message)


class MaterialUVRule:
    rule = Rule(4002, 'Material', 'UVs missing')

    def execute(self, data):
        is_error = len(data.obj.data.uv_layers) == 0
        return RuleResult(self.rule, is_error, "Object '{}' is missing UVs".format(data.obj.name))


class MaterialUVOverlapRule:
    rule = Rule(4003, 'Material', 'UVs overlap')

    def execute(self, data):
        if len(data.obj.data.uv_layers) > 0:
            ready_selection('FACE')
            bpy.ops.uv.select_overlapping(extend=False)

            overlap_count = sum(1 for f in data.bm.faces if f.select)
            is_error = overlap_count > 0
            message = "Object '{}' has {} overlapping UVs".format(data.obj.name, overlap_count)
        else:
            is_error = False
            message = 'No UVs found'

        return RuleResult(self.rule, is_error, message)


class SceneValidateAnalyzer:
    Rules = [
        ObjectNameRule(),
        ObjectDataNameRule(),
        GeometryTrianglesRule(),
        GeometryNGonRule(),
        GeometryIsolatedVertRule(),
        GeometryCoincidentVertRule(),
        GeometryInteriorFaceRule(),
        GeometryPoleRule(),
        GeometryOpenSubDivCreaseRule(),
        OrientationTransformRule(),
        MaterialRule(),
        MaterialNameRule(),
        MaterialUVRule(),
        # MaterialUVOverlapRule()
    ]

    def __init__(self, obj):
        self.obj = obj  # TODO: Remove
        ensure_edit_mode()
        self.rule_data = RuleData(self.obj, bmesh.from_edit_mesh(self.obj.data))

    def find_problems(self):
        analysis = []
        for rule in SceneValidateAnalyzer.Rules:
            result = rule.execute(self.rule_data)
            analysis.append(result)

        return analysis

    def enable_anything_select_mode(self):
        self.rule_data.bm.select_mode = {'VERT', 'EDGE', 'FACE'}


class SceneValidateObjectLooper:
    def examine_object(self, obj):
        analyzer = SceneValidateAnalyzer(obj)
        analyzer.enable_anything_select_mode()
        self.select_none()

        return analyzer.find_problems()

    def examine_all_selected_meshes(self):
        objects_to_check = bpy.context.selected_objects

        print("--------------------------------")
        print('Checking : ', len(objects_to_check))

        all_data = defaultdict(list)
        for obj in objects_to_check:
            print('Checking : ', obj.name)
            if obj.type != 'MESH':
                continue

            analysis = self.examine_object(obj)
            ensure_not_edit_mode()

            for result in analysis:
                if not result.rule in all_data:
                    all_data[result.rule] = []
                if result.is_error:
                    all_data[result.rule].append(result.detail)

        scene = bpy.context.scene
        scene.dc_validation_rules.clear()
        scene.dc_validation_rules_index = 0

        for key in all_data:
            errors = all_data[key]
            print('{} errors: {}'.format(len(errors), key))
            for err in errors:
                print('  {}'.format(err))

                item = scene.dc_validation_rules.add()
                item.name = key.label
                item.rule_category = key.category
                item.rule_label = key.label
                item.result_detail = err
                scene.dc_validation_rules_index += 1

        bpy.context.area.tag_redraw()
        print("--------------------------------")

    def select_none(self):
        bpy.ops.mesh.select_all(action='DESELECT')


class DC_OT_validate(SceneValidateObjectLooper, bpy.types.Operator):
    bl_idname = "view3d.dc_validate"
    bl_label = "DC Validate"
    bl_description = "Validate Model"

    @classmethod
    def poll(cls, context):
        return has_active_mesh(context)

    def execute(self, context):
        original_mode = bpy.context.mode
        if is_edit_mode():
            self.examine_active_object()
        else:
            self.examine_all_selected_meshes()

        return {'FINISHED'}


class CUSTOM_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.15, align=True)
        split.alignment = 'LEFT'
        split.label(text=item.rule_category)
        split = split.split(factor=0.3, align=True)
        split.alignment = 'LEFT'
        split.label(text=item.rule_label)
        split.label(text=item.result_detail)

    def invoke(self, context, event):
        pass


class DC_PT_rules(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "DC Validation Report"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        row = layout.row()
        row.template_list("CUSTOM_UL_items", "", scene, "dc_validation_rules", scene, "dc_validation_rules_index", rows=3)


class DC_ValidationRuleCollection(bpy.types.PropertyGroup):
    rule_category: bpy.props.StringProperty()
    rule_label: bpy.props.StringProperty()
    result_detail: bpy.props.StringProperty()


def menu_func(self, context):
    self.layout.operator("view3d.dc_validate", text="DC Validate")
    self.layout.separator()


def register():
    bpy.types.VIEW3D_MT_view.prepend(menu_func)
    bpy.types.Scene.dc_validation_rules = bpy.props.CollectionProperty(type=DC_ValidationRuleCollection)
    bpy.types.Scene.dc_validation_rules_index = bpy.props.IntProperty()


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
    del bpy.types.Scene.dc_validation_rules
    del bpy.types.Scene.dc_validation_rules_index
