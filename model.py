from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import requests
import cv2
import numpy as np

processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

Animals = ['cat', 'dog', 'bear']


def detect_animal(image):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    return results


def print_results(results):
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )


def visualize_results(image, results):
    image_np = np.array(image)

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        if model.config.id2label[label.item()] not in Animals:
            continue

        box = [round(i, 2) for i in box.tolist()]

        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        box = [x1, y1, width, height]

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imwrite("output.jpg", image_np)


url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

results = detect_animal(image)
print_results(results)
visualize_results(image, results)
