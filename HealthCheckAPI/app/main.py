from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os

from app.health import check_component_health
from app.graph import build_dag, bfs_traversal
from app.visualisation import visualize_dag

app = FastAPI()

# ---------------------------------------------------
# Global cache for latest computed health results
# ---------------------------------------------------
latest_health_result = None

# DAG image path
DAG_IMAGE_PATH = "dag.png"


# ---------------------------------------------------
# ROOT
# ---------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "System Health Check API Running"
    }


# ---------------------------------------------------
# POST /health
# Computes health + updates DAG + stores cache
# ---------------------------------------------------
@app.post("/health")
async def health_check(system: dict):

    global latest_health_result

    components = system.get("components", [])

    if not components:
        raise HTTPException(
            status_code=400,
            detail="No components provided."
        )

    # Build DAG
    dag = build_dag(components)
    ordered_nodes = bfs_traversal(dag)

    results = []
    status_map = {}

    # ---------------------------------------------------
    # Compute health with dependency propagation
    # ---------------------------------------------------
    for node in ordered_nodes:

        comp_data = dag.nodes[node]

        url = comp_data.get("url")
        deps = comp_data.get("depends_on", [])

        # ---------------------------------------------------
        # FIX: ANY non-healthy dependency blocks execution
        # ---------------------------------------------------
        if any(status_map.get(dep) != "healthy" for dep in deps):

            status = "unhealthy"
            reason = "dependency_failure"

        else:

            result = await check_component_health(node, url)
            status = result["status"]
            reason = "http_check"

        status_map[node] = status

        results.append({
            "component": node,
            "url": url,
            "status": status,
            "reason": reason,
            "depends_on": deps
        })

    overall_status = (
        "healthy"
        if all(r["status"] == "healthy" for r in results)
        else "unhealthy"
    )

    # ---------------------------------------------------
    # UPDATE DAG VISUALIZATION
    # ---------------------------------------------------
    visualize_dag(dag, results, DAG_IMAGE_PATH)

    # ---------------------------------------------------
    # CACHE RESULT
    # ---------------------------------------------------
    latest_health_result = {
        "overall_status": overall_status,
        "components": results
    }

    return latest_health_result


# ---------------------------------------------------
# GET /dashboard
# ---------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():

    global latest_health_result

    if not latest_health_result:
        return HTMLResponse("""
        <html>
            <body>
                <h2>No health data available.</h2>
                <p>POST data to /health first.</p>
            </body>
        </html>
        """)

    overall_status = latest_health_result["overall_status"]
    results = latest_health_result["components"]

    rows_html = ""

    for r in results:

        color = "green" if r["status"] == "healthy" else "red"

        depends_on = (
            ", ".join(r["depends_on"])
            if isinstance(r["depends_on"], list)
            else r["depends_on"]
        )

        rows_html += f"""
        <tr>
            <td>{r['component']}</td>
            <td>{r['url']}</td>
            <td style="color:{color}; font-weight:bold">
                {r['status']}
            </td>
            <td>{r['reason']}</td>
            <td>{depends_on if depends_on else "-"}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>System Health Dashboard</title>

        <style>
            body {{
                font-family: Arial;
                margin: 20px;
                background-color: #f7f7f7;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                background-color: white;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}

            th {{
                background-color: #4CAF50;
                color: white;
            }}

            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>

    <body>

        <h2>System Health Dashboard</h2>

        <h3>
            Overall Status:
            <span style="color:{'green' if overall_status == 'healthy' else 'red'}">
                {overall_status.upper()}
            </span>
        </h3>

        <table>
            <tr>
                <th>Component</th>
                <th>URL</th>
                <th>Status</th>
                <th>Reason</th>
                <th>Depends On</th>
            </tr>

            {rows_html}
        </table>

    </body>
    </html>
    """

    return HTMLResponse(content=html)


# ---------------------------------------------------
# GET /dag_image
# ---------------------------------------------------
@app.get("/dag_image")
def get_dag_image():

    if os.path.exists(DAG_IMAGE_PATH):
        return FileResponse(DAG_IMAGE_PATH)

    raise HTTPException(
        status_code=404,
        detail="DAG image not found."
    )