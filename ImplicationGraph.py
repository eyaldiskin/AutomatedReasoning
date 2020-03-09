from queue import Queue
from math import inf
from Formula import Formula


class Node:
    def __init__(self, varName, value, level, formula=None, parents=[], conflict=False):
        self.varName = varName
        self.value = value
        self.level = level
        self.formula = formula
        self.parents = []
        self.conflict = conflict


class ImplicationGraph:

    def __init__(self):
        self.nodes = []  # TODO - maybe keep sorted?

    def addRoot(self, varName, value, level):
        node = Node(varName, value, level)
        self.nodes.append(node)

    def getParents(self, formula, varName):
        if varName:
            return [node for node in self.nodes if node.variable is not varName and node.variable in formula.variables]
        return [node for node in self.nodes if node.variable in formula.variables]

    def addNode(self, value, formula, varName=None, conflict=False):
        if conflict:
            varName = "__conflict__"
        parents = self.getParents(formula, varName)
        level = max([parent.level for parent in parents])
        node = Node(varName, value, level, conflict)
        self.nodes.append(node)

    def backjump(self, level):
        self.nodes = [node for node in self.nodes if node.level < level]

    def findUIP(self, level):
        conflictNode = self.nodes[-1]
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

    def resolveConflict(self, UIP: Node):
        conflict = self.nodes[-1].formula
        if UIP.varName not in conflict.variables:
            for node in reversed(self.nodes):
                if node.varName in conflict.variables:
                    conflict = Formula.deduce(conflict, node.formula)
                    if UIP.varName in conflict.variables:
                        break
        return conflict
