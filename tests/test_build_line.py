"""

build123d BuildLine tests

name: build_line_tests.py
by:   Gumyr
date: July 27th 2022

desc: Unit tests for the build123d build_line module

license:

    Copyright 2022 Gumyr

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
import unittest
from math import sqrt, pi
from build123d import *


def _assertTupleAlmostEquals(self, expected, actual, places, msg=None):
    """Check Tuples"""
    for i, j in zip(actual, expected):
        self.assertAlmostEqual(i, j, places, msg=msg)


unittest.TestCase.assertTupleAlmostEquals = _assertTupleAlmostEquals


class BuildLineTests(unittest.TestCase):
    """Test the BuildLine Builder derived class"""

    def test_basic_functions(self):
        """Test creating a line and returning properties and methods"""
        with BuildLine() as test:
            l1 = Line((0, 0), (1, 1))
            TangentArc((1, 1), (2, 0), tangent=l1 % 1)
            self.assertEqual(len(test.vertices()), 3)
            self.assertEqual(len(test.edges()), 2)
            self.assertEqual(len(test.vertices(Select.LAST)), 2)
            self.assertEqual(len(test.edges(Select.LAST)), 1)
            self.assertEqual(len(test.edges(Select.ALL)), 2)

    def test_canadian_flag(self):
        """Test many of the features by creating a Canadian flag maple leaf"""
        with BuildSketch() as leaf:
            with BuildLine() as outline:
                l1 = Polyline((0.0000, 0.0771), (0.0187, 0.0771), (0.0094, 0.2569))
                l2 = Polyline((0.0325, 0.2773), (0.2115, 0.2458), (0.1873, 0.3125))
                RadiusArc(l1 @ 1, l2 @ 0, 0.0271)
                l3 = Polyline((0.1915, 0.3277), (0.3875, 0.4865), (0.3433, 0.5071))
                TangentArc(l2 @ 1, l3 @ 0, tangent=l2 % 1)
                l4 = Polyline((0.3362, 0.5235), (0.375, 0.6427), (0.2621, 0.6188))
                SagittaArc(l3 @ 1, l4 @ 0, 0.003)
                l5 = Polyline((0.2469, 0.6267), (0.225, 0.6781), (0.1369, 0.5835))
                ThreePointArc(
                    l4 @ 1, (l4 @ 1 + l5 @ 0) * 0.5 + Vector(-0.002, -0.002), l5 @ 0
                )
                l6 = Polyline((0.1138, 0.5954), (0.1562, 0.8146), (0.0881, 0.7752))
                Spline(
                    l5 @ 1, l6 @ 0, tangents=(l5 % 1, l6 % 0), tangent_scalars=(2, 2)
                )
                l7 = Line((0.0692, 0.7808), (0.0000, 0.9167))
                TangentArc(l6 @ 1, l7 @ 0, tangent=l6 % 1)
                mirror(outline.edges(), Plane.YZ)
            make_face(leaf.pending_edges)
        self.assertAlmostEqual(leaf.sketch.area, 0.2741600685288115, 5)

    def test_three_d(self):
        """Test 3D lines with a helix"""
        with BuildLine() as roller_coaster:
            powerup = Spline(
                (0, 0, 0),
                (50, 0, 50),
                (100, 0, 0),
                tangents=((1, 0, 0), (1, 0, 0)),
                tangent_scalars=(0.5, 2),
            )
            corner = RadiusArc(powerup @ 1, (100, 60, 0), -30)
            screw = Helix(75, 150, 15, center=(75, 40, 15), direction=(-1, 0, 0))
            Spline(corner @ 1, screw @ 0, tangents=(corner % 1, screw % 0))
            Spline(
                screw @ 1,
                (-100, 30, 10),
                powerup @ 0,
                tangents=(screw % 1, powerup % 0),
            )
        self.assertAlmostEqual(roller_coaster.wires()[0].length, 678.983628932414, 5)

    def test_bezier(self):
        pts = [(0, 0), (20, 20), (40, 0), (0, -40), (-60, 0), (0, 100), (100, 0)]
        wts = [1.0, 1.0, 2.0, 3.0, 4.0, 2.0, 1.0]
        with BuildLine() as bz:
            Bezier(*pts, weights=wts)
        self.assertAlmostEqual(bz.wires()[0].length, 225.86389406824566, 5)

    def test_elliptical_start_arc(self):
        with self.assertRaises(RuntimeError):
            with BuildLine():
                EllipticalStartArc((1, 0), (0, 0.5), 1, 0.5, 0)

    def test_elliptical_center_arc(self):
        with BuildLine() as el:
            EllipticalCenterArc((0, 0), 10, 5, 0, 180)
        bbox = el.line.bounding_box()
        self.assertGreaterEqual(bbox.min.X, -10)
        self.assertGreaterEqual(bbox.min.Y, 0)
        self.assertLessEqual(bbox.max.X, 10)
        self.assertLessEqual(bbox.max.Y, 5)

        e1 = EllipticalCenterArc((0, 0), 10, 5, 0, 180)
        bbox = e1.bounding_box()
        self.assertGreaterEqual(bbox.min.X, -10)
        self.assertGreaterEqual(bbox.min.Y, 0)
        self.assertLessEqual(bbox.max.X, 10)
        self.assertLessEqual(bbox.max.Y, 5)

    def test_filletpolyline(self):
        with BuildLine(Plane.YZ):
            p = FilletPolyline(
                (0, 0, 0), (0, 10, 2), (0, 10, 10), (5, 20, 10), radius=2
            )
        self.assertEqual(len(p.edges()), 5)
        self.assertEqual(len(p.edges().filter_by(GeomType.CIRCLE)), 2)
        self.assertEqual(len(p.edges().filter_by(GeomType.LINE)), 3)

        with BuildLine(Plane.YZ):
            p = FilletPolyline(
                (0, 0, 0), (0, 0, 10), (10, 2, 10), (10, 0, 0), radius=2, close=True
            )
        self.assertEqual(len(p.edges()), 8)
        self.assertEqual(len(p.edges().filter_by(GeomType.CIRCLE)), 4)
        self.assertEqual(len(p.edges().filter_by(GeomType.LINE)), 4)

        with self.assertRaises(ValueError):
            FilletPolyline((0, 0), (1, 0), radius=0.1)
        with self.assertRaises(ValueError):
            FilletPolyline((0, 0), (1, 0), (1, 1), radius=-1)

    def test_intersecting_line(self):
        with BuildLine():
            l1 = Line((0, 0), (10, 0))
            l2 = IntersectingLine((5, 10), (0, -1), l1)
        self.assertAlmostEqual(l2.length, 10, 5)

        l3 = Line((0, 0), (10, 10))
        l4 = IntersectingLine((0, 10), (1, -1), l3)
        self.assertTupleAlmostEquals((l4 @ 1).to_tuple(), (5, 5, 0), 5)

        with self.assertRaises(ValueError):
            IntersectingLine((0, 10), (1, 1), l3)

    def test_jern_arc(self):
        with BuildLine() as jern:
            JernArc((1, 0), (0, 1), 1, 90)
        self.assertTupleAlmostEquals((jern.edges()[0] @ 1).to_tuple(), (0, 1, 0), 5)

        with BuildLine() as l:
            l1 = JernArc(start=(0, 0, 0), tangent=(1, 0, 0), radius=1, arc_size=360)
        self.assertTrue(l1.is_closed)
        circle_face = Face.make_from_wires(l1)
        self.assertAlmostEqual(circle_face.area, pi, 5)
        self.assertTupleAlmostEquals(circle_face.center().to_tuple(), (0, 1, 0), 5)

        l1 = JernArc((0, 0), (1, 0), 1, 90)
        self.assertTupleAlmostEquals((l1 @ 1).to_tuple(), (1, 1, 0), 5)

    def test_polar_line(self):
        """Test 2D and 3D polar lines"""
        with BuildLine() as bl:
            PolarLine((0, 0), sqrt(2), 45)
        self.assertTupleAlmostEquals((bl.edges()[0] @ 1).to_tuple(), (1, 1, 0), 5)

        with BuildLine() as bl:
            PolarLine((0, 0), 1, 30)
        self.assertTupleAlmostEquals(
            (bl.edges()[0] @ 1).to_tuple(), (sqrt(3) / 2, 0.5, 0), 5
        )

        with BuildLine() as bl:
            PolarLine((0, 0), 1, 150)
        self.assertTupleAlmostEquals(
            (bl.edges()[0] @ 1).to_tuple(), (-sqrt(3) / 2, 0.5, 0), 5
        )

        with BuildLine() as bl:
            PolarLine((0, 0), 1, angle=30, length_mode=LengthMode.HORIZONTAL)
        self.assertTupleAlmostEquals(
            (bl.edges()[0] @ 1).to_tuple(), (1, 1 / sqrt(3), 0), 5
        )

        with BuildLine(Plane.XZ) as bl:
            PolarLine((0, 0), 1, angle=30, length_mode=LengthMode.VERTICAL)
        self.assertTupleAlmostEquals((bl.edges()[0] @ 1).to_tuple(), (sqrt(3), 0, 1), 5)

        l1 = PolarLine((0, 0), 10, direction=(1, 1))
        self.assertTupleAlmostEquals((l1 @ 1).to_tuple(), (10, 10, 0), 5)

        with self.assertRaises(ValueError):
            PolarLine((0, 0), 1)

    def test_spline(self):
        """Test spline with no tangents"""
        with BuildLine() as test:
            Spline((0, 0), (1, 1), (2, 0))
        self.assertTupleAlmostEquals((test.edges()[0] @ 1).to_tuple(), (2, 0, 0), 5)

    def test_radius_arc(self):
        """Test center arc as arc and circle"""
        with BuildSketch() as s:
            c = Circle(10)

        e = c.edges()[0]
        r = e.radius
        p1, p2 = e @ 0.3, e @ 0.9

        with BuildLine() as l:
            arc1 = RadiusArc(p1, p2, r)
            self.assertAlmostEqual(arc1.length, 2 * r * pi * 0.4, 6)
            self.assertAlmostEqual(arc1.bounding_box().max.X, c.bounding_box().max.X)

            arc2 = RadiusArc(p1, p2, r, short_sagitta=False)
            self.assertAlmostEqual(arc2.length, 2 * r * pi * 0.6, 6)
            self.assertAlmostEqual(arc2.bounding_box().min.X, c.bounding_box().min.X)

            arc3 = RadiusArc(p1, p2, -r)
            self.assertAlmostEqual(arc3.length, 2 * r * pi * 0.4, 6)
            self.assertGreater(arc3.bounding_box().min.X, c.bounding_box().min.X)
            self.assertLess(arc3.bounding_box().min.X, c.bounding_box().max.X)

            arc4 = RadiusArc(p1, p2, -r, short_sagitta=False)
            self.assertAlmostEqual(arc4.length, 2 * r * pi * 0.6, 6)
            self.assertGreater(arc4.bounding_box().max.X, c.bounding_box().max.X)

    def test_sagitta_arc(self):
        l1 = SagittaArc((0, 0), (1, 0), 0.1)
        self.assertAlmostEqual((l1 @ 0.5).Y, 0.1, 5)

    def test_center_arc(self):
        """Test center arc as arc and circle"""
        with BuildLine() as arc:
            CenterArc((0, 0), 10, 0, 180)
        self.assertTupleAlmostEquals((arc.edges()[0] @ 1).to_tuple(), (-10, 0, 0), 5)
        with BuildLine() as arc:
            CenterArc((0, 0), 10, 0, 360)
        self.assertTupleAlmostEquals(
            (arc.edges()[0] @ 0).to_tuple(), (arc.edges()[0] @ 1).to_tuple(), 5
        )
        with BuildLine(Plane.XZ) as arc:
            CenterArc((0, 0), 10, 0, 360)
        self.assertTrue(Face.make_from_wires(arc.wires()[0]).is_coplanar(Plane.XZ))

        with BuildLine(Plane.XZ) as arc:
            CenterArc((-100, 0), 100, -45, 90)
        self.assertTupleAlmostEquals((arc.edges()[0] @ 0.5).to_tuple(), (0, 0, 0), 5)

        arc = CenterArc((-100, 0), 100, 0, 360)
        self.assertTrue(Face.make_from_wires(arc.wires()[0]).is_coplanar(Plane.XY))
        self.assertTupleAlmostEquals(arc.bounding_box().max, (0, 100, 0), 5)

    def test_polyline(self):
        """Test edge generation and close"""
        with BuildLine() as test:
            Polyline((0, 0), (1, 0), (1, 1), (0, 1), close=True)
        self.assertAlmostEqual(
            (test.edges()[0] @ 0 - test.edges()[-1] @ 1).length, 0, 5
        )
        self.assertEqual(len(test.edges()), 4)
        self.assertAlmostEqual(test.wires()[0].length, 4)

    def test_polyline_with_list(self):
        """Test edge generation and close"""
        with BuildLine() as test:
            Polyline((0, 0), [(1, 0), (1, 1)], (0, 1), close=True)
        self.assertAlmostEqual(
            (test.edges()[0] @ 0 - test.edges()[-1] @ 1).length, 0, 5
        )
        self.assertEqual(len(test.edges()), 4)
        self.assertAlmostEqual(test.wires()[0].length, 4)

    def test_line_with_list(self):
        """Test line with a list of points"""
        l = Line([(0, 0), (10, 0)])
        self.assertAlmostEqual(l.length, 10, 5)

    def test_wires_select_last(self):
        with BuildLine() as test:
            Line((0, 0), (0, 1))
            Polyline((1, 0), (1, 1), (0, 1), (0, 0))
        self.assertAlmostEqual(test.wires(Select.LAST)[0].length, 3, 5)

    def test_error_conditions(self):
        """Test error handling"""
        with self.assertRaises(ValueError):
            with BuildLine():
                Line((0, 0))  # Need two points
        with self.assertRaises(ValueError):
            with BuildLine():
                Polyline((0, 0), (1, 1))  # Need three points
        with self.assertRaises(ValueError):
            with BuildLine():
                RadiusArc((0, 0), (1, 0), 0.1)  # Radius too small
        with self.assertRaises(ValueError):
            with BuildLine():
                TangentArc((0, 0), tangent=(1, 1))  # Need two points
        with self.assertRaises(ValueError):
            with BuildLine():
                ThreePointArc((0, 0), (1, 1))  # Need three points
        with self.assertRaises(NotImplementedError):
            with BuildLine() as bl:
                Line((0, 0), (1, 1))
                bl.faces()
        with self.assertRaises(NotImplementedError):
            with BuildLine() as bl:
                Line((0, 0), (1, 1))
                bl.solids()

    def test_obj_name(self):
        with BuildLine() as test:
            self.assertEqual(test._obj_name, "line")


if __name__ == "__main__":
    unittest.main()
