from enum import Enum


class UFType(Enum):
    VAR = 1
    FOO = 2
    PRED = 3


class UFData:
    def __init__(self, type: UFType, name, arguments: list = None):
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
        if type == UFType.VAR:
            self.variables = {name}
        else:
            self.arguments = arguments
            self.variables = set()
            for data in arguments:
                self.variables = self.variables.union(data.variables)

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type.name

    def __eq__(self, other):
        if self.type != other.type or self.name != other.name:
            return False
        if self.type == UFType.VAR:
            return True
        for i in range(len(self.arguments)):
            if self.arguments[i] != other.arguments[i]:
                return False
        return True

    def __str__(self):
        if self.type == UFType.VAR:
            return self.name
        if self.type == UFType.PRED:
            return str(self.arguments[0]) + self.name + str(self.arguments[1])

        string = self.name + "("
        for arg in self.arguments:
            string += str(arg) + ","
        string = string[:-1] + ")"
        return string
