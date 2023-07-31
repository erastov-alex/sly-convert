from ds_manager.datasets.dataset import Dataset
from ds_manager.objects.image import Image
from pycocotools.coco import COCO

import pycocotools.mask as mask
import pycocotools._mask as _mask_util
import numpy as np
import cv2


class Coco(Dataset):
    """
    WORKS WITH POLYGONS AND RECTANGLES
    """
    def __init__(self, image_ext, img_path, data, mask):
        name = 'COCO_Dataset'
        super().__init__(name=name, data=data, image_ext=image_ext, img_path=img_path, mask = mask)
        self.instances = []
        instance_names = []
        while self.findby_ext(extension='.json',datapath=self.data, avoid_name=instance_names):
            instance = self.findby_ext(extension='.json', datapath=self.data, avoid_name=instance_names)
            instance_names.append(instance[2])
            coco_instance = COCO(instance[1])
            self.instances.append(coco_instance)


    @classmethod
    def polygonFromMask(cls, maskedArr):
    # adapted from https://github.com/hazirbas/coco-json-converter/blob/master/generate_coco_json.py
        contours, _ = cv2.findContours(maskedArr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        segmentation = []
        valid_poly = 0
        for contour in contours:
        # Valid polygons have >= 6 coordinates (3 points)
            if contour.size >= 6:
                segmentation.append(contour.astype(float).flatten().tolist())
                valid_poly += 1
        if valid_poly == 0:
            raise ValueError
        return segmentation
 
    def segmentation_data_fixer(self, segmentation):
        segmentation_result=[]
        if not isinstance(segmentation, list):
            if isinstance(segmentation['counts'], str):
                maskedArr  = mask.decode(segmentation)
                mask2 = np.array(maskedArr, dtype=np.bool_)
                return mask2
            else:
                rle_obj = mask.frPyObjects(
                    segmentation,
                    segmentation["size"][0],
                    segmentation["size"][1],
                )
                maskedArr  = mask.decode(rle_obj)
                mask2 = np.array(maskedArr, dtype=np.bool_)
                # mask2 = maskedArr[:, :, 0].astype(bool)
                # try:
                #     segmentation_root = self.polygonFromMask(maskedArr)
                # except ValueError:
                #     print(f'somthing wrong wih geometry - Valid polygons have >= 6 coordinates (3 points)')
                #     return None
                # for area in segmentation_root:
                #     area_fix = self.segmentation_data_fixer([area])
                #     segmentation_result.extend(area_fix)
                # return segmentation_result
                return mask2
        else:
            list_hash = []
            for i in range(len(segmentation[0])):
                list_hash.append(segmentation[0][i])
                if len(list_hash) == 2:
                    list_hash.reverse()
                    segmentation_result.append(list_hash)
                    list_hash=[]
            return segmentation_result

    def parse(self,
              path,
              img: Image):
        
        annotation = []
        for inst in self.instances:
            instance = inst
            categories = instance.cats
            images = instance.imgs
            annotations = instance.imgToAnns
            for key, value in images.items():
                if value['file_name'] == img.name:
                    for label in annotations[key]:
                        geometry = self.segmentation_data_fixer(label['segmentation'])
                        cat_id = label["category_id"]
                        label_name = categories[cat_id]['name']
                        annotation.append([label_name, geometry])
        return annotation
