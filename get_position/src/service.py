import cv2
from detection.detect import RobisDetection
from detection.subscription_manager import GetAvalibleCamera
from PIL import Image as img
import json

from is_msgs.image_pb2 import ObjectAnnotations, ObjectAnnotation, BoundingPoly, Vertex
from is_wire.core import Message, Channel, Logger


class Service():

    def __init__(self,config_file):
        self.config = json.load(open(config_file, 'r'))
        self.broker_uri = self.config['broker_uri']
        self.threshold = self.config['threshold']
        self.channel = Channel(self.broker_uri)
        self.getAvalibleCamera = GetAvalibleCamera(self.broker_uri)
        self.camera_ids = self.getAvalibleCamera.run()
        self.robis_detection = RobisDetection(self.threshold)
        self.cameras = self.robis_detection.set_cameras(self.broker_uri,self.camera_ids)


    def publish(self, list_robis):
        Boundingpoly = BoundingPoly(vertices = [Vertex(x = list_robis[0][2], y = list_robis[0][3]), 
                                                Vertex(x = list_robis[0][2], y = list_robis[0][5]), 
                                                Vertex(x = list_robis[0][4], y = list_robis[0][3]), 
                                                Vertex(x = list_robis[0][4], y = list_robis[0][5])])
            
        objectannotation = ObjectAnnotation(region = Boundingpoly, id = 1)
        objectannotations = ObjectAnnotations(objects = [objectannotation])
        message = Message(content = objectannotations)
        self.channel.publish(message, topic = f"Robis.{self.camera_id}.Detection")


    def run(self):

        while True:
            detect_list = []

            for camera in self.cameras:
                try:
                    frame, self.camera_id = camera.consume_image()              
                except:
                    pass
                
                color_coverted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image=img.fromarray(color_coverted)

                results = self.robis_detection.score_frame(pil_image)
                list_robis = self.robis_detection.detect_boxes(results, frame, self.camera_id)

                if list_robis != []:
                    self.publish(list_robis)
                    detect_list.append(list_robis[0][0])   
                else:
                    pass 
            
            log_detector.info(f"Robis detected by cameras:{detect_list}")  
                

if __name__ == '__main__':

    log_detector = Logger(name="Detector")

    config_file = "../etc/config/config.json"
    service = Service(config_file)
    service.run()
