import os
import supervisely as sly
import numpy as np
from PIL import Image as pil

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
                