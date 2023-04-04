import numpy as np
import json
import socket
import math


# IS
from is_wire.core import Channel, Subscription, Logger
from is_msgs.common_pb2 import Pose
from streamChannel import StreamChannel


class PoseReconstructor:
    def __init__(self, config_file):
        self.config = json.load(open(config_file, 'r'))
        self.broker_uri = self.config['broker_uri']
        self.detection_id = self.config['detection']['id']
        self.detection_type = self.config['detection']['detection_type']
        self.alpha = self.config['variables']['alpha']
        self.norm_threshold = self.config['variables']['norm_theshrold']
        self.channel = StreamChannel(self.broker_uri)
        self.subscription = Subscription(self.channel)
        self.subscription.subscribe(topic=f"reconstruction.{self.detection_id}.{self.detection_type}")
        self.values = None
        self.pose_list = []
        self.value_list = []
        self.window_size = 3
        self.values_array = np.zeros((1,2))
        self.deg = "Not found"


    def exponential_smoothing(self, x, y):

        alpha = self.alpha
        output = alpha * x + (1 - alpha) * y

        return output


    def process_pose(self, pose):
        x_recontruction = math.trunc(pose.position.x*100)/100
        y_recontruction = math.trunc(pose.position.y*100)/100

        self.pose_list.append([x_recontruction, y_recontruction])
        pose_ref = self.pose_list[0]
        pose_act = self.pose_list[-1]

        x = pose_act[0] - pose_ref[0]
        y = pose_act[1] - pose_ref[1]
        norm = np.linalg.norm([y,x])

        if norm > self.norm_threshold:
            vector = np.array([y,x])
            if self.values is None:
                self.values = vector
            else:
                self.values = self.exponential_smoothing(vector, self.values)
                rads = math.atan2(self.values[0],self.values[1])
                self.deg = math.degrees(rads)

            self.pose_list = [self.pose_list[-1]]
        else:
            self.pose_list = [self.pose_list[0]]
        
        log_detector.info(f"Angle reconstruction:{self.deg}")  


    def run(self):
        while True:
            try:
                message = self.channel.consume()
                pose = message.unpack(Pose)
                self.process_pose(pose)

            except socket.timeout:
                pass


if __name__ == '__main__':

    log_detector = Logger(name="orientation")

    config_file = 'config.json'
    reconstructor = PoseReconstructor(config_file)
    reconstructor.run()
