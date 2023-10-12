import cv2
import os
from vidgear.gears import CamGear


def get_frames(video_path):
    # Check if the source is a live stream or a video of `.mp4` format
    stream_mode = True
    if video_path[-4::] == '.mp4':
        stream_mode = False

    # Open the source
    src_video = CamGear(source=video_path, stream_mode=stream_mode)
    src_video.start()

    # Directory where the frames are stored
    frames_dir = 'frames'
    os.makedirs(frames_dir, exist_ok=True)

    # Remove old data from `frames_dir` directory
    for file in os.listdir(frames_dir):
        file_name = os.path.join(frames_dir, file)
        os.remove(file_name)

    # Get frames from the source
    frame_number = 0
    while True:
        frame = src_video.read()
        if frame is None:
            break  # End of video
        frame_name = os.path.join(frames_dir, f'frame_{frame_number:03d}.jpg')
        cv2.imwrite(frame_name, frame)
        frame_number += 1

        # Used to avoid running out of memory when a live stream is the source.
        if frame_number > 500:
            break

    # Close the source
    src_video.stop()
