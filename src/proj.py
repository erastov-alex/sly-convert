import os



class Convert():
    def __init__(self, name = "Dataset", data_path = "~/input"):
      self.name = name
      self.data_path = data_path
      
    def format_detector(self):
      environment = os.listdir(self.data_path)
      """
      FOR FILES IN ENVIRONMENT CHECK FILES EXPANSION AND MAKE TRY BLOCK FOR PARSIN ANN FILE
      """
      return format 
      
    def coco_converter(self):
      """
      COCO CONVERTER
      """
      return geometry
      
    def pascal_converter(self):
      """
      PASCAL CONVERTER
      """
      return geometry
      
    def yolo_converter(self):
      """
      YOLO CONVERTER
      """
      return geometry
      
    def cityscapes_converter(self):
      """
      CITYSCAPES CONVERTER
      """
      return geometry
      
    def meta_creator(self, cats):
      project_dir = "outputsly/"
      meta_path = os.path.join(project_dir, "meta.json")
      meta = sly.ProjectMeta()
      # Create meta.json
      obj_classes = []
      categories = cats
      for obj in categories:
          obj_class = sly.ObjClass(obj , sly.AnyShape)
          meta = meta.add_obj_class(obj_class)
      meta_json = meta.to_json()
      sly.json.dump_json_file(meta_json, meta_path)
      
    def run(self):
      """main part of converter"""
      format = format_detector(self)
      if format == "pascal":
        meta = pascal_converter(self)
      elif format == "coco":
        meta = coco_converter(self)
      elif format == "yolo"
         meta = yolo_converter(self) 
      elif format == "cityscapes":
        meta = cityscapes_converter(self)
      elif format == "sly"
         print("already supervisely")
      else: 
         print("unsupported format") 
         break
      meta_create(cats)
      img_files_list = []
      for root, dirs, files in os.walk(self.data_path): for file in files:
        if(file.endswith(".jpeg")):
          file_name = os.path.basename(file)
          
       
    
      