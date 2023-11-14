from vidgear.gears import CamGear
from process_image import highlight_all_objects, print_detected_objects_info, check_something_unexpected
from model import detect_animal
import random
from sources import video_sources


# A dictionary where the key is the type of animal available in the telegram bot
# and the value is the path to a YouTube livestream.
# video_sources = {
#     'bird': 'https://youtu.be/EBer-aLmzM8',
#     'bear': 'https://www.youtube.com/watch?v=pgFwPGZQ5b0'
# }


def get_frames(video_stream, animal_type):
    """
    Process the frames which are extracted from the video source.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.
        animal_type: Type of animals which are expected to be seen on the video.
    """
    if video_stream is None:
        raise Exception("No stream source provided.")
    if animal_type is None:
        raise Exception("Animal type should not be None.")

    # Get frames from the source
    counter = 0
    while True:
        frame = video_stream.read()
        if frame is None:
            break  # End of video

        # Process the frame
        counter += 1
        results = detect_animal(frame)
        print_detected_objects_info(results)
        check_something_unexpected(frame, results, animal_type)


def get_current_frame(video_stream):
    """
    Extracts one frame from the livestream to show what is happening now.
    Objects detected in the frame are highlighted, and the result is saved in a `jpg` format in the `output` directory.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.

    Returns:
        file_name: Name of the jpg file with the resulting image.
    """
    if video_stream is None:
        raise Exception("No stream source provided.")

    # Get the current frame
    frame = video_stream.read()

    # Process the frame
    detected_objects = detect_animal(frame)
    file_name = highlight_all_objects(frame, detected_objects)

    return file_name


def start_camgear_stream(source_path):
    """
    Opens the video source provided with the source path.

    Args:
        source_path: A string representing the path to a YouTube live stream.

    Returns:
        An instance of `CamGear` with an opened source.
    """
    video_stream = CamGear(source=source_path, stream_mode=True)
    video_stream.start()  # Open the source
    return video_stream


def stop_camgear_stream(video_stream):
    """
    Closes the provided video source.

    Args:
        video_stream: An instance of `CamGear` -- an opened stream source.
    """
    if video_stream is None:
        raise Exception("No video source provided.")
    video_stream.stop()  # Close the source
