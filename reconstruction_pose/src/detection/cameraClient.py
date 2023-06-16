import cv2
import numpy as np
from is_wire.core import Subscription
from is_msgs.image_pb2 import Image
from detection.streamChannel import StreamChannel


class CameraClient():

    def __init__(self,broker_uri,camera_id):
        self.camera_id = camera_id
        self.channel = StreamChannel(broker_uri)
        self.subscription = Subscription(channel=self.channel,name="Intelbras_Camera_{}".format(self.camera_id))
        self.subscription.subscribe(topic='CameraGateway.{}.Frame'.format(self.camera_id))

        self.window = 'Camera {}'.format(camera_id)


    def to_np(self,input_image):
        if isinstance(input_image, np.ndarray):
            output_image = input_image
        elif isinstance(input_image, Image):
            buffer = np.frombuffer(input_image.data, dtype=np.uint8)
            output_image = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
        else:
            output_image = np.array([], dtype=np.uint8)

        return output_image


    def consume_image(self):
        message = self.channel.consume_last()   
        if type(message) != bool: 
            frame = message.unpack(Image)
            frame = self.to_np(frame)  

        return frame, self.camera_id