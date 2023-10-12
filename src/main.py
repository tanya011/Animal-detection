from frames import get_frames
import os


video_path = 'video.mp4'  # video stored locally
# video_path = 'https://www.youtube.com/watch?v=SmFK04m9VTM'  # youtube video
# video_path = 'https://youtu.be/EBer-aLmzM8'  # youtube live stream
get_frames(video_path)

files_amount = sum(1 for _ in os.listdir('frames'))
print(f'{files_amount} files were created.')
