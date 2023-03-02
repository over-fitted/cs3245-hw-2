#!/usr/bin/python3
import sys
import getopt
import pickle
import linkedlist
import nltk

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

# debugs postings
def printPostings(postings_file, dictionary):
    with open(postings_file, "rb") as postingsFp:
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

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    DOCID_FILE_PATH = "docIds.txt"


    with open(dict_file, "rb") as dict_file:
        # <word in string form, [start byte address, size in bytes]>
        dictionary = pickle.load(dict_file)
        # print(dictionary)
        
    # load list of sorted docIds
    with open(DOCID_FILE_PATH, "rb") as docid_file:
        docIds = pickle.load(docid_file)

    with open(queries_file, "r") as query_file, open(results_file, "w+") as out_file:
        for queryLine in query_file:
            query = queryLine.strip().split()
            offset = 0
            queryIdx = 0
            
            operators = []
            lists = []
            
            innerLayer = False
            exitInner = False
            innerOperators = []
            innerLists = []
            
            # shunting yard preprocess
            while queryIdx < len(query):                
                if innerLayer:
                    # print("innerLayer", queryIdx, innerOperators, "innerLists:", [str(xs) for xs in innerLists])
                    # should see term or NOT at this index. Offset indicates number of NOTs seen so far to account for this
                    if (queryIdx - offset) % 2 == 0:
                        if query[queryIdx] == "NOT":
                            innerOperators.append(query[queryIdx])
                            queryIdx += 1
                            offset += 1
                            continue
                            
                        else:
                            term = query[queryIdx]
                            # handle nesting-related artifacts
                            if term[-1] == ')':
                                term = term[:-1]
                                exitInner = True
                            if term[0] == '(':
                                term = term[1:]
                            
                            # print("term seen is",term)
                            singleWordPosting = single_word_query(term, dictionary, postings_file)
                            innerLists.append(singleWordPosting)
                            queryIdx += 1
                            
                            # end bracket seen, handle inner layer
                            if exitInner:
                                # print("handling inners")
                                lists.append(handleLayer(innerLists, innerOperators, docIds))
                                innerLayer = False
                                exitInner = False
                                
                            continue
                        
                    # Operator seen at this index
                    innerOperators.append(query[queryIdx])
                    queryIdx += 1
                    continue
                
                # print("outer", queryIdx, operators, "lists:", len(lists))
                
                # should see term or NOT at this index. Offset indicates number of NOTs seen so far to account for this
                if (queryIdx - offset) % 2 == 0:
                    if query[queryIdx] == "NOT":
                        operators.append(query[queryIdx])    
                        queryIdx += 1
                        offset += 1
                        continue
                        
                    # print("term seen", query[queryIdx])
                    
                    # nesting seen
                    if query[queryIdx][0] == '(':
                        innerLayer = True
                        innerOperators = []
                        innerLists = []
                        continue
                    
                    lists.append(single_word_query(query[queryIdx], dictionary, postings_file))
                    queryIdx += 1
                    continue
                
                operators.append(query[queryIdx])    
                queryIdx += 1
                
            lst = handleLayer(lists, operators, docIds).to_lst()
            lst = [str(i) for i in lst]
            out_file.write(' '.join(sorted(lst, key = lambda x : int(x))) + "\n")


def handleLayer(lists, operators, docIds):
    optimisedOperators = []
    # print("Lists and operators are ", [str(xs) for xs in lists], operators)
    for i in range(len(operators)):
        # NOT NOT is trivially the original list
        if len(optimisedOperators) > 0 and operators[i] == "NOT" and optimisedOperators[-1] == "NOT":
            optimisedOperators.pop()
            continue
        optimisedOperators.append(operators[i])
            
    # print([xs.getSize() for xs in lists])
    opIdx = 0
    listIdx = 0
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "NOT":
            # print("doing NOT to", listIdx)
            # print(len(docIds))
            lists[listIdx] = eval_NOT(lists[listIdx], docIds)
            optimisedOperators.pop(opIdx)
            continue
        # print("skip")
        opIdx += 1
        listIdx += 1

    # print([xs.getSize() for xs in lists])
        
    # Handle AND operations
    # index candidate AND operations
    opIdx = 0
    listIdx = 0
    # <estimatedLength, id>
    candidateOperations = []
    # print(lists)
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "AND":
            candidateOperations.append([min(lists[listIdx].getSize(), lists[listIdx + 1].getSize()), listIdx])
        
        opIdx += 1
        listIdx += 1
        
    while len(candidateOperations) > 0:
        bestAND = sorted(candidateOperations)[0]
        lists[bestAND[1]] = eval_AND(lists[bestAND[1]], lists[bestAND[1] + 1])
        lists.pop(bestAND[1] + 1)
        
        # VERIFIED CORRECT
        optimisedOperators.pop(bestAND[1])
        
        # re-index candidate add operations
        opIdx = 0
        listIdx = 0
        # <estimatedLength, id>
        candidateOperations = []
        while opIdx < len(optimisedOperators):
            if optimisedOperators[opIdx] == "AND":
                candidateOperations.append([min(lists[listIdx].getSize(), lists[listIdx + 1].getSize()), listIdx])
            
            opIdx += 1
            listIdx += 1
            
    
    # Handle OR operations
    # index candidate OR operations
    opIdx = 0
    listIdx = 0
    # <estimatedLength, id>
    candidateOperations = []
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "OR":
            candidateOperations.append([lists[listIdx].getSize() + lists[listIdx + 1].getSize(), listIdx])
        
        opIdx += 1
        listIdx += 1
        
    while len(candidateOperations) > 0:
        bestOR = sorted(candidateOperations)[0]
        lists[bestOR[1]] = eval_OR(lists[bestOR[1]], lists[bestOR[1] + 1])
        lists.pop(bestOR[1] + 1)
        
        # print("popping OR", optimisedOperators[bestOR[1]])
        # VERIFIED
        optimisedOperators.pop(bestOR[1])
        
        # re-index candidate or operations
        opIdx = 0
        listIdx = 0
        # <estimatedLength, id>
        candidateOperations = []
        while opIdx < len(optimisedOperators):
            if optimisedOperators[opIdx] == "OR":
                candidateOperations.append([lists[listIdx].size + lists[listIdx + 1].size, listIdx])
            
            opIdx += 1
            listIdx += 1
        
    return lists[0]


def single_word_query(word, dictionary, postings_file):
    """

    Given a word in string and dictoanay and a file of documents postings 
    it returns a linked list with all the documents_posting found in the dictonary. 

    Params: word: string, dictionary : a dictonray object loaded into memory, 
            postings_file: string path to the file of postings_file 
    
    Returns: a linkedlist object consisting of all the documents posting of the words 
    in the dictonary. 
    """
    stemmer = nltk.stem.PorterStemmer()
    word = stemmer.stem(word.lower()) # case folding and stemming

    start, sz  = dictionary.get(word, [-1, -1]) # -1 means that the word doesn't exist 
    # print("querying single word", word, start, sz)
            
    if start != -1:
        with open(postings_file, "rb") as post_file:
            post_file.seek(start)
            return pickle.loads(post_file.read(sz))

    return linkedlist.LinkedList([])

def eval_NOT(word_lst, docid_lst):
    """"
    Given a linked list with document posting list consisting of all the docIDs, where 
    the found is found, it returns a document posting list consisting of all the docIDs, 
    of which the word is not part of. 

    Params: 
        word_lst: a linked list with document postings 
        docid_lst: a string with file path with all the document postings 
    
    Returns:
        Returns a linkedlist after negating word_lst with all document postings. 
    """

    lst = [] 
    
    i = 0 # doc_id pointer 
    j = word_lst.head

    while i != len(docid_lst) and j != None:
        if docid_lst[i] == j.id:
            i += 1 
            j = j.nextNode 
        elif docid_lst[i] < j.id:
            lst.append(docid_lst[i])
            i += 1 
        else:
            j = j.nextNode 

    lst.extend(docid_lst[i:])

    return linkedlist.LinkedList(lst)

def eval_OR(w1_lst, w2_lst):
    """"
    Given two linked list with posting list of two words, it returns the a linkedlist 
    which consists of the doc IDs in which either of the word can be found. 

    Params: 
        w1_lst: a document posting list consisting of docIDs, where word1 is found 
        w2_lst: a document posting list comsisting of docIDs, where word2 is found 

    Returns: a linked list of document posting list consisting of docIDs, where either 
            word1, or word2 is found. 
    """

    p1 = w1_lst.head 
    p2 = w2_lst.head 

    output_lst = [] 

    while p1 != None and p2 != None:
        
        if p1.id == p2.id:
            output_lst.append(p1.id)
            p1 = p1.nextNode
            p2 = p2.nextNode
        
        elif p1.id < p2.id:
            output_lst.append(p1.id)
            p1 = p1.nextNode
        
        else:
            output_lst.append(p2.id)
            p2 = p2.nextNode
    
    while p1 != None:
        output_lst.append(p1.id)
        p1 = p1.nextNode
    
    while p2 != None:
        output_lst.append(p2.id)
        p2 = p2.nextNode
    
    return linkedlist.LinkedList(output_lst)

def eval_AND(w1_lst, w2_lst):
    """"
    Given two linked list with posting list of two words, it returns the a linkedlist 
    of posting lists which consists of the doc IDs in which both of the word are found. 

    Params: 
        w1_lst: a document posting list consisting of docIDs, where word1 is found 
        w2_lst: a document posting list comsisting of docIDs, where word2 is found 

    Returns: a linked list of document posting list consisting of docIDs, where either 
            word1, or word2 is found. 
    """

    p1 = w1_lst.head 
    p2 = w2_lst.head 

    output_lst = [] 

    while p1 != None and p2 != None:

        if p1.id == p2.id:
            output_lst.append(p1.id)
            p1 = p1.nextNode
            p2 = p2.nextNode
        
        elif p1.id < p2.id:
            
            if p1.skipPointer != None and (p1.skipPointer.id < p2.id):
                while p1.skipPointer != None and p1.skipPointer.id < p2.id:
                    p1 = p1.skipPointer

            else:
                p1 = p1.nextNode
        
        else:

            if p2.skipPointer != None and (p2.skipPointer.id < p1.id):
                while p2.skipPointer != None and p2.skipPointer.id < p1.id:
                    p2 = p2.skipPointer

            else:
                p2 = p2.nextNode
        
    return linkedlist.LinkedList(output_lst)

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

# print(eval_AND(linkedlist.LinkedList([1,2,3]), linkedlist.LinkedList([2,4,5])))