import fractions
import itertools
import logging
import math

from .Common import progress_bar
from .CspScopesRelations import CspScopesRelations
from .MaxSatOrTools import MaxSatOrTools


class MaxSatAcq:
    """
    MaxSat solver wrapper for the acquisition problem
    """

    def __init__(self, VARIABLES, DOMAINS, DELTA, SCOPES, LOG):
        self.model = MaxSatOrTools(LOG)
        self.variables_relations = {}
        self.variables_scopes = {}
        self.variables_relations = {}
        self.variables_scopes = {}
        self.variables_virtual = {}
        self.forbidden_virtual = {}
        self.variable_meta_graph = None
        self.VARIABLES = VARIABLES
        self.DOMAINS = DOMAINS
        self.DELTA = DELTA
        self.SCOPES = SCOPES
        self._log = LOG
        self.granularity = 1
        for u in range(1, len(DELTA) + 1):
            with progress_bar(len(DOMAINS) ** DELTA[u - 1], title="Relation {}".format(u),
                              active=self._log) as progress:
                for tpl in itertools.product(DOMAINS, repeat=DELTA[u - 1]):
                    self.variables_relations[u, tpl] = self.model.add_var()
                    progress.update()
        for u in range(1, len(DELTA) + 1):
            with progress_bar(len(self.SCOPES[u - 1]), title="Scope {}".format(u), active=self._log) as progress:
                for variables in self.SCOPES[u - 1]:
                    self.variables_scopes[u, variables] = self.model.add_var()
                    progress.update()

    def link_scope_relation(self, u, scope, relation):
        current_c = self.variables_virtual[u, scope, relation] = self.model.add_var()
        self.model.add_hard_literals(-current_c, self.variables_relations[u, relation])
        self.model.add_hard_literals(-current_c, self.variables_scopes[u, scope])
        self.model.add_hard_literals(current_c, -self.variables_relations[u, relation],
                                     -self.variables_scopes[u, scope])
        return current_c

    def positive_constraint(self, u, scope, relation):
        current_c = self.variables_virtual.get((u, scope, relation), self.link_scope_relation(u, scope, relation))
        self.model.add_hard_literals(-current_c)

    def negative_constraint(self, u_scopes_relations, assignement=None):
        le: MaxSatOrTools.Clause = MaxSatOrTools.Clause()
        for (u, scope, relation) in u_scopes_relations:
            current_c = self.variables_virtual.get((u, scope, relation), self.link_scope_relation(u, scope, relation))
            le += current_c
        self.model.add_hard_clause(le)

    def negative_constraint_weight(self, u_scopes_relations, weight: float):
        assert False, "Not implemented yet"
        le: MaxSatOrTools.Clause = MaxSatOrTools.Clause()
        for (u, scope, relation) in u_scopes_relations:
            current_c = self.variables_virtual.get((u, scope, relation), self.link_scope_relation(u, scope, relation))
            le += current_c
        self.model.add_hard_clause(le)

    def objective_scope(self, weight: float):
        literal_weight: float = weight / len(self.variables_scopes)
        if self.granularity % len(self.variables_scopes) != 0:
            self.granularity = self.lcm(self.granularity, len(self.variables_scopes))
        for u in range(1, len(self.DELTA) + 1):
            for variables in self.SCOPES[u - 1]:
                if literal_weight > 0:
                    self.model.add_soft_literals(literal_weight, self.variables_scopes[u, variables])
                else:
                    self.model.add_soft_literals(-literal_weight, -self.variables_scopes[u, variables])

    def objective_relation(self, weight: float):
        literal_weight: float = weight / len(self.variables_relations)
        if self.granularity % len(self.variables_relations) != 0:
            self.granularity = self.lcm(self.granularity, len(self.variables_relations))
        for u in range(1, len(self.DELTA) + 1):
            for tpl in itertools.product(self.DOMAINS, repeat=self.DELTA[u - 1]):
                if literal_weight > 0:
                    self.model.add_soft_literals(literal_weight, self.variables_relations[u, tpl])
                else:
                    self.model.add_soft_literals(-literal_weight, -self.variables_relations[u, tpl])

    def gen_meta_graph(self):
        assert self.variable_meta_graph is None
        self.variable_meta_graph = {}
        for pair in itertools.combinations(self.VARIABLES, 2):
            self.variable_meta_graph[tuple(pair)] = self.model.add_var()
            list_vars: MaxSatOrTools.Clause = MaxSatOrTools.Clause()
            list_vars += -self.variable_meta_graph[tuple(pair)]
            for u in range(1, len(self.DELTA) + 1):
                for scopes in self.SCOPES[u - 1]:
                    if scopes.__contains__(pair[0]) and scopes.__contains__(pair[1]):
                        list_vars += self.variables_scopes[u, scopes]
                        self.model.add_hard_literals(self.variable_meta_graph[tuple(pair)],
                                                     -self.variables_scopes[u, scopes])
            self.model.add_hard_clause(list_vars)

    def objective_triangle(self, weight: float):
        if self.variable_meta_graph is None:
            self.gen_meta_graph()
        literal_weight: float = weight / len(self.variable_meta_graph)
        if self.granularity % len(self.variable_meta_graph) != 0:
            self.granularity = self.lcm(self.granularity, len(self.variable_meta_graph))
        for (x, y, z) in itertools.combinations(self.VARIABLES, 3):
            lambda_var = self.model.add_var()
            self.model.add_hard_literals(-lambda_var, self.variable_meta_graph[(x, y)])
            self.model.add_hard_literals(-lambda_var, self.variable_meta_graph[(y, z)])
            self.model.add_hard_literals(-lambda_var, self.variable_meta_graph[(x, z)])
            if literal_weight > 0:
                self.model.add_soft_literals(literal_weight, lambda_var)
            else:
                self.model.add_soft_literals(-literal_weight, -lambda_var)

    def to_csp(self) -> CspScopesRelations:
        assert self.model.solved()
        csp = CspScopesRelations(list(self.VARIABLES), self.DOMAINS)
        for u in range(1, len(self.DELTA) + 1):
            relations = []
            for tpl in itertools.product(self.DOMAINS, repeat=self.DELTA[u - 1]):
                if self.model.get(self.variables_relations[u, tpl]):
                    relations.append(tpl)
            scopes = []
            for variables in self.SCOPES[u - 1]:
                if self.model.get(self.variables_scopes[u, variables]):
                    scopes.append(variables)
            csp.add_scopes_relations(scopes, relations)
        return csp

    def solve(self, timeout: int = None):
        self.model.solve(timeout)

    def solved(self) -> bool:
        if not self.model.optimum_found():
            logging.debug("The optimality is not proved.")
        return self.model.solved()

    def get_objective(self):
        return self.model.get_objective()

    def lcm(self, x, y):
        try:
            return (x * y) // fractions.gcd(x, y)
        except AttributeError:
            return (x * y) // math.gcd(x, y)
