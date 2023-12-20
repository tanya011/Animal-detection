import os
import cv2
from datetime import datetime
from model import detect_animal


def highlight_all_objects(image_bytes):
    """
    Highlights objects detected in the image. The resulting image with highlighted objects is created
    and saved in the `output` directory.

    Args:
        image_bytes: The image in bytes.

    Returns:
        file_name: Name of the jpg file where the result is saved.
    """
    # Find objects on the image
    detected_objects = detect_animal(image_bytes)
    print_detected_objects_info(detected_objects)

    # Process detected objects
    result = image_bytes
    for score, box in zip(detected_objects["scores"], detected_objects["boxes"]):
        # Highlight the detected object in the `result` image
        result = highlight_object(result, box, is_unexpected=False)

    # Write result into a jpg file
    date = datetime.now().strftime('%y-%m-%d:%H:%M:%S')
    file_name = write_into_jpg_file('../img', result, f'output_{date}')

    return file_name


def highlight_object(image_bytes, box, is_unexpected):
    """
    Highlights the object specified by coordinates.

    Args:
        image_bytes: The image in bytes.
        box: A tuple of two two-dimensional coordinates in the format (top_left_x, top_left_y, bottom_right_x, bottom_right_y).
        is_unexpected: A boolean flag showing whether the detected object is an unexpected object.
    """
    result = image_bytes
    x1, y1, x2, y2 = [int(coord) for coord in box]

    # If the detected object is an unexpected object, it is highlighted with red. Otherwise, green is used.
    color = (0, 255, 0)
    if is_unexpected:
        color = (0, 0, 255)

    # Highlight the object
    cv2.rectangle(result, (x1, y1), (x2, y2), color=color, thickness=2)
    return result


def check_something_unexpected(image_bytes, animal_type):
    """
    Checks if the type of the detected object is not as expected. If something unexpected is found, a jpg file
    with the highlighted object is created and saved in the `unexpected` directory.

    Args:
        image_bytes: The image in bytes.
        animal_type: The expected type of objects.

        Returns:
            file_name: Name of the jpg file where the unexpected objects are highlighted. Its value is the date and time when the objects were detected.
            unexpected_objects: A list describing what types the unexpected objects have.
    """
    # Find objects on the image
    detected_objects = detect_animal(image_bytes)

    # Process detected objects
    result = image_bytes
    unexpected_objects = list()

    for score, object_type, box in zip(detected_objects["scores"], detected_objects["obj_types"], detected_objects["boxes"]):
        # Check if something unexpected was found
        if object_type != animal_type:
            result = highlight_object(result, box, is_unexpected=True)  # Highlight the object in the resulting image
            unexpected_objects.append(object_type)                      # Save the type of the object

    print_unexpected_objects_info(animal_type, unexpected_objects)

    # Save result into a jpg file if any unexpected objects were detected
    file_name = None
    if len(unexpected_objects) > 0:
        date = datetime.now().strftime('%y-%m-%d:%H:%M:%S')
        file_name = write_into_jpg_file('../img', result, f'unexpected_{date}')

    return file_name, unexpected_objects


def write_into_jpg_file(dir_name, image_bytes, image_name):
    """
    Creates a jpg file.

    Args:
        dir_name: Name of the directory where the file should be saved.
        image_bytes: The image in bytes.
        image_name: Name used when creating a pjg file.

    Returns:
        file_name: Name of the jpg file where the result is saved.
    """
    os.makedirs(dir_name, exist_ok=True)  # Make sure the directory exists
    file_name = os.path.join(dir_name, f'{image_name}.jpg')
    cv2.imwrite(file_name, image_bytes)
    return file_name


def print_detected_objects_info(objects):
    """
    Prints information about objects detected in the image.

    Args:
        objects: A list of dictionaries, each dictionary containing the `scores`, `obj_types` and `boxes` keys for an image in the batch as predicted by the model.
    """
    for score, object_type, box in zip(objects["scores"], objects["obj_types"], objects["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        print(f"Detected {object_type} with confidence {round(score.item(), 3)} at location {box}")
    print()


def print_unexpected_objects_info(animal_type, unexpected_objects):
    print(f"'{animal_type}' [{datetime.now().strftime('%y-%m-%d:%H:%M:%S')}]:")
    if len(unexpected_objects) > 0:
        print(f"Detected {', '.join(map(repr, unexpected_objects))}.")
    else:
        print(f"Nothing unexpected is detected.")
    print()
