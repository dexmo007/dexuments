import os

def iterfiles(*files):
    for f in files:
        if os.path.isdir(f):
            for root, _, filenames in os.walk(f):
                for filename in filenames: 
                    yield os.path.join(root,filename) 
        else:
            yield f

def is_img(f):
    return os.path.isfile(f) and os.path.splitext(f)[1].lower() in ['.jpg','.jpeg','.png','.gif']