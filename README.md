# cs3245-hw-2

# TODO
## Andrew
Add BSBI to indexing

## Agam
Add search functionality

# Indexing
Following command assumes that all input files are preprocessed and place in a directory labelled `fakeInput`.
Currently 3 inputs are provided, feel free to add more.

dict.txt and posting.txt will be written in current directory in bytes.

```
python3 index.py -i fakeInput/ -d dict.txt -p posting.txt
```

# Searching
Following command works directly after indexing.
```
python3 search.py -d dict.txt -p posting.txt -q README.txt -o output.txt
```

`dictionary` is map of `<word in string form, [start address in pickle, size in bytes]>`. 

## Read a posting
1) open posting.txt with setting "rb". This will create a file pointer. 
2) `postingsFp.seek(startPos)`
3) `postingInBytes = postingsFp.read(sz)`
4) `posting = linkedlist.LinkedListSerialiser.deserialise(postingInBytes)`
    a) posting is in the form of a linkedlist, read `linkedlist.py` up till `__str__` part
    b) posting contains filenames of documents which contains the key associated with the posting

## development order
1) Make query that works with only one word
2) Make query that works with NOt statement
3) Make query that works with OR and AND, using only 2 words i.e. a AND b
4) Make query that works with multiple predicates, single nesting, greedy from the left
5) Add DP, with intermediate results pushed on the stack
6) Add nesting

## Algo
1) Have an outer stack that tracks nesting
2) Have an inner stack that tracks the current nesting level
3) for each word seen in current nesting level add to inner stack
4) when we see an open bracket, add a new inner stack before doing 3
5) when we see a close bracket, 
    a) we handle the inner stack
    b) get the intermediate result
    c) pop outer stack, getting us the next outer level of indentation as the top of the outer stack
    d) set the inner stack to this new level of indentation (outerstack.top())
    e) push intermediate result onto the stack

Handling inner stack is non-trivial, see dev order step 5