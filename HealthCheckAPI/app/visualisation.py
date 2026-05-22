# app/visualization.py
import networkx as nx
import matplotlib.pyplot as plt

def visualize_dag(G, health_results, filename="dag.png"):
    """
    Visualize DAG with node colors based on health status.
    """
    status_map = {r["component"]: r["status"] for r in health_results}
    node_colors = [
        "green" if status_map.get(node, "healthy") == "healthy" else "red"
        for node in G.nodes
    ]

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=2000,
        font_size=12,
        arrowsize=20,
        arrowstyle='-|>'
    )
    plt.title("System Health DAG")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename