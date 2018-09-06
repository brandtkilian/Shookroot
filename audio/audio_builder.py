from loader import Loader
import random
import os, glob
import numpy as np
from song import Song


def simple_test_with_chords():
    l = Loader("/media/pocket/HDD/SoundsPacks/Guitar/CDrop/Processed")

    chords = [[2,0,2,2,2,0], [2,3,2,0,1,0], [5,2,0,0,3,3], [2,2,2,1,0,0], [3,3,3,2,1,1], [2,2,2,0,0,0],
              [2,0,0,2,3,2]]

    #chords = []
    #for i in range(12):
    #    chords.append([i, i, i, -1, -1, -1])


    chords_song = None
    for _ in range(150):
        chord_length = random.randint(400, 1200)
        c = random.choice(chords)
        pos = 0
        current_chord = None
        for i, s in enumerate(c):
            if s > -1:
                if current_chord is None:
                    current_chord = l[i][s][:chord_length]
                else:
                    current_chord = current_chord.overlay(l[i].values()[s][:chord_length], position=pos)
                pos += random.randint(0,20)
        if chords_song is None:
            chords_song = current_chord
        else:
            chords_song = chords_song.append(current_chord)

        chords_song = chords_song.fade_out(100)

    with open("out.wav", "wb") as f:
        chords_song.export(f, format="wav")


def create_audio_from_file(song_file, output_dir, samples):

    if not os.path.exists(song_file):
        print("Song file not found... exiting...")
        return

    print("Creating audio wave for", song_file)
    song_sequence = np.load(song_file)
    pos = 100
    tot_duration = sum(x[6] for x in song_sequence) + pos
    print("duration of the song", tot_duration, "ms")
    song = Song(pos)
    for i, notes in enumerate(song_sequence):
        duration = notes[6]
        if sum(notes[:6]) == -6:
            song.add_silence(duration)
        else:
            for i in range(6):
                note = notes[5-i]
                if note > -1:
                    sample = samples[i][note]
                    song.add(sample, duration, pos)
        pos += duration

        if i % 10 == 0:
            print("{}/{}".format(pos, tot_duration))

        song.end_beat()

    output_file = os.path.join(output_dir, ".".join(["".join(os.path.split(song_file)[1].split('.')[:-1]), "wav"]))
    song.save(output_file)


if __name__ == '__main__':
    root = "../samples/numpy/"
    samples_folder = "./soundspacks/guitar/cdrop/processed"
    samples = Loader(samples_folder)

    for path in glob.glob(os.path.join(root, "*.npy")):
        try:
            create_audio_from_file(path, "../output/", samples)
        except KeyError as e:
            print("Error in file %s. Requested key %s" % (path, e.message))
