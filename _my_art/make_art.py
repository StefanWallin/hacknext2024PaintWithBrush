#!/usr/bin/env python
import math
import random
import sys
import os.path
from pyaxidraw import axidraw

MARGIN = 5
CANVAS_HEIGHT = 297
CANVAS_WIDTH = 420
MAX_X = CANVAS_WIDTH - MARGIN*2
MAX_Y = CANVAS_HEIGHT - MARGIN*2

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
# ad.options.units = 1                # Set units to centimeters
ad.update()                         # Process changes to options
ad.pendown()                          # Raise pen
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
    if x < MARGIN or x > MAX_X or y < MARGIN or y > MAX_Y:
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

  if origin_x > MAX_X:
    origin_x = MAX_X

  if origin_y < MARGIN:
    origin_y = MARGIN

  if origin_y > MAX_Y:
    origin_y = MAX_Y


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
      if x < MARGIN or x > MAX_X or y < MARGIN or y > MAX_Y:
          break

    rays.append(ray_points)

  return rays

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

def rand_circle(ad):
  """
  Generate a random circle at a random position with a random radius
  """
  print('rand_circle')
  radius = round(random.uniform(5,70), 2)
  center_x = round(random.uniform(0,MAX_X), 2)
  center_y = round(random.uniform(0,MAX_Y), 2)
  circle_points = generate_circle(center_x, center_y, radius, 720)
  paint_circle(ad, center_x, center_y, radius)

def rand_spiral(ad):
  """
  Generate a random spiral at a random position with a random radius and line spacing
  """
  print('rand_spiral')
  total_radius = round(random.uniform(10,50), 2)
  line_spacing = round(random.uniform(2,8), 2)
  center_x = random.randint(0, MAX_X)
  center_y = random.randint(0, MAX_Y)
  spiral_points = generate_archimedean_spiral(center_x, center_y, total_radius, line_spacing)
  paint_archimedean_spiral(ad, center_x, center_y, total_radius, line_spacing)

def rand_spread(ad):
  """
  Generate random rays at a random position with random parameters
  """
  print('rand_spread')
  origin_x = random.randint(0, MAX_X)
  origin_y = random.randint(0, MAX_Y)
  angle = round(random.uniform(0, 360), 2)
  num_rays = random.randint(3, 10)
  spread = random.randint(10, 60)
  max_bounces = random.randint(1, 10)
  paint_spread(ad, origin_x, origin_y, angle, num_rays, spread, max_bounces)

def pause_and_wait_for_user(ad):
  """input the drawing and wait for user  before continuing"""
  print('pause_and_wait_for_user')
  ad.goto(0, 0)
  print("If you want to adjust the pencil or brush and color, do it now.")
  input("Press Enter to continue...")

def generate_painting(ad):
  """
  Generate a random painting with multiple elements, rays, circles and spirals

  Loops through the canvas and generates random elements at each position.
  """

  min_x, min_y = 5, 5
  max_x, max_y = 415, 292

  # Randomize the number of elements
  rand_num_circles = random.randint(5, 10)
  rand_num_spirographs = random.randint(3, 5)
  rand_num_spreads = random.randint(2, 20)
  # rand_num_circles = 1
  # rand_num_spirographs = 1
  # rand_num_spreads = 1

  print('generate_painting')
  print('rand_num_circles', rand_num_circles)
  print('rand_num_spirographs', rand_num_spirographs)
  print('rand_num_spreads', rand_num_spreads)

  # Generate random elements
  for _ in range(rand_num_circles):
    rand_circle(ad)
    pause_and_wait_for_user(ad)

  for _ in range(rand_num_spirographs):
    rand_spiral(ad)
    pause_and_wait_for_user(ad)

  for _ in range(rand_num_spreads):
    rand_spread(ad)
    pause_and_wait_for_user(ad)


try:
  generate_painting(ad)
except Exception as e:
  print(e)
finally:
  ## Teardown
  ad.penup()
  ad.moveto(0,0)              # Pen-up return home
  ad.disconnect()             # Close serial port to AxiDraw


