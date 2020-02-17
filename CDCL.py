from Formula import Formula, FT
from random import shuffle


class CDCL:
    def __init__(self, formula: Formula):
        formula.preprocess()
        self.formula = formula
        self.partialAssignment = {}
        self.watchLiterals = [[]] * len(formula.formulas)
        self.VSIDSScores = {}
        self.satisfied = [False] * len(formula.formulas)
        clause: Formula

        for index, clause in enumerate(formula.formulas):
            shuffle(clause)
            self.watchLiterals[index].append(clause[0].getName())
            if len(clause.variables) > 1:
                self.watchLiterals[index].append(clause[1].getName())
            literal: Formula
            for literal in clause:
                if literal in self.VSIDSScores.keys:
                    self.VSIDSScores[literal] += 1
                else:
                    self.VSIDSScores[literal] = 1

    # use VSIDS heuristics

    def _decide(self):
        literal: Formula
        literal = max({k: v for k, v in self.VSIDSScores if k.getName(
        ) not in self.partialAssignment.keys}, key=self.VSIDSScores.__getitem__)
        self.partialAssignment[literal.getName()] = literal.type == FT.VAR
        # TODO - add decision to implication graph

    # TODO - understand when to call

    def _VSIDSDivideScores(self):
        self.VSIDSScores = {k: v/2 for k, v in self.VSIDSScores.values}

    def _learn(self, clause):
        self.formula.append(clause)
        self.watchLiterals.append([])

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

        # TODO - add propagation to implication graph
        
        clause: Formula
        for clause in self.formula:
            if clause.applyPartialAssignment(self.partialAssignment) is False:
                return False
        return self._propagate()

    def _updateWatchLiterals(self, literal: Formula):
        for index, watchers in enumerate(self.watchLiterals):
            if literal.getName() in [watcher.getName() for watcher in watchers]:
                self.watchLiterals[index] = [watcher.getName(
                ) for watcher in watchers if watcher.getName() != literal.getName()]
                for literal in self.formula[index]:
                    if literal.getName() not in self.partialAssignment.keys and literal.getName() is not watchers[0]:
                        self.watchLiterals[index].append(literal.getName())
                        break

    def _conflict(self):
        pass

    # conflict analysis (UIP finder)
    def _explain(self):
        pass

    def _backjump(self):
        pass

    def solveRec(self):
        pass

    def solve(self):
        pass
