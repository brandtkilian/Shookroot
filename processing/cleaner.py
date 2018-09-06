import numpy as np


class Cleaner:

    @staticmethod
    def clean_void_sequences(song, strings=6, cut_after=5, remains=3):
        start_cuting = -1
        to_remove = []
        for i, beat in enumerate(song):
            if sum(beat[:strings]) == -strings:
                if start_cuting < 0:
                    start_cuting = i
            elif start_cuting > 0:
                if i - start_cuting >= cut_after:
                    to_remove.append([start_cuting, i - remains])
                start_cuting = -1

        for rm_range in reversed(to_remove):
            for i in range(rm_range[1], rm_range[0]):
                song = np.delete(song, i, 0)
            print("removed %d beats!" % (rm_range[1] - rm_range[0]))

        return song
