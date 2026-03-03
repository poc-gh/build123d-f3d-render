from build123d import Line, Side, Spline, Wire
from numpy import linspace
# from ocp_vscode import Camera, set_defaults, show

n_teeth = 7
tooth_offset = 0.5
overlap = 0.25


line = Spline((0, 0), (4, 3), (3, 10), (5, 15))

tooth_size = line.length / (2 + n_teeth)
side = Side.RIGHT
start = (tooth_size / 2) / line.length
end = 1 - start
t_overlap = overlap / line.length

lines = [line.trim(0, 2 * start + t_overlap)]

last = start
for t in linspace(start, end, n_teeth + 2)[1:-1]:
    l_trim = line.trim(t - start - t_overlap, t + start + (t_overlap / 2)).offset_2d(
        tooth_offset, side=side, closed=False
    )

    if side == Side.LEFT:
        l_trim = Wire([e.reversed() for e in l_trim.edges()])

    lines.append(l_trim)

    if side == Side.RIGHT:
        side = Side.LEFT
    else:
        side = Side.RIGHT

lines.append(line.trim(1 - 2 * start - (t_overlap / 2), 1))

line = lines[0]
for l in lines[1:]:
    line += Line(line @ 1, l @ 0)
    line += l

# set_defaults(
#     reset_camera=Camera.KEEP,
#     ortho=True,
# )
# show([line, lines])