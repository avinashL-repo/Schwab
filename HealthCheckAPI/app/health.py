# app/health.py
import asyncio
import httpx

async def check_component_health(name, url=None):
    """
    Check component health via HTTP GET if URL is provided.
    If URL responds with 200 => healthy
    Any exceptions => unhealthy
    """
    if url:
        try:
            async with httpx.AsyncClient(timeout=10, verify=True) as client:
                response = await client.get(url)
                if 200 <= response.status_code < 300:
                    status = "healthy"
                else:
                    status = "unhealthy"
        except httpx.RequestError as e:
            print(f"[ERROR] {name} request failed: {e}")
            status = "unhealthy"
    else:
        status = "healthy"

    print(f"[INFO] {name} status: {status}")
    return {"component": name, "status": status}