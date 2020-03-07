import numpy as np
import re
np.seterr(divide='ignore', invalid='ignore')

# LP solver consts
STRATEGIES = 2
BLAND = 0
DANTZIG = 1
LU_FACT_SIZE_LIMIT = 500
EPSILON = 10**(-20)

# equations consts
EQ = '='
NEQ = '!='
GT = '>'
GEQ = '>='
LT = '<'
LEQ = '<='

VARIABLE_PATTERN = re.compile('[\-]?\d*\.?\d*[_A-z]+\d*')
CONST_PATTERN = re.compile('[\-]?\d*\.?\d+')
PROPOSITION_PATTERN = re.compile('[!=><]{1,2}')
COEFFICIENT_PATTERN = re.compile('[\-]?\d*\.?\d+|\-')
GENERAL_TOKEN_PATTERN = re.compile('[\-]?\d*\.?\d*[_A-z]+\d*|[\-]?\d*\.?\d+|[!=><]{1,2}')

class eta_matrix:
    def __init__(self, col_index, col_content):
        self.col_content = col_content
        self.col_index = col_index
        self.size = len(col_content)

    def BTRAN(self,result):
        left_vector = np.array([result[i] for i in range(self.size)]).astype(float)
        left_vector[self.col_index] = 0

        left_vector[self.col_index] = (result[self.col_index] - (left_vector @ self.col_content))/self.col_content[self.col_index]
        return left_vector

    def FTRAN(self,result):
        right_vector = np.zeros(len(result))
        right_vector[self.col_index] = np.array(result[self.col_index]).astype(float)/self.col_content[self.col_index]
        for j in range(self.size):
            if j == self.col_index: continue
            right_vector[j] = result[j] - self.col_content[j]*right_vector[self.col_index]

        return right_vector

    def invert(self):
        self.col_content[self.col_index] = 1/self.col_content[self.col_index]
        for i in range(self.size):
            if i == self.col_index: continue
            self.col_content[i] = -self.col_content[i]* self.col_content[self.col_index]


    def as_matrix(self):
        matrix = np.identity(self.size)
        for i in range(self.size):
            matrix[i, self.col_index] = self.col_content[i]
        return matrix

    def __repr__(self):
        return str(self.as_matrix())+'\n'

class LP_solver:

    def __init__(self, A, b, c):

        self.strategies_pool = [None for _ in range(STRATEGIES)]
        self.strategies_pool[BLAND] = self._Blands_rule
        self.strategies_pool[DANTZIG] = self._Dantzigs_rule

        self.A = A
        self.b = b
        self.c = c

        m, n = self.A.shape

        self.X_B = np.arange(n-m,n)
        self.X_N = np.arange(0,n-m)

        self.X_B_star = None

        self.A_B = None
        self._LU_factorization()

    def _FTRAN(self, entering_var):
        result = self.A[:,entering_var]
        for eta in self.A_B:
            result = eta.FTRAN(result)

        return result

    def _b_FTRAN(self):
        result = self.b
        for eta in self.A_B:
            result = eta.FTRAN(result)

        return result
        #d = np.linalg.inv(self.A[:,self.X_B]) @ self.A[:,entering_var]
        #return d

    def _BTRAN(self):
        result = self.c[self.X_B]
        for eta in reversed(self.A_B):
            result = eta.BTRAN(result)

        #y = self.c[self.X_B] @ np.linalg.inv(self.A[:,self.X_B])
        return result

    def _Blands_rule(self,z):
        entering_var = np.inf

        for i in range(len(z)):
            if z[i] >= EPSILON:
                entering_var = self.X_N[i]
                break

        return entering_var

    def _Dantzigs_rule(self,z):
        if max(z) >= EPSILON :
            entering_var = self.X_N[np.argmax(z)]
        else:
            entering_var = np.inf

        return entering_var

    def _LU_factorization(self):
        d_matrix = self.A[:,self.X_B].astype(float)
        L = []
        U = []

        #generate L_i according to Gaussian elimination
        for i in range(len(self.X_B)):
            eta_col = np.zeros(len(self.X_B))
            for j in range(i+1, len(self.X_B)):
                eta_col[j] = -d_matrix[j,i]/d_matrix[i,i]

            eta_col[i] = 1
            L += [eta_matrix(i,eta_col)]

            # keep working on L_i * d_matrix
            d_matrix = L[-1].as_matrix() @ d_matrix

        #generate U_i matrices by simply braking d_mat to colunms
        for i in range(len(self.X_B)):
            U += [eta_matrix(i,d_matrix[:,i])]

        #invert L's
        for eta in L:
            eta.invert()

        #reverse U's
        U.reverse()

        self.A_B = L+U
        return L+U

    def print_current_assignment(self):
        if self.X_B_star is None:
            print('no assignments are known')
            return

        assignment = [0 for _ in range(self.A.shape[1])]
        for i in range(len(self.X_B)):
            assignment[self.X_B[i]] = self.X_B_star[i]

        assignment = np.around(assignment, decimals=5)

        print('current assignment: ',assignment)
        print('current obj = ',assignment @ self.c)

    def get_current_assignment(self):
        if self.X_B_star is None:
            return('no assignments are known',None)

        assignment = [0 for _ in range(self.A.shape[1])]
        for i in range(len(self.X_B)):
            assignment[self.X_B[i]] = self.X_B_star[i]

        assignment = np.around(assignment, decimals=5)

        return (assignment,assignment @ self.c)

    def print_inner_state(self):
        print('A: ', self.A)
        print('b: ', self.b)
        print('c: ', self.c)
        print('X_B: ', self.X_B)
        print('X_N: ', self.X_N)
        print('A_B: ', self.A[:,self.X_B])
        print('A_N: ', self.A[:,self.X_N])
        print('c_B: ', self.c[self.X_B])
        print('c_N: ', self.c[self.X_N])
        print('X_B_star: ', self.X_B_star)
        print('LU fact length: ',str(len(self.A_B)))
        # print('LU_fact = ', self.A_B)

    def _debug_print(self, content, debug_flag):
        if debug_flag:
            print(content)

    def set_initial_feasible_solution(self, debug_flag, strategy):

        #if possible- just use the 0 assignment and finish
        if min(self.b) >= 0:
            self.X_B_star = self.b[:].astype(float)
            return True

        #if it's a non-trivial issue- solve the auxilery problem
        else:

            self._debug_print(('################# auxiliary problem created ###########################'), debug_flag)
            #generate auxiliry problem object
            x0_col = np.full((self.A.shape[0], 1), -1.)

            new_obj = np.zeros(self.A.shape[1] + 1)
            new_obj[0] = -1

            auxiliary = LP_solver(np.append(x0_col, self.A, axis=1), self.b, new_obj)

            #manually set first assingment
            auxiliary.X_B_star = auxiliary.b[:].astype(float)

            entering_var = 0
            leaving_var = np.argmin(auxiliary.b)

            auxiliary.X_N[0] = auxiliary.A.shape[1] - auxiliary.A.shape[0] + leaving_var
            auxiliary.X_B[leaving_var] = entering_var

            auxiliary.X_B_star[leaving_var] = 0
            auxiliary.X_B_star += -auxiliary.b[leaving_var]

            auxiliary._LU_factorization()

            #solve
            auxiliary.solve(debug_flag, strategy,True)

            #exctract feasible solution for self
            if 0 in auxiliary.X_B and auxiliary.X_B_star[np.where(auxiliary.X_B==0)] != 0 :
                print('no feasible solution found')
                return False

            else:
                self.X_B = auxiliary.X_B - 1
                self.X_B_star = auxiliary.X_B_star

                if -1 in self.X_B:
                    self.X_B[np.where(self.X_B == -1)] = auxiliary.X_N[0]-1
                    auxiliary.X_N[0] = 0
                self.X_N = auxiliary.X_N[auxiliary.X_N != 0] - 1
                self._LU_factorization()

                self._debug_print(('################# auxiliary problem solved ###########################'),
                                  debug_flag)
                if debug_flag: self.print_inner_state()
                return True


    def solve(self, debug_flag,strategy, stop_on_zero=False):

        #make sure we start from an initial feasible assignment
        if self.X_B_star is None:
            if not self.set_initial_feasible_solution(debug_flag, strategy):
                return

        iteration_number = 1
        while(True):
            self._debug_print(('--------------iteration ', iteration_number, '-----------------'), debug_flag)
            if debug_flag: self.print_inner_state()

            # calculate entering var
            y = self._BTRAN()
            self._debug_print(('y= ',y),debug_flag)

            optional_z_coefficients =  self.c[self.X_N] - y@self.A[:,self.X_N]
            self._debug_print(('optional_z_coefficients= ',optional_z_coefficients),debug_flag)

            entering_var = self.strategies_pool[strategy](optional_z_coefficients)
            self._debug_print(('entering_var= ', entering_var), debug_flag)

            if np.isinf(entering_var):
                print('optimal result was found')
                return

            # calculate leaving var
            d = self._FTRAN(entering_var)
            self._debug_print(('d= ', d), debug_flag)


            t_bounds = self.X_B_star / d
            for i in range(len(t_bounds)):
                if t_bounds[i] <= 0 :
                    t_bounds[i] = np.inf
            self._debug_print(('t_bounds= ', t_bounds), debug_flag)

            t = min(t_bounds)
            if np.isinf(t):
                print('unbounded problem, increase var x_'+str(entering_var+1)+' to inf')
                return

            self._debug_print(('t= ', t), debug_flag)
            leaving_var = self.X_B[np.argmin(t_bounds)]
            self._debug_print(('leaving_var= ', leaving_var), debug_flag)


            # update data structure
            p = None #show me a runtime error if LU decomp is broken
            for i in range(len(self.X_B)):
                if self.X_B[i] == leaving_var:
                    self.X_B[i] = entering_var
                    p = i

            for i in range(len(self.X_N)):
                if self.X_N[i] == entering_var:
                    self.X_N[i] = leaving_var

            self.X_B_star -= d*t
            self.X_B_star[np.argmin(t_bounds)] = t

            self.A_B += [eta_matrix(p,d)]

            if debug_flag: self.print_current_assignment()

            if stop_on_zero and self.c[self.X_B] @ self.X_B_star == 0:
                return

            #check for numeric issues
            if len(self.A_B) > LU_FACT_SIZE_LIMIT:
                self._LU_factorization()

            if d[p] <= EPSILON:
                self._LU_factorization()

            X_B_STAR_hat = self._b_FTRAN()
            delta = abs(X_B_STAR_hat - self.X_B_star)
            valid_delta = [True if j <= EPSILON else False for j in delta]
            if not all(valid_delta):
                self._LU_factorization()


            iteration_number += 1

class equstion:

    def __init__(self, formula):
        self.variables = {}
        self.const_value = None
        self.proposition = None
        self.slack_use = False

        #parse formula string
        tokens = GENERAL_TOKEN_PATTERN.findall(re.sub('\s','',formula))
        proposition_seen_flag = False

        for t in tokens:
            if VARIABLE_PATTERN.match(t):
                match = COEFFICIENT_PATTERN.match(t)
                if match:
                    coefficient = t[match.start():match.end()]
                    if coefficient == '-':
                        coefficient = '-1'

                    var_name = t[match.end():]
                else:
                    coefficient = '1'
                    var_name = t

                if var_name not in self.variables:
                    self.variables[var_name] = 0

                if proposition_seen_flag: #we are on the right side of the equation. flip sign.
                    self.variables[var_name] -= float(coefficient)
                else:
                    self.variables[var_name] += float(coefficient)


            elif CONST_PATTERN.match(t):
                if self.const_value is None:
                    self.const_value = 0

                if proposition_seen_flag: #we are on the right side of the equation. flip sign.
                    self.const_value += float(t)
                else:
                    self.const_value -= float(t)

            elif PROPOSITION_PATTERN.match(t):
                if proposition_seen_flag: #two propositions detected. invalid formula
                    self.proposition = None

                    return

                proposition_seen_flag = True
                self.proposition = t

    def __repr__(self):
        description = ''
        for key, value in self.variables.items():
            description += '+ ('+str(value)+key+') '
        if self.slack_use:
            description += '+slack '
        description += self.proposition + ' '
        description += ' '+str(self.const_value)
        return description

    def check_validity(self):
        if not bool(self.variables):
            return False
        if self.const_value is None:
            return False
        if self.proposition is None:
            return False

        return True

    def get_all_vars_names(self):
        return set(self.variables.keys())

    def get_slack_status(self):
        return self.slack_use

    def get_matrix_format(self, vars_order):
        assert self.proposition == LEQ

        row_len = len(vars_order) +1
        single_row = np.zeros(row_len)

        for i in range(len(vars_order)):
            if vars_order[i] in self.variables:
                single_row[i] = self.variables[vars_order[i]]

        if self.slack_use:
            single_row[-1] = 1

        return (single_row,self.const_value)


class Arithmatics_solver:
    def __init__(self):
        pass

    def parse_equations(self, strings):
        return [equstion(string) for string in strings]

    def _copy_equation(self,old_equation):
        new_equation = equstion('')
        for key in old_equation.variables:
            new_equation.variables[key] = old_equation.variables[key]

        new_equation.const_value = old_equation.const_value
        new_equation.proposition = old_equation.proposition
        new_equation.slack_use = old_equation.slack_use

        return new_equation

    def _flip_equation_sides(self,equation):
        for key in equation.variables:
            equation.variables[key] = -equation.variables[key]

        equation.const_value = -equation.const_value

    def _geq_to_leq(self, old_equation):
        assert old_equation.proposition == GEQ

        new_equation = self._copy_equation(old_equation)
        self._flip_equation_sides(new_equation)

        new_equation.proposition = LEQ
        return new_equation

    def _eq_to_geq_and_leq(self, old_equation):
        assert old_equation.proposition == EQ
        new_GT_equation = self._copy_equation(old_equation)
        new_LT_equation = self._copy_equation(old_equation)

        new_GT_equation.proposition = GEQ
        new_LT_equation.proposition = LEQ

        return (new_GT_equation, new_LT_equation)

    def _lt_to_eq(self,old_equation):
        assert old_equation.proposition == LT

        new_equation = self._copy_equation(old_equation)

        new_equation.proposition = EQ
        new_equation.slack_use = True

        return new_equation

    def _neq_to_slack_leqs(self,old_equation):
        assert old_equation.proposition == NEQ
        new_equation1 = self._copy_equation(old_equation)
        new_equation1.proposition = LEQ
        new_equation1.slack_use = True

        new_equation2 = self._copy_equation(new_equation1)
        self._flip_equation_sides(new_equation2)

        return (new_equation1, new_equation2)

    def _convert_constraints_to_matrix(self, constraints):
        variables_pool = set()
        slack_used = False
        for c in constraints:
            variables_pool = variables_pool.union(c.get_all_vars_names())
            slack_used = slack_used or c.get_slack_status()

        variables_pool = list(variables_pool)
        matrix_data = [c.get_matrix_format(variables_pool) for c in constraints]

        A = np.array([tup[0] for tup in matrix_data])
        b = np.array([tup[1] for tup in matrix_data])


        m,n = A.shape
        A = np.append(A, np.identity(m), axis=1)
        A.shape = (m,m+n)

        c = np.zeros(m+n)
        c[len(variables_pool)] = 1

        return (A,b,c, slack_used, variables_pool)

    def answer_LEQ_conflict(self, constraints, strategy=BLAND, debug_flag=False):

        #only look for feasible assumption
        A, b, c, slack_used, var_pool = self._convert_constraints_to_matrix(constraints)

        lp = LP_solver(A,b,c)
        lp.solve(debug_flag,strategy)

        assign , obj =lp.get_current_assignment()

        if obj is None:
            return False

        print(var_pool)
        print(assign[:len(var_pool)])
        print('obj: '+str(obj))

        if slack_used:
            return obj>0
        else:
            return True


    # def answer_propagate(self, constraints, unknown):
    #     # for each new condition, does it intersect the polytope?
    #     pass
    #
    # def answer_explain(self, low_level_constraints, latest_constraint):
    #     # maximize latest constraint
    #     # return slack vars with 0 assignment
    #     pass


def main():
    AS = Arithmatics_solver()

    equation_strings = ['-x_1 + x_2 <= -1', '-2x_1 -2x_2 <= -6', '-x_1 + 4x_2 <= 2']

    #SMT: parse these equations!

    equations = AS.parse_equations(equation_strings)
    for e in equations:
        print(e)

    #SMT: good. now take these equationd, do T_conflict.

    A, b, c, slack_stat, vars_pool = AS._convert_constraints_to_matrix(equations)
    print(A)
    print(b)
    print(c)
    print(vars_pool)

    print('------------------------')

    ans = AS.answer_LEQ_conflict(equations,BLAND)

    print(ans)

if __name__ == "__main__":
    main()
