from Formula import Formula, FT
from random import shuffle
from ImplicationGraph import ImplicationGraph


class CDCL:
    def __init__(self, formula: Formula):
        formula.preprocess()
        self.formula = formula
        self.partialAssignment = {}
        self.clauseFinder = {}
        self.watchLiterals = [[] for i in range(len(formula.formulas))]
        self.VSIDSScores = {}
        self.satisfied = [False] * len(formula.formulas)
        self.graph = ImplicationGraph()
        self.level = 0
        self.totalSteps = 0
        clause: Formula

        for index, clause in enumerate(formula.formulas):
            shuffle(clause.formulas)
            self.watchLiterals[index].append(clause[0])
            if len(clause.variables) > 1:
                self.watchLiterals[index].append(clause[1])
            literal: Formula
            for literal in clause.formulas:
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
        unassigned = {k: self.VSIDSScores[k] for k in self.VSIDSScores.keys(
        ) if k.getName() not in self.partialAssignment.keys()}
        literal = max(unassigned, key=unassigned.get)
        print("decided " + literal.toString())
        self.partialAssignment[literal.getName()] = literal.type == FT.VAR
        for index in self.clauseFinder[literal]:
            self.satisfied[index] = True
        self.level += 1
        self.graph.addRoot(literal.getName(),
                           literal.type == FT.VAR, self.level)
        self._updateWatchLiterals(literal)

    # TODO - understand when to call

    def _VSIDSDivideScores(self):
        self.VSIDSScores = {k: self.VSIDSScores[k]/2 for k in self.VSIDSScores}

    def _learn(self, clause):
        self.formula.append(clause)
        self.watchLiterals.append([])
        self.satisfied.append(False)
        for literal in clause.formulas:
            self.clauseFinder[literal].append(len(self.satisfied) - 1)
            self.VSIDSScores[literal] += 1

    def _propagate(self):
        """
        BCP
        Arguments:
            literal {Formula} -- literal to propagate
        """
        literal = None
        selected = 0
        for index, watchers in enumerate(self.watchLiterals):
            if len(watchers) is 1 and not self.satisfied[index]:
                literal = watchers[0]
                selected = index
                break
        # maybe move this to _decide?
        if literal is None:
            for index, clause in enumerate(self.formula.formulas):
                if not self.satisfied[index]:
                    if clause.applyPartialAssignment(self.partialAssignment) is False:
                        self.graph.addNode(None, clause, conflict=True)
            return True
        print("propagated " + literal.toString())
        self.partialAssignment[literal.getName()] = literal.type is FT.VAR

        for index in self.clauseFinder[literal]:
            self.satisfied[index] = True

        self.graph.addNode(literal.type is FT.VAR,
                           self.formula[selected], literal.getName())

        self._updateWatchLiterals(literal)

        # probably needs oprimizing
        clause: Formula
        for clause in self.formula.formulas:
            if clause.applyPartialAssignment(self.partialAssignment) is False:
                self.graph.addNode(None, clause, conflict=True)
                return False
        return self._propagate()

    def _updateWatchLiterals(self, literalSelected: Formula):
        for index, watchers in enumerate(self.watchLiterals):
            if literalSelected.getName() in [watcher.getName() for watcher in watchers]:
                self.watchLiterals[index] = [
                    watcher for watcher in watchers if not watcher.getName() == literalSelected.getName()]
                for literal in self.formula[index].formulas:
                    if literal.getName() not in self.partialAssignment.keys() and not literal in watchers:
                        self.watchLiterals[index].append(literal)
                        break

    # conflict analysis (UIP finder)

    def _explain(self):
        uip = self.graph.findUIP(self.level)
        return self.graph.resolveConflict(uip)

    def _backjump(self, level):
        self.graph.backjump(level)
        self.level = level
        self.partialAssignment = {var: self.partialAssignment[var] for var in self.partialAssignment if var in [
            node.varName for node in self.graph.nodes]}
        self.satisfied = [False] * len(self.formula.formulas)
        # create satisfied list
        for var in self.partialAssignment:
            val = self.partialAssignment[var]
            if val:
                for index in self.clauseFinder[self.formula.varFinder[var]]:
                    self.satisfied[index] = True
            else:
                for index in self.clauseFinder[Formula(FT.NEG, [self.formula.varFinder("var")])]:
                    self.satisfied[index] = True
        # update watch literals
        self.watchLiterals = [[] for i in range(len(self.formula.formulas))]
        for index, clause in enumerate(self.formula.formulas):
            if not self.satisfied[index]:
                shuffle(clause.formulas)
                relevant = [lit for lit in clause.formulas if lit.getName(
                ) not in self.partialAssignment.keys()]
                self.watchLiterals[index].append(relevant[0])
                if len(relevant) > 1:
                    self.watchLiterals[index].append(relevant[1])

    def solve(self, steps=-1, onlyPropagate=False):
        while steps != 0:
            if not self._propagate():
                if self.level is 0:
                    return False
                conflict, level = self._explain()
                self._learn(conflict)
                self._backjump(level)
                continue
            if len([sat for sat in self.satisfied if not sat]) is 0:
                return True
            if onlyPropagate:
                break
            self._decide()
            if len([sat for sat in self.satisfied if not sat]) is 0:
                return True
            steps -= 1
            self.totalSteps += 1
            if self.totalSteps % 5 == 0:
                self._VSIDSDivideScores()
        return None

    def getAssignment(self):
        for var in self.formula.variables:
            if var not in self.partialAssignment:
                self.partialAssignment[var] = True
        return {k: self.partialAssignment[k] for k in self.partialAssignment if not self.formula.varFinder[k].tseitlin}

    def assign(self, variable, value):
        self.partialAssignment[variable.getName()] = value
        self._updateWatchLiterals(variable)
        if not value:
            variable = -variable
        for index in self.clauseFinder[variable]:
            self.satisfied[index] = True

    def learnConflict(self, conflictClause):
        self._learn(conflictClause)
        self._backjump(self.graph.getSecondLargestLevel(conflictClause))

# TODO - add "assign" and "learnConflict" for SMT
