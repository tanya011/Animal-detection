from vidgear.gears import CamGear
from process_image import highlight_all_objects, check_something_unexpected
import random
from sources import video_sources


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

    frame = video_stream.read()               # Get the current frame
    file_name = highlight_all_objects(frame)  # Process the frame

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
