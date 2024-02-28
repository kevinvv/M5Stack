from datetime import datetime, timedelta
from json.decoder import JSONDecodeError

import subprocess
import json
import requests
import sys



class UnitV2Sender(object):

    """ 
        Wrapper class to send object detection data from the Unitv2 to an API server.
        Intended to be used together with Flask Python Server.
        
        Could be modified to work for other modus.
        The default available models are: "nanodet_80class" and "yolo_20class". 
        Custom models can be added to the UnitV2 as well and should work with this wrapper.
        Change server_ip to your own server address.
        Change the endpoint if this is different for your API.
        If you are using multiple UnitV2 devices increment the uuid.
        Data will be sent only if the selected classes are detected.
    """
    
    def __init__(self, 
                 modus = "object_recognition", # Unit V2 modus
                 model = "nanodet_80class", # Selected object detection model
                 server_ip = 'http://192.168.0.142:5000', # Server IP
                 endpoint = 'receiver', # API endpoint
                 uuid = '0001', # Unique device id
                 classes = ['person'], # only send data for these classes
                 probability_treshhold = 0.6, # only send data if model is over 60% confidence
                 interval = 1 # seconds
        ):

        # Sender info
        self.modes = f'/home/m5stack/payload/bin/{modus}'
        self.model = f'/home/m5stack/payload/uploads/models/{model}'

        self.server_ip = server_ip
        self.endpoint = endpoint
        self.uuid = uuid
        self.post_adress = f"{self.server_ip}/{self.endpoint}/{self.uuid}"
        
        # Sender process
        self.run = True # always true makes sure the loop runs
        self.test_run = True # if true only runs for three loops
        self.run_counter = 0 # keeps track of the runs
        self.classes = classes # the object classes to be detected
        self.probability_treshhold = probability_treshhold # threshold of detection
        self.recognizer = None # Will read output of the model
        self.payload = None # will contain the information send to the server
        self.timer = datetime.now() # will be used for the interval
        self.interval = interval # determines how often to send the data
        
        # sender setup                
        self.reset_payload() # prepares the payload
        self.setup() # starts the model and initiates recognizer
    
    def test_log(self, msg):

        if self.test_run_counter >= 3:
            print("Test Done")
            sys.exit()

        if not self.test_run:
            return
        
        print(msg)        
        

    def setup(self):    

        self.test_log("Setting up")

        self.recognizer = subprocess.Popen([self.modes, self.model],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.recognizer.stdin.write("_{\"stream\":1}\r\n".encode('utf-8'))
        self.recognizer.stdin.flush()
        self.recognizer.stdout.flush()

    def reset_payload(self):

        self.test_log('reset payload')

        self.payload = {}
        self.payload['object'] = []

    def check_payload(self):

        self.test_log('checking payload')

        return 'img' in self.payload and len(self.payload['object']) > 0
        
    def send_payload(self):      

        self.test_log(f'sending payload: {self.payload}')   

        if not self.test_run:
            requests.post(url=self.server_ip, json=self.payload)

        self.reset_payload()

    def check_timer(self):
        return self.timer < datetime.now()-timedelta(seconds=self.interval)

    def loop(self):

        self.test_log("Starting Loop")

        while self.run:

            line = self.recognizer.stdout.readline().decode('utf-8').strip()

            try:
                print("trying")
                print(line)
                doc = json.loads(line)                
                print("after trying")
                
                if 'img' in doc:
                    self.payload['img'] = doc['img']

                elif 'num' in doc: 
                    self.payload['num'] = doc['num']  

                    for object in doc['obj']:
                        for type in self.classes:
                        
                            if object['type'] == type and object['prob'] > self.probability_treshhold:
                                self.payload['object'].append(object)
                            else:
                                print('Class could not be found in image')

                if self.check_payload() & self.check_timer():

                    self.test_log('Payload valid!')

                    self.payload['time'] = self.timer.strftime("%Y_%m_%d_%H_%M_%S")
                    self.send_payload()

                    self.timer = datetime.now()     
                    self.test_run_counter = self.test_run_counter + 1   
                    self.test_log("counter: " + self.test_run_counter)

            except JSONDecodeError as e:
                print("Error: Invalid JSON string")
                print("JSONDecodeError:", str(e))
