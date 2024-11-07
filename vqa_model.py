import torch
import requests
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np

from lavis.common.gradcam import getAttMap
from lavis.models import load_model_and_preprocess

class VQAModel:
    def __init__(self, img_url=None, question=None):
        self.img_data = None
        self.question = None
        self.answer = None 
        self.image = None  
        self.samples = None  

    def answering_full_step(self):
        # 0. Tiền xử lý
        raw_image = Image.open(io.BytesIO(self.img_data)).convert("RGB")  # Mở ảnh từ dữ liệu nhị phân
        self.image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
        processed_question = txt_processors["eval"](self.question)
        self.samples = {"image": self.image, "text_input": [processed_question]}
        display(raw_image.resize((400, 300)))
        print(self.question)

        # 1. Image-Question Matching - Compute the relevancy score of image patches with respect to the question using GradCAM
        self.samples = model.forward_itm(samples=self.samples)

        # Gradcam visualisation
        dst_w = 720
        w, h = raw_image.size
        scaling_factor = dst_w / w
        
        resized_img = raw_image.resize((int(w * scaling_factor), int(h * scaling_factor)))
        norm_img = np.float32(resized_img) / 255
        gradcam = self.samples['gradcams'].reshape(24,24)
        
        # Chuyển `gradcam` từ kiểu dữ liệu của `torch` sang kiểu NumPy
        gradcam = gradcam.cpu().numpy()
        
        avg_gradcam = getAttMap(norm_img, gradcam, blur=True)
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        ax.imshow(avg_gradcam)
        ax.set_yticks([])
        ax.set_xticks([])

        # 2. Image Captioning - Generate question-guided captions based on the relevancy score
        self.samples = model.forward_cap(samples=self.samples, num_captions=100, num_patches=20)
        print('Question-guided captions: ')
        print(type(self.samples), len(self.samples))
        self.samples['captions'][0][:5]

        # 3. Question Answering - Answer the question by using the captions
        pred_answers = model.forward_qa(self.samples, num_captions=50)
        
        # Lưu câu trả lời vào thuộc tính answer
        self.answer = pred_answers[0]
        return self.answer