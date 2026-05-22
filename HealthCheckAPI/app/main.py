# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import asyncio
import os

from app.health import check_component_health
from app.graph import build_dag, bfs_traversal
from app.visualisation import visualize_dag

app = FastAPI(
    title="System Health Check API",
    description="Checks health of components arranged as a DAG",
    version="1.0.0"
)

# Path for DAG image
DAG_IMAGE_PATH = "dag.png"

@app.get("/")
def root():
    """
    Root endpoint to confirm API is running.
    """
    return {
        "message": "System Health Check API is running. Use /docs for Swagger UI."
    }

@app.post("/health")
async def health_check(system: dict):
    """
    Evaluate health of all components in the system DAG.
    Input JSON format:
    {
      "components": [
        {"name": "PowerBI_Website", "url": "https://www.powerbi.com", "depends_on": []},
        ...
      ]
    }
    """
    try:
        components = system.get("components", [])
        if not components:
            raise HTTPException(status_code=400, detail="No components provided.")

        # Build DAG
        dag = build_dag(components)

        # BFS traversal of DAG
        ordered_nodes = bfs_traversal(dag)

        # Run health checks asynchronously
        tasks = []
        for node in ordered_nodes:
            comp_data = dag.nodes[node]
            tasks.append(check_component_health(node, comp_data.get("url")))
        results = await asyncio.gather(*tasks)

        # Aggregate overall status
        overall_status = "healthy" if all(r["status"] == "healthy" for r in results) else "unhealthy"

        # Visualize DAG
        visualize_dag(dag, results, DAG_IMAGE_PATH)

        return {
            "overall_status": overall_status,
            "components": results,
            "dag_image": DAG_IMAGE_PATH
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dag_image")
def get_dag_image():
    """
    Returns the latest DAG image.
    """
    if os.path.exists(DAG_IMAGE_PATH):
        return FileResponse(DAG_IMAGE_PATH)
    else:
        raise HTTPException(status_code=404, detail="DAG image not found.")