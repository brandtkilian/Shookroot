import numpy as np
from sklearn.externals import joblib
import os
import glob
from utils.filenames import path_leaf
import re


def from_t7_file(file_path):
    x = torch.load(file_path)
    return x.asNumpyArray()


def rescale(x, scaler="../dataset/params/scaler.save"):
    scaler = joblib.load(scaler)
    x_prime = scaler.inverse_transform(x)

    return np.rint(x_prime).astype(np.int32)


def generate_new_keyboard_frame(n):
    return [-1 for _ in range(n)]


def from_text_file_same_length(file_path):
    numbers = re.compile("[^0-9]")
    with open(file_path, 'r') as f:
        content = f.read()
        key_boards = []
        text_boards = content.split('.')
        for text_board in text_boards:
            if len(text_board) != 11:
                continue
            frame = generate_new_keyboard_frame(7)
            for i, c in enumerate(text_board[:-5]):
                frame[i] = ord(c) - 98

            frame[-1] = int(numbers.sub("", text_board[-5:]))
            key_boards.append(frame)
    return np.array(key_boards, np.int32)


def from_text_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        key_boards = []
        text_boards = content.split('.')
        for text_board in text_boards:
            frame = generate_new_keyboard_frame(7)
            number = ''
            idx = 0
            for c in text_board:
                if c in "ABCDEFt":
                    if len(number) > 0:
                        frame[idx] = int(number)
                    idx = 6 if c == 't' else (ord(c) - 65)
                    number = ''
                else:
                    number += c
            if len(number) > 0:
                inum = int(number)
                if (idx < 6 and inum <= 24) or idx == 6:
                    frame[idx] = inum
            key_boards.append(frame)

        return np.array(key_boards, np.int32)


def convert_text_samples(input_folder, output_folder, same_length=False):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for f in glob.glob(os.path.join(input_folder, "*.txt")):
        if same_length:
            x = from_text_file_same_length(f)
        else:
            x = from_text_file(f)
        file_name = ".".join(path_leaf(f).split('.')[:-1] + ["npy"])
        np.save(os.path.join(output_folder, file_name), x)


if __name__ == '__main__':
    convert_text_samples("../samples/text", "../samples/numpy", True)