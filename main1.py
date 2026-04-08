from fastapi import FastAPI, UploadFile, File
from vision_agent.agent import root_agent
import base64

app = FastAPI()

@app.post("/analyze")
async def analyze_clothing(file: UploadFile = File(...)):
    # Read and encode image for Gemini
    image_data = await file.read()
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    
    # Call the ADK Agent
    response = root_agent.run(
        input_text="What is this clothing item?",
        input_images=[encoded_image] # ADK handles the multimodal part
    )
    
    return {"status": "success", "analysis": response.text}