import os, io 
from google.cloud import vision_v1
from google.cloud.vision_v1 import types


def transfo(img_link):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS' ] = r'to-fill-in'
    client = vision_v1.ImageAnnotatorClient()
    FILE_NAME='to-fill-in'+img_link
    with io.open(os.path.join(FILE_NAME),'rb') as image_file:
        content= image_file.read()
    image = vision_v1.types.Image(content=content)
    response= client.text_detection(image=image)
    texts = response.text_annotations
    final = texts[0].description
    return(final)
    
