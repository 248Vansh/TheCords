import os
from dotenv import load_dotenv
from google import genai
from pathwayPipeline import result 

# Load API key for Gemini
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Generate health advice for each city based on Pathway output
for row in result.to_dicts():
    city = row["city"]
    advice = row["advice"]
    prompt = f"City: {city}. Route advice: {advice}. Is it safe to run today?"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    print(f"HealthBot for {city}:\n{response.text}\n")

