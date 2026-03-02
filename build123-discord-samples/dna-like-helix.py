from build123d import *

height = 120
pitch = 90
radius = 20
circle_radius = 3

circles = Sketch() + [loc * Circle(circle_radius) for loc in PolarLocations(radius, 1)]
circles2 = Location((0, 0, height)) * circles

helix1 = Helix(pitch=pitch, height=height, radius=radius)
helix2 = Rot(Z=180) * helix1

circle1 = helix1.location_at(0) * Circle(circle_radius)
circle2 = helix2.location_at(0) * Circle(circle_radius)
dna = sweep(circle1, helix1) + sweep(circle2, helix2)
