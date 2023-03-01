#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import linkedlist
import resource
import sys

counter = {}

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

# assumes that input files are preprocessed
def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below

    dictionary = {}
    index = {}

    inFiles = sorted(os.listdir(in_dir))

    for inFile in inFiles:
        f = open(os.path.join(in_dir, inFile), "r", encoding="utf-8")
        fileSet = set()

        for line in f:
            words = line.split()
            for word in words:
                fileSet.add(word)
        
        for word in fileSet:
            if word not in dictionary.keys():
                dictionary[word] = len(dictionary.keys())
                index[dictionary[word]] = []
            index[dictionary[word]].append(inFile)

    outputPickles(index, dictionary, out_dict, out_postings)
    # outputText(index, out_postings)

    print("done")

def outputText(index, out_postings):
    with open(out_postings, "w") as outFp:
        for key in sorted(index.keys()):
            outFp.write(str(key) + " ")
            for docId in index[key]:
                outFp.write(" " + docId)
            outFp.write("\n")

# pickle recursion exceeds limit otherwise
# code taken from https://stackoverflow.com/questions/2134706/hitting-maximum-recursion-depth-using-pickle-cpickle
def increaseRecursionLimit():
    print(resource.getrlimit(resource.RLIMIT_STACK))
    print(sys.getrecursionlimit())

    max_rec = 0x100000

    # May segfault without this line. 0x100 is a guess at the size of each stack frame.
    resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
    sys.setrecursionlimit(max_rec)



def outputPickles(index, dictionary, out_dict, out_postings):
    for key in index:
        index[key] = linkedlist.LinkedList(index[key])

    startIdx = 0

    with open(out_postings, "wb") as postingsFile:
        for word in dictionary:
            dictionary[word] = [startIdx, postingsFile.write(linkedlist.LinkedListSerialiser.serialise(index[dictionary[word]]))]
            startIdx += dictionary[word][1]

    with open(out_dict, "wb") as dictFile:
        pickle.dump(dictionary, dictFile)



increaseRecursionLimit()

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
