from google.adk import Agent

from .vision_agent.agent import root_agent as vision_agent
from .context_agent.agent import root_agent as context_agent
from .wardrobe_agent.agent import root_agent as wardrobe_agent

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

    1. VISION: If the user uploads a photo, analyze it immediately. 
       Identify the garment type, color, and material.
    2. PERSISTENCE: After identifying a garment from a photo, call the 
       'wardrobe_agent.save_garment_to_history' tool to store it.
    3. REASONING: Once saved, tell the user how this new item fits with 
       their existing wardrobe by calling 'wardrobe_agent.find_matching_owned_items'.

    Your goal is to make every user feel confident and well-dressed.
    """,
    sub_agents=[
        vision_agent,
        context_agent,
        wardrobe_agent,
    ],
)

agents = [
    vision_agent,
    context_agent,
    wardrobe_agent,
]

print("Loaded agents:", agents)