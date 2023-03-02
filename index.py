#!/usr/bin/python3
import nltk
import sys
import getopt
import os
import pickle
import shutil
import linkedlist
import resource
import sys

# improvements:
# use temp directory
# standardise index and positingmap

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def buildDocIds(in_dir, out_file):
    inFiles = sorted([int(i) for i in os.listdir(in_dir)])
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
    reverseDictionary = {}
    index = {}

    inFiles = sorted(os.listdir(in_dir), key = lambda x: int(x))

    # pre-process the documents, first by tokenising the sentences, 
    # then words, then apply porter stemming and then finally writitng the result 
    # of the procesed file into a dictery consisting of all the processed documents. 

    TMP_DIR = "processed"
    stemmer = nltk.stem.PorterStemmer()
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    
    for file_name in inFiles:

        with open(os.path.join(in_dir, file_name), 'r') as f:
            contents = f.read()

        contents = contents.lower() # case folding
        sentences = nltk.tokenize.sent_tokenize(contents)
        
        words = [] 
        for sentence in sentences:
            words.extend(nltk.tokenize.word_tokenize(sentence)) 

        stemmed_words = [stemmer.stem(word) for word in words]
        processed_words = ' '.join(stemmed_words)

         # Write processed contents to tmp directory
        with open(os.path.join(TMP_DIR, file_name), 'w') as f:
            f.write(processed_words)
    
    in_dir = TMP_DIR # change the input directory to the processed documents folder 
    inFiles = sorted(os.listdir(in_dir), key = lambda x: int(x))

    # first pass: Create starting blocks indexing 500 documents each
    currentBlockDocs = 0
    currentTempId = 1
    runningTermId = 0
    for inFile in inFiles:
        with open(os.path.join(in_dir, inFile), "r", encoding="utf-8") as f:
            fileSet = set()

            for line in f:
                words = line.split()
                for word in words:
                    fileSet.add(word)
            
            for word in fileSet:
                if word not in dictionary.keys():
                    dictionary[word] = runningTermId
                    runningTermId += 1
                    reverseDictionary[dictionary[word]] = word
                    index[dictionary[word]] = []

                currTermId = dictionary[word]
                if currTermId not in index.keys():
                    index[currTermId] = []

                index[currTermId].append(inFile)

            # write out block of size 500 docs - get tens of blocks out
            currentBlockDocs += 1
            if currentBlockDocs == 500:
                writeOut(index, os.path.join('temp1', str(currentTempId) + '.txt'))
                currentTempId += 1
                currentBlockDocs = 0
                index = {}
                continue

    # write out partially filled block. Give smallest ID to give priority in merging at next step
    if len(index) > 0:
        writeOut(index, os.path.join('temp1', '0.txt'))
        index = {}


    # while at least one directory has at least two files
    # consolidate pairs of docs, chuck into other temp
    cwd = "temp1"
    nwd = "temp2"
    cwdFileList = sorted(os.listdir(cwd))
    while len(cwdFileList) > 1:
        while len(cwdFileList) > 1:
            file1 = os.path.join(cwd, cwdFileList[0])
            file2 = os.path.join(cwd, cwdFileList[1])
            mergeFiles(file1, file2, os.path.join(nwd, str(currentTempId) + '.txt'))
            currentTempId += 1
            cwdFileList = cwdFileList[2:]
        if len(cwdFileList) == 1:
            shutil.copy(os.path.join(cwd, cwdFileList[0]), os.path.join(nwd, str(currentTempId) + '.txt'))
            currentTempId += 1
        shutil.rmtree(cwd)
        os.mkdir(cwd)
        cwd, nwd = nwd, cwd
        cwdFileList = sorted(os.listdir(cwd))

    seen = set()
    with open(os.path.join(cwd, cwdFileList[0]), "r") as tempIndexFp, open(out_postings, "wb") as out_postingsFP:
        # python automatically handles memory
        startIdx = 0
        for line in tempIndexFp:
            # not likely necessary but just in case, guarded against a fixed bug
            if line == "\n":
                continue
            separatedTerms = line.split()
            postingTermId = separatedTerms[0]
            posting = separatedTerms[1:]
            # print(termId)
            postingTermId, *posting = line.split()
            if postingTermId in seen:
                print("seen", postingTermId)
            seen.add(postingTermId)
            originalTerm = reverseDictionary[int(postingTermId)]
            posting = linkedlist.LinkedList(posting)
            dictionary[originalTerm] = [startIdx, out_postingsFP.write(linkedlist.LinkedListSerialiser.serialise(posting))]
            startIdx += dictionary[originalTerm][1]
            
    with open(out_dict, "wb") as dictFile:
        pickle.dump(dictionary, dictFile)

    # cleanup
    shutil.rmtree("temp1")
    shutil.rmtree("temp2")

    # with open("plaintextDict.txt", "w") as plainDict:
    #     for key in dictionary.keys():
    #         plainDict.write(key + " " + str(dictionary[key]) + "\n")


def outputDictPickle(index, dictionary, out_dict, out_postings):
    for key in index:
        index[key] = linkedlist.LinkedList(index[key])

    startIdx = 0

    with open(out_postings, "wb") as out_postingsFP:
        for word in sorted(dictionary.keys()):
            dictionary[word] = [startIdx, out_postingsFP.write(linkedlist.LinkedListSerialiser.serialise(index[dictionary[word]]))]
            startIdx += dictionary[word][1]

    with open(out_dict, "wb") as dictFile:
        pickle.dump(dictionary, dictFile)


# pickle recursion exceeds limit otherwise
# code taken from https://stackoverflow.com/questions/2134706/hitting-maximum-recursion-depth-using-pickle-cpickle
def increaseRecursionLimit():
    # print(resource.getrlimit(resource.RLIMIT_STACK))
    # print(sys.getrecursionlimit())

    max_rec = 0x100000

    # May segfault without this line. 0x100 is a guess at the size of each stack frame.
    resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
    sys.setrecursionlimit(max_rec)


# writes <termId, space-separated docids> pair into a single line of postingsmap
def writeOut(postingsMap, outFile):
    with open(str(outFile), "w") as outFile:
        for key in sorted(postingsMap.keys()):
            outFile.write(str(key))
            for docId in postingsMap[key]:
                outFile.write(" " + str(docId))
            outFile.write("\n")
            
def writeSinglePosting(term, posting, outFp):
    # if len(posting) > 10:
    #     print("write", posting)
    outputStr = str(term)
    for docId in posting:
        outputStr += " " + str(docId)
    outputStr += "\n"
    outFp.write(outputStr)

def mergeFiles(file1, file2, outFile):
    # figure out why smaller size result in posting corruption
    sizePerFilePerBlock = 500000

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
                if currFile2Term == currFile1Term:
                    mergedPosting = mergePostings(file1PostingMap[currFile1Term], file2PostingMap[currFile2Term])
                    writeSinglePosting(currFile1Term, mergedPosting, outFp)
                    file1PostingKeyIdx += 1
                    file2PostingKeyIdx += 1
                    continue

                print("ERROR: terms do not compare", currFile1Term, currFile2Term)
                
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
            
        # likely previous source of bugs, when we write fp1.read() newline is not printed after, resulting in mistaken joining of postings
        oldPosFp1 = fp1.tell()
        oldPosFp2 = fp2.tell()

        outFp.write(fp1.read())
        outFp.write("\n")
        outFp.write(fp2.read())
        outFp.write("\n")

        # if oldPosFp1 != fp1.tell() or oldPosFp2 != fp2.tell():
        #     print("disjoint found")
        #     outFp.write("\n")

def mergePostings(posting1, posting2):
    posting1Idx = 0
    posting2Idx = 0
    mergedPosting = []

    while posting1Idx < len(posting1) and posting2Idx < len(posting2):
        file1DocId = posting1[posting1Idx]
        file2DocId = posting2[posting2Idx]
        if file1DocId < file2DocId:
            mergedPosting.append(file1DocId)
            posting1Idx += 1
            continue
            
        if file2DocId < file1DocId:
            mergedPosting.append(file2DocId)
            posting2Idx += 1
            continue

        mergedPosting.append(file1DocId)
        posting1Idx += 1
        posting2Idx += 1

    leftover = posting1[posting1Idx:] + posting2[posting2Idx:]
    mergedPosting.extend(leftover)
    return mergedPosting

def readPostingStrings(fp, sizePerFilePerBlock):
    fileBuffer = fp.read(sizePerFilePerBlock)

    # buffer filled to capacity, last posting is possibly partially filled
    filePostingStrings = [i for i in fileBuffer.split("\n") if i != ""]

    # remove incomplete last posting
    if len(fileBuffer) == sizePerFilePerBlock:
        # print("full buffer spotted")
        # print("rollback by", len(filePostingStrings[-1]))
        fp.seek(fp.tell() - len(filePostingStrings[-1]))
        filePostingStrings = filePostingStrings[:-1]

    postingsMap = {}

    for postingString in filePostingStrings:
        termId, *posting = postingString.split(" ")
        termId = int(termId)
        postingsMap[termId] = [int(i) for i in posting]
        # if len(postingsMap[termId]) > 5:
        #     print(postingsMap[termId])

    
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

increaseRecursionLimit()
build_index(input_directory, output_file_dictionary, output_file_postings)