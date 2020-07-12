import json
import io

import torch
from PIL import Image
from torchvision import transforms


def load_model(model_path = 'model.pth'):

    model = torch.load('model.pth')
    model.eval()
    return model

def get_transform():
    transform = transforms.Compose([            
                transforms.Resize(224),                    
                transforms.ToTensor(),                     
                transforms.Normalize(                      
                mean=[0.485, 0.456, 0.406],               
                std=[0.229, 0.224, 0.225]                  
                )])
    return transform

def get_input(raw):
    print(type(raw))
    img = Image.open(io.BytesIO(raw)).convert('RGB')
    return img

def model_run(transform,img,model):
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    out = model(batch_t)
    return out

def get_output_label(out,classes,k=5):
    _, indices = torch.sort(out, descending=True)

    return[classes[idx] for idx in indices[0][:k]]


