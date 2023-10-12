import cv2
import os


def get_frames(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise "Error: Video file '{video_path}' not found or could not be opened."

    # Directory where the frames are stored
    frames_dir = 'frames'
    os.makedirs(frames_dir, exist_ok=True)

    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            # End of video
            break

        frame_filename = os.path.join(frames_dir, f'frame_{frame_number:03d}.jpg')
        cv2.imwrite(frame_filename, frame)
        frame_number += 1

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
