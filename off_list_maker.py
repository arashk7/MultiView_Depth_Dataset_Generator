import os


off_dir = "D:\Dataset\ModelNet10\ModelNet10/bathtub/train"
list_files = os.listdir(off_dir)

ply_file = open("output.txt", "w")
for f in list_files:
    ply_file.write(off_dir+'/'+f+'\n')

ply_file.close()