import json
import base64
import numpy as np
from numpy.linalg import norm

def create_object(body):
  b = base64.b64decode(body)
  json_string = b.decode('utf-8')
  dictionary = json.loads(json_string)
  self_obj, bulk_obj = dictionary['selfie_image'], dictionary['bulk_images']
  return self_obj, bulk_obj

def get_matches(s_obj, b_obj):
  matchings = []
  s_faces = s_obj['face_info']
  for s_face in s_faces:
    for b_img in b_obj:
      if isinstance(b_img, dict):
        print('checking', b_img['id'])#, b_img['image_url'])
        b_face = b_img['face_info']
        if len(b_face) != 0 :
          distances = []
          for bs in b_face:
            distance = distance = np.sqrt(np.sum(np.square(np.array(s_face) - np.array(bs))))
            distances.append(distance)
          print(min(distances))
          if min(distances)<=0.8:
            matchings.append(b_img['id'])
  return list(set(matchings))
  
def lambda_handler(event, context):
  response = {}
  body = event['body']
  #print(body)
  s_obj, b_obj = create_object(body)
  #print('selfie', s_obj['image_url'])
  if len(s_obj['face_info']) > 2:
    response = {'body': json.dumps({'statusCode' : 422,'data' : 'More than 2 faces found in selfie'})} 
  elif len(s_obj['face_info']) == 0:
    response = {'body': json.dumps({'statusCode' : 422,'data' : 'No faces found in selfie'})}
  else :
    res = get_matches(s_obj, b_obj)
    final_matches = []
    for objects in b_obj:
      if isinstance(objects, dict):
        if objects['id'] in res:
          new_res = {}
          new_res['id'] = objects['id']
          new_res['type'] = objects['type']
          #new_res['url'] = objects['image_url']
          final_matches.append(new_res)
          response = {'body': json.dumps({'statusCode' : 200,'data' : final_matches})} 
  if len(response.keys()) == 0:
    response = {'body': json.dumps({'statusCode' : 200, 'data' : []})}
  #print(response)
  return response
