import boolean.boolean as boolean


class ExtendedAlgebra(boolean.BooleanAlgebra):
    '''
    This class extends the regular boolean algebra by including the operations iff, xor and
    both directions of implying.
    '''

    def __init__(self, TRUE_class=None, FALSE_class=None, Symbol_class=None,
                 NOT_class=None, AND_class=None, OR_class=None, IFF_class=None,
                 XOR_class = None, IMPS_class=None, IMPD_class=None,
                 allowed_in_token=('.', ':', '_')):

        boolean.BooleanAlgebra.__init__(self, TRUE_class, FALSE_class, Symbol_class,
                 NOT_class, AND_class, OR_class,
                 allowed_in_token)

        self.IFF = IFF_class or IFF
        self.XOR = XOR_class or XOR
        self.IMPS = IMPS_class or IMPS
        self.IMPD = IMPD_class or IMPD

        tf_nao = {
            'TRUE': self.TRUE,
            'FALSE': self.FALSE,
            'NOT': self.NOT,
            'AND': self.AND,
            'OR': self.OR,
            'Symbol': self.Symbol,
            'IFF': self.IFF,
            'XOR': self.XOR,
            'IMPS': self.IMPS,
            'IMPD': self.IMPD
        }

        # setup cross references such that all algebra types and
        # objects hold a named attribute for every other types and
        # objects, including themselves.
        for obj in tf_nao.values():
            for name, value in tf_nao.items():
                setattr(obj, name, value)

        # Set the set of characters allowed in tokens
        self.allowed_in_token = allowed_in_token

    def definition(self):
        """
        Return a tuple of this algebra defined elements and types as:
        (TRUE, FALSE, NOT, AND, OR, Symbol)
        """
        return self.TRUE, self.FALSE, self.NOT, self.AND, self.OR, self.Symbol, self.IFF, \
               self.XOR, self.IMPS, self.IMPD


class IFF(boolean.DualBase):
    """
    Boolean IFF operation, taking 2 arguments.
    It can also be created by using "=" between two boolean expressions.
    """

    sort_order = 50

    def __init__(self, arg1, arg2):
        super(IFF, self).__init__(arg1, arg2)
        self.dual = self.XOR
        self.operator = '='


class XOR(boolean.DualBase):
    """
    Boolean XOR operation, taking 2 arguments.
    It can also be created by using "^" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 50

    def __init__(self, arg1, arg2):
        super(XOR, self).__init__(arg1, arg2)
        self.dual = self.IFF
        self.operator = '^'


class IMPS(boolean.Function):
    """
    Boolean IMPS operation, taking 2 arguments.
    It can also be created by using ">" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 40

    def __init__(self, arg1, arg2):
        super(IMPS, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.operator = '>'
    # todo simplify


class IMPD(boolean.Function):
    """
    Boolean IMPD operation, taking 2 arguments.
    It can also be created by using "<" between two boolean expressions.
    You can subclass to define alternative string representation.
    """
    sort_order = 40

    def __init__(self, arg1, arg2):
        super(IMPD, self).__init__(arg1, arg2)
        self.identity = self.TRUE
        self.annihilator = self.FALSE
        self.operator = '<'
    # todo simplify
