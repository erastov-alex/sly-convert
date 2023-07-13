import os
import supervisely as sly
import shutil
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv
from supervisely.io.json import load_json_file

class Dataset():

    @classmethod
    def findby_ext(cls,
                   extension: str,
                   datapath: tuple = ('input',),
                   avoid_path: tuple = ('None',)):
        if  isinstance(datapath, str):
            datapath = (datapath,)
        for folder in datapath:
            for rootdir, dirs, files in os.walk(folder):
                if rootdir in avoid_path:
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
                    avoid_path = ('None',),
                    avoid_ext = ('None',)):
        max_index = 0
        root = None
        for rootdir, dirs, files in os.walk(datapath):
            if rootdir in avoid_path:
                continue
            else:
                for file in files:  
                    if file.endswith(avoid_ext):
                        continue
                    index = 0
                    for ch in enumerate(name):
                        try:
                            if ch[1] == file[ch[0]]:
                                index = ch[0]
                            else:
                                break
                        except IndexError:
                            continue
                    if index >= max_index:
                        max_index = index
                        root = rootdir, os.path.join(rootdir, file), file
        if max_index == 0:
            return None
        return root

    def __init__(self,
                 data = 'input',
                 name = "Dataset_1",
                 image_ext = None,
                 img_path = 'input',
                 mask = False):
        self.data = data
        self.root= []
        self.name = name
        self.mask = mask
        self.img_path = img_path
        self.image_ext = image_ext
        self.ann_path = data
        print(f'{self.name} found at {self.data} "')

    def img_ext_func(self):
        jpegfound = False
        pngfound = False # means that image ISNOT png file 
        img_ext = None
        mask = False
        img_path = []
        jpg_path = []
        png_path = []
        jpeg_path= []
        for rootdir, dirs, files in os.walk(self.data):
            for file in files:
                if file.endswith('jpg'):
                    img_ext = 'jpg'
                    jpegfound = True 
                    jpg_path.append(rootdir)
                    if pngfound:
                        mask = True
                elif file.endswith('jpeg'):
                    img_ext = 'jpeg'
                    jpegfound = True
                    if pngfound:
                        mask = True
                    jpeg_path.append(rootdir)
                elif file.endswith('png'):
                    if not jpegfound:
                        img_ext = 'png'
                        pngfound = True
                        png_path.append(rootdir)
                    else:
                        mask = True
                        png_path.append(rootdir)
        if not img_ext:
            raise NotImplemented
        elif img_ext == 'jpeg':
            img_path = jpeg_path 
        elif img_ext == 'jpg':
            img_path = jpg_path
        else:
            img_path = png_path
        if mask:
            if input('MASKS FOUNDED, CONVERT TO SHAPE BITMAP? \n     [y] for yes\n     [n] for no\n') == 'y':
                self.mask = True
        return img_ext, np.unique(img_path), self.mask

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

    def upload(self, delete = False):
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
        input_name = self.data
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
        if delete:
            shutil.rmtree("output_sly")
            return
        if input('Success! Delete local output? \n     [y] for yes\n     [n] for no\n') == 'y':
            shutil.rmtree("output_sly")
        pass




