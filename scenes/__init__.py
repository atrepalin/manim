from .flow import FordFulkersonFromAdjacency
from .tree import KruskalFromAdjacency, PrimFromAdjacency
from .transport import NorthwestCornerTransport
from .ford import BellmanFordFromAdjacency
from .dijkstra import DijkstraFromAdjacency
from .dp import DPShortestPathFromAdjacency

scenes = {
    "flow": FordFulkersonFromAdjacency,
    "transport": NorthwestCornerTransport,
    "mst_prim": PrimFromAdjacency,
    "mst_kruskal": KruskalFromAdjacency,
    "dijkstra": DijkstraFromAdjacency,
    "ford": BellmanFordFromAdjacency,
    "dp": DPShortestPathFromAdjacency,
}
