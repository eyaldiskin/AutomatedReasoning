from UFData import *


class _Element:
    def __init__(self, data: UFData, args: list = None):
        # the information for union-find alg
        self.parent = self
        self.rank = 0

        # restoration data
        self.default_dep = []
        self.back_parent = None
        self.back_rank = -1
        self.back_dep = []

        # the information for the dependency DAG
        self.data = data
        self.dep = []
        if args:
            self.args = args
            for i in range(len(data.arguments)):
                assert data.arguments[i] == args[i].data
                args[i].dep.append(self)
                args[i].default_dep.append(self)
        else:
            self.args = []

    def __eq__(self, other):
        return self.data == other.data

    def find(self):
        if self.parent != self:
            self.parent = self.parent.find()
        return self.parent

    def union(self, other):
        my_root = self.find()
        other_root = other.find()
        if my_root == other_root:
            return
        if my_root.rank < other_root.rank:
            my_root, other_root = other_root, my_root
        if my_root.rank == other_root.rank:
            my_root.rank += 1
        other_root.parent = my_root
        my_root.dep.extend([dep for dep in other_root.dep if dep not in my_root.dep])
        other_root.dep = []

    def is_congruence(self, other):
        if self.find() == other.find():
            return True
        if self.data.name != other.data.name:
            return False
        for i in range(len(self.args)):
            if self.args[i].find() != other.args[i].find():
                return False
        return True

    def reset(self):
        self.parent = self
        self.rank = 0
        self.dep = list(self.default_dep)

    def save(self):
        self.back_parent = self.parent
        self.back_rank = self.rank
        self.back_dep = list(self.dep)

    def load(self):
        self.parent = self.back_parent
        self.rank = self.back_rank
        self.dep = list(self.back_dep)


class UnionFind:
    def __init__(self):
        self.elems = []
        self.data_elems = []
        # self._get_elements(formula)

    def insert_element(self, data: UFData):
        if data in self.data_elems:
            return self.elems[self.data_elems.index(data)]
        if data.type == UFType.VAR:
            elem = _Element(data)
        else:
            children = [None] * len(data.arguments)
            for i in range(len(data.arguments)):
                children[i] = self.insert_element(data.arguments[i])
            elem = _Element(data, children)
        self.data_elems.append(data)
        self.elems.append(elem)
        return elem

    def add_equation(self, first, second):
        first_elem = self.elems[self.data_elems.index(first)].find()
        second_elem = self.elems[self.data_elems.index(second)].find()
        self._add_equation_helper(first_elem, second_elem)

    def _add_equation_helper(self, first, second):
        dep1 = list(first.dep)
        dep2 = list(second.dep)
        first.union(second)
        for first_dep in dep1:
            for second_dep in dep2:
                if first_dep.find() != second_dep.find() and first_dep.is_congruence(second_dep):
                    self._add_equation_helper(first_dep, second_dep)

    def are_equal(self, first, second):
        first_elem = self.elems[self.data_elems.index(first)].find()
        second_elem = self.elems[self.data_elems.index(second)].find()
        return first_elem == second_elem

    def __contains__(self, data):
        return data in self.data_elems

    def reset(self):
        for elem in self.elems:
            elem.reset()

    def save(self):
        for elem in self.elems:
            elem.save()

    def load(self):
        for elem in self.elems:
            elem.load()
