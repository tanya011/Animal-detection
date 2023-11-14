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


def get_frames(video_path, animal_type):
    """
    Process the frames which are extracted from the video source.

    Args:
        video_path: Path to the video source which can be a YouTube livestream of a YouTube video.
        animal_type: Type of animals which are expected to be seen on the video.
    """
    # Check if the source is a live stream or a video of `.mp4` format
    stream_mode = True
    if video_path[-4::] == '.mp4':
        stream_mode = False

    # Open the source
    src_video = CamGear(source=video_path, stream_mode=stream_mode)
    src_video.start()

    # Get frames from the source
    counter = 0
    while True:
        frame = src_video.read()
        if frame is None:
            break  # End of video

        # Process the frame
        counter += 1
        results = detect_animal(frame)
        print_detected_objects_info(results)
        check_something_unexpected(frame, results, animal_type)

    # Close the source
    src_video.stop()


def get_current_frame(video_stream):
    """
    Extracts one frame from the livestream to show what is happening now.
    Objects detected in the frame are highlighted, and the result is saved in a `jpg` format in the `output` directory.

    Args:
        video_stream: An opened stream source. The argument has the type `CamGear`.

    Returns:
        file_name: Name of the jpg file with the resulting image.
    """
    # Check that the specified animal type is available
    if animal_type not in video_sources.keys():
        raise Exception(f"No source found for the animal'{animal_type}'")

    # Get the current frame
    frame = video_stream.read()

    # Process the frame
    detected_objects = detect_animal(frame)
    file_name = highlight_all_objects(frame, detected_objects)

    return file_name


def open_frame():
    return None

def close_frame():
    i = 0
    # ...
