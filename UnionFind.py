from TData import *
import Formula


class _Element:
    def __init__(self, data: TData, args: list = None):
        # the information for union-find alg
        self.parent = self
        self.rank = 0
        # the information for the dependency DAG
        self.data = data
        self.args = args
        self.dependencies = set()
        if args:
            for i in range(len(data.arguments)):
                assert data.arguments[i] == args[i].data
                args[i].dependencies.add(self)

    def __eq__(self, other):
        return self.data == other.data

    def find(self):
        if self.parent != self:
            self.parent = self.find()
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
        my_root.dependencies |= other_root.dependencies
        other_root.dependencies = set()

    def is_congruence(self, other):
        if self.data.name != other.data.name:
            return False
        if self.find() == other.find():
            return True
        for i in range(len(self.args)):
            if self.args[i].find() != other.args[i].find():
                return False
        return True


class UnionFind:
    def __init__(self, formula: Formula):
        self.elems = []
        self.data_elems = []
        self._get_elements(formula)

    def _get_elements(self, formula):
        if formula.type == Formula.FT.VAR:
            self._insert_element(formula.data)
            return
        for clause in formula.formulas:
            if clause.type == Formula.FT.VAR:
                if getattr(clause, "data", None):
                    self._insert_element(clause.data)
            else:
                self._get_elements(clause)

    def _insert_element(self, data: TData):
        if data in self.data_elems:
            return self.elems[self.data_elems.index(data)]
        if data.type == TType.VAR:
            elem = _Element(data)
        else:
            children = [None] * len(data.arguments)
            for i in range(len(data.arguments)):
                children[i] = self._insert_element(data.arguments[i])
            elem = _Element(data, children)
        self.data_elems.append(data)
        self.elems.append(elem)
        return elem

    def add_equation(self, first, second):
        first_elem = self.elems[self.data_elems.index(first)].find()
        second_elem = self.elems[self.data_elems.index(second)].find()
        self._add_equation_helper(first_elem, second_elem)

    def _add_equation_helper(self, first, second):
        dependencies1 = first.dependencies
        dependencies2 = second.dependencies
        first.union(second)
        for first_dep in dependencies1:
            for second_dep in dependencies2:
                if first_dep.is_congruence(second_dep):
                    self._add_equation_helper(first_dep, second_dep)

    def find(self, elem):
        if elem not in self.elems:
            raise
        root = elem
        while root.parent != root:
            root = root.parent
        while elem.parent != root:
            elem, elem.parent = elem.parent, root
