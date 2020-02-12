from Formula import Formula, FT


class CDCL:
    def __init__(self, formula: Formula):
        formula.preprocess()
        self.formula = formula
        self.partialAssignment = {}
        self.watchLiterals = [[]] * len(formula.formulas)
        clause: Formula
        for index, clause in enumerate(formula.formulas):
            self.watchLiterals[index].append(clause.formulas[0])
            if len(clause.variables) > 1:
                self.watchLiterals[index].append(clause.formulas[1])

    # use VSIDS heuristics

    def _decide(self):
        pass

    def _learn(self):
        pass

    def _propagate(self):
        """
        BCP
        Arguments:
            literal {Formula} -- literal to propagate
        """
        literal = None
        for watchers in self.watchLiterals:
            if len(watchers) is 1:
                literal = watchers[0]
                break
        if literal is None:
            return True
        if literal.type is FT.VAR:
            self.partialAssignment[literal.getName()] = True
        else:
            self.partialAssignment[literal.getName()] = False

        self._updateWatchLiterals(literal)

        clause: Formula
        for clause in self.formula:
            if clause.applyPartialAssignment(self.partialAssignment) is False:
                return False
        return self._propagate()

    def _updateWatchLiterals(self, literal):
        pass

    def _conflict(self):
        pass

    # conflict analysis (UIP finder)
    def _explain(self):
        pass

    def _backjump(self):
        pass

    def solve(self):
        pass
