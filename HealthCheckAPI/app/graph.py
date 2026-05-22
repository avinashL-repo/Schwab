# app/graph.py
import networkx as nx

def build_dag(components):
    """
    Build a DAG from a list of components.
    Each component: {"name": str, "depends_on": [str]}
    """
    G = nx.DiGraph()
    for comp in components:
        G.add_node(comp["name"])
        for dep in comp.get("depends_on", []):
            G.add_edge(dep, comp["name"])
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("The input graph must be a DAG.")
    return G

def bfs_traversal(G, start_nodes=None):
    """Breadth-first traversal of DAG"""
    if start_nodes is None:
        start_nodes = [n for n, d in G.in_degree() if d == 0]
    visited = []
    queue = list(start_nodes)
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            queue.extend([n for n in G.successors(node) if n not in visited])
    return visited