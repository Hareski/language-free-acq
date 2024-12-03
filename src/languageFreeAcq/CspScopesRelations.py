import itertools
import logging


class CspScopesRelations:
    """
    A CSP described only with scopes and relations
    """

    def __init__(self, variables: list, domain: list):
        """
        Create a CSP described only with scopes and relations
        :param variables: list of variables
        :param domain: list of the domain for all variables
        """
        self.constraints_scopes_relations: [(list, list)] = []
        self.variables: list = []
        self.domain: list = []
        self.variables = variables
        self.domain = domain
        self.file_buffer = {}

    def add_scopes_relations(self, scopes, relations):
        """
        Add a new scope/relation to the CSP
        :param scopes: The scopes to apply
        :param relations: The relations to apply
        :return: None
        """
        self.constraints_scopes_relations.append((scopes, relations))

    def reset_scopes_relations(self):
        """
        Reset the scopes and relations
        :return: None
        """
        self.constraints_scopes_relations: [(list, list)] = []

    def get_scope_relation(self, index: int) -> (list, list):
        """
        Get the scope and relation at the given index
        :param index: The index of the scope/relation
        :return: The scope and relation
        """
        return self.constraints_scopes_relations[index]

    def get_scope(self, index: int) -> (list, list):
        """
        Get the scope at the given index
        :param index: The index of the scope
        :return: The scope
        """
        return self.constraints_scopes_relations[index][0]

    def get_relation(self, index: int) -> (list, list):
        """
        Get the relation at the given index
        :param index: The index of the relation
        :return: The relation
        """
        return self.constraints_scopes_relations[index][1]

    def get_delta(self):
        """
        Get the delta of the CSP (e.g. [3, 2, 2] for one ternary and two binary relation)
        :return: The delta of the CSP
        """
        delta = []
        for scopes, _ in self.constraints_scopes_relations:
            if len(scopes) > 0:
                delta.append(len(scopes[0]))
            else:
                delta.append(0)
        return delta

    def get_primal(self):
        """
        Get the primal graph of the CSP
        :return: The primal graph of the CSP
        """
        primal = {}
        for (scopes, _) in self.constraints_scopes_relations:
            for scope in scopes:
                for (x, y) in itertools.combinations(scope, 2):
                    primal[(x, y)] = True
        return primal

    def is_solution(self, assignment) -> bool:
        """
        Check if the given assignment is a solution of the CSP
        :param assignment: The assignment to check
        :return: True if the assignment is a solution, False otherwise
        """
        for (scopes, relations) in self.constraints_scopes_relations:
            for scope in scopes:
                values = [assignment[var] for var in scope]
                if tuple(values) in relations:
                    return False
        return True

    def display_model(self):
        """ Display the model """
        for i in range(0, len(self.constraints_scopes_relations)):
            logging.info("Relation " + str(i) + ":")
            logging.info("Scopes: " + str(self.constraints_scopes_relations[i][0]))
            logging.info("Tuples: " + str(self.constraints_scopes_relations[i][1]))

    def get_scopes_relations(self):
        """
        Get all scopes and relations of the CSP
        :return:
        """
        return self.constraints_scopes_relations

    def check_accuracy(self, file_path: str) -> float:
        """
        Check the accuracy of the CSP on the given file
        :param file_path: The path to the file
        :return: The accuracy of the CSP on the given file
        """
        assert file_path is not None
        if self.file_buffer.get(file_path) is None:
            self.file_buffer[file_path] = []
            with open(file_path, 'r') as file:
                for line in file:
                    example = line.split(",")
                    weight, assignment = int(example[-1]), [int(x) for x in example[:-1]]
                    assert weight in {0, 1}
                    self.file_buffer[file_path].append((weight, assignment))
        well_classified = 0
        total = 0
        for (weight, assignment) in self.file_buffer[file_path]:
            is_solution: bool = self.is_solution(assignment)
            if (weight == 1 and is_solution) or (weight == 0 and not is_solution):
                well_classified += 1
            else:
                logging.debug("Misclassified example: " + str(assignment) + " with weight " + str(weight))
            total += 1
        return well_classified / total
