from vidgear.gears import CamGear
from visualize_results import visualize_results, print_results
from model import detect_animal


def get_frames(video_path, animal_type):
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
        print_results(results)
        visualize_results(frame, counter, results, animal_type)

        # Used to avoid running out of memory when a live stream is the source.
        if counter > 10:
            break

    # Close the source
    src_video.stop()
