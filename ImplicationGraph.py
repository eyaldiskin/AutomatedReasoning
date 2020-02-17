from queue import Queue
from math import inf

class Node:
    def __init__(self, variable, value, level, formula=None, parents=[], conflict=False):
        self.variable = variable
        self.value = value
        self.level = level
        self.formula = formula
        self.parents = []
        self.conflict = conflict


class ImplicationGraph:

    def __init__(self):
        self.nodes = []  # TODO - maybe keep sorted?

    def addRoot(self, variable, value, level):
        node = Node(variable, value, level)
        self.nodes.append(node)

    def getParents(self, formula, varName):
        if varName:
            return [node for node in self.nodes if node.variable is not varName and node.variable in formula.variables]
        return [node for node in self.nodes if node.variable in formula.variables]

    def addNode(self, value, formula, variable=None, conflict=False):
        if conflict:
            variable = "__conflict__"
        parents = self.getParents(formula, variable)
        level = max([parent.level for parent in parents])
        node = Node(variable, value, level, conflict)
        self.nodes.append(node)

    def backjump(self, level):
        self.nodes = [node for node in self.nodes if node.level<level]
        

    def findUIP(self, level, conflictNode: Node):
        pushed = {node.variable: False for node in self.nodes}
        relevantChildren = {node.variable: 0 for node in self.nodes}
        relevantParents = {node.variable: 0 for node in self.nodes}
        queue = Queue(len(self.nodes))
        queue.put(conflictNode)

        parent: Node
        node: Node

        while not queue.empty():
            node = queue.get()
            for parent in node.parents:
                if parent.level == level:
                    relevantParents[node.variable] += 1
                    relevantChildren[parent.variable] += 1
                    if not pushed[parent.variable]:
                        queue.put(parent)
                        pushed[parent.variable]

        nodeScore = {node.variable: 0 for node in self.nodes}
        queue.put(conflictNode)
        nodeScore[conflictNode] = 1
        while not queue.empty():
            node = queue.get()
            parentScore = nodeScore[node.variable] / \
                relevantParents[node.variable]
            for parent in node.parents:
                if parent.level == level:
                    relevantChildren[parent.variable] -= 1
                    nodeScore[parent.variable] += parentScore
                    if relevantChildren[parent.variable] == 0:
                        queue.put(parent)

        return min([var for var in nodeScore.keys if var is not conflictNode.variable and nodeScore[var] == 1])

    def distance(self, src: Node, dest: Node):
        if src.variable == dest.variable:
            return 0
        if len(dest.parents) is 0:
            return inf
        return min([self.distance(src, parent) for parent in dest.parents]) + 1
