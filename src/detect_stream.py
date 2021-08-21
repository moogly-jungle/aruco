from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import field
import numpy as np
import json
import os
import zmq

ap = argparse.ArgumentParser()
ap.add_argument('-f', '--params', type=str,
    default='params.json',
    help="parameter file")
args = vars(ap.parse_args())

param_file = args['params']
if not os.path.exists(param_file):
    params = {
        'webcam_id' : 1,
        'dict' : cv2.aruco.DICT_5X5_50,
        'monitor' : False,
        'port' : 1978,
        'verbose' : False
    }

    with open(param_file, 'w') as f:
        json.dump(params,f)

with open(param_file, 'r') as f:
    params = json.load(f)

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("tcp://*:" + str(params['port']))

arucoDict = cv2.aruco.Dictionary_get(params['dict'])
arucoParams = cv2.aruco.DetectorParameters_create()
print('- starting video stream')
print('- tag position available on port %d' % params['port'])
if params['monitor']:
    print("  [press 'q' in the monitor window to quit]")
vs = VideoStream(src=params['webcam_id']).start()
time.sleep(2.0) # warmup of video stream

field = field.Field()

marker_detected = False

while True:
    try:
        poses = []
        t0 = time.time()
        frame = vs.read()
        # frame = imutils.resize(frame, width=1000)
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
                                                           arucoDict,
                                                           parameters=arucoParams)
        if len(corners) == 0:
            if params['verbose']:
                print('no marker')
        else:
            ids = ids.flatten()
            if params['verbose']:
                print('detected marker: ', end='')
                print(str(ids))
            if not marker_detected:
                print('- at least %d detected markers' % len(ids))
                marker_detected = True
            for (markerCorner, markerID) in zip(corners, ids):
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                field.set_id_gfx_corners(int(markerID),
                                         {
                                             'topRight' : (float(topRight[0]), float(topRight[1])),
                                             'bottomRight' : (float(bottomRight[0]), float(bottomRight[1])),
                                             'bottomLeft' : (float(bottomLeft[0]), float(bottomLeft[1])),
                                             'topLeft' : (float(topLeft[0]), float(topLeft[1]))
                                         })
            
                # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                # compute and draw the center (x, y)-coordinates of the
                # ArUco marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                
                gpos = np.array([cX,cY])
                pos = field.pos_of_gfx(gpos)
                pose = field.pose_of_tag(markerID)
                if pose is not None:
                    data = {}
                    data['id'] = int(markerID)
                    data['pose'] = pose
                    poses.append(data)
                # draw the ArUco marker ID on the frame
                cv2.putText(frame, str(markerID),
                            (topLeft[0], topLeft[1] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)
                if True or markerID in [0,5,20,25]:
                    pos_str = ''
                    if pos is not None:
                        pos_str = '(%0.2f, %0.2f)' % (pos[0],pos[1])
                    cv2.putText(frame, pos_str,
                                (topLeft[0], topLeft[1] + 40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)
        delta_t = time.time() - t0
        if delta_t > 0:
            freq = 1.0/delta_t
        else: freq = 0.0
        msg = { 'freq' : freq, 'data':poses }
        
        try: socket.send_json(msg, flags=zmq.NOBLOCK)
        except: pass

        if params['monitor']:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    except KeyboardInterrupt:
        break
cv2.destroyAllWindows()
vs.stop()
