<div align="center" markdown>

<img src="https://i.ibb.co/fHzfBCW/ds-manager.png"/>

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Requirements">Requirements</a> •
  <a href="#Test">Tests</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://https://supervisely.com/)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)

</div>

## Overview:

Introduce computer vision dataset manager designed for using in deep learning projects.
It contains tools for detecting and working with datasets presented in supported formats:

- [COCO](https://opencv.org/blog/2021/10/12/introduction-to-the-coco-dataset/)
- [YOLO](https://www.section.io/engineering-education/introduction-to-yolo-algorithm-for-object-detection/)
- [Pascal VOC](https://www.section.io/engineering-education/understanding-pascal-voc-dataset/)
- [Cityscapes](https://www.section.io/engineering-education/understanding-pascal-voc-dataset/)


### Supported shapes:
- COCO: polygon segmentation; object rectangles, RLE
- YOLO: polygon segmentation; object rectangles 
- Pascal VOC: object,class segmentation using png masks; object rectangles 
- Cityscapes: polygon segmentation

### Main functions:
- scan
    - input: Dataset in supported format
    - output: Dataset root (more about- click)
- dump_sly
    - input: Dataset root
    - output: Dataset in [Supervisely](https://supervisely.com/) format
- upload
    - Upload local output to Supervisely

## Requirements:
  
1. Create environment
((For using upload function) Create env folder in root. Create local.env, supervisely.env and advance.env using [link] instruction.)
2. Install requirements.txt
3. Check strict data format rule  
  
### Strict data format rule  
The data must follow strict rules:
 1. Images and annotations must be separated.
 2. Annotation name must refer to image.(except COCO)
 3. For COCO: there must be only one JSON file with images instance.
 UPDATE: you can use any quantity of instances
 4. For Pascal VOC: annotation must be XML file or presented in Object+Class PNG masks with labels in single file.
 5. For YOLO: annotation extension : TXT, meta extension: YAML.
 6. For Cityscapes: annotation, meta extension: JSON.

## Dataset root
Root will be created by using scan() function. 
This function creates list of tuples for each corresponding image and annotation.
Image presented as a class with size, name attributes.
Annotation - with image object and list of labels. Labels presented with separated
class with name(category) and geometry. Geometry presented in Supervisely geometry
classes (sly.Bitmap, sly.Polygon, sly.Rectangle)

## How to use 

For example you have folder `dataset` with dataset provide in (for example) in `YOLO` format with `input/dataset` path.
1. Initialize Dataset class. 
```
my_dataset = ds_manager.Dataset(
                 data = 'input/dataset', #path to folder
                 name = "My dataset", #name of your dataset [Optinal]
                 image_ext = None, #image extansion [Optinal]
                 img_path = 'input/dataset', #path to folder with images [Optinal]
                 mask = False # set True if dataset contatin PNG masks [Optinal]
                )
```
2. Scan your dataset and take root of the dataset 
```
my_dataset.root = ds_manager.scan()
```
3. Dump root to Supervisely
```
ds_manager.dump_sly(my_dataset.root)
```
You'll see `output_sly` folder
4. Upload your dataset to Supervisely
```
ds_manager.upload(
        delete = False, #Delete `output_sly` folder after import
        api=None, #use if you have Supervisely Api in globals
        WORKSPACE_ID=None, #use if you miss it in local.env
        proj_name=None, #use to set your project name on Supervisely
        progress_bar=None, #use if you have outsource tqdm widget
    )
```

## Tests
Here are datasets on which the functionality was tested.
All datasets are taken from [Supervisely](https://supervisely.com/) source. You can find some examles [here](https://github.com/erastov-alex/dataset_samples)


  
