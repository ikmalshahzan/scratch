import io
import json
import re
import time
import os
from PIL import Image
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────
# ▶▶ GEMINI API KEY SETUP
# ─────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = input("Please enter your Gemini API Key: ")

# Initialize the client — one client, all models
client = genai.Client(api_key=GEMINI_API_KEY)
print("[OK] Client initialized successfully")

def analyze_with_gemini(img_bytes: bytes, context: str = "", is_pdf: bool = False) -> dict:
    """
    Send a medical scan or PDF report to Gemini for diagnosis.
    Returns a structured JSON dict with diagnosis, findings, exercises, etc.
    """
    prompt = f"""You are a senior radiologist and clinical AI. Analyze this medical {"report" if is_pdf else "image"} carefully and thoroughly.

Respond ONLY with a raw JSON object — no markdown, no code fences, no extra text.

{{
  "image_type": "X-ray | MRI | CT | Ultrasound | Report | Photo | Other",
  "diagnosis": "Primary diagnosis in clear plain language (2-3 sentences, covering ALL key findings)",
  "confidence": "high | medium | low",
  "severity": "mild | moderate | severe",
  "affected_regions": ["every specific body region affected, be detailed"],
  "findings": ["finding 1", "finding 2", "finding 3", "finding 4", "finding 5"],
  "recommendations": ["rec 1", "rec 2", "rec 3", "rec 4"],
  "body_map_prompt": "Detailed prompt for Gemini image generation: a front-view and side-view full human body medical anatomical illustration on white background, with [SPECIFIC REGIONS] highlighted in glowing red/orange with arrows and labels.",
  "exercise_needed": true,
  "exercises": [
    {{
      "name": "Exercise name",
      "purpose": "Why this specific exercise helps this specific condition",
      "difficulty": "easy | moderate | hard",
      "duration": "e.g. 10-15 minutes",
      "reps": "e.g. 3 sets of 10",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "illustration_prompt": "A person performing [exercise] correctly. Clean white background, instructional style, bright studio lighting. No text overlays."
    }}
  ],
  "urgency": "routine | urgent | emergency",
  "disclaimer": "Always consult a qualified physician before acting on any AI-generated medical analysis."
}}

Give exactly 4 exercises tailored to the diagnosed condition.
{f'Patient context: {context}' if context else ''}"""

    # Build the contents list — PDF gets sent as a document, images as JPEG bytes
    if is_pdf:
        contents = [types.Part.from_bytes(data=img_bytes, mime_type="application/pdf"), prompt]
    else:
        contents = [types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"), prompt]

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=contents
    )

    # Strip any accidental markdown code fences Gemini might add
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$",     "", raw)
    raw = re.sub(r"^```\s*",     "", raw)

    return json.loads(raw)

def generate_body_map(prompt: str) -> Image.Image | None:
    """
    Generate an anatomical body map image from a text prompt.
    """
    full_prompt = prompt + " Medical illustration, white background, anatomical precision, professional."

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[full_prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]  # must explicitly request IMAGE output
        ),
    )

    # The response parts can be a mix of text and image — find the image part
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:          # inline_data = raw image bytes
            return Image.open(io.BytesIO(part.inline_data.data))

    print("[WARNING] No image returned by model.")
    return None

def generate_exercise_video(prompt: str, output_filename: str) -> bool:
    """
    Generate an exercise demonstration video using Veo.
    """
    full_prompt = (
        prompt
        + " Fitness demonstration video, clear body form, bright studio lighting, "
          "plain white background, slow and instructional pace, no text overlays."
    )

    print(f"   Submitting to Veo: {prompt[:70]}...")

    # Step 1: Submit — returns immediately with an operation handle
    operation = client.models.generate_videos(
        model="veo-3.1-lite-generate-preview",
        prompt=full_prompt,
    )

    # Step 2: Poll until done (typically 60–120s)
    for attempt in range(36):          # max ~6 minutes
        time.sleep(10)
        operation = client.operations.get(operation)
        elapsed = (attempt + 1) * 10
        print(f"   Polling... {elapsed}s | done={operation.done}")
        if operation.done:
            break

    # Step 3: Download and save
    if operation.done and operation.response and operation.response.generated_videos:
        video = operation.response.generated_videos[0]
        client.files.download(file=video.video)     # populates video.video.video_bytes
        video_bytes = video.video.video_bytes
        with open(output_filename, "wb") as f:
            f.write(video_bytes)
        print(f"   [OK] Saved -> {output_filename}  ({len(video_bytes)//1024} KB)")
        return True
    else:
        print(f"   [ERROR] No video returned. done={operation.done}")
        return False

if __name__ == "__main__":
    print("\n--- MediScan Setup Complete ---")
    
    # -------------------------------------------------------------
    # Example Usage:
    # -------------------------------------------------------------
    
    SCAN_FILE = r"C:\Users\imans\.gemini\antigravity\brain\dc9a291b-7499-4f00-8604-b1e84bd72e5d\mock_xray_1777086780387.png"
    is_pdf = SCAN_FILE.lower().endswith(".pdf")
    
    if os.path.exists(SCAN_FILE):
        with open(SCAN_FILE, "rb") as f:
            raw_bytes = f.read()
            
        print(f"Analyzing {SCAN_FILE}...")
        result = analyze_with_gemini(raw_bytes, context="Mock X-Ray Image Testing", is_pdf=is_pdf)
        print(json.dumps(result, indent=2))
        
        # Generate Body Map if needed
        if "body_map_prompt" in result:
            print("\nGenerating Body Map...")
            try:
                body_map = generate_body_map(result["body_map_prompt"])
                if body_map:
                    body_map.save("body_map_output.png")
                    print("Body map saved to 'body_map_output.png'")
            except Exception as e:
                print(f"[ERROR] Body Map Generation Failed: {e}")
                
        # Generate Exercise Videos
        exercises = result.get("exercises", [])
        for i, ex in enumerate(exercises):
            name = ex.get("name", f"exercise_{i+1}")
            prompt = ex.get("illustration_prompt", "")
            if prompt:
                filename = f"{name.replace(' ', '_').lower()}.mp4"
                print(f"\nGenerating Exercise Video: {name}")
                try:
                    generate_exercise_video(prompt, filename)
                except Exception as e:
                    print(f"[ERROR] Video Generation Failed: {e}")
    else:
        print(f"Please place a file named '{SCAN_FILE}' in the folder to test.")

