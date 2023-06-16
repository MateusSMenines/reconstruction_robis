import numpy as np
import json
import socket
import math


# IS
from is_wire.core import Channel, Subscription, Logger, Message
from is_msgs.common_pb2 import Pose, Orientation, Position
from streamChannel import StreamChannel


class PoseReconstructor:
    def __init__(self, config_file):
        self.config = json.load(open(config_file, 'r'))
        self.broker_uri = self.config['broker_uri']
        self.detection_id = self.config['detection']['id']
        self.detection_type = self.config['detection']['detection_type']
        self.alpha = self.config['variables']['alpha']
        #self.norm_threshold = self.config['variables']['norm_theshrold']
        self.norm_threshold = 0.1
        self.channel = StreamChannel(self.broker_uri)
        self.subscription = Subscription(self.channel)
        self.subscription.subscribe(topic=f"reconstruction.{self.detection_id}.{self.detection_type}")
        
        self.values = None
        self.data = []
        self.pose_list = []
        self.list = []
        self.deg = 0.0
        self.WINDOW_SIZE = 5


    def exponential_smoothing(self, Y, S):
        self.data.append(Y)
        if len(self.data) > self.WINDOW_SIZE:
            self.data.pop(0)
        
        if len(self.data) <= self.WINDOW_SIZE:
            data = np.array(self.data)
            alpha = self.alpha
            mean = np.array([np.mean(data[:,0]),np.mean(data[:,1])])

            output = alpha * mean + (1 - alpha) * np.array(S)

        return output
    

    def process_pose(self, pose, pose_obj):
        x_recontruction = math.trunc(pose.position.x*100)/100
        y_recontruction = math.trunc(pose.position.y*100)/100

        self.pose_list.append([x_recontruction, y_recontruction])
        pose_ref = self.pose_list[0]
        pose_act = self.pose_list[-1]

        x = pose_act[0] - pose_ref[0]
        y = pose_act[1] - pose_ref[1]
        norm = np.linalg.norm([y,x])

        if norm > self.norm_threshold:
            vector = [y,x]
            if self.values is None:
                self.values = vector
            else:
                self.values = self.exponential_smoothing(vector, self.values)
                rads = math.atan2(self.values[0],self.values[1])
                #self.deg = math.degrees(rads)
                self.deg = rads

            self.pose_list = [self.pose_list[-1]]
        else:
            self.pose_list = [self.pose_list[0]]
        

        pose_obj.position.x = pose.position.x
        pose_obj.position.y = pose.position.y
        pose_obj.position.z = 0
        pose_obj.orientation.yaw = self.deg
        # pose = Position(x = x, y = y, z = 0) 
        # orientation = Orientation(yaw = self.deg)
        message = Message(content = pose_obj)
        self.channel.publish(message, topic = f"pose.1.Robis")

        log_detector.info(f"x:{pose_obj.position.x},  y{pose_obj.position.y},  Yaw:{self.deg}")  

    def run(self):
        pose_obj = Pose()
        while True:
            try:
                message = self.channel.consume()
                pose = message.unpack(Pose)
                self.process_pose(pose, pose_obj)

            except socket.timeout:
                pass


if __name__ == '__main__':

    log_detector = Logger(name="orientation")

    config_file = '../etc/config/config.json'
    reconstructor = PoseReconstructor(config_file)
    reconstructor.run()
