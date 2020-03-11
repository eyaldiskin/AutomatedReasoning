from Formula import Formula, FT
from random import shuffle
from ImplicationGraph import ImplicationGraph


class CDCL:
    def __init__(self, formula: Formula):
        formula.preprocess()
        self.formula = formula
        self.partialAssignment = {}
        self.clauseFinder = {}
        self.watchLiterals = [[]] * len(formula.formulas)
        self.VSIDSScores = {}
        self.satisfied = [False] * len(formula.formulas)
        self.graph = ImplicationGraph()
        self.level = 0
        clause: Formula

        for index, clause in enumerate(formula.formulas):
            shuffle(clause.formulas)
            self.watchLiterals[index].append(clause[0])
            if len(clause.variables) > 1:
                self.watchLiterals[index].append(clause[1])
            literal: Formula
            for literal in clause:
                if literal in self.clauseFinder.keys():
                    self.clauseFinder[literal].append(index)
                else:
                    self.clauseFinder[literal] = [index]

                if literal in self.VSIDSScores.keys():
                    self.VSIDSScores[literal] += 1
                else:
                    self.VSIDSScores[literal] = 1

    # use VSIDS heuristics

    def _decide(self):
        literal: Formula
        literal = max({k: v for k, v in self.VSIDSScores if k.getName(
        ) not in self.partialAssignment.keys()}, key=self.VSIDSScores.__getitem__)
        self.partialAssignment[literal.getName()] = literal.type == FT.VAR
        for index in self.clauseFinder[literal]:
            self.satisfied[index] = True
        self.level += 1
        self.graph.addRoot(literal.getName(),
                           literal.type == FT.VAR, self.level)

    # TODO - understand when to call

    def _VSIDSDivideScores(self):
        self.VSIDSScores = {k: v/2 for k, v in self.VSIDSScores.values}

    def _learn(self, clause):
        self.formula.append(clause)
        self.watchLiterals.append([])
        self.satisfied.append(False)
        for literal in clause:
            self.clauseFinder[literal].append(len(self.satisfied) - 1)

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
        # maybe move this to _decide?
        if literal is None:
            for index, clause in enumerate(self.formula):
                if not self.satisfied[index]:
                    if clause.applyPartialAssignment(self.partialAssignment) is False:
                        self.graph.addNode(None, clause, conflict=True)
            return True

        self.partialAssignment[literal.getName()] = literal.type is FT.VAR

        for index in self.clauseFinder[literal]:
            self.satisfied[index] = True

        self.graph.addNode(literal.type is FT.VAR,
                           self.formula[index], literal.getName())

        self._updateWatchLiterals(literal)

        # probably needs oprimizing
        clause: Formula
        for clause in self.formula:
            if clause.applyPartialAssignment(self.partialAssignment) is False:
                self.graph.addNode(None, clause, conflict=True)
                return False
        return self._propagate()

    def _updateWatchLiterals(self, literal: Formula):
        for index, watchers in enumerate(self.watchLiterals):
            if not self.satisfied[index]:
                if literal.getName() in [watcher.getName() for watcher in watchers]:
                    self.watchLiterals[index] = [watcher.getName(
                    ) for watcher in watchers if watcher.getName() != literal.getName()]
                    for literal in self.formula[index]:
                        if literal.getName() not in self.partialAssignment.keys() and literal.getName() is not watchers[0]:
                            self.watchLiterals[index].append(literal.getName())
                            break

    # conflict analysis (UIP finder)

    def _explain(self):
        uip = self.graph.findUIP(self.level)
        return self.graph.resolveConflict(uip)

    def _backjump(self, level):
        self.graph.backjump(level)
        self.level = level
        self.partialAssignment = {var: val for var, val in self.partialAssignment if var in [
            node.getName() for node in self.graph.nodes]}
        self.satisfied = [False] * len(self.formula.formulas)
        # create satisfied list
        for var, val in self.partialAssignment:
            if val:
                for index in self.clauseFinder[self.formula.varFinder("var")]:
                    self.satisfied[index] = True
            else:
                for index in self.clauseFinder[Formula(FT.NEG, [self.formula.varFinder("var")])]:
                    self.satisfied[index] = True
        # update watch literals
        for index, clause in enumerate(self.formula.formulas):
            if not self.satisfied[index]:
                shuffle(clause)
                relevant = [lit for lit in clause.formulas if lit.getName(
                ) not in self.partialAssignment.keys()]
                self.watchLiterals[index].append(relevant[0])
                if len(relevant) > 1:
                    self.watchLiterals[index].append(relevant[1])

    def solve(self, steps=-1, onlyPropagate=False):
        while steps != 0:
            if not self._propagate:
                if self.level is 0:
                    return False
                conflict, level = self._explain()
                self._learn(conflict)
                self._backjump(level)
                continue
            if len([sat for sat in self.satisfied if sat]) is 0:
                return True
            if onlyPropagate:
                break
            self._decide()
            if len([sat for sat in self.satisfied if sat]) is 0:
                return True
            steps -= 1
        return None

# TODO - add "assign" and "learnConflict" for SMT
