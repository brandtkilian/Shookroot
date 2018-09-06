# Shookroot

Project for fun which goal is to generate music with the popular [Karpathy's char-rnn](https://github.com/karpathy/char-rnn)

## requirements

* pydub==0.9.0
* PyGuitarPro==0.4
* lutorpy==1.3.7
* ntpath==1534770254.427198
* scikit_learn==0.19.2

## How it works

This repository contains tools to parse Guitar Pro (from GP3 to GP5 files) and create numpy array containing vectors of length 7 (see processing/gp_files_to_vectors.py). Each vector contains the actual key played on the string and the 7th value is the duration in ms. Once the tabs turned into a list of vector the goal is to feed them into some recurent neural networks.

In addition there are tools to convert the vectors into text so it can directly be inputed in the char-rnn (processing/dataset_loader.py).

Once the LSTM give us some vectors (string format or not) the goal is to convert them back into a sequence of guitar keyboard states and duration (using processing/sample_loader.py) and turn the result into a wav song.

To turn the given vectors into a song I've build a module to concatenate string tones I've recorded on my guitar using the pydub library. Actually the samples I've recorded are all the 150 keys of my guitar (6 strings times 24 keys and open string) tuned in CDrop (I was trying to generate metal music initially).

See the audio/audio_builder.py to create .wav files from numpy array of guitar chords vectors.


## example

* run processing/gp_files_to_vectors.py to convert the Guitar Pro files into sequences of vector stored in a numpy array
* run dataset_loader (take a look on the different methods) to load the sequences, concatenate them and store them in a single file (dataset)
* train any recurent network
* generate samples from trained network
* convert samples back to initial sequence of vectors format
* convert the sequence into a wav file
* listen and profit


## results

Here are some of the results I've got

## How to make it better

* Train with more data
* Do not mix rythmic guitars tracks and solo guitars tracks together for training
* Train rythmic and solo guitar separately, train to generate rythmic from solo guitar track ?
* Play with models hyperparameters, I just tried a few training
* Actually I didn't manage to train an lstm using the sequence of vectors directly (with an updated version of char-rnn), I never managed to make it converge, the only thing that worked is to use a sequence of characters that are then OneHot-encoded into vectors. If someone manage to do it let me know.
* generate drum from guitar track or opposite.
* Write the args parser for all my scripts to make it easier to use :)

