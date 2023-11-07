import os
import cv2
from model import model
from datetime import datetime


def print_detected_objects_info(results):
    """
    Prints information about objects detected in the image.

    Args:
        results: A list of dictionaries, each dictionary containing the scores, labels and boxes for an image in the batch as predicted by the model.
    """
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )
    print()


def visualize_results(image_bytes, image_index, results):
    """
    Highlights objects detected in the image. The resulting image with highlighted objects is created
    and saved in the `output` directory.

    Args:
        image_bytes: The image in bytes.
        image_index: An integer, used for generating a unique name for a jpg file.
        results: A list of dictionaries, each dictionary containing the scores, labels and boxes for an image in the batch as predicted by the model.
    """
    result = image_bytes
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        # Highlight the detected object in the `result` image
        result = highlight_object(result, box)
    # Write result into a file
    write_into_jpg_file('output', result, f'output_{image_index:03d}')


def check_something_unexpected(image_bytes, results, animal_type):
    """
    Checks if the type of the detected object is not as expected. If something unexpected is found, a jpg file
    with the highlighted object is created and saved in the `unexpected` directory.

    Args:
        image_bytes: The image in bytes.
        results: A list of dictionaries, each dictionary containing the scores, labels and boxes for an image in the batch as predicted by the model.
        animal_type: The expected type of objects.
    """
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        # Check if something interesting happened
        object_type = model.config.id2label[label.item()]
        if object_type != animal_type:
            result = highlight_object(image_bytes, box)
            date = datetime.now().strftime('%y-%m-%d:%H:%M:%S')
            write_into_jpg_file('unexpected', result, f'{object_type}-{date}')


def write_into_jpg_file(dir_name, image_bytes, image_name):
    """
    Creates a jpg file.
    :param dir_name: Name of the directory where the file should be saved.
    :param image_bytes: The image in bytes.
    :param image_name: Name used when creating a pjg file.
    """
    os.makedirs(dir_name, exist_ok=True)  # Make sure the directory exists
    file_name = os.path.join(dir_name, f'{image_name}.jpg')
    cv2.imwrite(file_name, image_bytes)


def highlight_object(image_bytes, box):
    """
    Highlights the object specified by coordinates.

    Args:
        image_bytes: The image in bytes.
        box: A tuple of two two-dimensional coordinates in the format (top_left_x, top_left_y, bottom_right_x, bottom_right_y).
    """
    result = image_bytes
    x1, y1, x2, y2 = [int(coord) for coord in box]
    cv2.rectangle(result, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)
    return result
