from queue import Queue
from math import inf
from Formula import Formula
from helper import secondLargest


class Node:
    def __init__(self, varName, value, level, formula=None, parents=[], conflict=False):
        self.varName = varName
        self.value = value
        self.level = level
        self.formula = formula
        self.parents = parents
        self.conflict = conflict


class ImplicationGraph:

    def __init__(self):
        self.nodes = []  # TODO - maybe keep sorted?

    def addRoot(self, varName, value, level):
        node = Node(varName, value, level)
        self.nodes.append(node)

    def getParents(self, formula, varName):
        parents = [node for node in self.nodes if not node.varName ==
                   varName and node.varName in formula.variables]
        return parents

    def addNode(self, value, formula, varName=None, conflict=False):
        if conflict:
            varName = "__conflict__"
        parents = self.getParents(formula, varName)
        if len(parents) == 0:
            level = 0
        else:
            level = max([parent.level for parent in parents])
        node = Node(varName, value, level, parents=parents,
                    conflict=conflict, formula=formula)
        self.nodes.append(node)

    def backjump(self, level):
        self.nodes = [node for node in self.nodes if node.level < level]

    def findUIP(self, level):
        conflictNode = self.nodes[-1]
        pushed = {node.varName: False for node in self.nodes}
        relevantChildren = {node.varName: 0 for node in self.nodes}
        relevantParents = {node.varName: 0 for node in self.nodes}
        queue = Queue(len(self.nodes))
        queue.put(conflictNode)

        parent: Node
        node: Node

        while not queue.empty():
            node = queue.get()
            for parent in node.parents:
                if parent.level == level:
                    relevantParents[node.varName] += 1
                    relevantChildren[parent.varName] += 1
                    if not pushed[parent.varName]:
                        queue.put(parent)
                        pushed[parent.varName]

        nodeScore = {node.varName: 0 for node in self.nodes}
        queue.put(conflictNode)
        nodeScore[conflictNode.varName] = 1
        while not queue.empty():
            node = queue.get()
            parentScore = nodeScore[node.varName] / \
                relevantParents[node.varName]
            for parent in node.parents:
                if parent.level == level:
                    relevantChildren[parent.varName] -= 1
                    nodeScore[parent.varName] += parentScore
                    if relevantChildren[parent.varName] == 0:
                        if nodeScore[parent.varName] == 1:
                            return parent
                        queue.put(parent)

        return min([var for var in nodeScore.keys if var is not conflictNode.varName and nodeScore[var] == 1])

    def distance(self, src: Node, dest: Node):
        if src.varName == dest.varName:
            return 0
        if len(dest.parents) is 0:
            return inf
        return min([self.distance(src, parent) for parent in dest.parents]) + 1

    def resolveConflict(self, UIP: Node):
        conflict = self.nodes[-1].formula
        if UIP.varName not in conflict.variables:
            for node in reversed(self.nodes):
                if node.varName in conflict.variables:
                    conflict = Formula.deduce(conflict, node.formula)
                    if UIP.varName in conflict.variables:
                        break
        backJumpLevel = secondLargest(
            [node.level for node in self.nodes if node.varName in conflict.variables])
        return (conflict, backJumpLevel)
