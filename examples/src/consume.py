import cv2
import argparse
import json
import socket
import numpy as np
from detection.subscription_manager import GetAvalibleCamera
from detection.cameraClient import CameraClient

# IS
from is_wire.core import Channel, Subscription, Logger
from detection.streamChannel import StreamChannel
from is_msgs.image_pb2 import ObjectAnnotations


class DetectionManager:

    def __init__(self, config_file, camera_ids):
        self.config = json.load(open(config_file, 'r'))
        self.broker_uri = self.config['broker_uri']
        self.getAvalibleCamera = GetAvalibleCamera(self.broker_uri)
        self.camera_ids = camera_ids
        self.clients = [self.create_detection_client(camera) for camera in self.camera_ids]


    def create_detection_client(self, camera_id):
        channel = StreamChannel(self.broker_uri)
        camera = CameraClient(self.broker_uri, camera_id)
        subscription = Subscription(channel)
        subscription.subscribe(f"Robis.{camera_id}.Detection")
        return {"camera_sub": camera, "channel": channel}


    def plot_boxes(self, pixels, frame):
        bgr = (0,255,0)
        cv2.rectangle(frame, (int(pixels[0][0]), int(pixels[0][1])), (int(pixels[3][0]), int(pixels[3][1])), bgr, 1)
        cv2.putText(frame, "ROBOT", (int(pixels[0][0]), int(pixels[0][1]-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, bgr, 1)
        
        return frame
    

    def run(self):
        vertices = None
        frame = None
        camera_id = None

        while True:
            for client in self.clients:

                try:
                    frame, camera_id = client["camera_sub"].consume_image()
                except:
                    pass

                if frame is not None:
                    message = False

                    try:
                        message = client["channel"].consume_last()
                    except socket.timeout:
                        pass

                    if message is not False:
                        objectannotations = message.unpack(ObjectAnnotations)
                        if objectannotations.objects:
                            for objectannotation in objectannotations.objects:
                                vertices = objectannotation.region.vertices
                                vertices = np.array([[vertices[0].x, vertices[0].y], 
                                                    [vertices[1].x, vertices[1].y], 
                                                    [vertices[2].x, vertices[2].y], 
                                                    [vertices[3].x, vertices[3].y]])   

                            if vertices is not None:    
                                frame = self.plot_boxes(vertices, frame)

                    cv2.imshow("img {}".format(camera_id), cv2.resize(frame, (960,640)))
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

              
if __name__ == '__main__':

    config_file = '../etc/config.json'

    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--camera', nargs='+',required=True)
    args = parser.parse_args()
    
    detection_manager = DetectionManager(config_file, args.camera)
    detection_manager.run()
