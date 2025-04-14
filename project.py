from pyeda.inter import bddvars, expr2bdd, And, Or, expr

# creating boolean decision diagrams variables
iVars = bddvars('i', 5)
jVars = bddvars('j', 5)

# this function converts a number into a boolean expression based on the given variable list
# the number is represented in a 5-bit binary string and then mapped to either the variable or its negation
def numToExpr(num, var):
    # convert the number to a 5-digit binary string
    binary = format(num, '05b')
    terms = []
    for idx, bit in enumerate(binary):
        if bit == '1': # if the bit is a 1, append the var to terms
            terms.append(var[idx])
        else:  # but if the bit is 0, append the negation variable
            terms.append(~var[idx])
    return And(*terms)

# this function creates a dictionary mapping each variable to its binary value based on the number's 5-bit binary representation
def numToDict(num, var):
    # convert the number to a 5-digit binary string
    binary = format(num, '05b')
    # use a dictionary comprehension to map each variable to its value
    mapping = {}
    for idx, bit in enumerate(binary):
        mapping[var[idx]] = int(bit)
    return mapping


# this function builds the bdd for the double r
def buildBdd():
    edgeExprs = []
    for source in range(32):
        target1 = (source + 3) % 32
        target2 = (source + 8) % 32
        # create the expression for the edge from source to target1
        edgeExpr1 = And(numToExpr(source, iVars), numToExpr(target1, jVars))
        # create the expression for the edge from source to target2
        edgeExpr2 = And(numToExpr(source, iVars), numToExpr(target2, jVars))
        # add both the expressions to the list
        edgeExprs.extend([edgeExpr1, edgeExpr2])
    
    relationExpr = Or(*edgeExprs)
    
    return expr2bdd(relationExpr) # convert the boolean expression to a bdd and return it

# this function builds a bdd for the evens
def buildEvenBdd():
    evenExprs = []
    for node in range(32):
        if node % 2 == 0:
            expr_value = numToExpr(node, jVars) # convert the number into a boolean expression
            evenExprs.append(expr_value)
    # combine the expressions using pyeda Or
    evenExpr = Or(*evenExprs)
    # convert the boolean expression to a bdd and return it
    return expr2bdd(evenExpr)

# this function builds a bdd for the property prime, similar to the even one
def buildPrimeBdd():
    primeNodes = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
    primeExprs = []
    for node in primeNodes:
        expr_value = numToExpr(node, iVars)
        primeExprs.append(expr_value)
    # combine the prime expressions using disjunction (or)
    primeExpr = Or(*primeExprs)
    # convert the boolean expression to a bdd and return it
    return expr2bdd(primeExpr)

rrBdd = buildBdd()
evenBdd = buildEvenBdd()
primeBdd = buildPrimeBdd()

# test function to check if a source and target are reachable in the relation rr'
def testRr(source, target):
    mapping = {}
    mapping.update(numToDict(source, iVars))
    mapping.update(numToDict(target, jVars))
    # restrict the bdd using the mapping, and return true if the resulting bdd is satisfiable
    return bool(rrBdd.restrict(mapping))

# test function to check if a node in j is even by restricting the even bdd
# restricting checks if the mapping satisfies the even property
def testEven(node):
    mapping = numToDict(node, jVars)
    # check if the node satisfies the even property
    return bool(evenBdd.restrict(mapping))

# test function to check if a node in i is prime by restricting the prime bdd
def testPrime(node):
    mapping = numToDict(node, iVars)
    # return true if the mapping satisfies the prime property
    return bool(primeBdd.restrict(mapping))

# this function composes two relations takes in a and b via an intermediate variable set z
def composeRelations(A, B, z):
    subMappingA = {}
    for k in range(5):
        subMappingA[jVars[k]] = z[k]
    A_substituted = A.compose(subMappingA)
    
    subMappingB = {}
    for k in range(5):
        subMappingB[iVars[k]] = z[k]
    B_substituted = B.compose(subMappingB)
    
    andResult = A_substituted & B_substituted
    
    result = andResult.smoothing(z)
    
    return result

# this function builds the bdd for twostep reachability using the composition of rr with itself
def buildRr2Bdd():
    z = bddvars('z', 5)
    return composeRelations(rrBdd, rrBdd, z)

# build the two step reachability relation bdd rr2
rr2Bdd = buildRr2Bdd()

# function to test the two step reachability between a source and target
# returns bool
def testRr2(source, target):
    mapping = {}
    mapping.update(numToDict(source, iVars))
    mapping.update(numToDict(target, jVars))
    return bool(rr2Bdd.restrict(mapping))

# this function computes the transitive closure of a given relation bdd 'rel'
def transitiveClosure(rel):
    z = bddvars('z', 5)
    closure = rel
    while True:
        newClosure = closure | composeRelations(closure, rel, z) # compose the new closure with the original relation or compose a relation
        # if the new closure is equivalent to the old one break outta the loop
        if newClosure.equivalent(closure):
            break
        closure = newClosure
    return closure

# compute the transitive closure of the two-step reachability bdd and store in rr2StarBdd
rr2StarBdd = transitiveClosure(rr2Bdd)

# this function verifies that every prime node is reachable from an even node in the relation
def verifyStatementA():
    reachableEvenBdd = rr2StarBdd & evenBdd 
    
    reachableEvenProj = reachableEvenBdd.smoothing(jVars)
    
    testBdd = primeBdd & ~reachableEvenProj
    
    return testBdd.is_zero()

result = verifyStatementA()

# these are just the test cases to check if the functions work like the pdf say
def runTests():
    print("test cases for r, even, and prime:")
    print(f"rr(27, 3) is true: {testRr(27, 3)}")
    print(f"rr(16, 20) is false: {testRr(16, 20)}")
    print(f"even(14) is true: {testEven(14)}")
    print(f"even(13) is false: {testEven(13)}")
    print(f"prime(7) is true: {testPrime(7)}")
    print(f"prime(2) is false: {testPrime(2)}")
    
    print("\ntest cases for rr2 (two-step reachability):")
    print(f"rr2(27, 6) is true: {testRr2(27, 6)}")
    print(f"rr2(27, 9) is false: {testRr2(27, 9)}")
    
    print(f"\nverification of statementa: {verifyStatementA()}")

if __name__ == "__main__":
    runTests()
