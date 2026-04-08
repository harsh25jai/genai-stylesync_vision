import os
import json
import traceback
from google.adk import Agent
from sqlalchemy import create_engine, text

# Use the same DATABASE_URL pattern from your NeighborLoop example
DATABASE_URL = os.getenv("DATABASE_URL")
engine = None # Initialize to None

# Initialize Engine with Connection Pooling (Best Practice for Cloud Run)
try:
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment variables.")

    engine = create_engine(
        DATABASE_URL, 
        # pool_size=5, 
        # max_overflow=10, 
        pool_pre_ping=True
    )

    with engine.connect() as connection:
        print("✅ Database connection verified at startup!")
except Exception as e:
    print(f"Engine Initialization Error: {traceback.format_exc()}")

# 2. TOOLS (The Agent's "Hands")
def save_garment_to_history(user_id: str, garment_data: str) -> str:
    """
    Saves a garment's analysis to the user's permanent AlloyDB wardrobe.
    garment_data MUST be a valid JSON string.
    """
    # Guard against empty/malformed inputs from the LLM
    if not garment_data or not garment_data.strip():
        return "Error: No garment data provided. Please provide JSON details."
    
    if engine is None:
        return "Database not initialized. Check DATABASE_URL."

    try:
        data = json.loads(garment_data)
    except json.JSONDecodeError:
        return f"Error: Invalid JSON format. Received: {garment_data}"

    # Prepare metadata for embedding
    description = f"{data.get('color', '')} {data.get('material', '')} {data.get('garment_type', '')}"
    
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO user_wardrobe (user_id, garment_type, color, material, style_tags, embedding)
                VALUES (:uid, :type, :color, :mat, :tags, 
                        embedding('text-embedding-005', :desc)::vector)
            """)
            conn.execute(query, {
                "uid": user_id,
                "type": data.get('garment_type', 'Unknown'),
                "color": data.get('color', 'Unknown'),
                "mat": data.get('material', 'Unknown'),
                "tags": data.get('style_tags', []),
                "desc": description
            })
            conn.commit()
        return f"Successfully archived the {data.get('color')} {data.get('garment_type')} in your closet."
    except Exception as e:
        return f"save_garment_to_history Database Persistence Error: {str(e)}"


def find_matching_owned_items(user_id: str, style_query: str) -> str:
    """
    Uses Vector Search (RAG) to find items in the user's closet matching a vibe.
    Example: 'Find something vintage for a party'
    """
    if engine is None:
        return "Database not initialized. Check DATABASE_URL."

    try:
        with engine.connect() as conn:
            # Using pgvector <=> operator for Cosine Distance
            search_sql = text("""
                SELECT garment_type, color, material, style_tags 
                FROM user_wardrobe 
                WHERE user_id = :uid
                ORDER BY embedding <=> embedding('text-embedding-005', :query)::vector
                LIMIT 3
            """)
            result = conn.execute(search_sql, {"uid": user_id, "query": style_query})
            
            # Map results to list of dicts
            items = [dict(row._mapping) for row in result]
            
            if not items:
                return "Your wardrobe is currently empty or no matches were found."
            
            return json.dumps(items)
    except Exception as e:
        return f"Vector Search Error: {str(e)}"


def fetch_user_style_profile(user_id: str) -> str:
    """Retrieves long-term style preferences (fit, size, dislikes) from AlloyDB."""
    if engine is None:
        return "Database not initialized. Check DATABASE_URL."
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT preferred_fit, size, disliked_colors 
                FROM user_profiles 
                WHERE user_id = :uid
            """)
            result = conn.execute(query, {"uid": user_id}).fetchone()
            
            if result:
                # result._asdict() or _mapping works for SQLAlchemy 2.0
                return json.dumps(dict(result._mapping))
            
            # Default profile if none exists
            return json.dumps({
                "preferred_fit": "Standard", 
                "size": "Medium", 
                "disliked_colors": [],
                "note": "No profile found, using defaults."
            })
    except Exception as e:
        return f"Profile Retrieval Error: {str(e)}"

# The Wardrobe Agent Definition
wardrobe_agent = Agent(
    name="wardrobe_agent",
    model="gemini-2.5-flash",
    tools=[save_garment_to_history, find_matching_owned_items, fetch_user_style_profile],
    instruction="""
    ROLE: You are the StyleSync Wardrobe Manager. 

    1. PERSISTENCE: When a new garment is identified, save it using 'save_garment_to_history'.
    2. RAG RETRIEVAL: Always check 'find_matching_owned_items' when giving outfit advice to see what the user already owns.
    3. PERSONALIZATION: Call 'fetch_user_style_profile' to ensure your advice respects the user's preferred fit and color dislikes.
    
    1. USE 'fetch_user_style_profile' first to understand the user's fit and color dislikes.
    2. USE 'find_matching_owned_items' when a user asks for outfit advice to check what they ALREADY own.
    3. USE 'save_garment_to_history' to record new items.

    CORE LOGIC:
    - You manage the 'Digital Closet' stored in AlloyDB.
    - When a new item is analyzed, use 'save_garment_to_history'.
    - When asked for suggestions, use 'find_matching_owned_items' (Vector Search) to recommend what the user already owns.
    - Always respect the user's 'fetch_user_style_profile' (e.g., if they hate yellow, don't suggest it).
    
    STRICT JSON RULE: When calling 'save_garment_to_history', the 'garment_data' argument MUST be a raw JSON string. 
    Example: {"garment_type": "blazer", "color": "black", "material": "wool"}
    
    Always ground your fashion advice in the user's actual history and preferences.
    """
)

# Crucial for ADK loader
root_agent = wardrobe_agent