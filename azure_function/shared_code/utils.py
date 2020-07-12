import numpy as np
import requests
import cv2

def read_image_from_url(url):
    resp = requests.get(url, stream=True).raw
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def read_image_from_blob(blob,container_name,image_name,ty=1):
    if ty != 1:
        raw = np.asarray(bytearray(blob.get_blob_to_bytes(container_name,image_name).content), dtype='uint8')
        return cv2.imdecode(raw, cv2.IMREAD_COLOR)
    else:
        raw = bytearray(blob.get_blob_to_bytes(container_name,image_name).content)
        return raw

