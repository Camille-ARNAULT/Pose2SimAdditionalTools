#!/usr/bin/env python
# -*- coding: utf-8 -*-



###########################################################################
## PIPELINE MARKERLESS                                                   ##
###########################################################################


## INIT
import shutil
import os
from pathlib import Path
import time
import cv2
from rtmlib import BodyWithFeet, Wholebody, PoseTracker, draw_skeleton
import logging
from skelly_synchronize import skelly_synchronize as sync
from Pose2Sim import Pose2Sim
# import ffmpeg



## AUTHORSHIP INFORMATION
__author__ = "Camille ARNAULT"
__credits__ = ["Camille ARNAULT"]
__version__ = "0.1.0"
__maintainer__ = "Camille ARNAULT"
__email__ = "camille.arnault@univ-poitiers.fr"
__status__ = "Development"



def treatAll():
    
    #Création des dossiers de travail
    classification()
    #Calibration
    Pose2Sim.calibration()
    #Synchronisation des vidéos des essais
    synchronisation()
    #Vérification de la synchronisation
    synchronisationVerification()
    #Estimation de pose 
    Pose2Sim.PoseEstimation()
    #Association de personnes
    Pose2Sim.personAssociation()
    #Triangulation
    Pose2Sim.triangulation()
    #Filtrage
    Pose2Sim.filtering()
    
    
    

def classification(path=None) :

    """
    Input :
        * path : chemin où toutes les données de la session d'enregistrement on été stockées.
        
    Output :
        * nbcam : nombre de caméras détectées
        * nbtrials : nombre d'essais détectés
        
    ***
    
    Attention :
        /1\ Le programme est conçu pour fonctionner avec le setup de gopro du labo qui 
        disposent du GoPro labs i.e d'un nom de fichier associé au numéro de la 
        caméra et à l'heure et la date d'enregistrement. Pour le bon fonctionnement
        du code, ces caractéristiques doivent être conservées.
        
        /2\ Les expérimentations doivent toujours être faite dans ce même ordre : 
            - calibrations intrinsèques (peut avoir été faite avant)
            - calibrations extrinsèques 
            - acquisitions (xN)
            
        /3\ Mettez toutes vos vidéos dans votre dossier de travail
    """

    
    os.system("====================")
    print("File classification...")
    os.system("====================")  
    
    # 1 - Get working directory 
    
    if path==None :
        path=os.getcwd()
    else :
        path = path.replace('\\', '\\\\')
    
    # 2 - Find cam number and names
    
    filenames =[]
    for file in os.listdir(path):
        if file.endswith(".MP4"):
            filenames.append(file)
    nbfiles = len(filenames)
    camList = []
    for file in range(0,nbfiles) : 
        camList += [filenames[file][filenames[file].find("CAMERA"):filenames[file].find("CAMERA")+8]]
    camNames = list(set(camList))   
    nbcam = len(camNames)
    
    
    # 3 - Create calibration path
    
    # filenamesCalibInt = filenames[0:nbcam-1]
    # filenamesCalibExt = filenames[nbcam:2*nbcam-1] 
    calibFolderPath = os.path.join(path,"calibration")
    calibExtFolderPath = os.path.join(path,"calibration","extrinsics")
    calibIntFolderPath = os.path.join(path,"calibration","intrinsics")
    if not os.path.exists(calibFolderPath):os.mkdir(calibFolderPath)
    if not os.path.exists(calibExtFolderPath):os.mkdir(calibExtFolderPath)
    if not os.path.exists(calibIntFolderPath):os.mkdir(calibIntFolderPath)
    for n in range(1,nbcam+1) :
        if n<10:
            if not os.path.exists(os.path.join(calibExtFolderPath,"ext_cam0"+str(n))):os.mkdir(os.path.join(calibExtFolderPath,"ext_cam0"+str(n)))
            if not os.path.exists(os.path.join(calibIntFolderPath,"int_cam0"+str(n))):os.mkdir(os.path.join(calibIntFolderPath,"int_cam0"+str(n)))
        else :
            if not os.path.exists(os.path.join(calibExtFolderPath,"ext_cam"+str(n))):os.mkdir(os.path.join(calibExtFolderPath,"ext_cam"+str(n)))
            if not os.path.exists(os.path.join(calibIntFolderPath,"int_cam"+str(n))):os.mkdir(os.path.join(calibIntFolderPath,"int_cam"+str(n)))
            
    
    # 4 - Sort trials
    
    nbtrials = (nbfiles-nbcam*2)/nbcam
    if nbtrials%1 != 0 : print("ERROR : Number of video files not consistent with number of cameras.")
    elif nbtrials%1 == 0 :
        nbtrials = int(nbtrials)
        
        #Create trials folders
        for t in range(1,nbtrials+1):
            if not os.path.exists(os.path.join(path,"Trial_"+str(t))):os.mkdir(os.path.join(path,"Trial_"+str(t)))
            if not os.path.exists(os.path.join(path,"Trial_"+str(t),"video_raw")):os.mkdir(os.path.join(path,"Trial_"+str(t),"video_raw"))

        #Video classification
        try :
            for n in range(0,nbtrials+2) :
                if n == 0 :
                    for c in range(0,nbcam) :
                        if c<10 :
                            shutil.move(os.path.join(path,filenames[c]),os.path.join(path,"calibration","intrinsics","int_cam0"+str(c+1),filenames[c]))
                        else :
                            shutil.move(os.path.join(path,filenames[c]),os.path.join(path,"calibration","intrinsics","int_cam"+str(c+1),filenames[c]))
                                
                if n == 1 :
                    for c in range(0,nbcam) :
                        if c<10 :
                            shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"calibration","extrinsics","ext_cam0"+str(c+1),filenames[nbcam*(n)+c]))
                        else : 
                            shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"calibration","extrinsics","ext_cam"+str(c+1),filenames[nbcam*(n)+c]))
                            
                if n not in [0,1] :
                    for c in range(0,nbcam) :
                        # shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"Trial_"+str(n-1),"video_raw",filenames[nbcam*(n)+c]))
                        shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"Trial_"+str(n-1),"video_raw",filenames[nbcam*(n)+c][0:filenames[nbcam*(n)+c].find("CAMERA")+8]+".MP4"))
                        shutil.copyfile(os.path.join(path,'Config.toml'), os.path.join(path,"Trial_"+str(n-1),'Config.toml'))
        except :
            if n == 0 : logging.info("ERROR: unable to transfer intrinsics calibration files.")
            elif n == 1 : logging.info("ERROR: unable to transfer extrinsics calibration files.")
            elif n not in [0,1] : logging.info("ERROR: unable to transfer {filenames[nbcam*(n)+c]} file or copy config.toml file.")
                    
                
    logging.info("\n\n---------------------------------------------------------------------")
    logging.info("f'Dossier de travail : {path}")
    logging.info("f'Nombre de caméras trouvées : {nbcam}")
    logging.info("f'Nombre d'acquisitions classées : {nbtrials}")
    logging.info("\nClassement des enregistrements faits avec succès.")
    os.system("====================")
    

def synchronisation() :
    
    logging.info("====================")
    print("Videos Synchronization...")
    logging.info("====================")  
    
    #Get working directory
    path = os.getcwd()
    folders = os.listdir(path)
    
    #Get number of trials
    nbtrials=0
    print(folders)
    for i in range(0,len(folders)):
        if "Trial" in folders[i]: 
            print(folders[i])
            nbtrials += 1
        
            
            
    for trial in range(nbtrials) :
        
        #path config
        raw_video_folder_path = Path(os.path.join(path,"Trial_"+str(trial+1),"video_raw"))
        sync_video_folder_path = Path(os.path.join(path,"Trial_"+str(trial+1),"videos"))        
        
        if not os.path.exists(sync_video_folder_path): 
            logging.info("\n\n---------------------------------------------------------------------")
            logging.info("f'Acquisition en cours de traitement : ")
            print("Trial_",trial)
            logging.info("\n\n---------------------------------------------------------------------")
            os.mkdir(os.path.join(path,"Trial_"+str(trial+1),"videos"))
            sync.synchronize_videos_from_audio(raw_video_folder_path=raw_video_folder_path,
                                                synchronized_video_folder_path = sync_video_folder_path,
                                                video_handler="deffcode",
                                                create_debug_plots_bool=True)
            
        
    logging.info("\n\n---------------------------------------------------------------------")
    logging.info("Synchronisation des vidéos faites avec succès.")
    logging.info("---------------------------------------------------------------------")
    
        

def synchronisationVerification() :
    
    logging.info("====================")
    print("Synchronization verification...")
    logging.info("====================")  
    
    #Get working directory
    path = os.getcwd()
    folders = os.listdir(path)
    
    #Get number of trials
    nbtrials=0
    trialsName=[]
    for i in range(0,len(folders)):
        if "Trial" in folders[i]: 
            nbtrials += 1
            trialsName += [folders[i]]
        
            
            
    for trial in range(nbtrials) :
        
        #path config
        raw_video_folder_path = Path(os.path.join(path,trialsName[trial],"video_raw"))
        sync_video_folder_path = Path(os.path.join(path,trialsName[trial],"videos"))        
        
            
        #Récupération des noms des vidéos
        syncVideoName =[]
        for file in os.listdir(sync_video_folder_path):
            if file.endswith(".mp4"):
                syncVideoName.append(file)
        nbVideos = len(syncVideoName)
        
        #Calcul du dimensionnement des vidéos
        dimOverlay = 2
        while nbVideos/dimOverlay > dimOverlay : dimOverlay += 1
        
        #Assemblage de la ligne de commande
        mozaicMaker = "ffmpeg"
        #Nom des vidéos
        for vid in syncVideoName :
            mozaicMaker=mozaicMaker+" -i "+str(sync_video_folder_path)+"\\"+vid
        #Create overlay base
        mozaicMaker = mozaicMaker+' -filter_complex "nullsrc=size=1920x1080 [base];'
        
        #Specify output videos dimension
        for vid in range(0,nbVideos):
            mozaicMaker = mozaicMaker+"["+str(vid)+":v] setpts=PTS-STARTPTS, scale="+str(int(1920/dimOverlay))+"x"+str(int(1080/dimOverlay))+" [v"+str(vid)+"];"
        
        #Define vid position
        mozaicMaker = mozaicMaker+""
        xinc = 1920/dimOverlay
        yinc = 1080/dimOverlay
        vidInc=0
        
        for y in range(0,dimOverlay):
            ypos = yinc*y
            xpos = 0
            for x in range(0,dimOverlay):
                if y==0 and x==0 :
                    mozaicMaker = mozaicMaker+"[base][v"+str(int(vidInc))+"] overlay=shortest=1:x="+str(int(x*xinc))+":y="+str(int(ypos))+" "
                    vidInc += 1
                elif y==dimOverlay-1 and x ==dimOverlay-1 :
                    mozaicMaker = mozaicMaker+"[tmp"+str(int(vidInc))+"];[tmp"+str(int(vidInc))+"][v"+str(int(vidInc))+"] overlay=shortest=1:x="+str(int(x*xinc))+":y="+str(int(ypos))+'" '
                    vidInc += 1
                else :
                    mozaicMaker = mozaicMaker+"[tmp"+str(int(vidInc))+"];[tmp"+str(int(vidInc))+"][v"+str(int(vidInc))+"] overlay=shortest=1:x="+str(int(x*xinc))+":y="+str(int(ypos))
                    vidInc += 1
                    
        mozaicMaker = mozaicMaker+"-c:v libx264 "+str(sync_video_folder_path)+"\\"+"SyncVideos.mp4"
        os.system(mozaicMaker)
        
        
    logging.info("\n\n---------------------------------------------------------------------")
    logging.info("Synchronisation des vidéos faites avec succès.")
    logging.info("---------------------------------------------------------------------")
    

    
    
    
    