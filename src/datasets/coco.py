from src.datasets.dataset import Dataset
from src.objects.image import Image
from pycocotools.coco import COCO


class Coco(Dataset):#WORKS WITH POLYGONS AND RECTANGLES
    def __init__(self, image_ext, img_path, data, mask):
        name = 'COCO_Dataset'
        super().__init__(name=name, data=data, image_ext=image_ext, img_path=img_path, mask = mask)
        self.instance = COCO(self.findby_ext(extension='.json',
                                                datapath=self.data)[1])
    
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
              path,
              img: Image):
        instance = self.instance
        categories = instance.cats
        images = instance.imgs
        annotations = instance.imgToAnns
        annotation = []
        for key, value in images.items():
            if value['file_name'] == img.name:
                for label in annotations[key]:
                    if isinstance(label['segmentation'], list):
                        geometry = self.segmentation_data_fixer(label['segmentation'])
                        cat_id = label["category_id"]
                        label_name = categories[cat_id]['name']
                        annotation.append([label_name, geometry])
                    else:
                        continue

                    
        return annotation
