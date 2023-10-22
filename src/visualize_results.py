import os
import cv2
from model import model
from datetime import datetime


def print_results(results):
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )
    print()


def visualize_results(image_bytes, image_index, results, animal_type):
    result = image_bytes
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        # Highlight the detected object in the `result` image
        result = highlight_object(result, box)

        # Check if something interesting happened
        object_type = model.config.id2label[label.item()]
        if object_type != animal_type:
            unexpected_result = highlight_object(image_bytes, box)
            date = datetime.now().strftime('%y-%m-%d:%H:%M:%S')
            write_into_jpg_file('unexpected', unexpected_result, f'{object_type}-{date}')

    # Write result into a file
    write_into_jpg_file('output', result, f'output_{image_index:03d}')


def write_into_jpg_file(dir_name, image_bytes, image_name):
    os.makedirs(dir_name, exist_ok=True)  # Make sure the directory exists
    file_name = os.path.join(dir_name, f'{image_name}.jpg')
    cv2.imwrite(file_name, image_bytes)


def highlight_object(image_bytes, box):
    result = image_bytes
    x1, y1, x2, y2 = [int(coord) for coord in box]
    cv2.rectangle(result, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)
    return result
