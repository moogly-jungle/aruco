import time
import zmq
import random
import threading
import copy

# parameters:
ip = '127.0.0.1'
port = 1978
verbose = False

# global variables:
poses = {}
stop = False
client_thread = None
lock = threading.Lock()
freq = 0.0

# start the client
def init():
    global client_thread
    client_thread = threading.Thread(target=pose_client) 
    client_thread.start()

# get all the poses
def get_poses():
    lock.acquire()
    cpy = copy.deepcopy(poses)
    lock.release()
    return cpy

# get one particular pose (can be None)
def get_pose(id):
    if id in poses:
        lock.acquire()
        cpy = copy.deepcopy(poses[id])
        lock.release()
        return cpy
    return None

# get the frequency of the streaming
def get_frequency():
    lock.acquire()
    f = freq
    lock.release()
    return f

# close the client
def close():
    global stop, client_thread
    if client_thread is not None:
        stop = True
        client_thread.join()
        client_thread = None
        if verbose: print('- pose client stopped')

###############################################################################

def pose_client():
    global poses, freq
    data_received = False
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect('tcp://' + ip + ':' + str(port))
    while not stop:
        msg = consumer_receiver.recv_json()
        if len(msg['data']) > 0:
            if not data_received:
                if verbose: print('- receiving data, freq : %0.2fHz' % msg['freq'])
                data_received = True
        lock.acquire()
        freq = msg['freq']
        for d in msg['data']:
            poses[d['id']] = d['pose']
        lock.release()


if __name__ == "__main__":
    init()
    for i in range(5):
        print('frequency : %0.2fHz' % get_frequency())
        for k in get_poses():
            print('%d -> %s' % (k, str(get_pose(k))))
        time.sleep(1)
    close()
    
