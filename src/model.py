from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image

processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")


def detect_animal(image_bytes):
    """
    Detects and identifies animals in an image.

    Args:
        image_bytes: A byte array containing the image to be processed.

    Returns:
        results: A list of dictionaries, each dictionary containing the scores, labels and boxes for an image
        in the batch as predicted by the model.
    """
    image = Image.fromarray(image_bytes)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    results["obj_types"] = [model.config.id2label[label.item()] for label in results["labels"]]

    return results
