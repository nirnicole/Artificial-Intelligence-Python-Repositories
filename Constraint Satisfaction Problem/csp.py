import abc
import Util
from random import randrange

"""
    Summery: Basic framework for a Constraint search problem
    Author:  Nir Nicole
"""


# Base class for all constraints
class Constraint(object):
    # The variables that the constraint is between
    def __init__(self, variables):
        self.variables = variables

    # Must be overridden by subclasses
    @abc.abstractmethod
    def satisfied(self, assignment):
        """checking if X1,X2 can be given A,B or B,A (<(X1,X2),X1!=X2>)"""
        return

    # Must be overridden by subclasses
    @abc.abstractmethod
    def Conflicts(self, assignment):
        """checking how many conflicts has been created by an assignment"""
        return


# A constraint satisfaction problem consists of variables of type V
# that have ranges of values known as domains of type D and constraints
# that determine whether a particular variable's domain selection is valid
class CSP(object):
    """initializer creates the constraints dict and assigning variables to domains"""

    def __init__(self, variables, domains, heuristic_flags=None):
        # variables = list of variable {..}
        self.variables = variables
        # domains = dictionary mapping variables to lists of constraints imposed to it.
        self.domains = domains
        # constraints = {}, dictionary of variable as key, and constrain implementation as value each constraion
        # implementation gets 2 values and check if they are valid according to its unique implementaion.
        self.constraints = {}
        # default heuristics disabling
        if heuristic_flags is None:
            heuristic_flags = {"MRV": False, "LCV": False}
        # heuristic flags allow you to disable framework huristic if they are a burden.
        self.heuristic_flags = heuristic_flags
        self.arcs = {"unaryArc" : [] , "binarArc": [], "nArc": []}

        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    """method goes through all of the variables touched by a given constraint and adds
       itself to the constraints mapping for each of them. """
    def add_constraint(self, constraint):
        # constraint: Constraint[V, D]) -> None
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)
        # also create an arc associating with the constrain variables.
        arc = constraint.variables
        if len(arc) == 1:
            self.arcs["unaryArc"].append(arc)
        if len(arc) == 2:
            self.arcs["binarArc"].append(arc)
        elif len(arc) > 2:
            self.arcs["nArc"].append(arc)

    # Check if the value assignment is consistent by checking all constraints for the given variable against it
    # assignment = given configuration of variables and selected domains that should statisfy the constrains.
    # function that checks every constraint for a given variable against an assignment to see if the variables value
    # in the assignment works for the constraints.
    def consistent(self, variable, assignment):
        # variable: V, assignment: Dict[V, D]) -> bool
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True


    """ kind of recursive depth-first search. This functions added as a method to the CSP class."""
    def btsearch(self):
        return self.btSearchDfs({})

    def btSearchDfs(self, assignment):

        unassigned = [v for v in self.variables if v not in assignment]

        """goal test"""
        if len(unassigned) == 0:
            return assignment

        """choose variable with MRV heuristic"""
        if self.heuristic_flags["MRV"]:
            chosen_variable = self.MRVhuristicScore(unassigned)
        else:
            chosen_variable = unassigned[0]

        """sort domain values by LCV heuristic"""
        if self.heuristic_flags["LCV"]:
            sorted_domain = self.LCVhuristicScore(assignment, chosen_variable)
        else:
            sorted_domain = self.domains[chosen_variable]

        for value in sorted_domain:
            assignment[chosen_variable] = value         # Here we assign value to a variable !
            if self.consistent(chosen_variable, assignment):        # if we're still consistent, we recurse (continue)
                result = self.btSearchDfs(assignment)
                if result != None:
                    return result
            assignment.pop(chosen_variable, None)         # if we didn't find the result, we will end up backtracking without this option
        return None

    """ AC-3 detects conflicts that you will have in attributions, during the backtracking, and deletes them"""
    def ac3(self):

        # creating the arcs queue
        queue = Util.Queue()
        for arc in self.arcs["binarArc"]:
            if len(arc)!=2:
                raise LookupError("AC-3 work with binary arcs only.")
            else:
                queue.push(arc)

        # remove values from arcs domains till their are none to remove
        while not queue.isEmpty():
            x,y = queue.pop()
            if self.RemoveInconsistentValues(x,y):
               # Every time a value is removed from the domain, you'll have to recheck the neighbors of x.
               for arc in self.arcs:
                    if y not in arc:
                        queue.push(arc)

    # here we implement the value remove.
    def RemoveInconsistentValues(self, x,y):
        value_removed_flag = False
        temp_assignment = {}        # temp assigning to check constrain only!
        for x_value in self.domains[x]:
            is_consistent = False
            temp_assignment[x] = x_value
            for y_value in self.domains[y]:
                temp_assignment[y] = y_value
                if self.consistent(x, temp_assignment):
                    is_consistent = True
            if not is_consistent:
                self.domains[x].remove(x_value)
        return value_removed_flag

    def MRVhuristicScore(self, unassigned_variables):
        #  print unassigned_variables
        smallest_domain_variable = unassigned_variables[0]
        for variable in unassigned_variables:
            #     print "checking var :" , variable , " len is: ", len(self.domains[variable])
            if len(self.domains[variable]) < len(self.domains[smallest_domain_variable]):
                smallest_domain_variable = variable

        # print  "chosen is : " , smallest_domain_variable, "len: ",len(self.domains[smallest_domain_variable])
        # print "\n"
        return smallest_domain_variable

    def LCVhuristicScore(self, assignment, variable):
        # assignment = dictionary of {variable: domain list[] }

        new_domain = Util.PriorityQueue()

        for value in self.domains[variable]:

            lcv_score = 0
            local_assignment = assignment.copy()
            # Here we assign value to a variable !
            local_assignment[variable] = value

            for constraint in self.constraints[variable]:
                if not constraint.satisfied(local_assignment):
                    lcv_score = lcv_score + 1
            # print lcv_score
            new_domain.push(value, lcv_score)

        # converting to a sorted list
        new_domain_as_list = []
        while not new_domain.isEmpty():
            new_domain_as_list.append(new_domain.pop())

        # print new_domain_as_list
        return new_domain_as_list

    def MinConflicts(self, max_steps, assignment):
        """ gets itself = csp problem with attributes.
            max_steps = the number of steps allowed before giving up."""

        # assignment = dictionary of {variable: domain list[] }
        # assignment is complete if every variable is assigned (our base case)
        # current = an initial complete assignment for csp.
        current = assignment

        for i in range(1, max_steps):

            found_solution = True
            # if current is solution return it
            for possible_var in self.variables:
                for constraint in self.constraints[possible_var]:
                    if not constraint.satisfied(current):
                        found_solution = False
            if found_solution:
                print "exec steps: ", i
                return current

            is_not_conflicting = True
            while is_not_conflicting:
                var = current[randrange(0, len(current))]
                for constraint in self.constraints[var]:
                    if not constraint.satisfied(current):
                        is_not_conflicting = False

            maximum = 0  # initialize to minimum
            var_conflicting = []
            for potential_var in self.variables:
                current_num_of_conflicts = constraint.Conflicts(current, potential_var)
                if current_num_of_conflicts > 0 and current_num_of_conflicts >= maximum:
                    maximum = constraint.Conflicts(current, potential_var)
                    var_conflicting.append(potential_var)

            var = var_conflicting[randrange(0, len(var_conflicting))]

            # choose the var value that minimize Conflicts function (function that
            # counts the number of constrains violated by practicular value, given
            # the rest of the current assignment).
            current_num_of_conflicts = constraint.Conflicts(current, var)
            value_options = []
            minimum = current_num_of_conflicts
            for value_candidate in self.domains[var]:
                optional_current = current.copy()
                optional_current[var] = value_candidate
                if constraint.Conflicts(optional_current, var) <= minimum:
                    minimum = constraint.Conflicts(optional_current, var)
                    value_options.append(value_candidate)

            current[var] = value_options[randrange(0, len(value_options))]

        return None

    def clear(self):
        self.variables = None
        self.domains = None
        self.constraints = None
        self.heuristic_flags = None
