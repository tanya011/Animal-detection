from process_stream import start_camgear_stream, stop_camgear_stream
from sources import video_sources


class Animals:
    def __init__(self):
        # Maps animal type to an opened live stream. Keys are the same as in the `video_sources` dictionary.
        # If no stream is opened, value is `None`
        self.opened_streams = {animal_type: None for animal_type in video_sources.keys()}

    def open_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        # Return if the stream is already opened
        if self.opened_streams[animal_type] is not None:
            return

        source_path = video_sources[animal_type]    # Get source path
        stream = start_camgear_stream(source_path)  # Open stream
        self.opened_streams[animal_type] = stream   # Update the corresponding field

    def close_stream(self, animal_type):
        # Check that the given animal type is valid
        if animal_type not in video_sources.keys():
            raise Exception(f"Animal of type '{animal_type}' is not considered by our bot.")

        stream = self.opened_streams[animal_type]
        if stream is not None:                       # Check that the stream is opened
            stop_camgear_stream(stream)              # Close stream
            self.opened_streams[animal_type] = None  # Update the corresponding field
