#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import linkedlist

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def buildDocIds(in_dir, out_file):
    inFiles = sorted(os.listdir(in_dir))
    with open(out_file, "wb") as out_file:
        pickle.dump(inFiles, out_file)

# assumes that input files are preprocessed
def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below

    buildDocIds(in_dir, "docIds.txt")
    dictionary = {}
    index = {}

    inFiles = sorted(os.listdir(in_dir))

    # first pass: Create starting blocks indexing 500 documents each
    currentBlockDocs = 0
    currentTempId = 1
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

        # write out block of size 500 docs - get tens of blocks out
        currentBlockDocs += 1
        if currentBlockDocs == 5:
            writeOut(index, f'temp1/{currentTempId}.txt')
            currentTempId += 1
            currentBlockDocs = 0
            index = {}
            continue

    # write out partially filled block. Give smallest ID to give priority in merging at next step
    if len(index) > 0:
        writeOut(index, 'temp1/0.txt')
        index = {}

    usingTemp1 = True

    

    # while at least one directory has at least two files
    # consolidate pairs of docs, chuck into other temp





    # Output singular index file with 
    for key in index:
        index[key] = linkedlist.LinkedList(index[key])

    startIdx = 0

    with open(out_postings, "wb") as postingsFile:
        for word in dictionary:
            dictionary[word] = [startIdx, postingsFile.write(linkedlist.LinkedListSerialiser.serialise(index[dictionary[word]]))]
            print(word, dictionary[word][0], dictionary[word][1])
            startIdx += dictionary[word][1]

    with open(out_dict, "wb") as dictFile:
        pickle.dump(dictionary, dictFile)

    # with open(out_dict, "wb") as dictFile:
    #     dictFile.write(pickle.dumps(dictionary))

    print("done")

def writeOut(postingsMap, outFile):
    pass

# merging a pair of files
# for each file read 5000 characters, split by newline, discard last line
# when 
def mergeFiles(file1, file2, outFile):
    sizePerFilePerBlock = 5000
    with open(file1, "r") as file1, open(file2, "r") as file2:
        pass




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

# build_index(input_directory, output_file_dictionary, output_file_postings)
buildDocIds(input_directory, "docIds.txt")
