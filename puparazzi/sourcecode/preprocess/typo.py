'''
[ 22/12/07 ]
원본 json 데이터에서 
기타시설물 - ConstructionCover 中 195개가 typo가 있다.
그래서 193개는 코드를 통해 수정하고 
나머지 2개는 기타시설물이 아닌 다른 시설물 폴더에 있어
이건 직접 수정하기로... 
'''

import os
import json
import glob

DATA_PATH='./data/'
PATH_LIST=['라벨_처리전/Training/','라벨_처리전/Validation/']

cnt=0

for dir in PATH_LIST:
    path=DATA_PATH+dir+'기타시설물/'

    # target_dir = 정상 or 수리 or 교체폐기 directory
    for target_dir in os.listdir(path):
        json_path=path+target_dir
        print('>>>>> Where am I? : ' + json_path)
        json_list=glob.glob(json_path+'/*')

        for json_file in json_list:
            with open(json_file, 'r', encoding='UTF-8') as f:
                json_data=json.load(f)
            f.close()
            
            annotations_len=len(json_data['annotations'])

            for i in range(annotations_len):
                if json_data['annotations'][i]['category_id'] == 1 :
                    attributes=json_data['annotations'][i]['attributes']
                    class_name=attributes['class']

                    if class_name=='ConsturctionCover':
                        json_data['annotations'][i]['attributes']['class']='ConstructionCover'
                        cnt+=1
            with open(json_file, 'w', encoding='UTF-8') as f:
                json.dump(json_data, f, ensure_ascii=False)
            f.close()     
        print(f'>>>>>>>>>> Cumsum : {cnt}')
print('>>>>> [END]')
