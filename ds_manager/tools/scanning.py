import os

from ds_manager.datasets.dataset import Dataset
from ds_manager.datasets.pascal import Pascal
from ds_manager.datasets.coco import Coco
from ds_manager.datasets.cityscapes import Cityscapes
from ds_manager.datasets.yolo import Yolo

from ds_manager.objects.annotation import Annotation
from ds_manager.objects.image import Image

def scan(dataset: Dataset):
        root = []
        data = dataset.data
        img_ext, img_path, mask = dataset.img_ext_func()
        if len(img_path)>1:
            if img_ext == 'png':
                print('IMAGE EXTENSION == PNG, THERE CAN BE POLY MASKS, PLEASE CHOOSE IMAGE FOLDERS')
                [print(f'{item[0]} - {item[1]}') for item in enumerate(img_path)]
                inp = input('INSERT FOLDER NUMBERS w/ space [example: 1 4 5 11] or insert path to folder with images \n')
                inp = inp.strip()
                inp = inp.split(' ')
                img_new = []
                for num in inp:
                    try:
                        img_new.append(img_path[int(num)])
                    except ValueError:
                        img_new = inp
                img_path = img_new
        if not img_ext:
            raise NotImplementedError()
        random_img = dataset.findby_ext(extension=img_ext,
                                     datapath=img_path)
        img = Image(random_img[1])
        random_ann = dataset.findby_name(os.path.splitext(img.name)[0],
                                                datapath=dataset.ann_path,
                                                avoid_path=dataset.img_path,
                                                avoid_ext = ('jpg','png','jpeg'))
        if random_ann == None:
            dataset = Coco(image_ext=img_ext,
                              img_path=img_path,
                              data = data,
                              mask = mask)
        elif random_ann[2].endswith(".txt"):
            dataset = Yolo(image_ext=img_ext,
                              img_path=img_path,
                              data = data,
                              mask = mask)
        elif random_ann[2].endswith(".xml" or ".mat"):
            dataset = Pascal(image_ext=img_ext,
                              img_path=img_path,
                              data = data,
                              mask = mask)
        elif random_ann[2].endswith(".json"):
            dataset = Cityscapes(image_ext=img_ext,
                              img_path=img_path,
                              data = data,
                              mask = mask)
        i = 0
        for folder in dataset.img_path:
            if i == 10:
                break
            for img in os.listdir(folder):
                img = Image(os.path.join(folder, img))
                if dataset.__class__ != Coco:   
                    # ann_file = dataset.findby_name(os.path.splitext(img.name)[0],
                    #                             datapath=dataset.ann_path,
                    #                             avoid_path=dataset.img_path,
                    #                             avoid_ext = ('png','jpg','jpeg'))
                    ann_root_data = dataset.parse(dataset.instance,img=img)
                        
                else:
                    ann_file = dataset.findby_ext(extension='.json',
                                                datapath=dataset.data)
                ann_root_data = dataset.parse(ann_file[1],img=img)
                if ann_root_data:
                    annotation = Annotation(ann_root_data ,img)
                    root.append((img, annotation))
                    i+=1
        return root