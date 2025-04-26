def convert_to_string(matrix):
    return [[str(x) for x in row] for row in matrix]


tree = [
    [0, 4, 3, 1, 0, 0, 0, 8],
    [4, 0, 5, 2, 9, 0, 0, 0],
    [3, 5, 0, 6, 0, 7, 0, 0],
    [1, 2, 6, 0, 7, 3, 0, 0],
    [0, 9, 0, 7, 0, 8, 5, 0],
    [0, 0, 7, 3, 8, 0, 9, 0],
    [0, 0, 0, 0, 5, 9, 0, 10],
    [8, 0, 0, 0, 0, 0, 10, 0],
]

flow = [
    [0, 10, 5, 15, 0, 0, 0, 0],
    [0, 0, 4, 0, 9, 15, 0, 0],
    [0, 0, 0, 0, 4, 8, 0, 0],
    [0, 0, 0, 0, 0, 0, 16, 0],
    [0, 0, 0, 0, 0, 0, 0, 10],
    [0, 0, 0, 0, 0, 0, 0, 10],
    [0, 0, 0, 0, 0, 0, 0, 10],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

transport = [[8, 6, 10, 9, 20], [9, 7, 4, 2, 30], [3, 4, 2, 5, 25], [10, 25, 20, 20, 0]]

examples = {
    "mst_prim": convert_to_string(tree),
    "mst_kruskal": convert_to_string(tree),
    "flow": convert_to_string(flow),
    "transport": convert_to_string(transport),
}
