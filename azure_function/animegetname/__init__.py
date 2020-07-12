import logging
import os
import json

import azure.functions as func
import numpy as np
from azure.storage.blob import BlockBlobService
from __app__.shared_code.utils import * 
# from ..shared_code.utils import * 
from .helper import *


account_name = 'animefacerecog'
account_key = 'uHDXGLKui5bjKWCIoTERMLnJYL8M+hSRtgta8/PJvVdguIS4Gl+ukaU+cBO+zhNt9M5RE+V37PA7oJOW6jlCCg=='

block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
if not os.path.exists('model.pth'):
    block_blob_service.get_blob_to_path('resnetmodel','model.pth','model.pth')
    block_blob_service.get_blob_to_path('resnetmodel','data_classes.json','data_classes.json')

model_path = 'model.pth'

def main(req: func.HttpRequest) -> func.HttpResponse:
    image_path = req.params.get('imagepath')
    with open('data_classes.json','r') as f:
        classes = json.load(f)

    model = load_model(model_path)
    transform = get_transform()
    raw = read_image_from_blob(block_blob_service,'animeimage',image_path)
    img = get_input(raw)
    out = model_run(transform,img,model)
    label = {'label':get_output_label(out,classes)}

    return func.HttpResponse(
        json.dumps(label),
        mimetype='application/json'
    )
    
    

