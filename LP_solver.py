import numpy as np

class LP_solver:

    def __init__(self, A, b, c):
        self.A = A
        self.b = b
        self.c = c

        m, n = self.A.shape

        self.X_B = np.arange(m,n)
        self.X_N = np.arange(0,m)

        self.X_B_star = None

    def _FTRAN(self, entering_var):
        d = np.linalg.inv(self.A[:,self.X_B]) @ self.A[:,entering_var]
        return d

    def _BTRAN(self):
        y = self.c[self.X_B] @ np.linalg.inv(self.A[:,self.X_B])
        return y

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
        pass

    def print_current_assignment(self):
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

    def _debug_print(self, content, debug_flag):
        if debug_flag:
            print(content)

    def set_initial_feasible_solution(self):
        if min(self.b) >= 0:
            self.X_B_star = self.b[:].astype(float)

        else:
            new_col = np.full((self.A.shape[1],1), -1)
            auxiliary = LP_solver(new_col.hstack(self.A), self.b, self.c)
            auxiliary. X


    def solve(self, debug_flag, strategy):
        np.seterr(divide='ignore', invalid='ignore')

        if self.X_B_star == None:
            self.set_initial_feasible_solution()

        iteration_number = 1
        while(True):
            self._debug_print(('--------------iteration ', iteration_number, '-----------------'), debug_flag)
            if debug_flag: self.print_inner_state()

            # calculate entering var
            y = self._BTRAN() #TODO: write an actual BTRAN
            self._debug_print(('y= ',y),debug_flag)

            optional_z_coefficients =  self.c[self.X_N] - y@self.A[:,self.X_N]
            self._debug_print(('optional_z_coefficients= ',optional_z_coefficients),debug_flag)

            entering_var = strategy(optional_z_coefficients)
            self._debug_print(('entering_var= ', entering_var), debug_flag)

            if np.isinf(entering_var):
                print('optimal result was found')
                return

            # calculate leaving var
            d = self._FTRAN(entering_var) #TODO: write an actual FTRAN
            self._debug_print(('d= ', d), debug_flag)

            t_bounds = self.X_B_star / d
            for i in range(len(t_bounds)):
                if t_bounds[i] <= 0 :
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
            for i in range(len(self.X_B)):
                if self.X_B[i] == leaving_var:
                    self.X_B[i] = entering_var

            for i in range(len(self.X_N)):
                if self.X_N[i] == entering_var:
                    self.X_N[i] = leaving_var

            self.X_B_star -= d*t
            self.X_B_star[np.argmin(t_bounds)] = t

            iteration_number += 1

        #while(True):
        #    pass
            # fix numerical issues

def main():
    debug_flag = True
    #debug_flag = False

    A = np.array([[1,1,2,1,0,0],[2,0,3,0,1,0,],[2,1,3,0,0,1]])
    b = np.array([4,5,7])
    c = np.array([3,2,4,0,0,0])

    lp = LP_solver(A, b, c)
    lp.set_initial_feasible_solution()
    lp.solve(debug_flag,lp._Dantzigs_rule)
    lp.print_current_assignment()

if __name__ == "__main__":
    main()
