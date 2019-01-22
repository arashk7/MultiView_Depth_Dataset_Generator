import bpy
import sys
import os.path
import math


class Multiview_Gen:
    def __init__(self, width=150, height=100, is_rotated=0):
        self.width = width
        self.height = height
        self.is_rotated = is_rotated
        self.D = bpy.data
        self.C = bpy.context

        self.scene = self.D.scenes['Scene']
        # Output resolution (Stereoscopic images & depthmap)
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height

    def release_all(self):
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        for texture in bpy.data.textures:
            texture.user_clear()
            bpy.data.textures.remove(texture)

        # Remove objects from previsous scenes
        for item in bpy.data.objects:
            if item.type == "MESH":
                bpy.data.objects[item.name].select = True
                bpy.ops.object.delete()

        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)

    def init(self, model_name, image_dir):

        self.init_camera()
        self.fix_camera_to_origin()

        # Load model
        self.name = self.load_model(model_name)
        self.center_model(self.name)
        self.normalize_model(self.name)
        self.image_subdir = os.path.join(image_dir, self.name)

    def center_model(self, name):
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
        self.D.objects[name].location = (0, 0, 0)
        # def deg2rad(deg):
        #     return deg * math.pi / 180.
        if self.is_rotated == 1:
            ang = 1.5708
        else:
            ang = 0
        bpy.ops.transform.rotate(value=ang, axis=(1, 0, 0), constraint_axis=(True, False, False),
                                 constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                 proportional_edit_falloff='SMOOTH', proportional_size=1)

    def normalize_model(self, name):
        obj = self.D.objects[name]
        dim = obj.dimensions
        print('original dim:' + str(dim))
        if max(dim) > 0:
            dim = dim / max(dim)
        obj.dimensions = dim
        print('new dim:' + str(dim))

    def init_camera(self):
        cam = self.D.objects['Camera']
        # select the camera object
        self.scene.objects.active = cam
        cam.select = True

        # set the rendering mode to orthogonal and scale
        self.C.object.data.type = 'ORTHO'
        self.C.object.data.ortho_scale = 1.4

    def fix_camera_to_origin(self):
        origin_name = 'Origin'

        # create origin
        try:
            origin = self.D.objects[origin_name]
        except KeyError:
            bpy.ops.object.empty_add(type='SPHERE')
            self.D.objects['Empty'].name = origin_name
            origin = self.D.objects[origin_name]

        origin.location = (0, 0, 0)

        cam = self.D.objects['Camera']
        self.scene.objects.active = cam
        cam.select = True

        if 'Track To' not in cam.constraints:
            bpy.ops.object.constraint_add(type='TRACK_TO')

        cam.constraints['Track To'].target = origin
        cam.constraints['Track To'].track_axis = 'TRACK_NEGATIVE_Z'
        cam.constraints['Track To'].up_axis = 'UP_Y'

    def move_camera(self, coord):
        def deg2rad(deg):
            return deg * math.pi / 180.

        r = 3.
        theta, phi = deg2rad(coord[0]), deg2rad(coord[1])
        loc_x = r * math.sin(theta) * math.cos(phi)
        loc_y = r * math.sin(theta) * math.sin(phi)
        loc_z = r * math.cos(theta)

        self.D.objects['Camera'].location = (loc_x, loc_y, loc_z)

    def load_model(self, path):
        d = os.path.dirname(path)
        ext = path.split('.')[-1]

        name = os.path.basename(path).split('.')[0]
        # handle weird object naming by Blender for stl files
        if ext == 'stl':
            name = name.title().replace('_', ' ')

        if name not in self.D.objects:
            print('loading :' + name)
            if ext == 'stl':
                bpy.ops.import_mesh.stl(filepath=path, directory=d,
                                        filter_glob='*.stl')
            elif ext == 'off':
                bpy.ops.import_mesh.off(filepath=path, filter_glob='*.off')
            elif ext == 'obj':
                bpy.ops.import_scene.obj(filepath=path, filter_glob='*.obj')
            else:
                print('Currently .{} file type is not supported.'.format(ext))
                exit(-1)
        return name

    def save(self, image_dir, name):
        path = os.path.join(image_dir, name + '.png')
        self.D.images['Render Result'].save_render(filepath=path)
        print('save to ' + path)

    def render(self, cameras):
        for ii, c in enumerate(cameras):
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            links = tree.links
            self.move_camera(c)

            # create scene
            rl = tree.nodes.new(type="CompositorNodeRLayers")
            composite = tree.nodes.new(type="CompositorNodeComposite")

            #################
            # Render the scene
            #################
            map = tree.nodes.new(type="CompositorNodeMapValue")
            # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
            map.size = [0.29]
            map.use_min = True
            map.min = [0]
            map.use_max = True
            map.max = [1.5]
            links.new(rl.outputs[2], map.inputs[0])

            invert = tree.nodes.new(type="CompositorNodeInvert")
            links.new(map.outputs[0], invert.inputs[1])

            # ouput the depthmap:
            links.new(invert.outputs[0], composite.inputs['Image'])

            bpy.ops.render.render(write_still=True)
            self.save(self.image_subdir, 'depth_%d' % (ii))
            # scene.render.filepath = image_subdir+'/DepthMap_' + str(ii) + '.png'

            # output the stereoscopic images:
            links.new(rl.outputs['Image'], composite.inputs['Image'])

            bpy.ops.render.render(write_still=True)
            self.save(self.image_subdir, 'view_%d' % (ii))


def main():
    argv = sys.argv
    argv = argv[argv.index('--') + 1:]

    if len(argv) < 2 or len(argv) > 3:
        print('multiview_gen.py args: <3d mesh path> <image dir> <is_rotated_view (1 or 0)>')
        exit(-1)

    model = argv[0]
    image_dir = argv[1]
    is_rotated = 0
    if len(argv) > 2:
        is_rotated = int(argv[2])

    # spherical pos
    cameras = [
        (60, 0), (60, 30), (60, 60), (60, 90)
        , (60, 120), (60, 150),
        (60, 180), (60, 210), (60, 240), (60, 270), (60, 300), (60, 330)
    ]

    ext = model.split('.')[-1]
    print(ext)
    if ext == 'off':
        mvg = Multiview_Gen(300, 300, is_rotated)
        mvg.init(model_name=model, image_dir=image_dir)
        mvg.render(cameras)
        del mvg
    elif ext == 'txt':
        with open(model) as f:
            models = f.read().splitlines()
        for model in models:
            mvg = Multiview_Gen(300, 300, is_rotated)
            mvg.init(model_name=model, image_dir=image_dir)
            mvg.render(cameras)
            mvg.release_all()
            mvg = None
            del mvg

    elif ext == model:

        list_files = os.listdir(model)
        for f in list_files:
            ext2 = f.split('.')[-1]
            if ext2 == 'off':
                mvg = Multiview_Gen(300, 300, is_rotated)
                mvg.release_all()
                mvg.init(model_name=model + '/' + f, image_dir=image_dir)
                mvg.render(cameras)
                mvg.release_all()
                mvg = None
                del mvg


if __name__ == '__main__':
    main()
