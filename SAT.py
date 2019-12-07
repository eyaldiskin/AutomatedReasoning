import boolean.boolean as boolean


algebra = boolean.BooleanAlgebra()


def preproccess(formula: boolean.Expression):
    """
    gets a formula in cnf form
    returns an equivelant formula without redundant clauses
    """
    if(type(formula) == boolean.AND):
        args = formula.args
        new_args = []
        for arg in args:
            arg = arg.simplify()
            if not(arg == algebra.TRUE):
                new_args.append(arg)

        if(len(new_args) == 0):
            return algebra.TRUE
        if(len(new_args)>1):
            return boolean.AND(*new_args)
        return new_args[0]
    return formula


def tseitlin(formula: boolean.Expression):
    """
    gets a boolean formula
    return the tseitlin transformation of that formula
    """
    pass
