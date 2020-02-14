from enum import Enum


class TType(Enum):
    VAR = 1
    FUN = 2
    PRED = 3


class TData:
    def __init__(self, type: TType, name, arguments: list = None):
        """
        :param type: the type of this data - variable, function or predicate
        :param name: its' name, i.e. the name of f(x) is "f" and the name of x=y is "="
        :param arguments: if it's not a variable, a list of the arguments of this
                predicate\function by order, i.e. for f(x,y,x) it will be [x, y, x] and for
                f(x)=g(y) it will be [f(x),g(y)]
        """
        if type is None:
            raise
        self.type = type
        self.name = name
        if type == TType.VAR:
            self.variables = {name}
        else:
            self.arguments = arguments
            variables = set()
            for data in arguments:
                variables = variables.union(data.variables)
            self.variables = variables

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type.name

    # def applyAssignment(self, assignment: dict):
    #     if self.type is FT.VAR:
    #         return assignment[self.name]
    #     if self.type is FT.NEG:
    #         return not self.formulas[0].applyAssignment(assignment)
    #     if self.type is FT.AND:
    #         return all([formula.applyAssignment(assignment) for formula in self.formulas])
    #     if self.type is FT.OR:
    #         return any([formula.applyAssignment(assignment) for formula in self.formulas])
    #     first = self.formulas[0].applyAssignment(assignment)
    #     second = self.formulas[1].applyAssignment(assignment)
    #     if self.type is FT.IFF:
    #         return first == second
    #     if self.type is FT.IMPLIES:
    #         return not (first and not second)
    #
    # def applyPartialAssignment(self, assignment: dict):
    #     if len(self .variables - assignment.keys) > 0:
    #         return True
    #     return self.applyAssignment(assignment)
