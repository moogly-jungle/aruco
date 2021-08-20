# Aruco for holobot detection



Installation needs python3 and opencv. To install opencv:
```
sudo apt-get install python3-opencv
```
Then, all python packages requirements are listed in requirements.txt
Tested on Ubuntu 18.04 and Raspbian

Files:

* detect_stream.py : this is the server (zmq push) of aruco marker
poses. It must be launched independently to detect the aruco
markers. The parameters (e.g. webcam id, aruco dictionary id (default
is DICT_5X5_50), etc) of the servers are in params.json (created with
default if do not exists).  Launch it without arguments.

* field.py is internal material to compute the poses (i.e. position
  and orientation)

* client.py is the client to be used to get the poses of aruco markers:
  * Use init() and close() to start and stop the client
  * then use:
    * get_poses() gives the dictionary of all the pose associated to id of markers
    * get_pose(id) gives the pose of a particular makers
    * get_frequency() gives the frequency of video streaming
    (detect_stream.py must be launched)

Note:

* the camera is supposed to be immobile

* aruco of ids 0, 5, 25, and 20 define the frame to compute
  poses. They are supposed to be immobile, and visible. They must be
  disposed as a rectangle whose dimension are given in field.py

* a pose is a dictionary of form:
  ```
  {
    'pos' : <pair of 2D coordinates relative to the frame>,
    'orient' : orientation in degree
  }
  ```
