import os

modelnet10_dir = "D:\Dataset\ModelNet10\ModelNet10"
modelnet10_multiview_dir = "D:\Dataset\ModelNet10\ModelNet10_multiview"
list_cat = {'bathtub', 'bed', 'chair', 'desk', 'dresser', 'monitor', 'night_stand', 'sofa', 'table', 'toilet'}

for category in list_cat:
    in_dir = modelnet10_dir + '/' + category + '/test'
    out_dir = modelnet10_multiview_dir + '/' + category + '/test'
    list_files = os.listdir(in_dir)
    for f in list_files:
        ext = f.split('.')[-1]
        if ext == 'off':
            in_path = in_dir + '/' + f
            cmd = 'Blender ../scene.blend --background --python ../multiview_gen.py -- ' + in_path + ' ' + out_dir + ' 0'
            os.system(cmd)

    in_dir = modelnet10_dir + '/' + category + '/train'
    out_dir = modelnet10_multiview_dir + '/' + category + '/train'
    list_files = os.listdir(in_dir)
    for f in list_files:
        ext = f.split('.')[-1]
        if ext == 'off':
            in_path = in_dir + '/' + f
            cmd = 'Blender ../scene.blend --background --python ../multiview_gen.py -- ' + in_path + ' ' + out_dir + ' 0'
            os.system(cmd)
