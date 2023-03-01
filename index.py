#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import shutil
import linkedlist

# improvements:
# use temp directory
# standardise index and positingmap

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

    if not os.path.exists(in_dir):
        print("ERROR: in dir not exist")
        sys.exit(2)

    # temp dir setup
    # did not clean up
    if os.path.exists("temp1"):
        shutil.rmtree("temp1")
    
    if os.path.exists("temp2"):
        shutil.rmtree("temp2")
        
    os.mkdir("temp1")
    os.mkdir("temp2")
    
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

            termid = dictionary[word]
            if termid not in index.keys():
                index[termid] = []

            index[termid].append(inFile)

        # write out block of size 500 docs - get tens of blocks out
        currentBlockDocs += 1
        print(currentBlockDocs)
        if currentBlockDocs == 500:
            writeOut(index, os.path.join('temp1', str(currentTempId) + '.txt'))
            currentTempId += 1
            currentBlockDocs = 0
            index = {}
            continue


    # write out partially filled block. Give smallest ID to give priority in merging at next step
    if len(index) > 0:
        print("writing partial index")
        for key in index.keys():
            print(key, index[key])
        writeOut(index, os.path.join('temp1', '0.txt'))
        index = {}


    # while at least one directory has at least two files
    # consolidate pairs of docs, chuck into other temp
    cwd = "temp1"
    nwd = "temp2"
    cwdFileList = sorted(os.listdir(cwd))
    while len(cwdFileList) > 1:
        print("new cwd", cwd)
        fileCounter = 1
        while len(cwdFileList) > 1:
            print("merging files")
            file1 = os.path.join(cwd, cwdFileList[0])
            file2 = os.path.join(cwd, cwdFileList[1])
            mergeFiles(file1, file2, os.path.join(nwd, str(fileCounter) + '.txt'))
            fileCounter += 1
            cwdFileList = cwdFileList[2:]
        if len(cwdFileList) == 1:
            print("last file found")
            shutil.copy(os.path.join(cwd, cwdFileList[0]), os.path.join(nwd, '0.txt'))
        shutil.rmtree(cwd)
        os.mkdir(cwd)
        cwd, nwd = nwd, cwd
        cwdFileList = sorted(os.listdir(cwd))

    # postingslist = tempToIndex(cwdFileList[0])




    # Output singular index file with 
    # for key in index:
    #     index[key] = linkedlist.LinkedList(index[key])

    # startIdx = 0

    # with open(out_postings, "wb") as postingsFile:
    #     for word in dictionary:
    #         dictionary[word] = [startIdx, postingsFile.write(linkedlist.LinkedListSerialiser.serialise(index[dictionary[word]]))]
    #         print(word, dictionary[word][0], dictionary[word][1])
    #         startIdx += dictionary[word][1]

    # with open(out_dict, "wb") as dictFile:
    #     pickle.dump(dictionary, dictFile)

    # # with open(out_dict, "wb") as dictFile:
    # #     dictFile.write(pickle.dumps(dictionary))

    # print("done")

# writes <termId, space-separated docids> pair into a single line of postingsmap
def writeOut(postingsMap, outFile):
    print("printing to", outFile)
    with open(str(outFile), "w") as outFile:
        for key in sorted(postingsMap.keys()):
            outFile.write(str(key))
            for docId in postingsMap[key]:
                outFile.write(" " + docId)
            outFile.write("\n")
            
def writeSinglePosting(term, posting, outFp):
    outputStr = str(term) + " "
    for docId in posting:
        outputStr += " " + docId
    outputStr += "\n"
    outFp.write(outputStr)

# merging a pair of files
# for each file read 60000 characters, split by newline, discard last line
# when 
def mergeFiles(file1, file2, outFile):
    sizePerFilePerBlock = 5000

    with open(file1, "r") as fp1, open(file2, "r") as fp2, open(outFile, "w") as outFp:
        file1PostingMap = readPostingStrings(fp1, sizePerFilePerBlock)
        file2PostingMap = readPostingStrings(fp2, sizePerFilePerBlock)

        file1PostingKeyIdx = 0
        file2PostingKeyIdx = 0

        file1PostingKeys = sorted(list(file1PostingMap.keys()))
        file2PostingKeys = sorted(list(file2PostingMap.keys()))

        while len(file1PostingMap) > 0 and len(file2PostingMap) > 0:
            while file1PostingKeyIdx < len(file1PostingKeys) and file2PostingKeyIdx < len(file2PostingKeys):
                currFile1Term = file1PostingKeys[file1PostingKeyIdx]
                currFile2Term = file2PostingKeys[file2PostingKeyIdx]

                # file1 is ahead, write out current file2 posting as-is and continue
                if currFile1Term > currFile2Term:
                    writeSinglePosting(currFile2Term, file2PostingMap[currFile2Term], outFp)
                    file2PostingKeyIdx += 1
                    continue

                # file2 is ahead
                if currFile2Term > currFile1Term:
                    writeSinglePosting(currFile1Term, file1PostingMap[currFile1Term], outFp)
                    file1PostingKeyIdx += 1
                    continue

                # match found, merge postings for the same docId
                file1PostingIdx = 0
                file2PostingIdx = 0
                currFile1Posting = file1PostingMap[currFile1Term]
                currFile2Posting = file2PostingMap[currFile2Term]
                mergedPosting = []

                while file1PostingIdx < len(currFile1Posting) and file2PostingIdx < len(currFile2Posting):
                    file1DocId = currFile1Posting[file1PostingIdx]
                    file2DocId = currFile2Posting[file2PostingIdx]
                    if file1DocId < file2DocId:
                        mergedPosting.append(file1DocId)
                        file1PostingIdx += 1
                        continue
                        
                    if file2DocId < file1DocId:
                        mergedPosting.append(file2DocId)
                        file2PostingIdx += 1
                        continue

                    mergedPosting.append(file1DocId)
                    file1PostingIdx += 1
                    file2PostingIdx += 1

                mergedPosting.extend(currFile1Posting[file1PostingIdx:])
                mergedPosting.extend(currFile2Posting[file2PostingIdx:])

                writeSinglePosting(currFile1Term, mergedPosting, outFp)
                file1PostingKeyIdx += 1
                file2PostingKeyIdx += 1
                
            # chunk for one dictionary has been completed
            if file1PostingKeyIdx == len(file1PostingKeys):
                file1PostingKeyIdx = 0
                file1PostingMap = readPostingStrings(fp1, sizePerFilePerBlock)
                file1PostingKeys = sorted(list(file1PostingMap.keys()))

            if file2PostingKeyIdx == len(file2PostingKeys):
                file2PostingKeyIdx = 0
                file2PostingMap = readPostingStrings(fp2, sizePerFilePerBlock)
                file2PostingKeys = sorted(list(file2PostingMap.keys()))

        # one file's postings have been completely processed, write out rest of posting map and then copy the rest of file
        while file1PostingKeyIdx < len(file1PostingKeys):
            currFile1Term = file1PostingKeys[file1PostingKeyIdx]
            writeSinglePosting(currFile1Term, file1PostingMap[currFile1Term], outFp)
            file1PostingKeyIdx += 1

        while file2PostingKeyIdx < len(file2PostingKeys):
            currfile2Term = file2PostingKeys[file2PostingKeyIdx]
            writeSinglePosting(currfile2Term, file2PostingMap[currfile2Term], outFp)
            file2PostingKeyIdx += 1
            
        outFp.write(fp1.read())
        outFp.write(fp2.read())

def readPostingStrings(fp, sizePerFilePerBlock):
    fileBuffer = fp.read(sizePerFilePerBlock)

    # buffer filled to capacity, last posting is possibly partially filled
    filePostingStrings = [i for i in fileBuffer.split("\n") if i != ""]

    # remove incomplete last posting
    if len(fileBuffer) == sizePerFilePerBlock:
        fp.seek(fp.tell() - len(filePostingStrings[-1]))
        filePostingStrings = filePostingStrings[:-1]

    postingsMap = {}

    for postingString in filePostingStrings:
        termId, *posting = postingString.split(" ")
        termId = int(termId)
        postingsMap[termId] = posting

    return postingsMap



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
