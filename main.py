from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Create an MCP server named "AdvancedWeather"
mcp = FastMCP("AdvancedWeather")

# Helper: call WeatherAPI asynchronously
def validate_date(dt_str: str) -> None:
    """
    Ensure date string is in YYYY-MM-DD format.
    Raises HTTPException if invalid.
    """
    try:
        datetime.strptime(dt_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date: {dt_str}. Use YYYY-MM-DD.")

async def fetch(endpoint: str, params: dict) -> dict:
    """
    Perform async GET to WeatherAPI and return JSON.
    Raises HTTPException on errors.
    """
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key not set.")

    params["key"] = WEATHER_API_KEY
    url = f"https://api.weatherapi.com/v1/{endpoint}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            detail = resp.json().get("error", {}).get("message", resp.text)
            raise HTTPException(status_code=resp.status_code, detail=detail)
        return resp.json()

# MCP Tools

@mcp.tool()
async def weather_current(q: str, aqi: str = "no") -> dict:
    """Get current weather for a location."""
    return await fetch("current.json", {"q": q, "aqi": aqi})

@mcp.tool()
async def weather_forecast(
    q: str,
    days: int = 1,
    aqi: str = "no",
    alerts: str = "no"
) -> dict:
    """Get weather forecast (1–14 days) for a location."""
    if days < 1 or days > 14:
        raise HTTPException(status_code=400, detail="'days' must be between 1 and 14.")
    return await fetch("forecast.json", {"q": q, "days": days, "aqi": aqi, "alerts": alerts})

@mcp.tool()
async def weather_history(q: str, dt: str) -> dict:
    """Get historical weather for a location on a given date (YYYY-MM-DD)."""
    validate_date(dt)
    return await fetch("history.json", {"q": q, "dt": dt})

@mcp.tool()
async def weather_alerts(q: str) -> dict:
    """Get weather alerts for a location."""
    # Alerts come from forecast with alerts=yes
    return await fetch("forecast.json", {"q": q, "days": 1, "alerts": "yes"})

@mcp.tool()
async def weather_airquality(q: str) -> dict:
    """Get air quality for a location."""
    return await fetch("current.json", {"q": q, "aqi": "yes"})

@mcp.tool()
async def weather_astronomy(q: str, dt: str) -> dict:
    """Get astronomy data (sunrise, sunset, moon) for a date (YYYY-MM-DD)."""
    validate_date(dt)
    return await fetch("astronomy.json", {"q": q, "dt": dt})

@mcp.tool()
async def weather_search(q: str) -> dict:
    """Search for locations matching query."""
    return await fetch("search.json", {"q": q})

@mcp.tool()
async def weather_timezone(q: str) -> dict:
    """Get timezone info for a location."""
    return await fetch("timezone.json", {"q": q})

@mcp.tool()
async def weather_sports(q: str) -> dict:
    """Get sports events (e.g., football, cricket) for a location."""
    return await fetch("sports.json", {"q": q})

# Run the MCP server
if __name__ == "__main__":
    # This starts a Server-Sent Events (SSE) endpoint on port 8000
    mcp.run(host="0.0.0.0", port=8000)
