from frames import get_frames
import os


video_path = 'https://youtu.be/EBer-aLmzM8'  # youtube live stream with penguins
animal_type = 'bird'  # type of animals on the live stream. The value is equal to some from model's labels

# video_path = 'https://www.youtube.com/watch?v=pgFwPGZQ5b0'  # youtube live stream with bear
# animal_type = 'bear'

# Remove old data from `unexpected` directory
for file in os.listdir('unexpected'):
    file_name = os.path.join('unexpected', file)
    os.remove(file_name)

get_frames(video_path, animal_type)
