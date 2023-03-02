#!/usr/bin/python3
import sys
import getopt
import pickle
import linkedlist

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

    with open(dict_file, "rb") as dict_file:
        # <word in string form, [start byte address, size in bytes]>
        dictionary = pickle.load(dict_file)
        
    with open("docIds.txt", "rb") as docid_file:
        docIds = pickle.load(docid_file)
    
    # print(dictionary)
    # print() 

    with open(queries_file, "r") as query_file:
        for queryLine in query_file:
            query = queryLine.strip().split()
            offset = 0
            queryIdx = 0
            
            operators = []
            lists = []
            
            innerLayer = False
            
            innerOperators = []
            innerLists = []
            
            # shunting yard preprocess
            while queryIdx < len(query):
                if innerLayer:
                    if (queryIdx - offset) % 2 == 0:
                        if query[queryIdx] == "NOT":
                            innerOperators.append(query[queryIdx])
                            queryIdx += 1
                            offset += 1
                            continue
                            
                        else:
                            term = query[queryIdx + 1]
                            if term[-1] == ')':
                                term = term[:-1]
                                innerLayer = False
                            if term[0] == '(':
                                term = term[1:]
                            innerLists.append(single_word_query(query[queryIdx], dictionary, postings_file))
                            queryIdx += 1
                            continue
                        
                    innerOperators.append(query[queryIdx])
                    if not innerLayer:
                        lists.append(handleLayer(innerLists, innerOperators, docIds))
                    
                    continue
                
                
                if (queryIdx - offset) % 2 == 0:
                    if query[queryIdx] == "NOT":
                        operators.append(query[queryIdx])    
                        queryIdx += 1
                        offset += 1
                        continue
                        
                    print("term seen", query[queryIdx])
                    
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
                
            for list in lists:
                print(list)
            print(len(lists))
            print(operators)
            print(handleLayer(lists, operators, docIds))

    print() 
    
    return 

def handleLayer(lists, operators, docIds):
    optimisedOperators = []
    i = 0
    for i in range(len(operators)):
        if len(optimisedOperators) > 0 and operators[i] == "NOT" and optimisedOperators[-1] == "NOT":
            continue
        optimisedOperators.append(operators[i])
            
    print(len(lists))
    opIdx = 0
    listIdx = 0
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "NOT":
            lists[listIdx] = eval_NOT(lists[listIdx], docIds)
            optimisedOperators.pop(opIdx)
            listIdx += 1
            continue
        
        opIdx += 1
        listIdx += 1
    
    opIdx = 0
    listIdx = 0
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "AND":
            lists[listIdx] = eval_AND(lists[listIdx], lists[listIdx + 1])
            optimisedOperators.pop(opIdx)
            continue
        
        opIdx += 1
        listIdx += 1
        
    
    opIdx = 0
    listIdx = 0
    while opIdx < len(optimisedOperators):
        if optimisedOperators[opIdx] == "OR":
            lists[listIdx] = eval_OR(lists[listIdx], lists[listIdx + 1])
            optimisedOperators.pop(opIdx)
            continue
        
        opIdx += 1
        listIdx += 1
        
        # if operators[0] == "AND":
        #     lists[0] = eval_AND(lists[0], lists[1])
        #     lists.pop(1)
        #     operators.pop(0)
        #     continue
        
    return lists[0]

# # TODO: Handle one query string
# def handleQuery(query):
#     words = query.split()
#     layers = []
#     currentLayer = []
#     for word in words:
#         if "(" in word:
#             layers.append(currentLayer)
#             currentLayer = []
#             word = word[1:]
#         currentLayer.append(word)
#         if ")" in word:
#             newLayer = currentLayer[-2]
#             newLayer.append(processLayer(currentLayer))
#     pass

def processLayer(currentLayer):
    # implement DP of the current layer, assume no indentation
    pass

def single_word_query(word, dictionary, postings_file):
    
    output = linkedlist.LinkedList([])

    start, end  = dictionary.get(word, [-1, -1]) # -1 means that the word doesn't exist 
            
    if start != -1:
        with open(postings_file, "rb") as post_file:
            post_file.seek(start)
            output = pickle.load(post_file)

    return output

def eval_NOT(word_lst, docid_lst):

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