from .flow import FordFulkersonFromAdjacency
from .tree import KruskalFromAdjacency, PrimFromAdjacency
from .transport import NorthwestCornerTransport
from .ford import BellmanFordFromAdjacency
from .dijkstra import DijkstraFromAdjacency

scenes = {
    "flow": FordFulkersonFromAdjacency,
    "transport": NorthwestCornerTransport,
    "mst_prim": PrimFromAdjacency,
    "mst_kruskal": KruskalFromAdjacency,
    "dijkstra": DijkstraFromAdjacency,
    "ford": BellmanFordFromAdjacency,
}
