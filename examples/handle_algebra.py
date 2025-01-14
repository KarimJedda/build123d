from build123d import *

segment_count = 6

# Create a path for the sweep along the handle - added to pending_edges
handle_center_line = Spline(
    (-10, 0, 0),
    (0, 0, 5),
    (10, 0, 0),
    tangents=((0, 0, 1), (0, 0, -1)),
    tangent_scalars=(1.5, 1.5),
)
# Record the center line for display and workplane creation
handle_path = handle_center_line.edges()[0]


# Create the cross sections - added to pending_faces

sections = Sketch()
for i in range(segment_count + 1):
    plane = Plane(
        origin=handle_path @ (i / segment_count),
        z_dir=handle_path % (i / segment_count),
    )
    if i % segment_count == 0:
        circle = plane * Circle(1)
    else:
        circle = plane * Rectangle(1.25, 3)
        circle = fillet(circle.vertices(), radius=0.2)
    sections += circle

# Create the handle by sweeping along the path
handle = sweep(sections, path=handle_path, multisection=True)

if "show_object" in locals():
    show_object(handle_path.wrapped, name="handle_path")
    for i, circle in enumerate(sections):
        show_object(circle.wrapped, name="section" + str(i))
    show_object(handle, name="handle", options=dict(alpha=0.6))
