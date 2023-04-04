import cv2
from detection.detect import RobisDetection
from PIL import Image as img
import argparse


class Client():

    def __init__(self, broker_uri, camera_ids):
        self.camera_ids = camera_ids
        self.robis_detection = RobisDetection(0.75)
        self.cameras = self.robis_detection.set_cameras(broker_uri,self.camera_ids)
        

    def plot_boxes(self, list_robis, frame):
        print(list_robis)
        bgr = (0,255,0)
        for robis in list_robis:
            print(robis[2], robis[3])
            cv2.rectangle(frame, (robis[2], robis[3]), (robis[4], robis[5]), bgr, 1)
            cv2.putText(frame, robis[1], (robis[2], robis[3]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, bgr, 1)
            cv2.putText(frame, "{},{}". format(robis[2],robis[3]), (robis[2], robis[3]-5), cv2.FONT_HERSHEY_PLAIN, 0.8, bgr, 1)
            cv2.putText(frame, "{},{}". format(robis[2],robis[5]), (robis[2], robis[5]+10), cv2.FONT_HERSHEY_PLAIN, 0.8, bgr, 1)
            cv2.putText(frame, "{},{}". format(robis[4],robis[3]), (robis[4], robis[3]-5), cv2.FONT_HERSHEY_PLAIN, 0.8, bgr, 1)
            cv2.putText(frame, "{},{}". format(robis[4],robis[5]), (robis[4], robis[5]+10), cv2.FONT_HERSHEY_PLAIN, 0.8, bgr, 1)

        return frame


    def run(self):

        while True:

            for camera in self.cameras:

                try:
                    frame, camera_id = camera.consume_image() 
                except:
                    pass

                color_coverted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image=img.fromarray(color_coverted)
                results = self.robis_detection.score_frame(pil_image)
                list_robis = self.robis_detection.detect_boxes(results, frame, camera_id)
                frame = self.plot_boxes(list_robis, frame)
                cv2.imshow("img {}".format(camera_id), cv2.resize(frame, (960,640)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == '__main__':

    broker_uri = "amqp://10.10.0.68:30000"

    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--camera', nargs='+',required=True)
    args = parser.parse_args()

    client = Client(broker_uri, args.camera)
    client.run()
