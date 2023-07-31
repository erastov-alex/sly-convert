import yaml
from yaml.loader import SafeLoader

from ds_manager.datasets.dataset import Dataset
from ds_manager.objects.image import Image

class Yolo(Dataset):#WORKS WITH RECTANGLES AND POLYGONS
    def __init__(self, image_ext, img_path, data, mask):
        name = 'Yolo_Dataset'
        super().__init__(name=name, data=data, image_ext=image_ext, img_path=img_path , mask=mask)

    def data_converter(self, data_YOLO, img_size):
        #[x_center, y_center, width(x), height(y)]
        data_YOLO = [float(num) for num in data_YOLO]
        if len(data_YOLO) ==4:
            x_center = data_YOLO[0]*img_size[1]
            y_center = data_YOLO[1]*img_size[0]
            width_yolo = data_YOLO[2]*img_size[1]
            height_yolo = data_YOLO[3]*img_size[0]
            left = x_center - width_yolo/2  
            top = y_center - height_yolo/2
            right = x_center + width_yolo/2 
            bottom = y_center + height_yolo/2
            bbox_SLY = left, top, right, bottom
            return bbox_SLY
        else:
            flag = 'y'
            normal_data = []
            x_y=[]
            for polygon in data_YOLO:
                if flag == 'y':
                    polygon = polygon*img_size[1]
                    flag = 'x'
                    x_y.append(polygon)
                else:
                    polygon = polygon*img_size[0]
                    flag = 'y'
                    x_y.append(polygon)
                    normal_data.append(x_y[::-1])
                    x_y=[]
            normal_data = normal_data[::-1]
            return normal_data
                
    def parse(self,
              path_to_instances: str,
              img: Image):
        annotation= []
        yaml_meta = self.findby_ext(extension='yaml',datapath=self.data)[1]
        with open(yaml_meta) as f:
            data = yaml.load(f, Loader=SafeLoader)
            names = data['names']
        f = open(path_to_instances, 'r')
        annotation_yolo_root = [line.strip() for line in f]
        for item in annotation_yolo_root:
            item = item.split(' ')
            item = names[int(item[0])], self.data_converter(item[1:], img.size)
            annotation.append(item) 
        return annotation
