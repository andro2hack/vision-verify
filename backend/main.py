from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import uvicorn
import image_utils
import numpy as np
import random
import os
import shutil
import gdown
from google.cloud import vision
import pathlib

app = FastAPI()

# Allow CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database for Use Case 1 (List of dicts: {filename, embedding})
reference_database = []

@app.get("/")
def read_root():
    return {"message": "Image Analysis API is running"}


# --- Use Case 1: Image Match ---

@app.post("/upload_references")
async def upload_references(files: List[UploadFile] = File(...)):
    global reference_database
    # Clear old database? Assuming append or replace based on user requirement. 
    # "once the images are loaded" suggests a session. Let's append for now or clear.
    # User said "populate the matching image database", usually implies setting it up.
    # Let's clear to be safe/simple for this prototype.
    reference_database = [] 
    
    processed_count = 0
    for file in files:
        if len(reference_database) >= 100:
            break
        content = await file.read()
        embedding = image_utils.get_embedding(content)
        if embedding is not None:
            reference_database.append({
                "filename": file.filename,
                "embedding": embedding
            })
            processed_count += 1
            
            
    return {"message": f"Successfully loaded {processed_count} images into database.", "count": processed_count}

@app.post("/import_drive")
async def import_drive(link: str = Body(..., embed=True)):
    global reference_database

    # Create temp directory
    temp_dir = "temp_drive_download"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        # Check if it's a folder or file link
        # gdown.download_folder works for folders
        # We assume folder for "database" population
        
        # gdown usually prints to stdout, we supress or log?
        print(f"Downloading from Drive: {link}")
        
        # gdown.download_folder(url, output=output_folder, quiet=False, use_cookies=False)
        # It handles different link formats usually.
        # Note: Public folders only roughly supported without auth.
        
        extracted_files = gdown.download_folder(url=link, output=temp_dir, quiet=False)
        
        if not extracted_files:
            return {"error": "No files found or invalid link. Make sure the folder is Public.", "count": 0}

        # Clear old database
        reference_database = []
        processed_count = 0
        
        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                if len(reference_database) >= 100:
                    break
                    
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    try:
                        filepath = os.path.join(root, filename)
                        with open(filepath, "rb") as f:
                            content = f.read()
                            
                        embedding = image_utils.get_embedding(content)
                        if embedding is not None:
                            reference_database.append({
                                "filename": filename,
                                "embedding": embedding
                            })
                            processed_count += 1
                    except Exception as e:
                        print(f"Failed to process {filename}: {e}")

        return {"message": f"Successfully loaded {processed_count} images from Drive.", "count": processed_count}

    except Exception as e:
        print(f"Drive Import Error: {e}")
        return {"error": f"Failed to download from Drive: {str(e)}"}
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.post("/match_image")
async def match_image(file: UploadFile = File(...)):
    if not reference_database:
        return {"error": "Database is empty. Please upload reference images first."}
        
    content = await file.read()
    query_embedding = image_utils.get_embedding(content)
    
    if query_embedding is None:
        raise HTTPException(status_code=400, detail="Could not process image")
        
    # Find best match
    best_match = None
    best_score = -1.0
    
    for item in reference_database:
        score = image_utils.cosine_similarity(query_embedding, item["embedding"])
        if score > best_score:
            best_score = score
            best_match = item["filename"]
            
    # Simple thresholding logic, scaling -1..1 to 0..10?
    # Cosine similarity is usually 0..1 for non-negative vectors (like CNN relu outputs usually are)
    # But normalized vectors can be negative? CNN features after relu are non-negative.
    # So range is 0..1.
    # Let's map 0..1 to 0..10.
    final_score = float(round(max(0, best_score) * 10, 1))
    
    return {
        "match_found": True,
        "best_match_filename": best_match,
        "score": final_score, # out of 10
        "is_match": final_score > 8.0 # threshold
    }

# --- Use Case 2: Internet Check (Real via SerpApi) ---

@app.post("/check_internet")
async def check_internet(file: UploadFile = File(...)):

    # Check for credentials file
    # Check for credentials file
    # Ensure path is absolute or matches where running from
    creds_path = os.path.join(os.path.dirname(__file__), "service_account.json")
    if not os.path.exists(creds_path):
        return {
            "found_on_internet": False,
            "score": 0,
            "sources": [],
            "error": "Missing 'service_account.json' in backend folder. Please verify the file is present."
        }

    try:
        # Instantiate client with credentials
        client = vision.ImageAnnotatorClient.from_service_account_json(creds_path)
        
        # Read file content
        content = await file.read()
        image = vision.Image(content=content)
        
        # Perform Web Detection
        response = client.web_detection(image=image)
        annotations = response.web_detection
        
        if response.error.message:
            raise Exception(f"Google Vision API Error: {response.error.message}")

        found = False
        sources = []
        score = 0.0

        # Check for full matching images
        if annotations.full_matching_images:
            found = True
            for img in annotations.full_matching_images[:5]:
                if img.url:
                    sources.append(img.url)
                    
        # Check for partial matching images
        if annotations.partial_matching_images:
            found = True
            for img in annotations.partial_matching_images[:5]:
                if img.url and img.url not in sources:
                    sources.append(img.url)
                    
        # Check for pages with matching images
        if annotations.pages_with_matching_images:
            found = True
            for page in annotations.pages_with_matching_images[:5]:
                if page.url and page.url not in sources:
                    sources.append(page.url)

        # Calculate score (Mock logic based on matches)
        # In real scenario, web_entities can also provide context
        if found:
            score = 9.5
        else:
             # If entities found but no direct image match, slight score?
             # For now, keep it binary-ish
             score = 1.0

        return {
            "found_on_internet": found,
            "score": score,
            "sources": sources
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DEBUG: Exception in check_internet: {repr(e)}")
        return {
            "found_on_internet": False,
            "score": 0,
            "sources": [],
            "error": f"Google Vision Error: {str(e)}"
        }

# --- Use Case 3: AI Detection (Mock) ---

@app.post("/check_ai")
async def check_ai(file: UploadFile = File(...)):
    await file.read()
    
    # Randomly assign probability
    is_ai = random.choice([True, False])
    confidence = random.uniform(80, 99) if is_ai else random.uniform(0, 20)
    
    return {
        "is_ai_generated": is_ai,
        "confidence_score": round(confidence, 1),
        "details": "Detected high-frequency artifacts consistent with GANs" if is_ai else "Natural noise patterns detected"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
