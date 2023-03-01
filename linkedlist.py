import math
import pickle

class Node:
    def __init__(self, id):
        self.id = id
        self.nextNode = None
        self.skipPointer = None

class LinkedList:
    def __init__(self, inputList):
        nodeList = [Node(id) for id in inputList]
        self.head = nodeList[0]

        for i in range(len(nodeList) - 1):
            nodeList[i].nextNode = nodeList[i+1]
            if i % math.floor(math.sqrt(len(nodeList))):
                skipIdx = i + math.floor(math.sqrt(len(nodeList)))
                if skipIdx >= len(nodeList):
                    continue
                nodeList[i].skipPointer = nodeList[i + math.floor(math.sqrt(len(nodeList)))]

    def __str__(self):
        ret = "["
        it = self.head
        while it != None:
            ret += str(it.id) + ", "
            it = it.nextNode
        ret += "]"
        return ret
    
    def compare(self, otherLinkedList):
        tempSelf = self.head
        tempOther = otherLinkedList.head

        counter = 0

        while tempSelf is not None and tempOther is not None:
            if tempSelf.id != tempOther.id:
                return False
            counter += 1
            tempSelf = tempSelf.nextNode
            tempOther = tempOther.nextNode
            
        if tempSelf is None and tempOther is None:
            return True
        
class LinkedListSerialiser:
    @classmethod
    def serialise(cls, linkedlist):
        return pickle.dumps(linkedlist)
    
    @classmethod
    def deserialise(cls, serialisedLinkedList):
        return pickle.loads(serialisedLinkedList)
        



if __name__ == "__main__":
    xxs = [LinkedList([1,2,3,4,5]), LinkedList([2,3,4,5]), LinkedList([4,3,2,5])]
    serial = LinkedListSerialiser
    reinit = []

    nums = []
    start = 0
    end = 0

    with open("demo.txt", "wb") as f:
        for xs in xxs:
            [start, sz] = [end, f.write(LinkedListSerialiser.serialise(xs))]
            nums.append([start, sz])
            end = start + sz

    with open("demo.txt", "rb") as f:
        for start, sz in nums:
            f.seek(start)
            reinit.append(LinkedListSerialiser.deserialise(f.read(sz)))

    for xs in reinit:
        print(xs)
            
