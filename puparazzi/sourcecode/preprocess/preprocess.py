import os
import json
import glob
import cv2
from PIL import Image

'''
root
L—preprocess.py
L—dataset # 라벨 전처리 위한 폴더
    L—라벨_처리전
        L—train
            L—labels
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
        L—val
            L—labels
                L— # 위와 동일
    L—라벨_처리후
        L—train
            L—labels1
                L— # 위와 동일 (1번째 object detection을 위한 라벨)
            L—labels2
                L— # 위와 동일 (2번째 damage을 위한 라벨)
        L—val
            L— # 위와 동일
'''

CLASS_DICT={
    "Bench":0,
    "BenchBack":1,
    "Bollard":2,
    "BoundaryStone":3,
    "BrailleBlock":4,
    "Manhole":5,
    "ProtectionFence":6,
    "RoadSafetySign":7,
    "StreetLampPole":8,
    "StreetTreeCover":9,
    "Trench":10,
    }


## 이미지 박싱 그리기
## 사진 하나씩, 라벨도 하나씩(label1, label2 같이 보려면 수정 필요)
def drawRectangle(image_path, label_path):
    image=cv2.imread(image_path)
    
    height,width,c=image.shape
    
    boxes=[]
    
    with open(label_path, "r") as f:
        lines=f.readlines()
    f.close()
    
    for line in lines:
        boxes.append(list(map(float, line.split())))
    
    imageRectangle=image.copy()
    
    for i in range(len(lines)):
        cx=width*boxes[i][1]
        cy=height*boxes[i][2]
        w=width*boxes[i][3]
        h=width*boxes[i][4]
        
        sx=int(cx-w/2)
        sy=int(cy-h/2)
        ex=int(cx+w/2)
        ey=int(cy+h/2)

        imageRectangle=cv2.rectangle(imageRectangle,(sx,sy), (ex, ey), (255,0,0), thickness=2)
    
    # cv2.imshow('result', imageRectangle)
    # cv2.waitKey(0)
    # cv2.destroyAllWindow() 
    
    cv2.imwrite(f'./draw/{os.path.basename(image_path)}.jpeg',imageRectangle)
    return


## 이미지 리사이즈
## 이미지 폴더 안 모든 사진 한번에
def resizeImage(image_dir, destination_dir):
    image_list = glob.glob(image_dir+'*')
    
    for image in image_list:
        file_name=os.path.basename(image)[:-5]+'.jpeg'
        im = Image.open(image)
        im = im.resize((416, 416))
        im = im.convert('RGB')
        im.save(destination_dir+file_name,'JPEG')
    
    return


## annotation 작업 
def annotation(json_path, update_path, target_dir):
    json_list=glob.glob(json_path+'*')
    
    for json_file in json_list:
        # json 파일 읽기
        with open(json_file, 'r', encoding='UTF8') as f:
            json_data=json.load(f)
        f.close()
        
        # txt 파일명 추출
        file_name=os.path.basename(json_file)[:-5]+'.txt'
        
        # 전체 사진 width, height 추출
        width = json_data['images'][0]['width']
        height = json_data['images'][0]['height']

        # annotation 개수
        annotations_len=len(json_data['annotations'])
        
        for i in range(annotations_len):
            # 객체에 대한 annotation 추출
            if json_data['annotations'][i]['category_id'] == 1 :
                attributes=json_data['annotations'][i]['attributes']
                class_name=attributes['class']
                
                try:
                    class_label=CLASS_DICT[class_name]
                except KeyError:
                    continue
                
                sx,sy,w,h= json_data['annotations'][i]['bbox']
                cx=sx+w/2
                cy=sy+h/2
                
                if sx+w>width or sy+h>height:
                    with open('./error.txt', 'a+') as error_file:
                        error_file.write(f'>>>[label1] : {file_name}\n')
                    error_file.close()
                    continue
                    
                with open(update_path+'labels1/'+target_dir+file_name, 'a+') as f:
                    f.write(f'{class_label} {round(cx/width,5)} {round(cy/height,5)} {round(w/width,5)} {round(h/height,5)}\n')
                f.close()
                
            # 객체 손상에 대한 annotation 추출
            elif json_data['annotations'][i]['category_id'] == 2 :
                ## parent_id 없는 경우 있음
                try:
                    pid=json_data['annotations'][i]['parent_id']
                except KeyError:
                    pid=-1       
                
                if pid!=-1:
                    for j in range(annotations_len):
                        if json_data['annotations'][j]['id']==pid:
                            target_object=json_data['annotations'][j]['attributes']['class']
                            break
                else:
                    target_object=target_dir.split('/')[0]
                    
                if target_object==target_dir.split('/')[0]:
                    sx,sy,w,h= json_data['annotations'][i]['bbox']
                    cx=sx+w/2
                    cy=sy+h/2
                    
                    if sx+w>width or sy+h>height:
                        with open('./error.txt', 'a+') as error_file:
                            error_file.write(f'>>>[label2] : {file_name}\n')
                        error_file.close()
                        continue
                        
                    with open(update_path+'labels2/'+target_dir+file_name, 'a+') as f:
                        f.write(f'0 {round(cx/width,5)} {round(cy/height,5)} {round(w/width,5)} {round(h/height,5)}\n')
                    f.close()
                break
            
    return

# #############################################
# PATH - Training / Validation 구분해서 작업하기
# ORIGIN_PATH='./dataset/라벨_처리전/train/labels/'
# UPDATE_PATH='./dataset/라벨_처리후/train/'

# ORIGIN_PATH='./dataset/라벨_처리전/val/labels/'
# UPDATE_PATH='./dataset/라벨_처리후/val/'
# #############################################


ORIGIN_PATH=''
UPDATE_PATH=''

if ORIGIN_PATH!='' and UPDATE_PATH!='':
    dir_list=os.listdir(ORIGIN_PATH)

    for main_dir in ["Bench", "BenchBack", "Bollard", "BoundaryStone", "BrailleBlock", "Manhole", "ProtectionFence", "RoadSafetySign", "StreetLampPole", "StreetTreeCover","Trench"]:
        # main_dir - ex) Bench 총 11개 분류
        # sub_dir - ex) Normal or Damaged 
        if main_dir not in CLASS_DICT:
            continue
        
        for sub_dir in os.listdir(ORIGIN_PATH+main_dir):
            
            target_dir=main_dir+'/'+sub_dir+'/'
            
            json_path=ORIGIN_PATH+target_dir
    
            print(f'>>> [START] {json_path}  +   {UPDATE_PATH}[labels1/2]{target_dir}')
            annotation(json_path, UPDATE_PATH, target_dir)
            print('>>> [END]')