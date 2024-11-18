import math


def get_rotated_corners(rect, angle):
    # Get the center of the rect
    cx, cy = rect.center

    # Calculate the four corners of the rect
    corners = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.right, rect.bottom),
        (rect.left, rect.bottom)
    ]

    # Rotate each corner around the center of the rect
    rotated_corners = []
    for x, y in corners:
        # Translate corner to origin
        temp_x, temp_y = x - cx, y - cy

        # Apply rotation
        rotated_x = temp_x * math.cos(angle) - temp_y * math.sin(angle)
        rotated_y = temp_x * math.sin(angle) + temp_y * math.cos(angle)

        # Translate back to the original center
        rotated_corners.append((rotated_x + cx, rotated_y + cy))

    return rotated_corners


def project_polygon(corners, axis):
    min_proj = float("inf")
    max_proj = float("-inf")
    for corner in corners:
        proj = corner[0] * axis[0] + corner[1] * axis[1]
        min_proj = min(min_proj, proj)
        max_proj = max(max_proj, proj)
    return min_proj, max_proj


def overlap(min_a, max_a, min_b, max_b):
    return max_a >= min_b and max_b >= min_a


def check_collision(rotated_corners, static_rect):
    # Get the corners of the static rect
    static_corners = [
        (static_rect.left, static_rect.top),
        (static_rect.right, static_rect.top),
        (static_rect.right, static_rect.bottom),
        (static_rect.left, static_rect.bottom)
    ]

    # List of all axes (perpendicular vectors to each edge)
    axes = []
    for i in range(4):
        for corners in (rotated_corners, static_corners):
            # Get the edge between consecutive corners
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            edge = (x2 - x1, y2 - y1)
            # Find perpendicular axis (for SAT)
            axis = (-edge[1], edge[0])
            # Normalize axis
            length = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
            axis = (axis[0] / length, axis[1] / length)
            axes.append(axis)

    # Test projections on each axis
    for axis in axes:
        min_a, max_a = project_polygon(rotated_corners, axis)
        min_b, max_b = project_polygon(static_corners, axis)
        if not overlap(min_a, max_a, min_b, max_b):
            return False  # No collision on this axis

    return True  # All projections overlap, so there's a collision
