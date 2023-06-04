import numpy as np
import math


def transform_to_screen_coordinates(object_positions, camera_position, camera_orientation, fov, screen_width,
                                    screen_height):
    # Convert fov to radians
    fov_rad = math.radians(fov)

    # results list (distance, (x, y))
    results = []

    for obj in object_positions:

        # Get the position of the object relative to the camera
        relative_position = np.subtract(obj, camera_position)

        # Calculate the rotation matrix for the camera's orientation
        pitch, yaw, roll = [math.radians(i) for i in camera_orientation]
        rotation_matrix = np.array([
            [math.cos(yaw) * math.cos(pitch),
             math.cos(yaw) * math.sin(pitch) * math.sin(roll) - math.sin(yaw) * math.cos(roll),
             math.cos(yaw) * math.sin(pitch) * math.cos(roll) + math.sin(yaw) * math.sin(roll)],
            [math.sin(yaw) * math.cos(pitch),
             math.sin(yaw) * math.sin(pitch) * math.sin(roll) + math.cos(yaw) * math.cos(roll),
             math.sin(yaw) * math.sin(pitch) * math.cos(roll) - math.cos(yaw) * math.sin(roll)],
            [-math.sin(pitch), math.cos(pitch) * math.sin(roll), math.cos(pitch) * math.cos(roll)]
        ])

        # Rotate the object into camera space
        rotated_position = np.matmul(rotation_matrix, relative_position)

        # Calculate the projection of the object onto the camera's screen
        projected_position = rotated_position / rotated_position[2]
        projected_x = ((projected_position[0] / math.tan(fov_rad / 2)) + 1) * screen_width / 2
        projected_y = ((projected_position[1] / math.tan(fov_rad / 2)) + 1) * screen_height / 2

        # If the object is outside the screen's dimensions, ignore it
        if projected_x < 0 or projected_x > screen_width or projected_y < 0 or projected_y > screen_height:
            continue

        # Calculate the distance to the object
        distance = math.sqrt(sum((relative_position ** 2)))

        # Add the result to the list
        results.append((distance, (projected_x, projected_y)))

    return results
