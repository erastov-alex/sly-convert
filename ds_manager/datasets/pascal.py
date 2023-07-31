import os
import numpy as np
import xml.etree.ElementTree as ET

from ds_manager.datasets.dataset import Dataset
from ds_manager.objects.image import Image


class Pascal(Dataset):
     #WORKS WITH BITMAPS AND RECTANGLES
    def __init__(self, image_ext, img_path, data, mask):
        name = 'Pacsal_Dataset'
        super().__init__(name=name, data=data, image_ext=image_ext, img_path=img_path, mask=mask)

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

    def mask_parse(self, img: Image):
        annotation = []
        colors = open(self.findby_ext(extension='txt',datapath=self.data)[1], 'r')
        label_color = [line.strip() for line in colors]
        label_color = [name.split() for name in label_color]
        label_dict = dict()
        for obj in label_color:
            label_dict[obj[0]]= [int(cord) for cord in obj[1:]]
        print(label_dict)
        mask_path_1 = self.findby_name(os.path.splitext(img.name)[0] + '.png',
                                        datapath=self.data,
                                        avoid_path=self.img_path,
                                        avoid_ext=('xml','mat'))
        mask1 = Image(mask_path_1[1])
        mask1_array = mask1.pixeliz(mask1.img_path)
        mask_path_2 = self.findby_name(os.path.splitext(img.name)[0] + '.png',
                                        datapath=self.data,
                                        avoid_path=mask_path_1[0],
                                        avoid_ext=('xml','mat'))
        mask2 = Image(mask_path_2[1])
        mask2_array = mask2.pixeliz(mask2.img_path)
        uniq2_colors = self.get_unique_numbers(mask2_array)
        uniq_colors = self.get_unique_numbers(mask1_array)
        bitmaps_obj = []
        bitmaps_cls = dict()
        for obj in uniq_colors:
            if obj != [0,0,0] and obj != label_dict['neutral']:
                if obj in label_dict.values():
                    obj_mask = mask2_array
                    obj_uniq = uniq2_colors
                    class_mask = mask1_array
                    class_uniq = uniq_colors
                else:
                    
                    obj_mask = mask1_array
                    obj_uniq = uniq_colors
                    class_mask = mask2_array
                    class_uniq = uniq2_colors
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
              img: Image
              ):
        # parse xml file
        assert os.path.isfile(path_to_xml)
        tree = ET.parse(path_to_xml) 
        root = tree.getroot()
        annotation = []
        if self.mask:
            return self.mask_parse(img)
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