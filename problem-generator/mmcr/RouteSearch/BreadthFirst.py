#! /usr/bin/python
# Breadth-First Implementation
class Node:
    def __init__(self, name, cost, parent, fromBridge=False):
        self.name = name
        self.parent = parent
        self.cost = cost
        self.fromBridge = fromBridge

class Queue:
    def __init__(self):
        self.items = []

    def __getitem__(self, index):
        return self.items[index]

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
        
def getSuccessors(node, connectivityMap, openset, closedset):
    for name in connectivityMap[node.name]:
        fromBridge = len(connectivityMap[node.name][name]) > 1
        cost = node.cost + sum(connectivityMap[node.name][name])
        succ = Node(name, cost, node, fromBridge)
        if succ not in closedset:
            openset.enqueue(succ)

def search(start, goal, connectivityMap):
    
    #create Node from start
    start = Node(start, 0, 0)
    #The open and closed sets
    openset = Queue()
    closedset = set()
    #Current point is the starting point
    current = start
    #Add the starting point to the open set
    openset.enqueue(current)
    #While the open set is not empty
    while openset.size():
        #Get next item in the queue
        current = openset.dequeue()
        #If it is the item we want, retrace the path and return it
        if current.name == goal:
            return current
        #Add it to the closed set
        closedset.add(current)
        #Loop through the node's successors
        getSuccessors(current, connectivityMap, openset, closedset)
    raise ValueError('No Path Found')