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
    dataset.image_ext, dataset.img_path, dataset.mask = dataset.img_ext_func()
    # if len(img_path)>1:
    #     if img_ext == 'png' and dataset.mask:
    #         inp = dataset.img_path
    #         if isinstance(inp, str):
    #             dataset.img_path = []
    #             inp = inp.split()
    #             for folder in inp:
    #                 for rootdir, dir, file in os.walk(dataset.data):
    #                     if dir == folder:
    #                         dataset.img_path = rootdir
    #         img_path = dataset.img_path
    if not dataset.image_ext:
        raise NotImplementedError()
    random_img = dataset.findby_ext(extension=dataset.image_ext,
                                    datapath=dataset.img_path)
    img = Image(random_img[1])
    random_ann = dataset.findby_name(os.path.splitext(img.name)[0],
                                            datapath=dataset.ann_path,
                                            avoid_path=dataset.img_path,
                                            avoid_ext = ('jpg','png','jpeg'))
    if random_ann == None:
        dataset = Coco(image_ext=dataset.image_ext,
                            img_path=dataset.img_path,
                            data = data,
                            mask = dataset.mask)
    elif random_ann[2].endswith(".txt"):
        dataset = Yolo(image_ext=dataset.image_ext,
                            img_path=dataset.img_path,
                            data = data,
                            mask = dataset.mask)
    elif random_ann[2].endswith(".xml" or ".mat"):
        dataset = Pascal(image_ext=dataset.image_ext,
                            img_path=dataset.img_path,
                            data = data,
                            mask = dataset.mask)
    elif random_ann[2].endswith(".json"):
        dataset = Cityscapes(image_ext=dataset.image_ext,
                            img_path=dataset.img_path,
                            data = data,
                            mask = dataset.mask)
    i = 0
    for folder in dataset.img_path:
        for img in os.listdir(folder):
            if isinstance(img,bytes):
                img = img.decode()
            img = Image(os.path.join(folder, img))  
            if dataset.__class__ != Coco:   
                ann_file = dataset.findby_name(os.path.splitext(img.name)[0],
                                            datapath=dataset.ann_path,
                                            avoid_path=dataset.img_path,
                                            avoid_ext = ('png','jpg','jpeg'))
                ann_root_data = dataset.parse(ann_file[1],img=img)
            else:
                ann_root_data = dataset.parse(dataset.instances,img=img)
            if ann_root_data:
                annotation = Annotation(ann_root_data ,img)
                root.append((img, annotation))
                i+=1
    dataset.root = root
    return dataset