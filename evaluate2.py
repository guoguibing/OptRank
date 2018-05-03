#!/usr/bin/env python3
#
# Copyright (c) 2017-present, All rights reserved.
# Written by Julien Tissier <30314448+tca19@users.noreply.github.com>
#
# This file is part of Dict2vec.
#
# Dict2vec is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dict2vec is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License at the root of this repository for
# more details.
#
# You should have received a copy of the GNU General Public License
# along with Dict2vec.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import math
import argparse
import numpy as np
import scipy.stats as st 
import codecs
import struct

FILE_DIR = "data/eval/"
results = dict()
oov     = dict()


def tanimotoSim(v1, v2):
    """Return the Tanimoto similarity between v1 and v2 (numpy arrays)"""
    dotProd = np.dot(v1, v2)
    return dotProd / (np.linalg.norm(v1)**2 + np.linalg.norm(v2)**2 - dotProd)


def cosineSim(v1, v2):
    """Return the cosine similarity between v1 and v2 (numpy arrays)"""
    dotProd = np.dot(v1, v2)
    return dotProd / (np.linalg.norm(v1) * np.linalg.norm(v2))


def init_results():
    """Read the filename for each file in the evaluation directory"""
    for filename in os.listdir(FILE_DIR):
        if not filename in results:
            results[filename] = []


def evaluate(filename):
    """Compute Spearman rank coefficient for each evaluation file"""

    # step 0 : read the first line to get the number of words and the dimension
    nb_line = 0
    nb_dims = 0
    with open(filename,"rb") as f:
        nb_line = ''
        nb_dims = ''
        while(1):
            li = f.read(1).decode()
            if(li == ' '):
                break
            else:
                nb_line += li
        nb_line = int(nb_line)
        nb_dims = int(f.read(3).decode())
    mat = np.zeros((nb_line, nb_dims))
    wordToNum = {}
    count = 0

    with open(filename,"rb") as f:
        f.read(10) # skip first line because it does not contains a vector
        for i in range(nb_line):
            line = []
            word_name = ''
            while(1):
                try:
                    sn3 = f.read(1)
                    sn3 = sn3.decode('utf-8')
                    if (sn3 == ' '):
                        break
                    else:
                        word_name += sn3
                except Exception as ex:
                    word_name = 'unknown'
            line.append(word_name)
            for j in range(nb_dims):
                sn4 = f.read(4)
                (word_value,) = struct.unpack('f',sn4)
                line.append(word_value)
            f.read(1)
            word, vals = line[0], list(map(float, line[1:]))
            mat[count] = np.array(vals)
            wordToNum[word] = count
            count += 1

    # step 1 : iterate over each evaluation data file and compute spearman
    for filename in results:
        found, not_found = 0, 0
        with open(os.path.join(FILE_DIR, filename),"r") as f:
            file_similarity = []
            embedding_similarity = []
            for line in f:
                w1, w2, val = line.split()
                w1, w2, val = w1.lower(), w2.lower(), float(val)
                if not w1 in wordToNum or not w2 in wordToNum:
                    not_found += 1
                else:
                    found += 1
                    v1, v2 = mat[wordToNum[w1]], mat[wordToNum[w2]]
                    cosine = cosineSim(v1, v2)
                    file_similarity.append(val)
                    embedding_similarity.append(cosine)

                    #tanimoto = tanimotoSim(v1, v2)
                    #file_similarity.append(val)
                    #embedding_similarity.append(tanimoto)

            rho, p_val = st.spearmanr(file_similarity, embedding_similarity)
            results[filename].append(rho)
            oov[filename] = (found, found+not_found)


def stats():
    """Compute statistics on results"""
    title = "{}| {}| {}| {}| {}| {}".format("Filename".ljust(16),
                              "AVG".ljust(5), "MIN".ljust(5), "MAX".ljust(5),
                              "STD".ljust(5), "oov".ljust(5))
    print(title)
    print("="*len(title))

    weighted_avg = 0
    total_found  = 0

    for filename in sorted(results.keys()):
        average = sum(results[filename]) / float(len(results[filename]))
        minimum = min(results[filename])
        maximum = max(results[filename])
        std = sum([(results[filename][i] - average)**2 for i in
                   range(len(results[filename]))])
        std /= float(len(results[filename]))
        std = math.sqrt(std)

        weighted_avg += oov[filename][0] * average
        total_found  += oov[filename][0]

        ratio_oov = 100 - (oov[filename][0] /  oov[filename][1]) * 100

        print("{0}| {1:.3f}| {2:.3f}| {3:.3f}| {4:.3f}|  {5}%".format(
              filename.ljust(16),
              average, minimum, maximum, std, int(ratio_oov)))

    print("-"*len(title))
    print("{0}| {1:.3f}".format("W.Average".ljust(16),
                                weighted_avg / total_found))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
             description="Evaluate semantic similarities of word embeddings.",
             )

    parser.add_argument('filenames', metavar='FILE', nargs='+',
                        help='Filename of word embedding to evaluate.')

    args = parser.parse_args()

    init_results()
    for f in args.filenames:
        evaluate(f)
    stats()
