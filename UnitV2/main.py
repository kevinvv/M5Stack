from flask import Flask, request
from flask_cors import CORS
from PIL import Image # change for pillow?

import base64
import io
import json

app = Flask(__name__)
CORS(app)

@app.route('/receiver/<uuid>', methods=['POST'])
def add_message(uuid):    
    
    byte_data = base64.b64decode(request.json['img'])
    img = Image.open(io.BytesIO(bytes(byte_data)))

    img_location = f"resources/devices/{uuid}/{request.json['time']}-{len(request.json['object'])}"

    img.save(f'{img_location}.jpg', 'jpeg')    
    request.json['img'] = f'{img_location}.jpg'

    with open(f'{img_location}.json', 'w') as f:
        json.dump(request.json, f)

    return "Succes"


