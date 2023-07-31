import os
import shutil
import supervisely as sly


def dump_sly(root, path=None):
    if not path:
        try:
            os.makedirs(os.path.join('output_sly', 'ann'))
            os.makedirs(os.path.join('output_sly', 'img'))
        except Exception as e:
            print('Folders already created')
    meta = sly.ProjectMeta()
    uniq_cats = []
    for obj in root:
        for label in obj[1].labels:   
            uniq_cats.append((label.name, sly.AnyGeometry))
    uniq_cats = set(uniq_cats)
    for cat in uniq_cats:  
        obj_class = meta.get_obj_class(cat[0])
        if obj_class is None:   
            obj_class = sly.ObjClass(cat[0], cat[1])
            meta = meta.add_obj_class(obj_class)
    meta_json = meta.to_json()
    sly.json.dump_json_file(meta_json, os.path.join('output_sly', "meta.json"))
    i=0
    for obj in root:
        shutil.copy2(os.path.join(obj[0].img_path),os.path.join('output_sly','img'))
        sly_labels = []
        for label in obj[1].labels:
            geometry = label.geometry
            obj_class = meta.get_obj_class(obj_class_name= label.name)
            sly_label = sly.Label(geometry, obj_class)
            sly_labels.append(sly_label)
        sly_ann = sly.Annotation(img_size= obj[0].size, labels=sly_labels,image_id= i)
        ann_json = sly_ann.to_json()
        ann_path_json = os.path.join(os.path.join('output_sly','ann'), obj[0].name +'.json')
        sly.json.dump_json_file(ann_json, ann_path_json)
        i+=1
    print('DONE')
