from google.adk import Agent

from .vision_agent.agent import root_agent as vision_agent
from .context_agent.agent import root_agent as context_agent


# Root agent (REQUIRED for adk run)
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",  # ✅ REQUIRED
    description="Main orchestrator",
    instruction="""
    You are StyleSync Vision, a personal fashion assistant.

    Help users understand, improve, and style their outfits with confidence.

    - Use VisionAgent when images are provided to analyze clothing, colors, and style.
    - Use ContextAgent when advice depends on factors like weather, occasion, or setting.
    - Combine insights when needed to give complete, practical recommendations.
    - Keep responses stylish, clear, and actionable.

    Your goal is to make every user feel confident and well-dressed.
    """,
    sub_agents=[
        vision_agent,
        context_agent,
    ],
)

agents = [
    vision_agent,
    context_agent,
]

print("Loaded agents:", agents)