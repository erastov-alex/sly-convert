____
# Deep Learning dataset manager for computer vision

## Overview:

Introduce computer vision dataset manager designed for using in deep learning projects.
It contains tools for detecting and working with datasets presented in supported formats:
*- [COCO](https://opencv.org/blog/2021/10/12/introduction-to-the-coco-dataset/)
- [YOLO](https://www.section.io/engineering-education/introduction-to-yolo-algorithm-for-object-detection/)
- [Pascal VOC](https://www.section.io/engineering-education/understanding-pascal-voc-dataset/)
- [Cityscapes](https://www.section.io/engineering-education/understanding-pascal-voc-dataset/)*

### Supported shapes:
COCO: polygon segmentation; object rectangles
YOLO: polygon segmentation; object rectangles 
Pascal VOC: object,class segmentation using png masks; object rectangles 
Cityscapes: polygon segmentation

### Main functions:
-scan
    -input: Dataset in supported format
    -output: Dataset root (more about- click) 
-dump_sly
    -input: Dataset root
    -output: Dataset in [Supervisely](https://supervisely.com/) format
-upload
    -Upload local output to Supervisely

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
 4. For Pascal VOC: annotation must be XML file or presented in Object+Class PNG masks with labels in single file.
 5. For YOLO: annotation extension : TXT, meta extension: YAML.
 6. For Cityscapes: annotation, meta extension: JSON.

## Dataset root
Root will be created by using Dataset.scan(). 
This function creates list of tuples for each corresponding image and annotation.
Image presented as a class with size, name attributes.
Annotation - with image object and list of labels. Labels presented with separated
class with name(category) and geometry. Geometry presented in Supervisely geometry
classes (sly.Bitmap, sly.Polygon, sly.Rectangle) 

## How to use 
 1. Clone repository
 2. Insert your data (Default- /input)
 3. Init your data by init Dataset class [a = Dataset(data= path_to_your_dataset) you can use more than one datasets
 4. Call scan function and overwrite root data (default root data = []) [a.root = a.scan()]
 5. Dump to Supervisely format [a.dump_sly()]
 6. Upload your data to Supervisely [a.upload()] (be careful and don’t forget to activate entertainment)

## Tests
Here are datasets on which the functionality was tested.
All datasets are taken from [Supervisely](https://supervisely.com/) source.


  
