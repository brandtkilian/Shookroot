from __future__ import print_function

import os
import fnmatch
import numpy as np
import guitarpro
import math
from cleaner import Cleaner
from dataset_loader import load_dataset, to_t7_array

N_KEYS = 24.


def main(source, output):
    print("Filtering...\n")
    exts = '*.gp[345]'
    length = 0
    tracks = 0
    for dirpath, dirs, files in os.walk(source):
        for filen in fnmatch.filter(files, exts):
            file_path = os.path.join(dirpath, filen)
            try:
                tab = guitarpro.parse(file_path)
            except Exception as exc:
                print("###This is not a supported Guitar Pro file:",
                      file_path, ":", exc)
            else:
                guitars_tracks = file_guitar_tracks(tab)
                if len(guitars_tracks) > 0:
                    n_tracks = len(guitars_tracks)
                    print(file_path, "does contain {} guitar track(s)".format(n_tracks))
                    if n_tracks > 2:
                        print("Keeping only the first track (usually rythmic and lead guitars)")
                        guitars_tracks = guitars_tracks[:2]

                    for t, i in enumerate(guitars_tracks):
                        tracks += 1
                        track_valid, vectorized = create_vectorized_track(tab.tracks[t])
                        if not track_valid:
                            continue
                        vectorized = Cleaner.clean_void_sequences(vectorized)
                        length += vectorized.shape[0]
                        _, subdir = os.path.split(dirpath)
                        splited_name = filen.split('.')
                        filename = '.'.join(splited_name[:-1])
                        new_name = "{}_track{}".format(filename, i)
                        save(vectorized, os.path.join(output, subdir), new_name)
    dataset = load_dataset(output)
    final_file_path = os.path.join(output, "dataset.t7")
    to_t7_array(dataset, final_file_path)
    print("\nDone! %d guitars tracks vectorized for a total of %d vectors of guitar keyboard state. Saved %s" % (tracks, length, final_file_path))


def file_guitar_tracks(tab):
    guitars = []
    for i, track in enumerate(tab.tracks):
        if not track.isPercussionTrack and not track.isBanjoTrack:
            if len(track.strings) == 6:
                guitars.append(i)

    return guitars


def create_vectorized_track(track):
    def played_notes(track):
        for measure in track.measures:
            num = measure.header.timeSignature.numerator
            tempo = measure.tempo.value
            beat_duration = 60. / tempo
            for voice in measure.voices:
                for beat in voice.beats:
                    notes_duration = (1./beat.duration.value) * beat_duration * num
                    factor = 1
                    if beat.duration.isDotted:
                        factor = 1.5
                    if beat.duration.tuplet.enters > 1:
                        factor = float(beat.duration.tuplet.times) / beat.duration.tuplet.enters
                    notes_duration *= factor
                    notes_duration = int(math.ceil(1000 * notes_duration))  # convert to milisecond so everything can be store as int
                    yield beat.notes, notes_duration
                    if measure.header.isRepeatOpen:
                        for _ in range(measure.header.repeatClose):
                            yield beat.notes, notes_duration

    def generate_new_keyboard_frame(n):
        return [-1 for _ in range(n)]

    song = []
    for notes, duration in played_notes(track):
        keyboard = generate_new_keyboard_frame(7)
        keyboard[6] = duration
        for note in notes:
            keyboard[note.string - 1] = note.value
        if max(keyboard[:6]) > N_KEYS:
            print("Error key greater than 24, skipping track")
            return False, None
        song.append(keyboard)

    return True, np.array(song, np.int32)


# TODO find a way to normalize / center datas before training
# and reshift/rescale afterfards


def save(array, directory, name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    np.save(os.path.join(directory, name), array)


if __name__ == '__main__':
    import argparse
    description = ("Convert GuitarPro tabs files guitar tracks into a sequence of notes vectors. Save output files as serialized numpy arrays")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('source', help='path to the source tabs folder')
    parser.add_argument('output', help='path to the output folder to store processed files')
    args = parser.parse_args()
    main(args.source, args.output)