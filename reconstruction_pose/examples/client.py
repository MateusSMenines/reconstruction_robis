
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