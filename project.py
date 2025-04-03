from pyeda.inter import bddvars, expr2bdd, And, Or, expr

i = bddvars('i', 5)
j = bddvars('j', 5)

def num_to_expr(num, var):
    binary = format(num, '05b')
    terms = []
    for idx, bit in enumerate(binary):
        if bit == '1':
            terms.append(var[idx])
        else:
            terms.append(~var[idx])
    return And(*terms)

def num_to_dict(num, var):
    binary = format(num, '05b')
    return {var[idx]: int(bit) for idx, bit in enumerate(binary)}


def build_R_BDD():
    edge_exprs = []
    for source in range(32):
        target1 = (source + 3) % 32
        target2 = (source + 8) % 32
        edge_expr1 = And(num_to_expr(source, i), num_to_expr(target1, j))
        edge_expr2 = And(num_to_expr(source, i), num_to_expr(target2, j))
        edge_exprs.extend([edge_expr1, edge_expr2])
    relation_expr = Or(*edge_exprs)
    return expr2bdd(relation_expr)

RR_BDD = build_R_BDD()

def build_even_BDD():
    even_exprs = [num_to_expr(node, j) for node in range(32) if node % 2 == 0]
    even_expr = Or(*even_exprs)
    return expr2bdd(even_expr)

EV_EN_BDD = build_even_BDD()

def build_prime_BDD():
    prime_nodes = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
    prime_exprs = [num_to_expr(node, i) for node in prime_nodes]
    prime_expr = Or(*prime_exprs)
    return expr2bdd(prime_expr)

PRIME_BDD = build_prime_BDD()

def test_RR(source, target):
    mapping = {}
    mapping.update(num_to_dict(source, i))
    mapping.update(num_to_dict(target, j))
    return bool(RR_BDD.restrict(mapping))

def test_even(node):
    mapping = num_to_dict(node, j)
    return bool(EV_EN_BDD.restrict(mapping))

def test_prime(node):
    mapping = num_to_dict(node, i)
    return bool(PRIME_BDD.restrict(mapping))

def build_RR2_BDD():
    z = bddvars('z', 5)
    R1 = RR_BDD.compose({j[k]: z[k] for k in range(5)})
    R2 = RR_BDD.compose({i[k]: z[k] for k in range(5)})
    return (R1 & R2).smoothing(z)

RR2_BDD = build_RR2_BDD()

def test_RR2(source, target):
    mapping = {}
    mapping.update(num_to_dict(source, i))
    mapping.update(num_to_dict(target, j))
    return bool(RR2_BDD.restrict(mapping))

def compose_relations(A, B, z):
    return (A.compose({j[k]: z[k] for k in range(5)}) &
            B.compose({i[k]: z[k] for k in range(5)})).smoothing(z)

def transitive_closure(rel):
    z = bddvars('z', 5)
    closure = rel
    while True:
        new_closure = closure | compose_relations(closure, rel, z)
        if new_closure.equivalent(closure):
            break
        closure = new_closure
    return closure

RR2star_BDD = transitive_closure(RR2_BDD)

def verify_statementA():
    reachable_even_BDD = RR2star_BDD & EV_EN_BDD
    reachable_even_proj = reachable_even_BDD.smoothing(j)
    return (PRIME_BDD & ~reachable_even_proj).is_zero()