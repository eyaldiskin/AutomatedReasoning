import SMT
import TUF
import LP_solver
import Parse_SMT
import CDCL

GET_THEORY_TXT = "please insert the theory you want to use:"\
                 "\n\tSAT for SAT solver with no theory,"\
                 "\n\tTUF for uninterpreted functions theory or"\
                 "\n\tLP for arithmetic solver.\n"

GET_FORMULA_TXT = "\nplease insert the formula you want to solve, for help type 'help'.\n"

HELP = "\nFor help in the specific theory you chose, look at its' documentation.\n"\
    "Here is a list of currently existing operations for the SAT\\SMT solver:\n"\
    "\tAND:\t\t\t'&&'\n\tOR:\t\t\t\t'||'\n\tNOT:\t\t\t'~'\n\tIFF:\t\t\t'=='\n\t'a' IMPLIES 'b':'a>>b'\n"\
    "If you want to use parentheses, use square ones('[' and ']').\n"

if __name__ == "__main__":
    theory_name = input(GET_THEORY_TXT)
    if theory_name == "TUF":
        theory = TUF.TUF()
    elif theory_name == "LP":
        theory = LP_solver.Arithmatics_solver()
    elif theory_name != "SAT":
        raise ValueError('Theory name mismatch')
    else:
        theory = None
    finish = False
    while not finish:
        formula = input(GET_FORMULA_TXT)
        if formula == "help":
            print(HELP)
            continue
        if theory:
            smt = SMT.SMT(formula, theory)
            print(smt.solve())
        else:
            sat = CDCL.CDCL(Parse_SMT.parse(formula))
            sol = sat.solve()
            if sol:
                print(sat.getAssignment())
            else:
                print(False)
        if input("do you want to solve another formula using the same theory?(Y/N)\n") != "Y":
            finish = True
