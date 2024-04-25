from flask import Flask, request, render_template
from flask_cors import CORS
from PIL import Image

import base64
import io
import json
import os

app = Flask(__name__, static_folder='resources')
CORS(app)


@app.route('/')
def home():
    print(os.getcwd())
    print(os.listdir('./resources/gifs'))
    gifs = os.listdir('./resources/gifs/')
    gifs.remove('.gitignore')
    print(gifs)
    return render_template('index.html', gifs=gifs)

@app.route('/receiver/<uuid>', methods=['POST'])
def add_message(uuid):    
    
    byte_data = base64.b64decode(request.json['img'])
    img = Image.open(io.BytesIO(bytes(byte_data)))
    
    print(uuid)
    print(request)

    img_location = f"resources/devices/{uuid}/{request.json['time']}-{len(request.json['object'])}"

    img.save(f'{img_location}.jpg', 'jpeg')    
    request.json['img'] = f'{img_location}.jpg'

    with open(f'{img_location}.json', 'w') as f:
        json.dump(request.json, f)

    return "Succes"


