import torch
import requests
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import uvicorn
import nest_asyncio
import io
from lavis.common.gradcam import getAttMap
from lavis.models import load_model_and_preprocess
from vqa_model import VQAModel  # Import class VQAModel

# setup device to use
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load pnp-vqa model
model, vis_processors, txt_processors = load_model_and_preprocess(name="pnp_vqa", model_type="base", is_eval=True, device=device)

# Sử dụng nest_asyncio để chạy Uvicorn trong notebook
nest_asyncio.apply()

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

class Query(BaseModel):
    img_data: bytes = None
    question: str = None
    answer: str = None

query = Query()
vqamodel = VQAModel()  # Khởi tạo instance của VQAModel

@app.get("/get")
async def home():
    global query
    return {"answer": query.answer}

@app.post("/submit")
async def submit(img: UploadFile = File(...), question: str = Form(...)):
    global query
    global vqamodel
    query.img_data = vqamodel.img_data = await img.read()  # Đọc dữ liệu từ file ảnh
    query.question = vqamodel.question = question
    query.answer = vqamodel.answering_full_step()
    return {"message": "Submit thành công", "answer": query.answer}

# Tạo đường hầm ngrok cho server trên cổng 8000
# ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")  
# public_url = ngrok.connect(8000)
# print("Public URL:", public_url)

# Chạy server FastAPI với Uvicorn trên cổng 8000
uvicorn.run(app, host="0.0.0.0", port=8000)
