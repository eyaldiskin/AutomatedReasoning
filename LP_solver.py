import numpy as np
np.seterr(divide='ignore', invalid='ignore')

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
        self.A = A
        self.b = b
        self.c = c

        m, n = self.A.shape

        self.X_B = np.arange(m,n)
        self.X_N = np.arange(0,m)

        self.X_B_star = None

        self.A_B = None
        self._LU_factorization()

    def _FTRAN(self, entering_var):
        result = self.A[:,entering_var]
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
        candidates = [self.X_N[i] if z[i]>=0 else np.inf for i in range(len(z))]
        entering_var = min(candidates)
        return entering_var

    def _Dantzigs_rule(self,z):
        if max(z) >= 0 :
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

        print(assignment)
        print('obj = ',assignment @ self.c)

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
        print('LU_fact = ', self.A_B)

    def _debug_print(self, content, debug_flag):
        if debug_flag:
            print(content)

    def _set_initial_feasible_solution(self, debug_flag):

        #if possible- just use the 0 assignment and finish
        if min(self.b) >= 0:
            self.X_B_star = self.b[:].astype(float)
            return True

        #if it's a non-trivial issue- solve the auxilery problem
        else:
            print('please supply an initial assignment')
            return False

            '''x0_col = np.full((self.A.shape[0], 1), -1.)

            new_obj = np.zeros(self.A.shape[1]+1)
            new_obj[0] = -1


            auxiliary = LP_solver(np.append(x0_col, self.A, axis=1), self.b, new_obj)
            auxiliary.X_B_star = np.zeros(auxiliary.X_B.shape[0]).astype(float)
            auxiliary.print_inner_state()

            minimize = True
            auxiliary.solve(debug_flag, auxiliary._Blands_rule,minimize)

            self.X_B = auxiliary.X_B
            self.X_B_star = auxiliary.X_B_star

            X_N = []
            for i in range(self.A.shape[1]):
                if i+1 not in self.X_B:
                    X_N += [i]

            self.X_N = np.array(X_N)'''

    def solve(self, debug_flag, strategy):

        #make sure we start from an initial feasible assignment
        if self.X_B_star is None:
            if not self._set_initial_feasible_solution(debug_flag):
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

            entering_var = strategy(optional_z_coefficients)
            self._debug_print(('entering_var= ', entering_var), debug_flag)

            if np.isinf(entering_var):
                print('optimal result was found')
                return

            # calculate leaving var
            d = self._FTRAN(entering_var)
            self._debug_print(('d= ', d), debug_flag)


            t_bounds = self.X_B_star / d
            for i in range(len(t_bounds)):
                if t_bounds[i] < 0 :
                    t_bounds[i] = np.inf
            self._debug_print(('t_bounds= ', t_bounds), debug_flag)

            t = min(t_bounds)
            if np.isinf(t):
                print('unbounded problem, increase var '+str(entering_var)+' to inf')
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

            #if numeric issues:
            #    self._LU_factorization()
            iteration_number += 1


def main():
    debug_flag = True
    #debug_flag = False

    A = np.array([[1,1,2,1,0,0],[2,0,3,0,1,0],[2,1,3,0,0,1]])
    b = np.array([4,5,7])
    c = np.array([3,2,4,0,0,0])

    '''A = np.array([[-1,1,1,0,0],[-2,-2,0,1,0],[-1,4,0,0,1]])
    b = np.array([-1,-6,2])
    c = np.array([1,3,0,0,0,0])'''


    lp = LP_solver(A, b, c)

    lp._set_initial_feasible_solution(debug_flag)
    #lp.solve(debug_flag,lp._Blands_rule)
    lp.solve(debug_flag, lp._Dantzigs_rule)
    lp.print_current_assignment()



if __name__ == "__main__":
    main()
