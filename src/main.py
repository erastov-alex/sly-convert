import os
import supervisely as sly
import yaml
from yaml.loader import SafeLoader
import shutil
import xml.etree.ElementTree as ET
from pycocotools.coco import COCO
import json
import shutil
from PIL import Image

from tqdm import tqdm
from dotenv import load_dotenv
from supervisely.io.json import load_json_file


class Dataset():
    def __init__(self, name = "Dataset_1", data_path = "~/input", img_path = None, ann_path = None):
        self.name = name
        self.data_path = data_path
        self.img_path = img_path
        self.ann_path = ann_path
        print(f'{self.name} found at {self.data_path} "')

    def format(self):
        for rootdir, dirs, files in os.walk('input'):
            for file in files:       
                if file.endswith(".yaml"):
                    self = Yolo(self)
                    Yolo.convert(self)
                    break
                elif file.endswith(".xml" or ".png"):
                    self = Pascal(self)
                    Pascal.convert(self)
                    break
                elif file == 'instances.json':
                    self = Coco(self)
                    Coco.convert(self)
                elif file.endswith(".json"):
                    self = Cityscapes(self)
                    Cityscapes.convert(self)
                elif Dataset.image_extension(self) == 'mask':
                    #self = Mask(self)
                    #Mask.convert(self)
                    break
                         
    def folder_creator(self):
        try:
            os.makedirs('output_sly/ann')
            os.makedirs('output_sly/img')
        except Exception as e:
            print('Folders already created')
        pass

    def img_moover(self, extension, file_source = 'input'):
        for rootdir, dirs, files in os.walk(file_source):
            for file in files: 
                    if file.endswith(extension):
                        shutil.copy2(os.path.join(rootdir, file),'output_sly/img')
        pass

    def txt_parser(self, path_to_txt):
        f = open(path_to_txt, 'r')
        l = [line.strip() for line in f]
        return l
    
    def create_meta(self, names): #names type - list/set format [kiwi,lemon,apple]
        meta = sly.ProjectMeta()
        categories = names 
        for obj in categories:
            obj_class = sly.ObjClass(obj , sly.Rectangle)
            meta = meta.add_obj_class(obj_class)
        return meta
    
    def create_annotation(self, item, meta, img_size, annotation, image_index, image_extension):
        """
        item - file name, example 'img1.xml', str
        meta - meta of the project
        img_size - Tuple[int, int] or List[int, int], [height, width]
        annotation - list of label+(geometry), example [[label,(geometry)],[label,(geomerty)]]
        image_index - counter, int
        image_extension - type of image 'jpg' or 'jpeg' or 'png' , str
        """
        sly_labels = []
        for ann in annotation:
            bbox = ann[1]
            geometry = sly.Rectangle(left= bbox[0],top= bbox[1],right= bbox[2],bottom= bbox[3])
            name = ann[0]
            obj_class = meta.get_obj_class(obj_class_name= name)
            sly_label = sly.Label(geometry= geometry, obj_class= obj_class)
            sly_labels.append(sly_label)
        sly_ann = sly.Annotation(img_size= img_size, labels=sly_labels,image_id= image_index)
        ann_path = 'output_sly\\ann\\'
        ann_json = sly_ann.to_json()
        ann_path_json = ann_path + os.path.splitext(item)[0] + '.' + image_extension +'.json'
        sly.json.dump_json_file(ann_json, ann_path_json)
        pass

    def image_extension(self):
        jpegfound = False
        type = None
        for rootdir, dirs, files in os.walk('input'):
            for file in files:
                if file.endswith('jpg'):
                    type = 'jpg'
                    jpegfound = True # means that image ISNOT png file 
                elif file.endswith('jpeg'):
                    type = 'jpeg'
                    jpegfound = True
                elif file.endswith('png'):
                    if not jpegfound:
                        type = 'png'
                    else:
                        print('PNG MASKs FOUNDED')
                        return 'mask'
        return type

    def findby_ext(self, extension):
        for rootdir, dirs, files in os.walk('input'):
            for file in files:       
                if((file.split('.')[-1])==extension):
                    return rootdir, os.path.join(rootdir, file), file
        return None
    
    def findby_name(self, name):
        for rootdir, dirs, files in os.walk('input'):
            for file in files:       
                if name in file:
                    return rootdir, os.path.join(rootdir, file), file
        return None

    def img_size(self, img_path):
        im = Image.open(img_path)
        return im.size[::-1]
    
    def upload():
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

class Yolo(Dataset): #WORKS
    def __init__(self, name="Dataset_1", data_path="~/input"):
        name = 'YOLO_Dataset'
        super().__init__(name, data_path)
        self.img_path = Dataset.findby_ext(Dataset.image_extension(self))
        self.ann_path = Dataset.findby_ext('')

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
   
    def data_fixer(self, annotation_yolo_root, img_size, names):
        annotation = []
        for item in annotation_yolo_root:
            item = item.split(' ')
            item = names[int(item[0])], Yolo.bbox_converter(self, item[1:], img_size)
            annotation.append(item)
        return annotation
 
    def convert(self):
        Dataset.folder_creator(self)
        yaml_meta = Dataset.findby_ext(self, 'yaml')[1]
        with open(yaml_meta) as f:
            data = yaml.load(f, Loader=SafeLoader)
            names = data['names']
        meta = Dataset.create_meta(self, names)
        project_dir = "output_sly"
        meta_path = os.path.join(project_dir, "meta.json")
        meta_json = meta.to_json()
        sly.json.dump_json_file(meta_json, meta_path)
        image_index = 0
        for rootdir, dirs, files in os.walk('input'):
            for file in files:
                if file.endswith(".txt"):
                    annotation_yolo_root = Dataset.txt_parser(self, os.path.join(rootdir, file))
                    img_path = os.path.join(Dataset.findby_ext(self, Dataset.image_extension(self))[0], 
                                        file[:-3] +  Dataset.image_extension(self))
                    img_size = Dataset.img_size(self, img_path)
                    annotation = Yolo.data_fixer(self, annotation_yolo_root, img_size, names)
                    Dataset.create_annotation(self, file, meta, img_size,
                                          annotation, image_index,
                                          image_extension = Dataset.image_extension(self))
                    image_index+=1
        Dataset.img_moover(self, extension=Dataset.image_extension(self))
        print('DONE')
        pass

class Pascal(Dataset): #WORKS
    def __init__(self, name="Dataset_1", data_path="~/input"):
        name = 'Pacsal_Dataset'
        super().__init__(name, data_path)

    def xml_parse(self, inst_path):
        # parse xml file
        assert os.path.isfile(inst_path)
        tree = ET.parse(inst_path) 
        root = tree.getroot() # get root object
        annotation = []
        for member in root.findall('object'):
            class_name = member[0].text # class name  
            # bbox coordinates
            xmin = int(member[5][0].text)
            ymin = int(member[5][1].text)
            xmax = int(member[5][2].text)
            ymax = int(member[5][3].text)
            # store data in list
            annotation.append([class_name, (xmin, ymin, xmax, ymax)])

        return annotation

    def convert(self):
        Dataset.folder_creator(self)
        class_names = []
        for rootdir, dirs, files in os.walk('input'):
            for file in files:       
                if file.endswith(".xml"):
                    class_name = Pascal.xml_parse(self, os.path.join(rootdir, file))[0]
                    class_names.append(class_name[0])
        class_names = set(class_names)
        project_dir = "output_sly"
        meta_path = os.path.join(project_dir, "meta.json")
        meta = Dataset.create_meta(self, class_names)
        meta_json = meta.to_json()
        sly.json.dump_json_file(meta_json, meta_path)
        image_index =0
        if Dataset.findby_ext(self, 'xml') != None:
            ann_filelist = os.listdir(Dataset.findby_ext(self, 'xml')[0])
        else:
            print('!!! !!! Mask type of annotation. ABORT !!! !!!')
            #Dataset.findby_ext(self, 'mat')
        for file in ann_filelist:
            if file.endswith(".xml"):
                path_ann= (os.path.join(Dataset.findby_ext(self, 'xml')[0], file))
                annotation = Pascal.xml_parse(self, path_ann)
                img_path = os.path.join(Dataset.findby_ext(self, Dataset.image_extension(self))[0], 
                                        file[:-3] +  Dataset.image_extension(self))
                img_size = Dataset.img_size(self, img_path)
                Dataset.create_annotation(self, file, meta, img_size,
                                          annotation, image_index,
                                          image_extension = Dataset.image_extension(self))
        Dataset.img_moover(self, extension=Dataset.image_extension(self))
        print('Done')
        pass

class Coco(Dataset):

    def __init__(self, name="Dataset_1", data_path="~/input"):
        super().__init__(name, data_path)

    def segmentation_data_fixer(segmentation):
        segmentation_result=[]
        list_hash = []
        for i in range(len(segmentation[0])):
            list_hash.append(segmentation[0][i])
            if len(list_hash) == 2:
                list_hash.reverse()
                segmentation_result.append(list_hash)
                list_hash=[]
        return segmentation_result
    
    def convert(self):
        inst_path = os.path.join('input', 'annotations', 'instances.json')
        coco = COCO(inst_path)
        categories = coco.cats
        images = coco.imgs
        annotations = coco.imgToAnns
        Dataset.folder_creator(self)
        meta = Dataset.create_meta(self, categories)
        sly_anns = []
        for image_id in annotations:
            sly_labels = []
            for annotation in annotations[image_id]:
                segmentation = annotation['segmentation']
                geomery = sly.Polygon(Coco.segmentation_data_fixer(segmentation))
                cat_id = annotation["category_id"]
                name = categories[cat_id]['name']
                obj_class = meta.get_obj_class(obj_class_name= name)
                sly_label = sly.Label(geometry= geomery, obj_class= obj_class)
                sly_labels.append(sly_label)
            img_size = images[image_id]['height'], images[image_id]['width']
            sly_ann = sly.Annotation(img_size= img_size, labels=sly_labels,image_id= image_id)
            sly_anns.append(sly_ann)
        ann_path = 'output_sly\\dataset\\ann\\'
        for ann in sly_anns:
            ann_json = ann.to_json()
            ann_path_json = ann_path + images[ann_json['imageId']]['file_name'] + '.json'
            sly.json.dump_json_file(ann_json, ann_path_json)
        Dataset.img_moover(self)
        print('DONE')

class Cityscapes(Dataset):
    def __init__(self, name="Dataset_1", data_path="~/input"):
        name = 'Cityscapes_Dataset'
        super().__init__(name, data_path)
 
    def annotation_reader(self, item_json):
        with open(item_json, "r") as f:
            data = json.load(f)
            return data
    
    def polygon_data_fixer(self, polygons):
        polygon_fixed = []
        for cords in polygons:
            polygon_fixed.append(cords[::-1])
        return polygon_fixed 

        
    def convert(self):
        Dataset.folder_creator(self)
        meta_ciy_path = Dataset.findby_ext(self, 'json')[1]
        data = Cityscapes.annotation_reader(self, meta_ciy_path)
        names=list()
        for item in data:
            names.append(item['name'])
        meta = Dataset.create_meta(self, names)
        meta_json = meta.to_json()
        project_dir = "output_sly"
        meta_path = os.path.join(project_dir, "meta.json")
        sly.json.dump_json_file(meta_json, meta_path)
        image_index =0
        for rootdir, dirs, files in os.walk('input'):
            for file in files:       
                if file.endswith(".json") and file != 'class_to_id.json':
                    img_path = Dataset.findby_name(self, file[:-15])[1]
                    img_size = Dataset.img_size(self, img_path)
                    annotation_root = Cityscapes.annotation_reader(self, os.path.join(rootdir, file))
                    Dataset.create_annotation(self, file, meta, img_size,
                                          annotation, image_index,
                                          image_extension = Dataset.image_extension(self))
                    image_index+=1
        Dataset.img_moover(self)
        pass

class Convert():
    def __init__(self, input):
        self.input = 'input'
        new_covert = Dataset()
        Dataset.format(new_covert)
        pass
    
Dataset.upload()


