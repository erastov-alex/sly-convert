import json

from ds_manager.datasets.dataset import Dataset
from ds_manager.objects.image import Image


class Cityscapes(Dataset):#WORKS WITH POLYGONS
    def __init__(self, image_ext, img_path, data, mask):
        name = 'Cityscapes_Dataset'
        super().__init__(name=name, data=data, image_ext=image_ext, img_path=img_path, mask=mask)

    def parse(self,
              path_to_ann: str,
              img: Image):
        meta_city_path = self.findby_ext(extension='json',
                                         datapath=self.data)[1]
        annotation=[]
        with open(meta_city_path, "r") as f:
            meta = json.load(f)
        with open(path_to_ann, "r") as f:
            ann = json.load(f)
        for obj in ann['objects']:
            segmentation = obj['polygon']
            label_name = obj['label']
            # label color in meta 
            geometry = []
            for cords in segmentation:
                geometry.append(cords[::-1])
            annotation.append([label_name, geometry])
        return annotation