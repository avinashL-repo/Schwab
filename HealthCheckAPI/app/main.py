from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os

from app.health import check_component_health
from app.graph import build_dag, bfs_traversal
from app.visualisation import visualize_dag

app = FastAPI(
    title="System Health Check API",
    description="Checks health of components arranged as a DAG",
    version="1.0.0"
)

DAG_IMAGE_PATH = "dag.png"


@app.get("/")
def root():
    return {
        "message": "System Health Check API is running. Use /docs for Swagger UI."
    }


@app.post("/health")
async def health_check(system: dict):

    components = system.get("components", [])
    if not components:
        raise HTTPException(status_code=400, detail="No components provided.")

    # Build DAG
    dag = build_dag(components)

    # Get traversal order
    ordered_nodes = bfs_traversal(dag)

    results = []
    status_map = {}

    # ✅ Dependency-aware execution
    for node in ordered_nodes:
        comp_data = dag.nodes[node]
        url = comp_data.get("url")
        deps = comp_data.get("depends_on", [])

        # ❗ propagate dependency failure
        if any(status_map.get(dep) != "healthy" for dep in deps):
            result = {
                "component": node,
                "status": "unhealthy"
            }
            status_map[node] = "unhealthy"
            results.append(result)
            continue

        # actual health check
        result = await check_component_health(node, url)
        status_map[node] = result["status"]
        results.append(result)

    overall_status = (
        "healthy"
        if all(r["status"] == "healthy" for r in results)
        else "unhealthy"
    )

    visualize_dag(dag, results, DAG_IMAGE_PATH)

    return {
        "overall_status": overall_status,
        "components": results,
        "dag_image": DAG_IMAGE_PATH
    }


@app.get("/dag_image")
def get_dag_image():
    if os.path.exists(DAG_IMAGE_PATH):
        return FileResponse(DAG_IMAGE_PATH)
    raise HTTPException(status_code=404, detail="DAG image not found.")