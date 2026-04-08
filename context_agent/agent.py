import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from ..shared.weather_tool import get_weather

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

root_agent = Agent(
    name="contextual_tailor",
    model="gemini-2.5-flash",
    tools=[get_weather], # MCP: Custom Tool
    instruction="""
    1. RECALL: Check the session state for 'garment_metadata' from the Vision Agent.
    2. CONTEXT: If location is missing, ask the user: 'Which city are you in?'
    3. TRENDS: Use 'google_search' for 2026 social media trends regarding this item.
    4. ADVISE: Provide a final styling recommendation based on the Weather + Trends.
    """
)