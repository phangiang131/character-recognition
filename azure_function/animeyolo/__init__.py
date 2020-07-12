
import argparse
import cv2
import os
import logging
import json

import azure.functions as func
import numpy as np
from azure.storage.blob import BlockBlobService

from __app__.shared_code.utils import * 
from .yolo_helper import * 



account_name = 'animefacerecog'
account_key = 'uHDXGLKui5bjKWCIoTERMLnJYL8M+hSRtgta8/PJvVdguIS4Gl+ukaU+cBO+zhNt9M5RE+V37PA7oJOW6jlCCg=='

block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
if not os.path.exists('data.names'):
    block_blob_service.get_blob_to_path('yolomodel','data.names','data.names')
    block_blob_service.get_blob_to_path('yolomodel','yolov3.cfg','yolov3.cfg')
    block_blob_service.get_blob_to_path('yolomodel','yolov3.weights','yolov3.weights')


labelsPath = 'data.names'
LABELS = open(labelsPath).read().strip().split("\n")


weightsPath = "yolov3.weights"
configPath = "yolov3.cfg"

net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # url = 'https://vignette.wikia.nocookie.net/swordartonline/images/7/7d/Kazuto.png/revision/latest/scale-to-width-down/350?cb=20140228021321'
    # image = read_image_from_url(url)
    image_path = req.params.get('imagepath')
    image = read_image_from_blob(block_blob_service,'animeimage',image_path,0)

    layer_ouput = get_outputlayer(image,net)
    bouding_box = {'bouding_box':get_boudingbox(image,layer_ouput)}
    return func.HttpResponse(
        json.dumps(bouding_box),
        mimetype='application/json'
    )
    
