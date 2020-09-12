import pycosat

## Hard coded sudoku dimensions
N = 9
M = 3


def getAllValidMoves(x0, y0):
    """Get all valid knight's moves from location x0, y0 on the 9x9 sudoku grid."""
    deltas = [
        (-2, -1),
        (-2, +1),
        (+2, -1),
        (+2, +1),
        (-1, -2),
        (-1, +2),
        (+1, -2),
        (+1, +2),
    ]
    validPositions = []

    for (x, y) in deltas:
        xCandidate = x0 + x
        yCandidate = y0 + y
        if 0 < xCandidate < 8 and 0 < yCandidate < 8:
            validPositions.append([xCandidate, yCandidate])

    return validPositions


def exactly_one_knights_move(variables):
    """Checks for the same value in all cells that are a knights move away from a given cell."""
    cnf = []

    for valid_move in variables[:-1]:
        # print(valid_move)
        cnf.append([-valid_move, -variables[-1]])

    return cnf


def exactly_one(variables):
    cnf = [variables]
    n = len(variables)

    for i in range(n):
        for j in range(i + 1, n):
            v1 = variables[i]
            v2 = variables[j]
            cnf.append([-v1, -v2])

    return cnf


def transform(i, j, k):
    '''Transform the cell X(i, j, k) into an integer for conversion to CNF.'''
    return i * N * N + j * N + k + 1


def inverse_transform(v):
    '''Convert the integer back into i, j, k values.'''
    v, k = divmod(v - 1, N)
    v, j = divmod(v, N)
    v, i = divmod(v, N)
    return i, j, k


if __name__ == "__main__":
    cnf = []

    # Knight's move contraints
    for s in range(N):
        for x in range(N):
            for y in range(N):
                valid_moves = getAllValidMoves(x, y)
                valid_moves.append([x, y])
                cnf = cnf + exactly_one_knights_move(
                    [transform(x, y, s) for x, y in valid_moves]
                )

    # Diagonal constraints
    for s in range(N):
        cnf = cnf + exactly_one([transform(x, N - (x + 1), s) for x in range(N)])
        cnf = cnf + exactly_one([transform(x, x, s) for x in range(N)])

    # Cell, row and column constraints
    for x in range(N):
        for s in range(N):
            cnf = cnf + exactly_one([transform(x, y, s) for y in range(N)])
            cnf = cnf + exactly_one([transform(y, x, s) for y in range(N)])
        for y in range(N):
            cnf = cnf + exactly_one([transform(x, y, k) for k in range(N)])

    # Sub-matrix constraints
    for k in range(N):
        for x in range(M):
            for y in range(M):
                v = [
                    transform(y * M + i, x * M + j, k)
                    for i in range(M)
                    for j in range(M)
                ]
                cnf = cnf + exactly_one(v)

    # cnf = {frozenset(x) for x in cnf}
    # cnf = list(cnf)

    # A 16-constraint Sudoku
    # constraints = [
    # (0, 3, 7),
    # (2, 3, 4),
    #     (2, 4, 3),
    #     (2, 6, 2),
    #     (3, 8, 6),
    #     (4, 3, 5),
    #     (4, 5, 9),
    #     (5, 6, 4),
    #     (5, 7, 1),
    #     (5, 8, 8),
    #     (6, 4, 8),
    #     (6, 5, 1),
    #     (7, 2, 2),
    #     (7, 7, 5),
    #     (8, 1, 4),
    #     (8, 6, 3),
    # ]

    # Knight's move, diagonal, magic square sudoku
    constraints = [
        (8, 8, 2),
        (3, 0, 3),
        (3, 1, 8),
        (3, 2, 4),
        # Magic square hardcoded
        (3, 3, 6),
        (3, 4, 7),
        (3, 5, 2),
        (4, 3, 1),
        (4, 4, 5),
        (4, 5, 9),
    ]

    cnf = cnf + [[transform(z[0], z[1], z[2]) - 1] for z in constraints]

    ## Outputs all valid sudoku solutions.
    for solution in pycosat.itersolve(cnf):
        X = [inverse_transform(v) for v in solution if v > 0]
        for i, cell in enumerate(sorted(X, key=lambda h: h[0] * N * N + h[1] * N)):
            print(cell[2] + 1, end=" ")
            if (i + 1) % N == 0:
                print("")
        print("\n-----------------\n")
