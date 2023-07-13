import os
import shutil
import yaml
import glob
import cv2
import torch


CLASS_DICT = {
    0 : "Bench",
    1 : "BenchBack",
    2 : "Bollard",
    3 : "BoundaryStone",
    4 : "BrailleBlock",
    5 : "Manhole",
    6 : "ProtectionFence",
    7 : "RoadSafetySign",
    8 : "StreetLampPole",
    9 : "StreetTreeCover",
    10 : "Trench",
}

#BGR
COLOR_DICT={
    0 : (0,0,0),
    1 : (0,255,255),
    2 : (255,0,0),
    3 : (255,0,255),
    4 : (0,102,0),
    5 : (0,255,0),
    6 : (0,204,255),
    7 : (255,255,0),
    8 : (0,0,255),
    9 : (255,102,153),
    10 : (255,255,255),
}


def detect(report_path) :
    YOLO_PATH = 'C://Users//User//Desktop//1227//YOLOv5' # YOLO_PATH 변경 필수!!
    WEIGHT_PATH = os.path.join(YOLO_PATH, 'weights')    # weights 폴더에 학습 모델 12개 저장!!
    FACILITY_PATH = os.path.join(WEIGHT_PATH, 'Facility.pt')
    ROOT_PATH = os.path.join(*(report_path.split('/')[:-2]))
    
    ORIGIN_PATH = os.path.join(ROOT_PATH, 'origin')
    DETECT_PATH = os.path.join(ROOT_PATH, 'detect')
    VALID_PATH = os.path.join(ROOT_PATH, 'validate')

    # 이미 존재하면 detect, valid 폴더 다 지우고 새로만들기
    if os.path.exists(DETECT_PATH):
        shutil.rmtree(DETECT_PATH)
    os.mkdir(DETECT_PATH)
    
    if os.path.exists(VALID_PATH):
        shutil.rmtree(VALID_PATH)
    os.mkdir(VALID_PATH)
        
    image_name = os.path.splitext(report_path)[0].split('/')[-1]
    image_ext =os.path.splitext(report_path)[1]

    # 1. 시설물 탐지 모델 이용하여 탐지
    model1 = torch.hub.load(os.path.join(YOLO_PATH, 'yolov5'), 'custom', path = FACILITY_PATH, source = 'local')
    result1 = model1(report_path) # size=416
    
    detection_list = result1.xyxy[0].tolist() # xmin | ymin | xmax | ymax | confidence | class(float)
    num = len(detection_list)

    # 2. Detection 1단계
    image = cv2.imread(report_path)
    height, width, c = image.shape
    imageRectangle = image.copy()

    yaml_data1 = {'name' : []}

    for idx in range(num) : 
        sx = int(detection_list[idx][0])
        sy = int(detection_list[idx][1])
        ex = int(detection_list[idx][2])
        ey = int(detection_list[idx][3])
        # conf = detection_list[idx][4]
        cidx = int(detection_list[idx][5])
        cname = CLASS_DICT[cidx]

        dx = int(width * 0.05)
        dy = int(height * 0.05)
        
        sx = 0 if sx-dx < 0 else sx-dx
        sy = 0 if sy-dy < 0 else sy-dy
        ex = width if ex+dx > width else ex+dx
        ey = height if ey+dy > height else ey+dy
        
        # 1단계 - 시설물 bbox들 원본 사진에 그리기
        imageRectangle = cv2.rectangle(imageRectangle,(sx,sy), (ex, ey), COLOR_DICT[cidx], thickness=5) 

        if cname not in yaml_data1['name'] :
            yaml_data1['name'].append(cname)
            yaml_data1[cname] = {'is_ok' : True, 'count' : 0, 'pos' : [] }
        
        yaml_data1[cname]['count'] += 1
        yaml_data1[cname]['pos'].append({'x_min' : sx, 'y_min' : sy, 'x_max' : ex, 'y_max' : ey})

        # 2단계 위한 미리 저장
        croppedImage = image[sy:ey, sx:ex]
        cnt = yaml_data1[cname]['count']
        
        if not os.path.exists(os.path.join(VALID_PATH, cname)) :
            os.mkdir(os.path.join(VALID_PATH, cname))
            
        croppedImage_path = os.path.join(VALID_PATH, cname, f'{image_name}_{cnt}{image_ext}')
        
        cv2.imwrite(croppedImage_path, croppedImage)
    
    cv2.imwrite(os.path.join(DETECT_PATH, f'{image_name}{image_ext}'), imageRectangle)
    
    # 2단계 - 각 시설물 파손 부위 bbox들 crop된 사진에 그리기
    for subdir in os.listdir(VALID_PATH): # subdir == 시설물 이름
        cimage_list  =glob.glob(os.path.join(VALID_PATH, subdir,'*'))

        model2 = torch.hub.load(os.path.join(YOLO_PATH, 'yolov5'), 'custom', path = os.path.join(WEIGHT_PATH, f'{subdir}.pt'), source = 'local')
        yaml_data2 = {'file_name':[]}

        for cimage_path in cimage_list :
            file_name = os.path.basename(cimage_path)
            yaml_data2['file_name'].append(file_name)
            yaml_data2[file_name] = {'is_ok' : True, 'count' : 0, 'pos' : []}
            
            result2 = model2(cimage_path)
            damage_list = result2.xyxy[0].tolist() 
            num = len(damage_list)
    
            if num == 0:
                continue
            
            yaml_data1[subdir]['is_ok'] = False
            yaml_data2[file_name]['is_ok'] = False
            yaml_data2[file_name]['count'] = num
            
            cimage = cv2.imread(cimage_path)
            cimageRectangle = cimage.copy()
            cheight, cwidth, cc = cimage.shape
            
            ###
            area=[[0 for _ in range(cwidth)] for _ in range(cheight)]
            ###
            
            for idx in range(num) :
                sx = int(damage_list[idx][0])
                sy = int(damage_list[idx][1])
                ex = int(damage_list[idx][2])
                ey = int(damage_list[idx][3])
                
                ###
                for i in range(sy, ey):
                    for j in range(sx, ex):
                        area[i][j]=1
                ###
                    
                yaml_data2[file_name]['pos'].append({'x_min' : sx, 'y_min' : sy, 'x_max' : ex, 'y_max' : ey})
                cimageRectangle = cv2.rectangle(cimageRectangle,(sx,sy), (ex, ey), (0,0,255), thickness=3) 
            
            ###
            darea=0
            for i in range(cheight):
                darea+=sum(area[i])
            
            yaml_data2[file_name]['percentage']=round(100*darea/(cheight*cwidth),2)
            ###
            
            cv2.imwrite(cimage_path, cimageRectangle)
        
        with open(os.path.join(VALID_PATH, subdir, 'info.yaml'), 'w') as f:
            yaml.dump(yaml_data2, f)
        f.close()
            
    with open(os.path.join(DETECT_PATH, 'info.yaml'), 'w') as f:
        yaml.dump(yaml_data1, f)
    f.close()
    
    return

## Test Code ## 
post_id = 2
REPORT_PATH = f'./report/{post_id}/origin/tmp.jpeg'

detect(REPORT_PATH)