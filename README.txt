This is the README file for A0217487U's submission
Email(s): e0543523@u.nus.edu

== Python Version ==

I'm (We're) using Python Version 3.10.6 for my
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

# Indexing

Files were first preprocessed, we essentially open all the files one by one, read all the contents of the file, applying case folding to the text of each documents. 
then tokensize each sentence, and following which each word is tokensized and finally we apply porter stemming to all the tokensized words of the documents. 

Following which each of the processed_words are written into seperate files, with ach file just consisting of one line of processed strings that 
are seperated by space into a directory called processed. Even though we are storing the processed documents into a seperate folder from the nltk_data/corpora/reuters/training/
we keep the name of the files same. For example if the file had the name "1" in the nltk_data/corpora/reuters/training/ dataset that after being processed it is stored 
into the processed directory with the same file name of "1". 

The BSBI algorithm assumes that it words being taken in as input are preprocessed. 

BSBI Algorithm was used for file indexing. We used an entirely in-memory indexing programme (inMemoryIndex.py) as a way to double check that our BSBI version worked correctly.
First run created documents containing <termId, [docIds]> pairs, each indexing 500 documents before being written to disk, creating tens of mergable buffers as requested.
We then did 2-way merge between files until we ended up with one final file which we converted into our final index. 
2-way merge utilised buffers of 500000 characters, sufficiently large to store postings but sufficiently small so as to demonstrate reading only part of each file in,
utilising sorted output and memory adjacency to theoretically handle files larger than memory.

Finally we end up with a serialised dictionary of <termId, [docIds]>. We used LinkedList custom class in linkedlist.py to store the docIds array. This way we were able to code 
actual skip pointers. We then used pickle to serialise each posting, and recorded down the starting byte-address + byte-size of each posting in the dictionary, 
which we also pickled thereafter. To lookup a posting, we do file.seek(starting byte-address), then file.read(byte-size). Deserialisation is also handled 
by custom serialiser in linkedlist.py

# Query Handling
We processed queries line by line. We processed the query by aggregating the operators into one list and the postings associated with each term in another list similar to shunting yard.

We implemented our own function implementation of evaluation functions for AND, OR and NOT query handling, taking in the linkedlists required for the operation.
We optimised "NOT" by removing adjacent NOT operators since that would result in the original posting. We then linearly substituted each NOT posting list with their 
NOT counterpart, removing "NOT" from operator list thereafter, effectively substituting "NOT a" with the answer.

We handled each other operator similarly in the order AND > OR: 
1) Create candidateOperations list
2) Add <estimated size of intermediate result, [leftPosting, rightPosting]> to the list
3) sort list and get the smallest estimated size candidate
4) substitute leftPosting with the intermediate result, delete rightPosting
5) repeat step 1 until there are no more candidateOperations

To handle nested queries, we created a separate inner postings and inner operations list. We handle the nested query similar to how we handle outer query, then add the result to the postings list in the outer query.

For the query search .

<Andrew write about how the query is handled over here>

Finally after the query has been preprocessed, we write the result into output-file-of-results by writing out all the docIds in increasing ordered 
seperated by spaces, if the query returns no docIds an empty string is written into the output-file-of-results. 


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

test.py: used to compare between a model index and dictionary, and our output
inMemoryIndex.py: used to generate a model index to compare to
index.py: Actual indexer that implements BSBI
search.py: implements search features
dictionary.txt: dictionary from indexing
postings.txt: postings from indexing
docIds.txt: pickled data structure containing all docIds for use in resolving NOT queries


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I/We, A0217487U and A0226619Y, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0217487U and A0226619Y, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

code taken from https://stackoverflow.com/questions/2134706/hitting-maximum-recursion-depth-using-pickle-cpickle
for increasing recursion depth in order to handle pickling of massive linkedlist. Comment can be found with similar info in our code marking what we copied.