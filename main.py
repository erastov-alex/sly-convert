import src
import os

# for folder in os.listdir('input'):
#     a = src.Dataset(data = os.path.join('input', folder))
#     a.root = src.scan(a)
#     a.dump_sly()
#     a.upload(delete = True)



a = src.Dataset()
# a.root = src.scan(a)
# a.dump_sly()
a.upload(delete = False)