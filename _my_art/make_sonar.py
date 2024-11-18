#!/usr/bin/env python
import math
import random
import sys
import os.path
from pyaxidraw import axidraw

MARGIN = 5
CANVAS_HEIGHT = 300
CANVAS_WIDTH = 300
MAX_X = CANVAS_WIDTH - MARGIN
MAX_Y = CANVAS_HEIGHT - MARGIN

## CONNECT
ad = axidraw.AxiDraw() # Initialize class
ad.interactive()            # Enter interactive mode
connected = ad.connect()    # Open serial port to AxiDraw
if not connected:
  print('cannot connect to AxiDraw')
  sys.exit() # end script

# ## OPTIONS
ad.options.speed_pendown = 20       # Set maximum pen-down speed to 90%
ad.options.model = 2                # Set AxiDraw model to V3/A3
ad.options.units = 2                # Set units to millimeters
ad.options.pen_pos_up = 100          # Set pen-up position to 0%
# ad.options.units = 1                # Set units to centimeters
ad.update()                         # Process changes to options
# ad.pendown()                          # Raise pen
ad.penup()                          # Raise pen
ad.goto(0,0)

## FUNCTIONS

def generate_archimedean_spiral(center_x, center_y, total_radius, line_spacing):
  """
  Generate an Archimedean spiral centered at (center_x, center_y).

  Parameters:
  - center_x, center_y: The center of the spiral.
  - total_radius: The maximum radius of the spiral.
  - line_spacing: The distance between spiral lines.

  Returns:
  - A list of (x, y) points representing the spiral.
  """
  print('generate_archimedean_spiral', center_x, center_y, total_radius, line_spacing)
  # Calculate the number of loops needed
  num_loops = total_radius / line_spacing

  # The growth factor b is equal to the line spacing
  b = line_spacing

  # Maximum theta for the spiral
  max_theta = 2 * math.pi * num_loops

  # Number of points to generate (increase for smoother spirals)
  num_points = int(num_loops * 400)

  # Angle increment
  delta_theta = max_theta / num_points

  # Generate spiral points
  vertices = []
  for i in range(num_points + 1):
    theta = i * delta_theta
    r = b * theta / (2 * math.pi)  # Linear relationship: r = b * loops

    if r > total_radius:
        break
    x = center_x + r * math.cos(theta)
    y = center_y + r * math.sin(theta)
    # if vertice is out of bounds, skip it
    if x < MARGIN or x > MAX_X-MARGIN or y < MARGIN or y > MAX_Y-MARGIN:
      continue
    else:
      vertices.append((x, y))

  return vertices

def generate_circle(center_x, center_y, total_radius, num_points=360):
  """
  Generate points for a circle centered at (center_x, center_y).

  Parameters:
  - center_x, center_y: The center of the circle.
  - total_radius: The radius of the circle.
  - num_points: The number of points to generate for the circle (higher = smoother).

  Returns:
  - A list of (x, y) points representing the circle.
  """
  print('generate_circle', center_x, center_y, total_radius, num_points)
  vertices = []
  angle_increment = 2 * math.pi / num_points  # Full circle divided into num_points

  for i in range(num_points):
    theta = i * angle_increment
    x = center_x + total_radius * math.cos(theta)
    y = center_y + total_radius * math.sin(theta)
    # If the vertice is out of bounds, skip it
    if x < MARGIN or x > MAX_X or y < MARGIN or y > MAX_Y:
        continue  # Skip this point
    else:
      vertices.append((x, y))

  # Connect the circle by appending the first point at the end
  vertices.append(vertices[0])

  return vertices

def generate_rays(origin_x, origin_y, angle, num_rays, spread, max_bounces=10):
  """
  Generate rays originating from a point, with a spread and bouncing off canvas walls.

  Parameters:
  - origin_x, origin_y: Starting point of the rays.
  - angle: Initial direction of the center ray, in degrees.
  - num_rays: Total number of rays to generate.
  - spread: Total spread angle, in degrees (e.g., 30 means rays spread ±15° from the center angle).
  - canvas_width, canvas_height: Dimensions of the canvas.
  - max_bounces: Maximum number of wall bounces per ray.

  Returns:
  - A list of rays, where each ray is a list of (x, y) points.
  """
  print('generate_rays', origin_x, origin_y, angle, num_rays, spread, max_bounces)

  if origin_x < MARGIN:
    origin_x = MARGIN

  if origin_x > MAX_X-MARGIN:
    origin_x = MAX_X-MARGIN

  if origin_y < MARGIN:
    origin_y = MARGIN

  if origin_y > MAX_Y-MARGIN:
    origin_y = MAX_Y-MARGIN


  rays = []
  center_angle = math.radians(angle)
  half_spread = math.radians(spread / 2)

  # Generate angles for rays
  ray_angles = [
    center_angle + (i - (num_rays - 1) / 2) * (half_spread * 2 / (num_rays - 1))
    for i in range(num_rays)
  ]

  # For each ray, calculate its path with bounces
  for ray_angle in ray_angles:
    ray_points = [(origin_x, origin_y)]  # Start at the origin
    current_angle = ray_angle
    x, y = origin_x, origin_y

    for _ in range(max_bounces):
      # Determine the next intersection with the canvas boundary
      if math.cos(current_angle) > 0:  # Moving right
        next_x = MAX_X
        t_x = (next_x - x) / math.cos(current_angle)
      else:  # Moving left
        next_x = MARGIN
        t_x = (next_x - x) / math.cos(current_angle)

      if math.sin(current_angle) > 0:  # Moving down
        next_y = MAX_Y
        t_y = (next_y - y) / math.sin(current_angle)
      else:  # Moving up
        next_y = MARGIN
        t_y = (next_y - y) / math.sin(current_angle)

      # Use the smaller t to find the actual next point
      if t_x < t_y:
        x = next_x
        y += t_x * math.sin(current_angle)
        current_angle = math.pi - current_angle  # Reflect horizontally
      else:
        x += t_y * math.cos(current_angle)
        y = next_y
        current_angle = -current_angle  # Reflect vertically

      ray_points.append((x, y))

      # Stop if the ray is out of bounds (shouldn't happen now)
      if x < MARGIN or x > MAX_X-MARGIN or y < MARGIN-MARGIN or y > MAX_Y:
          break

    rays.append(ray_points)

  return rays

def generate_random_polygon(center_x, center_y, num_sides, bounding_circle_diameter, box_width, box_height, brush_diameter):
    """
    Generate a random polygon with a specified number of sides, fitting within a bounding circle
    and constrained by a bounding box, and prepare it for filling with a given brush diameter.

    Parameters:
    - center_x, center_y: Center of the polygon.
    - num_sides: Number of sides of the polygon (minimum 3).
    - bounding_circle_diameter: Diameter of the bounding circle in which the polygon is inscribed.
    - box_width, box_height: Width and height of the bounding box.
    - brush_diameter: Diameter of the brush used for filling the polygon.

    Returns:
    - A tuple containing:
      - A list of (x, y) vertices representing the random polygon.
      - A list of filling paths (each path is a list of (x, y) points).
    """
    if num_sides < 3:
        raise ValueError("A polygon must have at least 3 sides.")

    # Determine the radius of the bounding circle
    bounding_circle_radius = bounding_circle_diameter / 2

    # Constrain the radius to the smaller of the circle or the bounding box
    max_radius = min(bounding_circle_radius, box_width / 2, box_height / 2)
    min_radius = max_radius * 0.5  # Allow some randomness in the radius

    # Angle between vertices in radians
    angle_increment = 2 * math.pi / num_sides

    # Generate random vertices for the polygon
    vertices = []
    for i in range(num_sides):
        angle = i * angle_increment
        radius = random.uniform(min_radius, max_radius)  # Randomize the radius
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vertices.append((x, y))

    # Generate filling paths
    fill_paths = []
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)
    current_y = min_y

    while current_y <= max_y:
        path = []
        for i in range(len(vertices)):
            # Get the current and next vertex
            v1 = vertices[i]
            v2 = vertices[(i + 1) % len(vertices)]

            # Check if the current scan line intersects this edge
            if (v1[1] <= current_y <= v2[1]) or (v2[1] <= current_y <= v1[1]):
                # Calculate the intersection point
                if v1[1] != v2[1]:  # Avoid division by zero
                    t = (current_y - v1[1]) / (v2[1] - v1[1])
                    intersect_x = v1[0] + t * (v2[0] - v1[0])
                    path.append(intersect_x)

        # Sort intersection points and pair them
        if len(path) >= 2:
            path.sort()
            for i in range(0, len(path) - 1, 2):
                fill_paths.append([(path[i], current_y), (path[i + 1], current_y)])

        current_y += brush_diameter  # Move to the next line

    # Calculate the centroid
    centroid_x = sum(v[0] for v in vertices) / len(vertices)
    centroid_y = sum(v[1] for v in vertices) / len(vertices)
    centroid = (centroid_x, centroid_y)

    return vertices, fill_paths, centroid

def generate_nautilus_with_crossbeams(center_x, center_y, canvas_width, canvas_height, a=1, b=0.15, taper=0.9, num_points=1000, max_theta=4*math.pi, beam_curvature=0.3, beam_segments=19):
  """
  Generate a nautilus shell with an inner spiral, outer spiral, and connecting crossbeams.

  Parameters:
  - center_x, center_y: Center of the shell.
  - canvas_width, canvas_height: Dimensions of the drawing canvas.
  - a: Initial scaling factor for the spirals.
  - b: Growth rate of the spirals (controls how fast they expand).
  - taper: Tapering factor to decrease size outward (0 < taper <= 1).
  - num_points: Number of points to generate for the spirals.
  - max_theta: Maximum angle for the spirals in radians.
  - beam_curvature: Curvature factor for the crossbeams.

  Returns:
  - A dictionary with:
    - 'inner_spiral': List of (x, y) points for the inner spiral.
    - 'outer_spiral': List of (x, y) points for the outer spiral.
    - 'crossbeams': List of beam paths, where each beam is a list of (x, y) points.
  """
  golden_ratio = (1 + math.sqrt(5)) / 2  # Golden ratio
  inner_spiral = []
  outer_spiral = []
  crossbeams = []

  last_beam_inner = None  # Tracks the last inner spiral position to enforce spacing

  for i in range(num_points):
    theta = i * max_theta / num_points  # Increment angle
    r_inner = a * golden_ratio**(b * theta) * taper**(theta / max_theta)  # Inner spiral
    r_outer = r_inner * 1.5  # Slightly larger radius for outer spiral

    # Compute inner and outer spiral points
    x_inner = center_x + r_inner * math.cos(theta)
    y_inner = center_y + r_inner * math.sin(theta)
    x_outer = center_x + r_outer * math.cos(theta)
    y_outer = center_y + r_outer * math.sin(theta)

    inner_spiral.append((x_inner, y_inner))
    outer_spiral.append((x_outer, y_outer))

    # Calculate beam length (distance between inner and outer endpoints)
    beam_length = math.sqrt((x_outer - x_inner)**2 + (y_outer - y_inner)**2)

    # Enforce spacing based on the inner spiral points
    if last_beam_inner:
      distance_to_last_inner = math.sqrt((x_inner - last_beam_inner[0])**2 + (y_inner - last_beam_inner[1])**2)
      if distance_to_last_inner < beam_length:
        continue  # Skip adding this beam if spacing is insufficient

    beam_curve = []
    for t in range(beam_segments + 1):  # Generate beam_segments points along the curve
      t /= beam_segments  # Normalize t to [0, 1]
      # Quadratic Bézier formula:
      # B(t) = (1-t)^2 * P0 + 2*(1-t)*t * P1 + t^2 * P2
      bx = (1 - t)**2 * x_inner + 2 * (1 - t) * t * (x_inner + beam_curvature * (y_outer - y_inner)) + t**2 * x_outer
      by = (1 - t)**2 * y_inner + 2 * (1 - t) * t * (y_inner - beam_curvature * (x_outer - x_inner)) + t**2 * y_outer
      beam_curve.append((bx, by))

    crossbeams.append(beam_curve)  # Add the full curve to the crossbeams list
    last_beam_inner = (x_inner, y_inner)

  return {
    'inner_spiral': inner_spiral,
    'outer_spiral': outer_spiral,
    'crossbeams': crossbeams
  }

def paint_nautilus_shell(ad, center_x, center_y, a=10, b=0.12, taper=0.95, num_points=500, max_theta=6*math.pi, beam_curvature=0.2):
  """
  Paint a nautilus shell based on the golden ratio using logarithmic spirals.

  Parameters:
  - ad: The AxiDraw object.
  - center_x, center_y: Center of the shell.
  - a: Initial scaling factor for the spirals.
  - b: Growth rate of the spirals (controls how fast they expand).
  - taper: Tapering factor to decrease size outward (0 < taper <= 1).
  - num_points: Number of points to generate for the spirals.
  - max_theta: Maximum angle for the spirals in radians.
  """
  print('paint_nautilus_shell', center_x, center_y, a, b, taper, num_points, max_theta)
  nautilus = generate_nautilus_with_crossbeams(
    center_x, center_y, MAX_X, MAX_Y, a, b, taper, num_points, max_theta
  )

  # Draw the shell
  # Draw inner and outer spirals
  ad.draw_path(nautilus['inner_spiral'])
  ad.draw_path(nautilus['outer_spiral'])

  # # Draw crossbeams
  for beam in nautilus['crossbeams']:
    ad.draw_path(beam)  # Each beam is a small path

def paint_archimedean_spiral(ad, center_x, center_y, total_radius, line_spacing):
  """
  Paint an Archimedean spiral centered at (center_x, center_y).

  Parameters:
  - ad: The AxiDraw object.
  - center_x, center_y: The center of the spiral.
  - total_radius: The maximum radius of the spiral.
  - line_spacing: The distance between spiral lines.
  """
  print('paint_archimedean_spiral', center_x, center_y, total_radius, line_spacing)
  spiral_points = generate_archimedean_spiral(center_x, center_y, total_radius, line_spacing)
  try:
    print("Press Ctrl+C to pause drawing.")
    ad.draw_path(spiral_points)
  except KeyboardInterrupt:
    input("Paused drawing. Press Ctrl+C again to stop, or Enter to continue.")
    ad.draw_path(spiral_points)

def dip_brush(ad, centroid):
  ad.penup()
  ad.goto(centroid[0], centroid[1])

  input("PREP BRUSH WITH PAINT. PRESS ENTER TO CONTINUE")

  ad.pendown()
  ad.penup()
  ad.pendown()
  circle_points = generate_circle(centroid[0], centroid[1], 2, 360)
  ad.draw_path(circle_points)
  ad.penup()

def paint_random_polygon(ad, brush_diameter):
  center_x = round(random.uniform(MARGIN,MAX_X), 2)
  center_y = round(random.uniform(MARGIN,MAX_Y), 2)
  num_sides = random.randint(6, 36)
  bounding_circle_diameter = random.uniform(20, 150)
  box_width = random.uniform(10, 150)
  box_height = random.uniform(10, 150)

  # Generate polygon and fill paths
  polygon_vertices, fill_paths, centroid = generate_random_polygon(
      center_x, center_y, num_sides, bounding_circle_diameter, box_width, box_height, brush_diameter
  )

  print("Will print polygon with properties:")
  print(f"  Center:                     ({center_x}, {center_y})")
  print(f"  Number of sides:            {num_sides}")
  print(f"  Bounding circle diameter:   {bounding_circle_diameter}")
  print(f"  Bounding box width:         {box_width}")
  print(f"  Bounding box height:        {box_height}")
  print(f"  Brush diameter:             {brush_diameter}")

  dip_brush(ad, centroid)


  # Example of drawing polygon and fill paths
  ad.draw_path(polygon_vertices + [polygon_vertices[0]])  # Draw the polygon

  input("DRAWING POLYGON. PRESS ENTER TO CONTINUE")

  for index, fill_path in enumerate(fill_paths):
    if index % 10 == 0:
      dip_brush(ad, centroid)
    ad.draw_path(fill_path)  # Draw each fill path

def paint_circle(ad, center_x, center_y, total_radius, num_points=360):
  """
  Paint a circle centered at (center_x, center_y).

  Parameters:
  - ad: The AxiDraw object.
  - center_x, center_y: The center of the circle.
  - total_radius: The radius of the circle.
  - num_points: The number of points to generate for the circle (higher = smoother).
  """
  print('paint_circle', center_x, center_y, total_radius, num_points)
  circle_points = generate_circle(center_x, center_y, total_radius, num_points)
  try:
    print("Press Ctrl+C to pause drawing.")
    ad.draw_path(circle_points)
  except KeyboardInterrupt:
    input("Paused drawing. Press Ctrl+C again to stop, or Enter to continue.")
    ad.draw_path(circle_points)

def paint_spread(ad, origin_x, origin_y, angle, num_rays, spread, max_bounces=10):
  """
  Paint rays originating from a point, with a spread and bouncing off canvas walls.

  Parameters:
  - ad: The AxiDraw object.
  - origin_x, origin_y: Starting point of the rays.
  - angle: Initial direction of the center ray, in degrees.
  - num_rays: Total number of rays to generate.
  - spread: Total spread angle, in degrees (e.g., 30 means rays spread ±15° from the center angle).
  - max_bounces: Maximum number of wall bounces per ray.
  """
  print('paint_spread', origin_x, origin_y, angle, num_rays, spread, max_bounces)
  ray_paths = generate_rays(origin_x, origin_y, angle, num_rays, spread, max_bounces)
  for ray in ray_paths:
    try:
      print("Press Ctrl+C to pause drawing.")
      ad.draw_path(ray)
    except KeyboardInterrupt:
      input("Paused drawing. Press Ctrl+C again to stop, or Enter to continue.")
      ad.draw_path(ray)

def generate_painting(ad):
  """
  Generate a random painting with multiple elements, rays, circles and spirals

  Loops through the canvas and generates random elements at each position.
  """

  min_x, min_y = MARGIN, MARGIN
  max_x, max_y = MAX_X, MAX_Y

  # Draw a golden ratio shell centered at the focal point, covering the entire A3 canvas
  ad.moveto(MAX_X-MAX_X/1.618+180, MAX_Y-MAX_Y/1.618-40)
  focal_point = (MAX_X-MAX_X/1.618+180, MAX_Y-MAX_Y/1.618-40)
  paint_nautilus_shell(ad, focal_point[0], focal_point[1], 3, 0.19, 0.9, 15000, 15*math.pi, 0.2)

  # paint_circle(ad, 150, 150, 0.2, 360)
  # ad.goto(150, 150)
  # ad.pen
  # input("CENTER CIRCLE INDICATED BY BRUSH POSITION. PRESS ENTER TO CONTINUE")

  # paint_circle(ad, 150, 150, 0.2, 360)
  # paint_circle(ad, 150, 150, 0.5, 360)
  # paint_circle(ad, 150, 150, 1, 360)
  # paint_circle(ad, 150, 150, 1.5, 360)
  # paint_circle(ad, 150, 150, 2, 360)
  # paint_circle(ad, 150, 150, 2.5, 360)
  # paint_circle(ad, 150, 150, 3, 360)
  # paint_circle(ad, 150, 150, 3.5, 360)

  # # Make a spirograph up to 300mm in diameter
  # paint_archimedean_spiral(ad, 80, 180, 40, 2)

  # paint_spread(ad, 70, 40, 40, 5, 3, 1)

  # for i in range(30):
  #   paint_random_polygon(ad, 1)

try:
  generate_painting(ad)
except Exception as e:
  print(e)
finally:
  ## Teardown
  ad.penup()
  ad.delay(500)
  ad.moveto(0,0)              # Pen-up return home
  ad.disconnect()             # Close serial port to AxiDraw


