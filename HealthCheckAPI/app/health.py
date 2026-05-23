# app/health.py
import asyncio
import httpx

async def check_component_health(name, url=None):
    """
    Perform HTTP health check.
    """
    if not url:
        return {"component": name, "status": "healthy"}

    try:
        async with httpx.AsyncClient(timeout=10, verify=True) as client:
            response = await client.get(url)

        status = "healthy" if 200 <= response.status_code < 300 else "unhealthy"

    except httpx.RequestError as e:
        print(f"[ERROR] {name} request failed: {e}")
        status = "unhealthy"

    print(f"[INFO] {name} status: {status}")
    return {"component": name, "status": status}