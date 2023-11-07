from vidgear.gears import CamGear
from process_image import visualize_results, print_detected_objects_info, check_something_unexpected
from model import detect_animal


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
        # visualize_results(frame, counter, results)
        check_something_unexpected(frame, results, animal_type)

    # Close the source
    src_video.stop()
