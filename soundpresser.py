#! /usr/bin/env python3
#
# Copyright (C) Viktor Sjölind 2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse

from aubio import pitch, source
from math import log
from pykeyboard import PyKeyboard

import json
import os

KEYBOARD = PyKeyboard()

def applyKeyTap(freq, freq_map, dry_run=False):
    """
    Trigger keyboard taps for any frequencies that have a match in the frequency map.
    """
    if freq in freq_map:
        key = freq_map[freq]
        if not dry_run:
            KEYBOARD.tap_key(key)
        else:
            print("Tapping key '{}'".format(key))

def applyGranularityFilter(freq, granularity):
    """
    Apply a granularity filter to a frequency. In order for granularity to make sense, the values needs to grow
    linearly. Therefore, log(freq) is used rather than raw freq.

    This function is not defined for frequencies equal to or less than zero. In these cases None will be returned.
    """
    if freq <= 0:
        return None

    freq = int(log(freq) * 1000)
    filtered_freq = freq - (freq % granularity)

    return filtered_freq


def analyzeSource(soundSource):
    """
    Analyze the source and yield the frequencies found.
    """
    p = pitch()

    while True:
        samples, samples_read = soundSource()
        yield p(samples)[0]

        # Break when reading less than 512 samples
        if samples_read < 512: break


def applyGranularityFilterToMap(freq_map, granularity):
    """
    Apply the granularity filter to all keys
    """

    filtered_freq_map = {}
    for key, value in freq_map.items():
        key = applyGranularityFilter(key, granularity)
        filtered_freq_map[key] = value
    return filtered_freq_map


def processFrequencies(frequencies, freq_map, granularity, dry_run):
    """
    Process frequencies by matching them against the frequency map
    """

    for freq in frequencies:
        freq = applyGranularityFilter(freq, granularity)
        applyKeyTap(freq, freq_map, dry_run=dry_run)


def readFrequencyMap(frequency_map_path):
    """
    Read frequency map from given path and convert all keys to floats.
    """

    # Read the frequency map json file
    json_str = ""
    with open(frequency_map_path, "r") as f:
        for json_line in f.readlines():
            json_str += json_line

    freq_map_raw = dict(json.loads(json_str))

    # Make all keys floats
    freq_map = {}
    for key, value in freq_map_raw.items():
        freq_map[float(key)] = value

    return freq_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser("SoundPresser is a tool for converting"
                                     " frequencies found in sound to keyboard presses")
    parser.add_argument("source", help="The source to get the audio from. Example: /home/foo/bar.wav")
    parser.add_argument("frequency_map", type=str, help="The path to a json file containing mapping of"
                                                        " frequencies to keys.")
    parser.add_argument("--granularity", default=56, type=int, help="How close log(freq) has to be to"
                                                                    " log(freq of perfect note) in thousands.")
    parser.add_argument("--dry-run", action="store_true", help="Print name of keys to be pressed to stdout"
                                                               " instead of generating key presses.")
    args = parser.parse_args()

    # Sanity check the arguments
    if not os.path.exists(args.source):
        print("Could not specified source '{}' on the system!".format(args.source))
        exit(1)

    # Setup the sound source and start calculate frequencies
    soundSource = source(args.source)
    frequencies = analyzeSource(soundSource)

    # Read and prepare frequency map
    freq_map = readFrequencyMap(args.frequency_map)
    freq_map = applyGranularityFilterToMap(freq_map, args.granularity)

    # Process the frequencies found in the sound. Since analyzeSource returns a generator this can be done directly.
    processFrequencies(frequencies, freq_map, args.granularity, args.dry_run)