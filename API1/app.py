import json
import base64
import os
import time
import io
from io import BytesIO
from PIL import Image
import requests
import pyheif
from keras_facenet import FaceNet


def create_object(encoding):
  b = base64.b64decode(encoding)
  json_string = b.decode('utf-8')
  dictionary = json.loads(json_string)
  #print('data', dictionary)
  return dictionary


def get_img(data_url, data_format, data_type):
    print('checking for', data_url)
    key = data_format.split('/')[-1]
    #print(key)
    if key.lower() == 'png':
      return 'png'
    
    if data_type == 'User': fix_path = '/tmp/selfie_'
    else: fix_path = '/tmp/'
    
    new_path = fix_path+data_url.lower().split('?')[0].split('/')[-1].split('.')[0]+'.jpg'
    
    r = requests.get(data_url, stream=True)
    print(r)
    if r.status_code != 200:
      return 'invalid'
    
    if key == '.heic':
        heif_file = pyheif.read(io.BytesIO(r.content))
        img = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode)

    else:
        img = Image.open(io.BytesIO(r.content))

    #if data_type =='Media': img = img.resize((600, 600))
    img = img.save(new_path)
    
    return new_path


def find_faces(embedder, img_path):
  info =embedder.extract(img_path, threshold=0.95)
  os.remove(img_path)
  #print(info)
  info = [face['embedding'].tolist() for face in info]
  return info

def clear_cache(cache_folder = '/tmp/.keras-facenet'):
 max_age = 5 * 60  # 5 mins in seconds
 for filename in os.listdir(cache_folder):
    file_path = os.path.join(cache_folder, filename)
    if os.path.isfile(file_path):
        file_age = time.time() - os.path.getctime(file_path)
        if file_age > max_age:
            os.remove(file_path)


def lambda_handler(event, context):
  new_res= {}
  global embedder
  embedder = FaceNet(cache_folder='/tmp/.keras-facenet')
  img = event['body']
  data = create_object(img)
  if len(data) == 0:
    response = {'body': json.dumps({'statusCode' : 200,'data' : new_res})}
    return response
  else:
    data_id, data_type, data_format, data_url = data['id'], data['type'], data['format'], data['image_url']
    new_p = get_img(data_url, data_format, data_type)
    #print(new_p.lower())
    if new_p.lower() == 'png' or new_p.lower() == 'invalid':
      response = {'body': json.dumps({'statusCode' : 422,'data' : 'Invalid input type'})}
      #print('into invalid')
      return response
    else: 
      res = find_faces(embedder, new_p)
      new_res['id'] = data_id
      new_res['type'] = data_type
      new_res['face_info'] = res
      print('faces found', len(new_res['face_info']))
      response = {'body': json.dumps({'statusCode': 200, 'data': new_res})}
      clear_cache()
      return response
