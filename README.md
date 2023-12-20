# Animal-detection

### Libraries / Technologies

- ML:
  [facebook/detr-resnet-50](https://huggingface.co/facebook/detr-resnet-50) - End-to-End Object Detection with Transformers

- Backend:
  - `os` - for manipulating with images
  - `cv2` - highlighting an object on the image
  - `vidgear` - interaction with YouTube live streams

- Multiprocessing:
  - multiprocessing - for creating daemon processes
  - threading - simple thread safety 

### Functionality

Currently, animals available for monitoring are pernguins and pandas. 

Commands supported by the bot:
- `/add` & `/remove` - create and modify a list of animals that the user would like to monitor
- `/animals` - see the current list of animals
- '/now' - monitor animals in real time. The user chooses which animal they would like to see at the moment and receives a corresponding photo with highlighted animals.

Moreover, the user may get a notification if something unexpected is detected. For example, a message is sent when a person enters the pengiuns' environment. This part of functionality is implemented by executing some background processes. 


### Project structure
```
src
├── bot
│   ├── animals.py           # Responsible for storing YouTube streams as `CamGear` instances
│   ├── bot.py               # Stores logic and functionality for a Telegram bot           
│   ├── daemon_processes.py  # Manages processes which are executed in the background
│   └── sticker.webp
├── img                # Temprarily created images are stored here
├── model.py           # Responsible for detecting objects on an image
├── process_image.py   # Responsible for manipulating with stream frames
├── process_stream.py  # Responsible for manipulating with streams
└── static
    ├── sources.py           # Stores links to YouTube streams
    └── word_declensions.py  # Declensions of russian words
```