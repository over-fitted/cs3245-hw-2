#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
import linkedlist

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def printPostings(postings_file, dictionary):
    with open(postings_file, "rb") as postingsFp:
        # print(sorted(dictionary.keys()))
        # print(dictionary["1,130,000"])
        for word in sorted(dictionary.keys()):
            print("printing", word)
            print(dictionary[word])
            [startPos, sz] = dictionary[word]

            # sample of how to use file pointers from dictionary
            postingsFp.seek(startPos)
            postingInBytes = postingsFp.read(sz)
            # posting is a linkedlist
            posting = linkedlist.LinkedListSerialiser.deserialise(postingInBytes)

            print(word, posting)
            # print(word, dictionary[word])
        # print("dict size", len(dictionary.keys()))
        # print("postings size", len(postingsFp.readlines()))

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    with open(dict_file, "rb") as dict_file:
        # <word in string form, [start byte address, size in bytes]>
        dictionary = pickle.load(dict_file)
        
    # debug postings load
    printPostings(postings_file, dictionary)

    # with open(queries_file, "r") as queries:
    #     for query in queries:
    #         handleQuery(query)

# TODO: Handle one query string
def handleQuery(query):
    words = query.split()
    layers = []
    currentLayer = []
    for word in words:
        if "(" in word:
            layers.append(currentLayer)
            currentLayer = []
            word = word[1:]
        currentLayer.append(word)
        if ")" in word:
            newLayer = currentLayer[-2]
            newLayer.append(processLayer(currentLayer))
    pass

def processLayer(currentLayer):
    # implement DP of the current layer, assume no indentation
    pass

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
