import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# Define the Vision Agent
root_agent = Agent(
    name="VisionAgent",
    model="gemini-2.5-flash", # Essential for image support
    instruction="""
    You are a professional fashion consultant. 
    Analyze the provided image and return a structured JSON response.
    Identify:
    - item_name: (e.g., Slim-fit Chinos)
    - color_palette: (Primary and secondary colors)
    - material_guess: (e.g., Denim, Silk, Cotton)
    - style_vibe: (e.g., Business Casual, Streetwear, Minimalist)
    - quick_tip: A 1-sentence advice on how to style this.
    """
)