import time
import cv2
import os 
from rtmlib import BodyWithFeet, Wholebody, PoseTracker, draw_skeleton



"""
Input :
    * path : chemin des vidéos à analyser.
    * Model : modèle squelettique à appliquer : 
    * nbcam :
    * nbtrials :
Output :
    *  
***

Attention :
    /1\
"""

#%%  input

model = "BodyWithFeet"
visualVerification = True
path = "C:\\Users\\carnau22\\Documents\\MARKERLESS\\Pipeline"
nbcam = 1
nbtrials = 1

#%% init

cams = range(0,nbcam)
trials = range(0,nbtrials)
device = 'cpu'
backend = 'onnxruntime'  # opencv, onnxruntime, openvino



for cam, trial in cams, trials : 
    
    if nbtrials == 1 :
        cap = cv2.VideoCapture(os.path.join(path,"video_sync"))
    else :
        cap = cv2.VideoCapture(os.path.join(path,"Participant","Trial_"+str(trial),"video_sync","Trial_"+str(trial)))
    
    
    if model == "BodyWithFeet" :
        
        openpose_skeleton = False  # True for openpose-style, False for mmpose-style
        body_feet_tracker = PoseTracker(
            BodyWithFeet,
            det_frequency=7,
            to_openpose=openpose_skeleton,
            mode='performance',  # balanced, performance, lightweight
            backend=backend,
            device=device)
        frame_idx = 0
        while cap.isOpened():
            success, frame = cap.read()
            frame_idx += 1
        
            if not success:
                break
            s = time.time()
            keypoints, scores = body_feet_tracker(frame)
            det_time = time.time() - s
            print('det: ', det_time)
        
            if visualVerification == True :
                img_show = frame.copy()
                img_show = draw_skeleton(img_show,
                                         keypoints,
                                         scores,
                                         openpose_skeleton=openpose_skeleton,
                                         kpt_thr=0.3,
                                         line_width=3)
            
                img_show = cv2.resize(img_show, (960, 640))
                cv2.imshow('Body and Feet Pose Estimation', img_show)
                cv2.waitKey(1)
    
    elif model == "Wholebody" :
    
        device = 'cpu'
        backend = 'onnxruntime'  # opencv, onnxruntime, openvino
        
        
        
        openpose_skeleton = False  # True for openpose-style, False for mmpose-style
        
        wholebody=PoseTracker(
            Wholebody,
            det_frequency=7,
            to_openpose=openpose_skeleton,
            mode='performance',  # balanced, performance, lightweight
            backend=backend,
            device=device)
        
        frame_idx = 0
        
        while cap.isOpened():
            success, frame = cap.read()
            frame_idx += 1
        
            if not success:
                break
            s = time.time()
            keypoints, scores = wholebody(frame)
            det_time = time.time() - s
            print('det: ', det_time)
        
            img_show = frame.copy()
        
            # if you want to use black background instead of original image,
            # img_show = np.zeros(img_show.shape, dtype=np.uint8)
            # print(scores)
            img_show = draw_skeleton(img_show,
                                     keypoints,
                                     scores,
                                     openpose_skeleton=openpose_skeleton,
                                     kpt_thr=4)
        
            img_show = cv2.resize(img_show, (960, 540))
            cv2.imshow('img', img_show)
            cv2.waitKey(10)
    
        
        
