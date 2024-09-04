import shutil, os
import logging, logging.handlers

def classification(path) :

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
    #path = "C:\\Users\\carnau22\\Documents\\MARKERLESS\\Pipeline"

    
    # CREATION DES DOSSIERS
    
    #Récupération des noms et du nombre de caméras
    filenames = os.listdir(path)
    nbfiles = len(filenames)
    camList = []
    for file in range(0,nbfiles) : camList += [filenames[file][filenames[file].find("CAMERA"):filenames[file].find("CAMERA")+8]]
    camNames = list(set(camList))   
    nbcam = len(camNames)
    
    
    #calib
    filenamesCalibInt = filenames[0:nbcam-1]
    filenamesCalibExt = filenames[nbcam:2*nbcam-1] 
    os.mkdir(os.path.join(path,"calibration"))
    os.mkdir(os.path.join(path,"calibration","extrinsics"))
    os.mkdir(os.path.join(path,"calibration","intrinsics"))
    for n in range(1,nbcam+1) :
        os.mkdir(os.path.join(path,"calibration","extrinsics","ext_cam"+str(n)))
        os.mkdir(os.path.join(path,"calibration","intrinsics","int_cam"+str(n)))
    
    #trials
    existingfolders = [name for name in os.listdir(path) if os.path.isdir(name)]
    trialnum = 1
    nbtrials = (nbfiles-nbcam*2)/nbcam
    #Si pas le bon nombre de vidéo
    if nbtrials%1 != 0 : print("Erreur : Nombre de fichiers vidéos non cohérent avec le nombre de caméras.")
    #Si nombre de vidéos cohérent
    if nbtrials%1 == 0 :
        nbtrials = int(nbtrials)
        #Si un seul trial
        if nbtrials == 1:
            for t in range(1,nbtrials+1):
                os.mkdir(os.path.join(path,"pose"))
                os.mkdir(os.path.join(path,"video"))
                for n in range(1,nbcam+1) :  
                    os.mkdir(os.path.join(path,"pose","cam"+str(n)+"_json")) 
        #Si plusieurs trials           
        if nbtrials != 1:
            os.mkdir(os.path.join(path,"Participant"))
            for t in range(1,nbtrials+1):
                os.mkdir(os.path.join(path,"Participant","Trial_"+str(t)))
                os.mkdir(os.path.join(path,"Participant","Trial_"+str(t),"pose"))
                os.mkdir(os.path.join(path,"Participant","Trial_"+str(t),"video"))
                for n in range(1,nbcam+1) :
                    os.mkdir(os.path.join(path,"Participant","Trial_"+str(t),"pose","cam"+str(n)+"_json"))
            
    
    # CLASSIFICATION DES FICHIERS
    
    for n in range(0,nbtrials+2) :
        if n == 0 :
            for c in range(0,nbcam) :
                shutil.move(os.path.join(path,filenames[c]),os.path.join(path,"calibration","intrinsics","int_cam"+str(c+1),filenames[c]))
        if n == 1 :
            for c in range(0,nbcam) :
                shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"calibration","extrinsics","ext_cam"+str(c+1),filenames[nbcam*(n)+c]))
        if n not in [0,1] :
            for c in range(0,nbcam) :
                shutil.move(os.path.join(path,filenames[nbcam*(n)+c]),os.path.join(path,"Participant","Trial_"+str(n-1),"video",filenames[nbcam*(n)+c]))
            
    logging.info("\n\n---------------------------------------------------------------------")
    logging.info("Classement des enregistrements faits avec succès.")
    logging.info("Etape suivante suggérées : définir les paramètres de l'étude via la fonction configuration()")
    logging.info("---------------------------------------------------------------------")
    
    return nbcam, nbtrials            
            
    
