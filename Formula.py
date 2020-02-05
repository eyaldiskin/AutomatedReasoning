from enum import Enum


class FT(Enum):
    VAR = 1
    NEG = 2
    AND = 3
    OR = 4
    IMPLIES = 5
    IFF = 6


class Formula():
    def __init__(self, type: FT,
                 formulas: list = None, varName=None, data=None, tseitlin=False):
        if type is None:
            raise
        self.type = type
        if data is not None:
            self.data = data
        if(type == FT.VAR):
            self.variables = {varName}
            self.tseitlin = tseitlin
            self.formulas = []
        else:
            self.formulas = formulas
            variables = {}
            for formula in formulas:
                variables = variables.union(formula.varList)
            self.variables = variables

    def __and__(self, other):
        return Formula(FT.AND, formulas=[self, other])

    def __or__(self, other):
        return Formula(FT.OR, formulas=[self, other])

    def __neg__(self):
        return Formula(FT.NEG, formulas=[self])

    def __eq__(self, other):
        return Formula(FT.IFF, formulas=[self, other])

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
        self.distributeAndOverOr()
        self.flatten()

    def eliminateImplications(self):
    """
    convert to equivilant formula without IMPLIES and IFF 
    """
    if self.type is FT.IFF:
        self.type = FT.AND
        self.formulas = [self.formulas[0] <= self.formulas[1],
                         self.formulas[1] <= self.formulas[0]]
    for formula in self.formulas:
        formula.eliminateImplications()
    if self.type is FT.IMPLIES:
        self.type = FT.OR
        self.formulas = [-self.formulas[0], self.formulas[1]]

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

    # might be the wrong name for function
    def distributeAndOverOr(self):
        if self.type == FT.OR:
            for index, formula in enumerate(self.formulas):
                if formula.type is FT.AND:
                    self.type = FT.AND
                    self.formulas = [inner | self.formulas.pop(index) for inner in formula[]]
                    break
        for formula in self.formulas:
            formula.distributeAndOverOr()

    def toTseitlin(self):
        tseitlinIndex = 1
        formulas = []

        def tseiltinRec(formula: Formula):
            if not formula.isLiteral():
                if not hasattr(formula, "tseitlinVar"):
                    formula.tseitlinVar = Formula(
                        FT.VAR, varName="_ts_" + tseitlinIndex, tseitlin=True)
                    tseitlinIndex += 1
                for inner in formula.formulas:
                    formula.tseitlinVar = Formula(
                        FT.VAR, varName="_ts_" + tseitlinIndex, tseitlin=True)
                    tseitlinIndex += 1
                    tseiltinRec(inner)
                formulas.append(formula.tseitlinVar == Formula(formula.type, formulas=[
                                inner.tseitlinVar if not inner.isLiteral() else inner for inner in formula.formulas]))

        tseiltinRec(self)
        formulas.append(self.tseitlinVar)
        tseitlinFormula = Formula(FT.AND, formulas=formulas)
        self.type = TF.AND
        self.formulas = tseitlinFormula.formulas
        self.variables = tseitlinFormula.variables
        for formula in self.formulas:
            formula.toCNF()

    def preprocess(self):
        pass
