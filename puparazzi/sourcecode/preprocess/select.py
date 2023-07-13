import os
import glob
import shutil

'''
root
L—preprocess.py
L—typo.py
L—selectd_data  
    L—train
        L—images
            L—Bench
                L—Damaged
                L—Normal
            L—BenchBack
            L—Bollard
            L—BoundaryStone
            L—BrailleBlock
            L—Manhole
            L—ProtectionFence
            L—RoadSafetySign
            L—StreetLampPole
            L—StreetTreeCover
            L—Trench
        L—labels
            L— # 위와 동일
        L—selected_images
            L— # 위와 동일
        L—selected_labels
            L— # 위와 동일
    L—val
        L—images
            L— # 위와 동일
        L—labels
            L— # 위와 동일
        L—selected_images
            L— # 위와 동일
        L—selected_labels
            L— # 위와 동일
'''


CLASS_DIR=[
    "Bench/", "BenchBack/", "Bollard/", "BoundaryStone/", "BrailleBlock/","Manhole/", 
    "ProtectionFence/", "RoadSafetySign/", "StreetLampPole/", "StreetTreeCover/", "Trench/"
    ]


for sub_dir1 in ['train/','val/']:
    
    DATA_PATH='./selected_data/'+sub_dir1
    
    for class_dir in CLASS_DIR:       
        for sub_dir2 in ['Damaged/', 'Normal/']:

            IMAGE_PATH=DATA_PATH+'images/'+class_dir+sub_dir2
            LABEL_PATH=DATA_PATH+'labels/'+class_dir+sub_dir2

            DEST_IMAGE_PATH=DATA_PATH+'selected_images/'+class_dir+sub_dir2
            DEST_LABEL_PATH=DATA_PATH+'selected_labels/'+class_dir+sub_dir2
                      
            image_list=glob.glob(IMAGE_PATH+'*')
            label_list=glob.glob(LABEL_PATH+'*')
        
            name_list=[]
            for label_path in label_list:
                name_list.append(os.path.basename(label_path)[:-4])
            
            print(f'>>>[START] {sub_dir1}{class_dir}{sub_dir2} image : {len(image_list)} label : {len(label_list)}')
        
            for file_name in name_list:
                if os.path.exists(IMAGE_PATH+file_name+'.jpeg'):
                    shutil.copyfile(IMAGE_PATH+file_name+'.jpeg', DEST_IMAGE_PATH+file_name+'.jpeg')
                    shutil.copyfile(LABEL_PATH+file_name+'.txt', DEST_LABEL_PATH+file_name+'.txt')
                
            image_list=glob.glob(DEST_IMAGE_PATH+'*')
            label_list=glob.glob(DEST_LABEL_PATH+'*')
            print(f'>>>[END] {sub_dir1}{class_dir}{sub_dir2} image : {len(image_list)} label : {len(label_list)}')
            