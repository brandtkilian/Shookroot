from pydub import AudioSegment
import os


class Song:
    def __init__(self, init_silence=100):
        self.seq = AudioSegment.silent(duration=init_silence) # initial immuable audio segment
        self.should_append = True

    def append(self, note, duration):
        self.seq = self.seq.append(note[:duration], crossfade=0)

    def overlay(self, note, duration, position):
        self.seq = self.seq.overlay(note[:duration], position)

    def fade_in(self, duration):
        self.seq = self.seq.fade_in(duration)

    def fade_out(self, duration):
        self.seq = self.seq.fade_out(duration)

    def add(self, note, duration, position=0):
        if self.should_append:
            self.should_append = False
            self.append(note, duration)
        else:
            self.overlay(note, duration, position)

    def add_silence(self, duration):
        self.should_append = True
        self.seq = self.seq.append(AudioSegment.silent(duration=duration), crossfade=0)

    def end_beat(self):

        self.should_append = True

    def save(self, file):
        dirname = os.path.dirname(file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(file, "wb") as f:
            self.seq.export(f, format="wav")