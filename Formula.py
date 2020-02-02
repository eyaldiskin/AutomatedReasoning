from enum import Enum


class ExpType(Enum):
    VAR = 1
    NEG = 2
    AND = 3
    OR = 4
    IMPLIES = 5
    IFF = 6


class Formula():
    def __init__(self, type: ExpType, expList: list = None, varName=None):
        if type is None:
            raise
        self.type = type
        if(type == ExpType.VAR):
            self.varList = {varName}
        else:
            if type == ExpType.NEG and len(expList) != 1:
                raise
            elif len(expList) < 2:
                raise
            self.expList = expList
            varList = {}
            for exp in expList:
                varList = varList.union(exp.varList)
            self.varList = varList

    def __and__(self, other):
        return Formula(ExpType.AND, expList=[self, other])

    def __or__(self, other):
        return Formula(ExpType.OR, expList=[self, other])

    def __neg__(self):
        return Formula(ExpType.NEG, expList=[self])

    def tseitlin(self):
        pass

    def preprocess(self):
        pass
