import Formula
import TData


class TUF:
    def __init__(self, formula: Formula):
        self.formula = formula.preprocess()
        self.symbols = dict()
        for t in TData.TType:
            self.symbols[t.name] = dict()
        self._get_symbols(self.formula)

    def _get_symbols(self, formula: Formula):
        for clause in formula.formulas:
            if clause.type == Formula.FT.VAR:
                if getattr(clause, "data", None):
                    self._insert_symbol(clause.data)
            else:
                self._get_symbols(clause)

    def _insert_symbol(self, data: TData):
        name = data.name
        type = data.type
        if type == TData.TType.VAR:
            self.symbols[type][name] = name
            return
        arity = len(data.arguments)
        if name in self.symbols[type] and self.symbols[type][name] != arity:
            raise
        else:
            self.symbols[type][name] = arity
        for argument in data.arguments:
            self._insert_symbol(argument)

    def UF_formula_to_boolean_representation(self):
        pass

    def congruence_closure(F, M):
        pass

    def _T_conflict(F, M):
        pass

    def _T_propagate(F, M):
        pass
