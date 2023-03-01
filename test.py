#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
import linkedlist

def usage():
    print("usage: " + sys.argv[0] + " -d dictionaryAttempt-file -p postingsAttempt-file -D dictionaryActual-file -P postingsActual-file")

def getPostings(postings_file, dictionary):
    postings = {}
    with open(postings_file, "rb") as postingsFp:
        for word in dictionary:
            [startPos, sz] = dictionary[word]

            # sample of how to use file pointers from dictionary
            postingsFp.seek(startPos)
            postingInBytes = postingsFp.read(sz)
            # posting is a linkedlist
            posting = linkedlist.LinkedListSerialiser.deserialise(postingInBytes)
            postings[word] = posting
    return postings

def compare(dictionary_file, postings_file, dictionaryAns_file, postingsAns_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    # print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    with open(dictionary_file, "rb") as dict_file:
        # <word in string form, [start byte address, size in bytes]>
        print("loading pickle dict")
        dictionary = pickle.load(dict_file)

    with open(dictionaryAns_file, "rb") as dict_file:
        # <word in string form, [start byte address, size in bytes]>
        print("loading pickle dict ans")
        dictionaryAns = pickle.load(dict_file)
        
    # debug postings load
    print("loading pickle postings")
    postings = getPostings(postings_file, dictionary)
    print("loading pickle postings ans")
    postingsAnswer = getPostings(postingsAns_file, dictionaryAns)

    for term in sorted(dictionaryAns.keys()):
        if not postings[term].compare(postingsAnswer[term]):
            print("not same", term)
            return
        print("same", term)

    

dictionary_file = postings_file = dictionaryAns_file = postingsAns_file = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:D:P:')
except getopt.GetoptError:
    print("opt error")
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-D':
        dictionaryAns_file = a
    elif o == '-P':
        postingsAns_file = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or dictionaryAns_file == None or postingsAns_file == None:
    print("none error")
    print(dictionary_file == None)
    print(postings_file == None)
    print(dictionaryAns_file == None)
    print(postingsAns_file == None)
    usage()
    sys.exit(2)

compare(dictionary_file, postings_file, dictionaryAns_file, postingsAns_file)
