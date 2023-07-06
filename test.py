import os


def findby_extension(extension = 'yaml'):
    for rootdir, dirs, files in os.walk('input'):
        for file in files:       
            if((file.split('.')[-1])==extension):
                print(os.path.join('input', file))

findby_extension()