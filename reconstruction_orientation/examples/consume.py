import numpy as np
import json
import socket

# IS
from is_wire.core import Channel, Subscription
from is_msgs.common_pb2 import Pose, Orientation

if __name__ == '__main__':

    config_file = '../etc/config/config.json'
    config = json.load(open(config_file, 'r'))
    broker_uri = config['broker_uri']
    
    channel = Channel(broker_uri)
    subscription = Subscription(channel)
    subscription.subscribe(topic=f"Robis.reconstruction.orientation")
    while True:
        try:
            message = channel.consume()
            orientatio = message.unpack(Orientation)
            yaw_rad_recontruction = orientatio.yaw    
            print(f'yaw = {yaw_rad_recontruction} deg')

        except socket.timeout:
            pass
