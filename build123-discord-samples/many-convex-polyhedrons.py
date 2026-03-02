from build123d import *
# from ocp_vscode import show
import timeit

start_time = timeit.default_timer()

num_sides = 20
cyc_radius = 17
spike_len = 2
num_rows = 46
num_spikes = 60
cyl_height = 2 * num_rows + 1
spike_pitch = cyl_height / num_rows
wall_thickness = 3

lower_inside_pnts = [l.position for l in PolarLocations(cyc_radius, num_spikes)]
upper_inside_pnts = [p + (0, 0, spike_pitch) for p in lower_inside_pnts]
tip_pnts = [
    l.position + (0, 0, spike_pitch / 2)
    for l in PolarLocations(
        cyc_radius + spike_len, num_spikes, start_angle=180 / num_spikes
    )
]
single_spike_faces = [
    Polygon(*lower_inside_pnts[:2], tip_pnts[0]),
    Polygon(*upper_inside_pnts[:2], tip_pnts[0]),
    Polygon(lower_inside_pnts[0], upper_inside_pnts[0], tip_pnts[0]),
    Polygon(lower_inside_pnts[1], upper_inside_pnts[1], tip_pnts[0]),
]
row_spike_faces = [
    l * f for l in PolarLocations(0, num_spikes) for f in single_spike_faces
]
spike_faces = [
    Pos(Z=i * spike_pitch) * f for i in range(num_rows) for f in row_spike_faces
]
bottom_face = Face(
    Polyline(lower_inside_pnts, close=True),
    [Wire(CenterArc((0, 0), cyc_radius - wall_thickness, 0, 360))],
)
top_face = Pos(Z=cyl_height) * bottom_face
inside_face = Face.revolve(
    Line(
        (cyc_radius - wall_thickness, 0, 0),
        (cyc_radius - wall_thickness, 0, cyl_height),
    ),
    360,
    Axis.Z,
)
surface = Shell([bottom_face, top_face, inside_face] + spike_faces)
solid_obj = Solid(surface)
print(f"Time: {timeit.default_timer() - start_time:0.3f}s") # Time: 16.597s
# show(solid_obj)
