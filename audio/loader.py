from pydub import AudioSegment
import glob
import os


class Loader():

    def __init__(self, root_path, extension="wav"):
        self.root_path = root_path
        self.extension = extension
        self.files = dict()
        self.load_files()

    def load_files(self):
        load_count = 0
        for file in glob.glob(os.path.join(self.root_path, "**/*.{}".format(self.extension))):
            head, tone = os.path.split(file)
            head, string = os.path.split(head)
            string_number = int(string)
            key_number = int(tone.split('.')[0]) - 1
            wav_file = AudioSegment.from_file(file, self.extension)
            string = self.files.get(string_number, {})
            string[key_number] = wav_file
            self.files[string_number] = string
            print("loaded key {} for string {}".format(key_number, string_number))
            load_count += 1

        print("Loading ended, loaded {} sound files".format(load_count))

    def __len__(self):
        return  len(self.files)

    def __getitem__(self, key):
        return self.files[key]

    def __iter__(self):
        for v in self.files.values():
            yield v
