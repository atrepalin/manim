from .flow import FordFulkersonFromAdjacency
from .tree import KruskalFromAdjacency, PrimFromAdjacency
from .transport import NorthwestCornerTransport

scenes = {
    "flow": FordFulkersonFromAdjacency,
    "transport": NorthwestCornerTransport,
    "mst_prim": PrimFromAdjacency,
    "mst_kruskal": KruskalFromAdjacency
}