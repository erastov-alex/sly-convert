import os
import shutil
import supervisely as sly
from tqdm import tqdm
from dotenv import load_dotenv
from supervisely.io.json import load_json_file


def upload(
        delete = False,
        api=None, 
        WORKSPACE_ID=None, 
        proj_name=None, 
        progress_bar=None):
    if not api:
        path_advanced = os.path.expanduser("~\\env\\advanced.env")
        path_local = os.path.expanduser("~\\env\\local.env")
        path_supervisely = os.path.expanduser("~\\env\\supervisely.env")
        if sly.is_production():
            load_dotenv(path_advanced)
        else:
            load_dotenv(path_local)
        load_dotenv(os.path.expanduser(path_supervisely ))
        # Get ENV variables
        WORKSPACE_ID = sly.env.workspace_id()
        # Create api object to communicate with Supervisely Server
        api = sly.Api.from_env()
        # Initialize application
        app = sly.Application()
    input_name = proj_name
    # Create project and dataset on Supervisely server
    project = api.project.create(WORKSPACE_ID, input_name , change_name_if_conflict=True)
    dataset = api.dataset.create(project.id, "ds0", change_name_if_conflict=True)
    project_id = project.id
    path_to_meta = os.path.join("output_sly","meta.json")
    project_meta_json = load_json_file(path_to_meta)
    api.project.update_meta(project_id, project_meta_json)
    images_names = []
    images_paths = []
    for file in os.listdir(os.path.join('output_sly','img')):
        if isinstance(file, bytes):
            file = file.decode()
        file_path = os.path.join(os.path.join('output_sly','img'), file)
        images_names.append(file)
        images_paths.append(file_path)
    ann_names = []
    ann_paths = []
    for file in os.listdir(os.path.join('output_sly','ann')):
        if isinstance(file, bytes):
            file = file.decode()
        file_path = os.path.join(os.path.join('output_sly','ann'), file)
        ann_names.append(file)
        ann_paths.append(file_path)
    images_names.sort()
    images_paths.sort()
    ann_paths.sort()
    if not progress_bar:
        progress_bar = tqdm
    #Process folder with images and upload them to Supervisely server
    with progress_bar(total=len(images_paths)) as pbar:
        for img_name, img_path, ann_path in zip(images_names, images_paths, ann_paths):
            try:
                # Upload image and annotation into dataset on Supervisely server
                info = api.image.upload_path(dataset_id=dataset.id, name=img_name, path=img_path)
                sly.logger.trace(f"Image has been uploaded: id={info.id}, name={info.name}")
                inf_ann = api.annotation.upload_path(img_id= info.id, ann_path=ann_path)
                sly.logger.trace(f"Annotation has been uploaded")
            except Exception as e:
                sly.logger.warn("Skip image", extra={"name": img_name, "reason": repr(e)})
                shutil.rmtree("output_sly")
                shutil.rmtree("input")
            finally:
                # Update progress bar
                pbar.update(1)
    sly.logger.info(f"Result project: id={project.id}, name={project.name}")
    if delete:
        shutil.rmtree("output_sly")
        shutil.rmtree("input")
        return
    if input('Success! Delete local output? \n     [y] for yes\n     [n] for no\n') == 'y':
        shutil.rmtree("output_sly")
        shutil.rmtree("input")
    pass
