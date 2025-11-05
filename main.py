from fastapi import FastAPI, Query
from fastapi.responses import Response, JSONResponse
import requests
import base64

app = FastAPI()

GEMINI_API_KEY = "AIzaSyC2Fsjk3yCRA8hDVYgg5LlMn4sxwoJJaWU"
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_API_KEY}"

@app.get("/")
async def root(prompt: str = Query(None, description="Prompt for image generation")):
    if not prompt or prompt.strip() == "":
        return JSONResponse(
            content={
                "message": "Gemini Image Generator API running... use ?prompt=your_prompt",
                "creator": "Sujan rai"
            }
        )
    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }
        response = requests.post(API_ENDPOINT, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        response.raise_for_status()
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        image_part = None
        for part in parts:
            if "inlineData" in part and part["inlineData"]["mimeType"].startswith("image/"):
                image_part = part
                break
        if not image_part:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "no image returned by model."
                }
            )
        image_base64 = image_part["inlineData"]["data"]
        mime_type = image_part["inlineData"]["mimeType"]
        image_bytes = base64.b64decode(image_base64)
        headers = {"Content-Disposition": f'inline; filename="generated_image.{mime_type.split("/")[-1]}"'}
        return Response(content=image_bytes, media_type=mime_type, headers=headers)
    except Exception:
        return JSONResponse(
            content={
                "success": False,
                "error": "failed to generate image. check prompt or try again."
            }
        )