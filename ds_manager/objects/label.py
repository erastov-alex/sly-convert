import supervisely as sly

class Label():

    @classmethod
    def rect(cls,
               geometry: list):
        if geometry[0][0] == geometry[1][0] and geometry[1][1] == geometry[2][1]:
            if geometry[2][0] == geometry[3][0] and geometry[3][1] == geometry[3][1]:
                left= geometry[0][1]
                top= geometry[0][0]
                right= geometry[2][1]
                bottom= geometry[2][0]
                return left, top, right, bottom
        return None

    def __init__(self,
                 obj : tuple or list): #[lable_name,(geometry)]
        self.name = obj[0]
        self.geometry = obj[1]
        if isinstance(self.geometry, type(None)):
            print(f'{self.name} has no geometry')
            return None
        if len(self.geometry) == 4 and (type(self.geometry[0]) == float or type(self.geometry[0]) == int):
            self.geometry = sly.Rectangle(left= self.geometry[0],
                                          top= self.geometry[1],
                                          right= self.geometry[2],
                                          bottom= self.geometry[3])
        elif len(self.geometry[0]) == 2:
            if self.rect(self.geometry):
                bbox = self.rect(self.geometry)
                self.geometry = sly.Rectangle(left= bbox[0],
                                          top= bbox[1],
                                          right= bbox[2],
                                          bottom= bbox[3])
            else:
                self.geometry = sly.Polygon(self.geometry)
        else:
            # mask = np.array(self.geometry, dtype=np.bool_) 
            self.geometry = sly.Bitmap(self.geometry)
