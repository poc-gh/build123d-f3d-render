from build123d import *

import math
from operator import itemgetter

KEY_STEM_BASE_HEIGHT=1.8
def superellipse_points(a: float, b: float, n: float, N: int = 20):
    points: list[tuple[float, float]] = []
    points.append((0, b))

    for time_interval in range(N + 1):
        cosine = math.cos(time_interval)
        sine = math.sin(time_interval)

        sign_cosine = 1.0 if cosine >= 0 else -1.0
        sign_sine = 1.0 if sine >= 0 else -1.0

        x = a * sign_cosine * (abs(cosine) ** (2.0 / n))
        y = b * sign_sine * (abs(sine) ** (2.0 / n))
        points.append((abs(x), abs(y)))

    points.sort(key=itemgetter(0))

    fourth_quadrant = list(map(lambda p: (p[0], -p[1]), points))
    fourth_quadrant.sort(key=itemgetter(0), reverse=True)
    points.extend(fourth_quadrant)

    second_third_quadrant = list(map(lambda p: (-p[0], p[1]), points))
    second_third_quadrant.sort(key=itemgetter(1))
    points.extend(second_third_quadrant)

    points = list(dict.fromkeys(points))

    points.append((0, b))
    return points

FLAG_HEIGHT = KEY_STEM_BASE_HEIGHT * 2
FLAG_LENGTH = 6  # 5 from lalboard; 6 is used by sval
FLAG_WIDTH = 13

def poly_root(x: float | int, polynomial: float | int) -> int | float:
    sign = 1.0 if x >= 0 else -1.0
    return sign * (abs(x) ** polynomial)

with BuildPart() as key_head:
    height = KEY_STEM_BASE_HEIGHT
    border_offset = 0.5

    top_loft_superellipse_length = FLAG_WIDTH * (1 / 8)
    top_loft_superellipse_width = FLAG_LENGTH * (1 / 2)
    top_loft_superellipse_origin_x = (
        -(FLAG_WIDTH / 2) + top_loft_superellipse_length
    )

    a = FLAG_WIDTH / 2.0
    b = FLAG_LENGTH
    n = 4
    y_intersect_2 = (1 - math.fabs(top_loft_superellipse_origin_x / a) ** n) ** (
        1 / n
    ) * b
    guide_line_top_surface_left = Line(
        (top_loft_superellipse_origin_x, top_loft_superellipse_width, height),
        (top_loft_superellipse_origin_x, y_intersect_2, 0),
    )
    guide_line_top_surface_right = Line(
        (-top_loft_superellipse_origin_x, top_loft_superellipse_width, height),
        (-top_loft_superellipse_origin_x, y_intersect_2, 0),
    )

    guide_line_top_surface_center = Line(
        (0, FLAG_LENGTH, 0),
        (0, border_offset * 0.25, height),
    )
    guide_line_left = Line((-FLAG_WIDTH / 2, 0, 0), (-FLAG_WIDTH / 2, 0, height))
    guide_line_right = Line((FLAG_WIDTH / 2, 0, 0), (FLAG_WIDTH / 2, 0, height))

    guides = [
        guide_line_left,
        guide_line_right,
        guide_line_top_surface_center,
        guide_line_top_surface_left,
        guide_line_top_surface_right,
    ]

    with BuildSketch() as key_bottom:
        with BuildLine() as key_bottom_line:
            a = FLAG_WIDTH / 2.0
            b = FLAG_LENGTH

            points = superellipse_points(a=a, b=b, n=4, N=5)
            points = list(filter(lambda p: p[1] >= 0, points))

            points.append((top_loft_superellipse_origin_x, y_intersect_2))
            points.append((-top_loft_superellipse_origin_x, y_intersect_2))

            points.sort(key=itemgetter(0))
            points = list(dict.fromkeys(points))

            _ = Spline(points) + Line((-a, 0), (a, 0))
        make_face()

    with BuildSketch(Plane.XY.offset(height)) as key_dummy_top:
        with BuildLine() as key_dummy_top_line:
            a = FLAG_WIDTH / 2.0
            b = FLAG_LENGTH

            points = superellipse_points(a=a, b=b, n=4)
            points = list(filter(lambda p: p[1] >= 0, points))

            points.append((top_loft_superellipse_origin_x, y_intersect_2))
            points.append((-top_loft_superellipse_origin_x, y_intersect_2))

            points.sort(key=itemgetter(0))
            points = list(dict.fromkeys(points))

            _ = Spline(points) + Line((-a, 0), (a, 0))
        make_face()

    with BuildSketch(Plane.XY.offset(height)) as key_top:
        top_loft_superellipse_n = 3

        a = top_loft_superellipse_length
        b = top_loft_superellipse_width
        n = top_loft_superellipse_n
        h = top_loft_superellipse_origin_x
        k = 0
        x_1 = a * -1
        y_1 = b * -1
        poly_root_input = a**n * y_1**n + b**n * x_1**n
        poly_root_output = poly_root(poly_root_input, 1 / n)
        x_intersect = ((a * b) / -poly_root_output) * x_1 - h
        y_intersect = ((a * b) / poly_root_output) * y_1 - k

        opp = a
        adj = b
        angle_radians = math.atan(opp / adj)

        opp = math.tan(angle_radians) * (y_intersect - border_offset)

        with BuildLine(
            Plane(origin=(top_loft_superellipse_origin_x, 0))
        ) as loft_wire_sides_superellipses:
            points = superellipse_points(a=a, b=b, n=n)
            points = list(filter(lambda p: p[1] >= 0, points))
            points.sort(key=itemgetter(0))

            end_point = -x_intersect - top_loft_superellipse_origin_x
            points = list(filter(lambda p: p[0] <= end_point, points))
            points.append((end_point, y_intersect))
            points = list(dict.fromkeys(points))
            _ = Spline(points)
            _ = mirror(loft_wire_sides_superellipses.line, about=Plane.YZ)

        with BuildLine() as loft_wire_indent:
            Polyline(
                    (-x_intersect, y_intersect),
                    (-x_intersect + opp, border_offset),
                )
            Spline(
                    (-x_intersect + opp, border_offset),
                    (0, border_offset * 0.25),
                    (-(-x_intersect + opp), border_offset),
                )
            Polyline(
                    (-(-x_intersect + opp), border_offset),
                    (x_intersect, y_intersect),
                )

        with BuildLine() as loft_wire_flat:
            Line((-FLAG_WIDTH / 2, 0), (FLAG_WIDTH / 2, 0))

        make_face()

    af = key_bottom.face()
    bf = key_top.face().translate((0, 0, height))

afs = split(af, bisect_by=Plane.YZ)
bfs = split(bf, bisect_by=Plane.YZ)

afs_nonlinear = afs.edges().sort_by(Axis.Y)[-1]
bfs_nonlinear = Wire(bfs.edges().sort_by(Axis.Y)[-3::])
start = afs_nonlinear@0
start = bfs_nonlinear@0
start_line = Line(afs_nonlinear@0, bfs_nonlinear@0)
end_line = Line(afs_nonlinear@1, bfs_nonlinear@1)

ms = Face.make_surface([afs_nonlinear,*bfs_nonlinear.edges(),start_line,end_line])
rs = Face.make_surface_from_curves(afs.edges().sort_by(Axis.Y)[0],bfs.edges().sort_by(Axis.Y)[0])

sh_right = Shell([ms,rs,afs,bfs])
sh = Shell([sh_right,mirror(sh_right,about=Plane.YZ)])
solid = Solid(sh)

if __name__ == "__main__":
  from ocp_vscode import *
  show_all()
