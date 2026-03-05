import math
from operator import itemgetter

from build123d import *

# from _cluster_key_stem import KEY_STEM_BASE_HEIGHT
KEY_STEM_BASE_HEIGHT=1.8

# from _superellipse import superellipse_points


def superellipse_points(a: float, b: float, n: float, N: int = 20):
    # Technically N=20 converted into cadquery should be roughly 80
    points: list[tuple[float, float]] = []

    # Hack to make the top point connect, part 1. The edge points causes
    # issues, unless deduplicated, but we do that with dict.fromkeys.
    points.append((0, b))

    for time_interval in range(N + 1):
        cosine = math.cos(time_interval)
        sine = math.sin(time_interval)

        sign_cosine = 1.0 if cosine >= 0 else -1.0
        sign_sine = 1.0 if sine >= 0 else -1.0

        # Edit of https://grida.co/docs/math/superellipse#parametric-form
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

    # Hack to make the top point connect, part 2. The edge points causes
    # issues, unless deduplicated, but we do that with dict.fromkeys.
    points.append((0, b))
    return points


FLAG_HEIGHT = KEY_STEM_BASE_HEIGHT * 2
FLAG_LENGTH = 6  # 5 from lalboard; 6 is used by sval
FLAG_WIDTH = 13


def poly_root(x: float | int, polynomial: float | int) -> int | float:
    sign = 1.0 if x >= 0 else -1.0
    return sign * (abs(x) ** polynomial)


def total_assembly():

    with BuildPart() as key_head:
        height = KEY_STEM_BASE_HEIGHT
        border_offset = 0.5

        top_loft_superellipse_length = FLAG_WIDTH * (1 / 8)
        top_loft_superellipse_width = FLAG_LENGTH * (1 / 2)
        top_loft_superellipse_origin_x = (
            -(FLAG_WIDTH / 2) + top_loft_superellipse_length
        )

        # https://www.desmos.com/calculator/ihp7s1s1ob
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

                # Splits superellipse in half, keeping top
                points = superellipse_points(a=a, b=b, n=4)
                points = list(filter(lambda p: p[1] >= 0, points))

                # Add extra points to make sure surface modelling goes smoothly
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

                # Splits superellipse in half, keeping top
                points = superellipse_points(a=a, b=b, n=4)
                points = list(filter(lambda p: p[1] >= 0, points))

                # Add extra points to make sure surface modelling goes smoothly
                points.append((top_loft_superellipse_origin_x, y_intersect_2))
                points.append((-top_loft_superellipse_origin_x, y_intersect_2))

                points.sort(key=itemgetter(0))
                points = list(dict.fromkeys(points))

                _ = Spline(points) + Line((-a, 0), (a, 0))
            make_face()

        with BuildSketch(Plane.XY.offset(height)) as key_top:
            top_loft_superellipse_n = 3

            # Tries to find the corner of the superellipse
            # https://www.desmos.com/calculator/76ona44bgl
            # Yep this is about as incomprensible as I feel like it is.
            # https://mathworld.wolfram.com/Ellipse-LineIntersection.html
            #
            # x_{intersect}=\frac{ab}{\left(a^{n}y_{1}^{n}+b^{n}x_{1}^{n}\right)^{\frac{1}{n}}}x_{1}\ +\ h
            # y_{intersect}=\frac{ab}{\left(a^{n}y_{1}^{n}+b^{n}x_{1}^{n}\right)^{\frac{1}{n}}}y_{1}\ +\ k
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

            # More trig :3
            #
            #       │🯒🯓
            #   adj │θ  🯒🯓
            #       │      🯒🯓
            #       └─────────🯒
            #           opp (top_loft_superellipse_length)
            # adj = top_loft_superellipse_width
            #
            # tan(θ) = opp/adj
            # θ = atan(opp/adj)
            opp = a
            adj = b
            angle_radians = math.atan(opp / adj)

            #       │🯒🯓
            #   adj │θ  🯒🯓
            #       │      🯒🯓
            #       └─────────🯒
            #           opp
            #
            # tan(θ) = opp/adj
            # opp = tan(θ)*adj
            # https://www.desmos.com/calculator/76ona44bgl
            opp = math.tan(angle_radians) * (y_intersect - border_offset)

            with BuildLine(
                Plane(origin=(top_loft_superellipse_origin_x, 0))
            ) as loft_wire_sides_superellipses:
                # Splits superellipse in half, keeping top
                points = superellipse_points(a=a, b=b, n=n)
                points = list(filter(lambda p: p[1] >= 0, points))
                points.sort(key=itemgetter(0))

                # Additionally removes points past x intersect of superellipse (on the
                # left side, hence the -x_intersect)
                end_point = -x_intersect - top_loft_superellipse_origin_x
                points = list(filter(lambda p: p[0] <= end_point, points))
                # Adds a proper connector to our next wire
                points.append((end_point, y_intersect))
                # And finally removes duplicates
                points = list(dict.fromkeys(points))
                _ = Spline(points)
                _ = mirror(loft_wire_sides_superellipses.line, about=Plane.YZ)

            with BuildLine() as loft_wire_indent:
                _ = (
                    Polyline(
                        (-x_intersect, y_intersect),
                        (-x_intersect + opp, border_offset),
                        # (0, border_offset),
                        # (0, 0),
                        # (-x_intersect, 0),
                    )
                    + (
                        Spline(
                            (-x_intersect + opp, border_offset),
                            (0, border_offset * 0.25),
                            (-(-x_intersect + opp), border_offset),
                        )
                    )
                    + Polyline(
                        (-(-x_intersect + opp), border_offset),
                        (x_intersect, y_intersect),
                    )
                )

            with BuildLine() as loft_wire_flat:
                _ = Line((-FLAG_WIDTH / 2, 0), (FLAG_WIDTH / 2, 0))

            make_face()

        # profiles = key_bottom.edges() + key_top.edges()
        # Face.make_gordon_surface(profiles, guides)

        # profiles = key_bottom.edges() + key_dummy_top.edges()
        # guide_line_dummy = Line((0, FLAG_LENGTH, 0), (0, FLAG_LENGTH, height))
        # dummy_guide = [guide_line_left, guide_line_right, guide_line_dummy]
        # Face.make_gordon_surface(
        #     profiles,
        #     dummy_guide,
        # )
        #

        af = key_bottom.face()
        bf = key_top.face().translate((0, 0, height))

        # l = loft([af, bf])

        def split_edges(
            face: Face,
            edge_indexes: list[int],
            plane_offsets: list[float],
        ):
            edges = face.edges().sort_by(Wire.children)
            edgs = []
            sel_edgs = []
            for i, edg in enumerate(edges):
                if i in list(edge_indexes):
                    sel_edgs.append(edg)
                    tmp = edg
                    for offs in plane_offsets:
                        tmp = split(tmp, Plane.right.offset(offs), Keep.BOTH)
                    for e in tmp.edges():
                        edgs.append(e)
                else:
                    edgs.append(edg)
            res_wr = Wire(edgs)
            return Face(res_wr), sel_edgs

        af = key_bottom.face()
        af, sae = split_edges(af, [0], [-2.566, -3.585, -4.875, 0, 2.566, 3.585, 4.875])

        bf = key_top.face().translate((0, 0, height))
        bf, sbe = split_edges(bf, [0, 2, 4], [-4.875, 0, 4.875])

        l = loft([af, bf])

    if __name__ == "__main__":
        show_all()

    return l


def export():
    total_assembly()
    pass


if __name__ == "__main__":
    from ocp_vscode import *  # pyright: ignore[reportMissingTypeStubs]

    set_port(3939)
    set_defaults(
        reset_camera=Camera.CENTER,
        helper_scale=1,
        axes0=True,
        axes=True,
        # grid=True,
        transparent=False,
    )
    export()
else:
    assembly = total_assembly()
