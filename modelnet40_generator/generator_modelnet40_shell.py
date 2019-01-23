import os

modelnet40_dir = "E:\Dataset\ModelNet40\ModelNet40"
modelnet40_multiview_dir = "E:\Dataset\ModelNet40\ModelNet40_multiview"

list_cat = os.listdir(modelnet40_dir)

for category in list_cat:
    in_dir = modelnet40_dir + '/' + category + '/test'
    out_dir = modelnet40_multiview_dir + '/' + category + '/test'
    list_files = os.listdir(in_dir)
    for f in list_files:
        ext = f.split('.')[-1]
        if ext == 'off':
            in_path = in_dir + '/' + f
            cmd = 'Blender ../scene.blend --background --python ../multiview_gen.py -- ' + in_path + ' ' + out_dir + ' 0'
            os.system(cmd)

    in_dir = modelnet40_dir + '/' + category + '/train'
    out_dir = modelnet40_multiview_dir + '/' + category + '/train'
    list_files = os.listdir(in_dir)
    for f in list_files:
        ext = f.split('.')[-1]
        if ext == 'off':
            in_path = in_dir + '/' + f
            cmd = 'Blender ../scene.blend --background --python ../multiview_gen.py -- ' + in_path + ' ' + out_dir + ' 0'
            os.system(cmd)
