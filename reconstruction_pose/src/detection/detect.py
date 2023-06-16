import torch
from detection.cameraClient import CameraClient


class RobisDetection():
    
    def __init__(self):
        self.model = torch.hub.load('../etc/yolov5/', 'custom', path= "../etc/weight/weight.pt", source='local')
        self.classes = self.model.names
        self.THRESHOLD = 0.75
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:",self.device)


    def score_frame(self, frame):
        self.model.to(self.device)
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        

        return labels, cord


    def class_to_label(self, x):
        return self.classes[int(x)]

    
    def set_cameras(self, broker_uri,camera_ids):  
        cameras = []
        for camera_id in camera_ids:
            cameras.append(CameraClient(broker_uri,camera_id))

        return cameras


    def detect_boxes(self, results, frame, camera_id):
        labels, cord = results
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        list_cord = []
        for i in range(len(labels)):
            row = cord[i]
            if row[4] >= self.THRESHOLD:
                list_label = [camera_id, self.class_to_label(labels[i]) + f" {i}", int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)]
                list_cord.append(list_label) 
            else:
                list_cord = [] 
        
        return list_cord


