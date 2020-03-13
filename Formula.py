from enum import Enum
from helper import powerset


class FT(Enum):
    VAR = 1
    NEG = 2
    AND = 3
    OR = 4
    IMPLIES = 5
    IFF = 6


class Formula:
    def __init__(self, type: FT,
                 formulas: list = None, varName=None, data=None, tseitlin=False):
        if type is None:
            raise
        self.type = type
        self.data = data
        self.tseitlinVar = None
        if type == FT.VAR:
            self.name = varName
            self.variables = {varName}
            self.tseitlin = tseitlin
            self.formulas = []
            self.varFinder = {self.name: self}
        else:
            self.formulas = formulas
            variables = set()
            varFinder = dict()
            for formula in formulas:
                varFinder.update(formula.varFinder)
                variables = variables.union(formula.variables)
            self.varFinder = varFinder
            self.variables = variables

    def __and__(self, other):
        return Formula(FT.AND, formulas=[self, other])

    def __or__(self, other):
        return Formula(FT.OR, formulas=[self, other])

    def __neg__(self):
        return Formula(FT.NEG, formulas=[self])

    def __le__(self, other):
        return Formula(FT.IMPLIES, formulas=[other, self])

    def __ge__(self, other):
        return Formula(FT.IMPLIES, formulas=[self, other])

    def flatten(self):
        for formula in self.formulas:
            formula.flatten()
        formulas = []
        if self.type is FT.AND or self.type is FT.OR:
            for formula in self.formulas:
                if formula.type == self.type:
                    formulas += formula.formulas
                else:
                    formulas += [formula]
            self.formulas = formulas

    def getName(self):
        """
        should only be called if literal
        """
        return next(iter(self.variables))

    def isLiteral(self):
        if self.type == FT.VAR:
            return True
        elif self.type == FT.NEG and self.formulas[0].type is FT.VAR:
            return True
        return False

    def toNNF(self):
        self.eliminateImplications()
        self.pushAndEliminateNegations()

    def toCNF(self):
        self.toNNF()
        self.distributeOrOverAnd()
        self.flatten()

    def eliminateImplications(self):
        """
        convert to equivilant formula without IMPLIES and IFF
        """
        if self.type is FT.IFF:
            self.type = FT.AND
            self.formulas = [self.formulas[0] <= self.formulas[1],
                             self.formulas[1] <= self.formulas[0]]
        formula: Formula
        for formula in self.formulas:
            formula.eliminateImplications()
        if self.type is FT.IMPLIES:
            self.type = FT.OR
            self.formulas = [- self.formulas[0], self.formulas[1]]

    def pushAndEliminateNegations(self):
        if self.type is FT.NEG:
            if self.formulas[0].type is FT.NEG:
                self.type = self.formulas[0].formulas[0].type
                self.formulas = self.formulas[0].formulas[0].formulas
                self.pushAndEliminateNegations()
                return
            # deMorgan
            elif self.formulas[0].type is FT.AND:
                self.type = FT.OR
                self.formulas = [-formula for formula in self.formulas[0].formulas]
            elif self.formulas[0].type is FT.OR:
                self.type = FT.AND
                self.formulas = [-formula for formula in self.formulas[0].formulas]
        for formula in self.formulas:
            formula.pushAndEliminateNegations()

    def distributeOrOverAnd(self):
        for formula in self.formulas:
            formula.distributeOrOverAnd()

        if self.type == FT.OR:
            for index, formula in enumerate(self.formulas):
                if formula.type is FT.AND:
                    self.type = FT.AND
                    self.formulas.pop(index)
                    if len(self.formulas) == 1:
                        self.formulas = [self.formulas[0] |
                                         inner for inner in formula.formulas]
                    else:
                        self.formulas = [
                            Formula(FT.AND, formulas=self.formulas) | inner for inner in formula.formulas]
                    break

    def toTseitlin(self):
        if self.isLiteral():
            self.toCNF()
            return

        tseitlinIndex = 1
        formulas = []

        def tseiltinRec(formula: Formula):
            nonlocal tseitlinIndex
            nonlocal formulas
            if not formula.isLiteral():
                if formula.tseitlinVar is None:
                    formula.tseitlinVar = Formula(
                        FT.VAR, varName="_ts_" + str(tseitlinIndex), tseitlin=True)
                    tseitlinIndex += 1
                for inner in formula.formulas:
                    formula.tseitlinVar = Formula(
                        FT.VAR, varName="_ts_" + str(tseitlinIndex), tseitlin=True)
                    tseitlinIndex += 1
                    tseiltinRec(inner)
                formulas.append(Formula(FT.IFF, [formula.tseitlinVar, Formula(formula.type, formulas=[
                                inner.tseitlinVar if not inner.isLiteral() else inner for inner in formula.formulas])]))

        tseiltinRec(self)
        formulas.append(Formula(FT.OR, [self.tseitlinVar]))
        tseitlinFormula = Formula(FT.AND, formulas=formulas)
        self.type = FT.AND
        self.formulas = tseitlinFormula.formulas
        self.variables = tseitlinFormula.variables
        for formula in self.formulas:
            formula.toCNF()
        self.varFinder = tseitlinFormula.varFinder
        self.flatten()

    def isRedundantFormula(self):
        """
        should be run on CNF clauses only, unexpected behavior overwise
        """
        if self.isLiteral():
            return False

        varMap = {}
        for literal in self.formulas:
            if literal.type is FT.VAR:
                if literal.getName() in varMap:
                    if varMap[literal.getName()] is False:
                        return True
                else:
                    varMap[literal.getName()] = True
            else:
                name = literal.formulas[0].getName()
                if name in varMap:
                    if varMap[name] is True:
                        return True
                else:
                    varMap[name] = False
        return False

    def removeRedundantLiterals(self):
        """
        should be run on CNF clauses only, unexpected behavior overwise
        works only after removal of redundant formulas
        """
        varSet = set()
        for index, literal in reversed(list(enumerate(self.formulas))):
            if literal.type is FT.VAR:
                if literal.getName() in varSet:
                    del self.formulas[index]
                else:
                    varSet.add(literal.getName())
            else:
                if literal.formulas[0].getName() in varSet:
                    del self.formulas[index]
                else:
                    varSet.add(literal.formulas[0].getName())

    def preprocess(self):
        self.toTseitlin()
        self.formulas = [
            formula for formula in self.formulas if not formula.isRedundantFormula()]
        for clause in self.formulas:
            clause.removeRedundantLiterals()

    def applyAssignment(self, assignment: dict):
        if self.type is FT.VAR:
            return assignment[self.getName()]
        if self.type is FT.NEG:
            return not self.formulas[0].applyAssignment(assignment)
        if self.type is FT.AND:
            return all([formula.applyAssignment(assignment) for formula in self.formulas])
        if self.type is FT.OR:
            return any([formula.applyAssignment(assignment) for formula in self.formulas])
        first = self.formulas[0].applyAssignment(assignment)
        second = self.formulas[1].applyAssignment(assignment)
        if self.type is FT.IFF:
            return first == second
        if self.type is FT.IMPLIES:
            return not (first and not second)

    def applyPartialAssignment(self, assignment: dict):
        if len(self .variables - assignment.keys()) > 0:
            return True
        return self.applyAssignment(assignment)

    def __getitem__(self, key):
        return self.formulas[key]

    def toString(self):
        if self.type is FT.VAR:
            return self.getName()

        string = self.type.name + "("
        first = True
        formula: Formula
        for formula in self.formulas:
            if not first:
                string += ","
            first = False
            string += formula.toString()
        string += ")"
        return string

    def __eq__(self, other):
        f1 = self
        f2 = other
        if not f1.variables == f2.variables:
            return False
        for assignment in getAssignmentGenerator(f1):
            if not f1.applyAssignment(assignment) == f2.applyAssignment(assignment):
                return False
        return True

    def __hash__(self):
        return self.toString().__hash__()

    def append(self, clause):
        """assumes clause doesn't have new variables

        Arguments:
            clause {Formula} -- clause to append
        """
        self.formulas.append(clause)

    def __contains__(self, formula):
        for f in self.formulas:
            if areEqualFormulas(f, formula):
                return True
        return False

    @classmethod
    def deduce(cls, f1, f2, literal):
        f3 = Formula(FT.OR, formulas=[lit for lit in f1.formulas if lit.getName(
        ) != literal]+[lit for lit in f2.formulas if lit.getName() != literal])
        f3.removeRedundantLiterals()
        return f3


def areEqualFormulas(f1: Formula, f2: Formula):
    if f1.type == f2.type:
        if len(f1.formulas) == len(f2.formulas):
            for i in range(len(f1.formulas)):
                if not areEqualFormulas(f1[i], f2[i]):
                    return False
            return True
    return False


def areEquivalentFormulas(f1: Formula, f2: Formula):
    if not f1.variables == f2.variables:
        return False
    for assignment in getAssignmentGenerator(f1):
        if not f1.applyAssignment(assignment) == f2.applyAssignment(assignment):
            return False
    return True


def getAssignmentGenerator(formula):
    vars = list(formula.variables)
    for subset in powerset(vars):
        assignment = {}
        for var in vars:
            if var in subset:
                assignment[var] = True
            else:
                assignment[var] = False
        yield assignment
