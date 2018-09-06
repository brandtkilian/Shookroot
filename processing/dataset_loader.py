import numpy as np
import os
import fnmatch
import math
import random
import lutorpy
from sklearn import preprocessing
from sklearn.externals import joblib


N_KEYS = 24

def next_dataset_sample(source):
    exts = '*.npy'
    for dirpath, dirs, files in os.walk(source):
        for file in fnmatch.filter(files, exts):
            file_path = os.path.join(dirpath, file)
            yield np.load(file_path)


def load_dataset(source, samples_count=-1, flat=True, shuffle=True):
    samples_count = 10e10 if samples_count < 0 else samples_count
    cnt = 0
    dataset = []
    for sample in next_dataset_sample(source):
        cnt += 1
        dataset.append(sample)
        if cnt >= samples_count:
            break

    if shuffle:
        random.shuffle(dataset) # songs are shuffled not the sequences of notes of course (applied before flattening

    return flatten(dataset) if flat else dataset


def flatten(dataset):
    appended = dataset[0]
    width = appended.shape[1]

    for d in dataset[1:]:
        if d.shape[1] == width:
            appended = np.append(appended, d, axis=0)

    return appended.reshape((appended.shape[0], width))


def print_some_to_see(source, some, lines):
    samples = load_dataset(source, some, flat=False)
    for s in samples:
        song = [[] for _ in range(6)]
        for sequence in s[:lines]:
            nop = '-' if max(sequence) < 10 else '--'
            frame = [str(n) if n > 9 else nop if n < 0 else "%d-" % n for n in sequence[:6]]
            for j, n in enumerate(frame):
                song[j].append(str(n))

        for line in song:
            print('-'.join(line))
        print("\n\n\n")


def split_dataset(dataset, train_split=0.8, valid_split=0.1, output_dir="../dataset/processed/split"):
    assert sum([train_split, valid_split]) > 0 and sum([train_split, valid_split]) < 1

    dataset_size = dataset.shape[0]

    nb_train = int(math.ceil(train_split * dataset_size))
    nb_val = int(math.ceil(valid_split * dataset_size))
    nb_test = dataset_size - nb_val - nb_train

    print("Dataset spliting training samples {}, validation samples {}, testing samples {}".format(nb_train, nb_val, nb_test))

    train_part = dataset[:nb_train]
    val_part = dataset[nb_train:nb_train+nb_val]
    test_part = dataset[nb_train+nb_val:nb_train+nb_val+nb_test]

    arrays = [train_part, val_part, test_part]
    filenames = ["train_{}.t7".format(nb_train), "val_{}.t7".format(nb_val), "test_{}.t7".format(nb_test)]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for a, f in zip(arrays, filenames):
        to_t7_array(os.path.join(output_dir, f), a)


def to_t7_array(dataset, filepath):
    x = torch.fromNumpyArray(dataset)
    torch.save(filepath, x)


def to_text_file(dataset, output_file):
    dirname = os.path.dirname(output_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    text_boards = []
    for keyboard in dataset:
        keyboard = keyboard.tolist()
        text_boards.append("".join(["{}{}".format(chr(65+i), k) for i, k in enumerate(keyboard[:6]) if k >= 0] + ["t{}".format(keyboard[6])]))

    with open(output_file, "w") as f:
        f.write(".".join(text_boards))


def to_text_file_same_length(dataset, output_file):
    dirname = os.path.dirname(output_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    text_boards = []
    for keyboard in dataset:
        keyboard = keyboard.tolist()
        keyb_string = ""
        for k in keyboard[:-1]:
            keyb_string += chr(98 + k)

        t = keyboard[-1]
        len_t = len(str(t))
        if len_t <= 5:
            zeros = 5 - len_t
            str_t = "".join(['0' for _ in range(zeros)] + [str(t)])
        else:
            str_t = "10000"
        keyb_string += str_t
        text_boards.append(keyb_string)

    with open(output_file, "w") as f:
        f.write(".".join(text_boards))




def scale(x, output_scaler):
    #scaler = preprocessing.StandardScaler().fit(x)
    scaler = preprocessing.MinMaxScaler().fit(x)
    if not os.path.exists(os.path.dirname(output_scaler)):
        os.makedirs(os.path.dirname(output_scaler))
    joblib.dump(scaler, output_scaler)
    return scaler.transform(x)


if __name__ == '__main__':
    #print_some_to_see("../dataset/processed", 10, 100)
    dataset = load_dataset("../dataset/processed")
    to_text_file_same_length(dataset, "../dataset/processed/text/input.txt")
    #scaled = scale(dataset, output_scaler="../dataset/params/scaler.save")
    #to_t7_array(scaled, "../dataset/processed/dataset.t7")
