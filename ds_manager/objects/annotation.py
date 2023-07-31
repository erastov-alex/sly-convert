from ds_manager.objects.image import Image
from ds_manager.objects.label import Label

class Annotation():
    def __init__(self,
                 data: list or tuple, #list of label+(geometry), example [[lable_name,(geometry)],[label,(geomerty)]...]
                 image: Image)->list:
        self.labels = []
        self.image = image
        for obj in data:
            label = Label(obj)
            if not label.geometry:
                print(f'^^^^^^^^^ empty label in {image.name}')
                continue
            self.labels.append(label)
        pass

    # def __iter__(self):
    #     self.index = 0
    #     return self.labels
    
    # def __next__(self):
    #     if self.index <= len(self.labels):
    #         self.index+=1
    #         return self.labels[self.index]
    