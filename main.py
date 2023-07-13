import ds_manager
import os

# for folder in os.listdir('input'):
#     a = ds_manager.Dataset(data = os.path.join('input', folder))
#     a.root = ds_manager.scan(a)
#     a.dump_sly()
#     a.upload(delete = True)

a = True

a = ds_manager.Dataset()
a.root = ds_manager.scan(a)
a.dump_sly()
a.upload(delete = True)

