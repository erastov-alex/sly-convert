import os
import supervisely as sly
import yaml
from yaml.loader import SafeLoader
import shutil
import xml.etree.ElementTree as ET
from pycocotools.coco import COCO
import numpy as np
import json
import shutil
from PIL import Image as pil
from skimage.io import imread

from tqdm import tqdm
from dotenv import load_dotenv
from supervisely.io.json import load_json_file

class Image():
    @classmethod
    def pixeliz(cls,
                img_path: str): 
        img = sly.imaging.image.read(img_path)
        img = np.array(img)
        width = len(img)
        height = len(img[0])
        mask= []
        for x in range(width):
            mask_line= []
            for y in range(height):
                mask_line.append(img[x][y])
            mask.append(mask_line)
        # mask = img[:, :, 0].astype(int)
        return mask
    
    @classmethod
    def getsize(cls,
                mask):
        return len(mask) , len(mask[0]) 
    
    def __init__(self,
                 img_path = None):
        if not img_path:
            raise NotImplemented('Image not founded')
        self.img_path = img_path
        image = pil.open(img_path)
        self.width = image.size[0] #Определяем ширину. 
        self.height = image.size[1]
        # self.height, self.width = self.getsize(self.pixeliz(self.img_path))
        self.size = self.height, self.width
        self.name = os.path.basename(self.img_path)
                
class Annotation():
    def __init__(self,
                 data: list or tuple, #list of label+(geometry), example [[lable_name,(geometry)],[label,(geomerty)]...]
                 image: Image)->list:
        self.labels = []
        self.image = image
        for obj in data:
            label = Label(obj)
            self.labels.append(label)
        pass

    # def __iter__(self):
    #     self.index = 0
    #     return self.labels
    
    # def __next__(self):
    #     if self.index <= len(self.labels):
    #         self.index+=1
    #         return self.labels[self.index]
    
class Label():

    @classmethod
    def rect(cls,
               geometry: list):
        if geometry[0][0] == geometry[1][0] and geometry[1][1] == geometry[2][1]:
            if geometry[2][0] == geometry[3][0] and geometry[3][1] == geometry[3][1]:
                left= geometry[0][1]
                top= geometry[0][0]
                right= geometry[2][1]
                bottom= geometry[2][0]
                return left, top, right, bottom
        return None

    def __init__(self,
                 obj : tuple or list): #[lable_name,(geometry)]
        self.name = obj[0]
        self.geometry = obj[1]
        if len(self.geometry) == 4:
            self.geometry = sly.Rectangle(left= self.geometry[0],
                                          top= self.geometry[1],
                                          right= self.geometry[2],
                                          bottom= self.geometry[3])
        elif len(self.geometry[0]) == 2:
            if self.rect(self.geometry):
                bbox = self.rect(self.geometry)
                self.geometry = sly.Rectangle(left= bbox[0],
                                          top= bbox[1],
                                          right= bbox[2],
                                          bottom= bbox[3])
            else:
                self.geometry = sly.Polygon(self.geometry)
        else:
            # mask = np.array(self.geometry, dtype=np.bool_) 
            self.geometry = sly.Bitmap(self.geometry)

class Dataset():
    data_path = 'input'

    @classmethod
    def findby_ext(cls,
                   extension: str,
                   datapath = 'input',
                   avoid_path = None):
        for rootdir, dirs, files in os.walk(datapath):
            if rootdir == avoid_path:
                continue
            else:
                for file in files:       
                   if file.endswith(extension):
                        return rootdir, os.path.join(rootdir, file), file
        return None
                
    @classmethod
    def findby_name(cls, 
                    name,
                    datapath = 'input',
                    avoid_path = None):
        for rootdir, dirs, files in os.walk(datapath):
            if rootdir == avoid_path:
                continue
            else:
                for file in files:       
                    if name in file:
                        return rootdir, os.path.join(rootdir, file), file
        return None

    def __init__(self, name = "Dataset_1"):
        self.root= []
        self.name = name
        self.mask = False
        self.img_ext = self.img_ext_func()
        if not self.img_ext:
            raise NotImplementedError()
        self.img_path = self.findby_ext(self.img_ext)[0]
        self.ann_path = 'input'
        print(f'{self.name} found at {self.data_path} "')

    def img_ext_func(self):
        jpegfound = False # means that image ISNOT png file 
        self.img_ext = None
        for rootdir, dirs, files in os.walk(self.data_path):
            for file in files:
                if file.endswith('jpg'):
                    self.img_ext = 'jpg'
                    jpegfound = True 
                elif file.endswith('jpeg'):
                    self.img_ext = 'jpeg'
                    jpegfound = True
                elif file.endswith('png'):
                    if not jpegfound:
                        self.img_ext = 'png'
                    else:
                        print('PNG MASKs FOUNDED')
                        self.mask = True
        if not self.img_ext:
            raise NotImplemented
        return self.img_ext

    def scan(self):
        flag = True
        root = []
        for img in os.listdir(self.img_path):
            img = Image(os.path.join(self.img_path, img))
            if self.__class__ != Coco:   
                ann_file = self.findby_name(os.path.splitext(img.name)[0],
                                            datapath=self.ann_path,
                                            avoid_path=self.img_path)
                if flag:
                    if ann_file == None:
                        ann_file = self.findby_name('instances.json')
                        self = Coco(self)
                        flag = False
                    elif ann_file[2].endswith(".txt"):
                        self = Yolo(self)
                        flag = False
                    elif ann_file[2].endswith(".xml" or ".mat"):
                        self = Pascal(self)
                        flag = False
                    elif ann_file[2].endswith(".json"):
                        self = Cityscapes(self)
                        flag = False
                    elif self.img_ext == 'mask':
                    #self = Mask(self)
                    #Mask.convert(self)
                        raise ImportError
            else:
                ann_file = self.findby_name('instances.json')
            annotation = Annotation(self.parse(ann_file[1],img), img)
            root.append((img, annotation))
        return root

    def dump_sly(self):
        try:
            os.makedirs(os.path.join('output_sly', 'ann'))
            os.makedirs(os.path.join('output_sly', 'img'))
        except Exception as e:
            print('Folders already created')
        meta = sly.ProjectMeta()
        uniq_cats = []
        for obj in self.root:
            for label in obj[1].labels:
                uniq_cats.append((label.name, type(label.geometry)))
        uniq_cats = set(uniq_cats)
        for cat in uniq_cats:
            obj_class = sly.ObjClass(cat[0], cat[1])
            meta = meta.add_obj_class(obj_class)
        meta_json = meta.to_json()
        sly.json.dump_json_file(meta_json, os.path.join('output_sly', "meta.json"))
        i=0
        for obj in self.root:
            shutil.copy2(os.path.join(obj[0].img_path),'output_sly/img')
            sly_labels = []
            for label in obj[1].labels:
                geometry = label.geometry
                obj_class = meta.get_obj_class(obj_class_name= label.name)
                sly_label = sly.Label(geometry, obj_class)
                sly_labels.append(sly_label)
            sly_ann = sly.Annotation(img_size= obj[0].size, labels=sly_labels,image_id= i)
            ann_json = sly_ann.to_json()
            ann_path_json = os.path.join('output_sly\\ann', obj[0].name +'.json')
            sly.json.dump_json_file(ann_json, ann_path_json)
            i+=1
        print('DONE')

    def upload(self):
        path_advanced = os.path.expanduser("~\\env\\advanced.env")
        path_local = os.path.expanduser("~\\env\\local.env")
        path_supervisely = os.path.expanduser("~\\env\\supervisely.env")
        if sly.is_production():
            load_dotenv(path_advanced)
        else:
            load_dotenv(path_local)
        load_dotenv(os.path.expanduser(path_supervisely ))
        # Get ENV variables
        WORKSPACE_ID = sly.env.workspace_id()
        # Create api object to communicate with Supervisely Server
        api = sly.Api.from_env()
        # Initialize application
        app = sly.Application()
        input_name = input('Set project name \n')
        # Create project and dataset on Supervisely server
        project = api.project.create(WORKSPACE_ID, input_name , change_name_if_conflict=True)
        dataset = api.dataset.create(project.id, "ds0", change_name_if_conflict=True)
        project_id = project.id
        path_to_meta = "output_sly\meta.json"
        project_meta_json = load_json_file(path_to_meta)
        api.project.update_meta(project_id, project_meta_json)
        images_names = []
        images_paths = []
        for file in os.listdir('output_sly\img'):
            file_path = os.path.join('output_sly\img', file)
            images_names.append(file)
            images_paths.append(file_path)
        ann_names = []
        ann_paths = []
        for file in os.listdir('output_sly\\ann'):
            file_path = os.path.join('output_sly\\ann', file)
            ann_names.append(file)
            ann_paths.append(file_path)
        #Process folder with images and upload them to Supervisely server
        with tqdm(total=len(images_paths)) as pbar:
            for img_name, img_path, ann_path in zip(images_names, images_paths, ann_paths):
                try:
                    # Upload image and annotation into dataset on Supervisely server
                    info = api.image.upload_path(dataset_id=dataset.id, name=img_name, path=img_path)
                    sly.logger.trace(f"Image has been uploaded: id={info.id}, name={info.name}")
                    inf_ann = api.annotation.upload_path(img_id= info.id, ann_path=ann_path)
                    sly.logger.trace(f"Annotation has been uploaded")
                except Exception as e:
                    sly.logger.warn("Skip image", extra={"name": img_name, "reason": repr(e)})
                finally:
                    # Update progress bar
                    pbar.update(1)
        sly.logger.info(f"Result project: id={project.id}, name={project.name}")
        pass

class Coco(Dataset):#WORKS WITH POLYGONS AND RECTANGLES
    def __init__(self, name="Coco"):
        super().__init__(name=name)
        self.ann_path = Dataset.findby_ext('json')[0]
    
    def segmentation_data_fixer(self, segmentation):
        segmentation_result=[]
        list_hash = []
        for i in range(len(segmentation[0])):
            list_hash.append(segmentation[0][i])
            if len(list_hash) == 2:
                list_hash.reverse()
                segmentation_result.append(list_hash)
                list_hash=[]
        return segmentation_result

    def parse(self,
              path_to_instances: str,
              img: Image):
        annotation = []
        coco = COCO(path_to_instances)
        categories = coco.cats
        images = coco.imgs
        annotations = coco.imgToAnns
        for key, value in images.items():
            if value['file_name'] == img.name:
                for label in annotations[key]:
                    geometry = self.segmentation_data_fixer(label['segmentation'])
                    cat_id = label["category_id"]
                    label_name = categories[cat_id]['name']
                    annotation.append([label_name, geometry])
        return annotation

class Cityscapes(Dataset):
    def __init__(self, name="Dataset_1", data_path="~/input"):
        name = 'Cityscapes_Dataset'
        super().__init__(name, data_path)

class Pascal(Dataset): #WORKS WITH BITMAPS AND RECTANGLES
    def __init__(self, name='Pacsal_Dataset'):
        super().__init__(name=name)
        self.ann_path = Dataset.findby_ext('xml')[0]

    def mask_creator(self, mask_origin, cat_origin): #creating bool type array using mask and category
        mask_currect = []
        cat_origin = [int(cat) for cat in cat_origin]
        for line_y in mask_origin:
            mask_line= []
            for line_x in line_y:
                line_x = [int(c) for c in line_x]
                if line_x == cat_origin:
                    mask_line.append(1)
                else:
                    mask_line.append(0)
            mask_currect.append(mask_line)
        return mask_currect
    
    def get_unique_numbers(self, array):
        unique = []
        for x in array:
            for y in x: 
                if list(y) not in unique:
                    unique.append(list(y))
        return unique
    
    def maskin(self, mask1, mask2):
        mask1 = list(mask1)
        mask2 = list(mask2)
        for obj in zip(mask1,mask2):
            d = zip(obj[0],obj[1])
            for item_y in d:
                if item_y == (True, True):
                    return True
        return False

    def mask_parse(self,
                   path_to_xml: str,
                   img: Image):
        annotation = []
        colors = open(self.findby_ext('txt')[1], 'r')
        label_color = [line.strip() for line in colors]
        label_color = [name.split() for name in label_color]
        labels = []
        label_dict = dict()
        for obj in label_color:
            label_dict[obj[0]]= [int(cord) for cord in obj[1:]]
        print(label_dict)
        mask_path_1 = self.findby_name(os.path.splitext(img.name)[0] + '.png',
                                        datapath=self.data_path,
                                        avoid_path=self.img_path)
        mask1 = Image(mask_path_1[1])
        mask1_array = mask1.pixeliz(mask1.img_path)
        mask_path_2 = self.findby_name(os.path.splitext(img.name)[0] + '.png',
                                        datapath=self.data_path,
                                        avoid_path=mask_path_1[0])
        mask2 = Image(mask_path_2[1])
        mask2_array = mask2.pixeliz(mask2.img_path)
        uniq2_colors = self.get_unique_numbers(mask2_array)
        uniq_colors = self.get_unique_numbers(mask1_array)
        bitmaps_obj = []
        bitmaps_cls = dict()
        for obj in uniq_colors:
            if obj in label_dict.values() and obj != [0,0,0] and obj != label_dict['neutral']:
                obj_mask = mask2_array
                obj_uniq = uniq2_colors
                class_mask = mask1_array
                class_uniq = uniq_colors 
        for label in class_uniq:
            if label != [0, 0, 0] and label_dict['neutral'] != label:
                bitmap = self.mask_creator(class_mask, label)
                bitmap = np.array(bitmap, dtype=np.bool_)
                for item in label_dict.items():
                    if label in item:
                        bitmaps_cls[item[0]] = bitmap
        for obj in obj_uniq:
            if  obj != [0,0,0] and obj != label_dict['neutral']:
                bitmap = self.mask_creator(obj_mask, obj)
                bitmap = np.array(bitmap, dtype=np.bool_)
                for map in bitmaps_cls.items():
                    if self.maskin(bitmap, map[1]):
                        label_name = map[0]
                        annotation.append((label_name, bitmap))
        return annotation

    def parse(self,
              path_to_xml: str,
              img: Image):
        # parse xml file
        assert os.path.isfile(path_to_xml)
        tree = ET.parse(path_to_xml) 
        root = tree.getroot()
        annotation = []
        if self.mask:
            return self.mask_parse(path_to_xml,img)
        for member in root.findall('object'):
            for name in member.findall('name'):
                label_name = str(name.text)
            for cord in member.findall('bndbox'):
                xmin = int(cord[0].text)
                ymin = int(cord[1].text)
                xmax = int(cord[2].text)
                ymax = int(cord[3].text)
                geometry = xmin, ymin, xmax, ymax
            # store data in list
            annotation.append([label_name, geometry])
        return annotation

class Yolo(Dataset):#WORKS WITH RECTANGLES
    def __init__(self, name="Yolo"):
        super().__init__(name=name)
        self.ann_path = self.findby_ext('txt')[0]

    def bbox_converter(self, bbox_YOLO, img_size):
        #[x_center, y_center, width(x), height(y)]
        bbox_YOLO = [float(item) for item in bbox_YOLO]
        x_center = bbox_YOLO[0]*img_size[1]
        y_center = bbox_YOLO[1]*img_size[0]
        width_yolo = bbox_YOLO[2]*img_size[1]
        height_yolo = bbox_YOLO[3]*img_size[0]
        left = x_center - width_yolo/2  
        top = y_center - height_yolo/2
        right = x_center + width_yolo/2 
        bottom = y_center + height_yolo/2
        bbox_SLY = left, top, right, bottom   
        return bbox_SLY

    def parse(self,
              path_to_instances: str,
              img: Image):
        annotation= []
        yaml_meta = self.findby_ext('yaml')[1]
        with open(yaml_meta) as f:
            data = yaml.load(f, Loader=SafeLoader)
            names = data['names']
        f = open(path_to_instances, 'r')
        annotation_yolo_root = [line.strip() for line in f]
        for item in annotation_yolo_root:
            item = item.split(' ')
            item = names[int(item[0])], self.bbox_converter(item[1:], img.size)
            annotation.append(item) 
        return annotation
        
        

a = Dataset()
a.root = a.scan()
a.dump_sly()
a.upload()