import boolean.boolean as boolean


class IFF(boolean.DualBase):
    """
    Boolean IFF operation, taking 2 arguments.
    It can also be created by using "=" between two boolean expressions.
    """

    sort_order = 10

    def __init__(self, arg1, arg2):
        super(IFF, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.dual = self.XOR
        self.operator = '='


class XOR(boolean.DualBase):
    """
    Boolean XOR operation, taking 2 arguments.
    It can also be created by using "^" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 10

    def __init__(self, arg1, arg2):
        super(XOR, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.dual = self.IFF
        self.operator = '^'


class IMPS(boolean.DualBase):
    """
    Boolean IMPS operation, taking 2 arguments.
    It can also be created by using ">" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 10

    def __init__(self, arg1, arg2):
        super(IMPS, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.dual = None
        self.operator = '>'


class IMPD(boolean.DualBase):
    """
    Boolean IMPD operation, taking 2 arguments.
    It can also be created by using "<" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 10

    def __init__(self, arg1, arg2):
        super(IMPD, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.dual = None
        self.operator = '<'
