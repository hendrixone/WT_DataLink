# process the data received from the server.

def transform_to_screen_coordinates(object_position, camera_position, camera_target, fov, screen_width, screen_height):
    # Convert positions to vectors
    object_position = Vector3([object_position[0], object_position[1], object_position[2]])
    camera_position = Vector3([camera_position[0], camera_position[1], camera_position[2]])
    camera_target = Vector3([camera_target[0], camera_target[1], camera_target[2]])

    # Create a perspective projection matrix
    aspect_ratio = screen_width / screen_height
    projection_matrix = Matrix44.perspective_projection(fov, aspect_ratio, 0.1, 1000.0)

    # Create a look_at matrix to position and orient the camera
    view_matrix = Matrix44.look_at(camera_position, camera_target, Vector3([0.0, 1.0, 0.0]))

    # Combine transformations into one matrix
    transformation_matrix = np.matmul(projection_matrix, view_matrix)

    # Transform the object's position
    transformed_position = np.matmul(transformation_matrix, np.append(object_position, 1.0))

    # Perspective divide
    transformed_position /= transformed_position[3]

    # Convert from clip space to screen space
    screen_x = (transformed_position[0] * 0.5 + 0.5) * screen_width
    screen_y = (transformed_position[1] * -0.5 + 0.5) * screen_height

    return screen_x, screen_y