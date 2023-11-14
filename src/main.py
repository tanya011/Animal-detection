from frames import get_frames, get_current_frame
import os


# Remove old data from `unexpected` directory
# for file in os.listdir('../img/unexpected'):
#     file_name = os.path.join('..img/unexpected', file)
#     os.remove(file_name)

# video_path = 'https://youtu.be/EBer-aLmzM8'  # youtube live stream with penguins
# animal_type = 'bird'  # type of animals on the live stream. The value is equal to some from model's labels

# get_frames(video_path, animal_type)


get_current_frame('bird')
