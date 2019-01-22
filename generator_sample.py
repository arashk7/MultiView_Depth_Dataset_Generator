import bpy
import sys
import os.path
import math

C = bpy.context
D = bpy.data
scene = D.scenes['Scene']
# Output resolution (Stereoscopic images & depthmap)
bpy.context.scene.render.resolution_x = 150
bpy.context.scene.render.resolution_y = 100

# Total number of set of stereoscopic images and depth maps
total_scene_number = 10

cameras = [
    (60, 0), (60, 30), (60, 60), (60, 90)
    # ,(60, 120), (60, 150), (60, 180), (60, 210), (60, 240), (60, 270), (60, 300), (60, 330)
]


###################################
# Start iteration to generate scenes
###################################


def load_model(path):
    d = os.path.dirname(path)
    ext = path.split('.')[-1]

    name = os.path.basename(path).split('.')[0]
    # handle weird object naming by Blender for stl files
    if ext == 'stl':
        name = name.title().replace('_', ' ')

    if name not in D.objects:
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


def center_model(name):
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    D.objects[name].location = (0, 0, 0)


def normalize_model(name):
    obj = D.objects[name]
    dim = obj.dimensions
    print('original dim:' + str(dim))
    if max(dim) > 0:
        dim = dim / max(dim)
    obj.dimensions = dim

    print('new dim:' + str(dim))


def init_camera():
    cam = D.objects['Camera']
    # select the camera object
    scene.objects.active = cam
    cam.select = True

    # set the rendering mode to orthogonal and scale
    C.object.data.type = 'ORTHO'
    C.object.data.ortho_scale = 1.2


def fix_camera_to_origin():
    origin_name = 'Origin'

    # create origin
    try:
        origin = D.objects[origin_name]
    except KeyError:
        bpy.ops.object.empty_add(type='SPHERE')
        D.objects['Empty'].name = origin_name
        origin = D.objects[origin_name]

    origin.location = (0, 0, 0)

    cam = D.objects['Camera']
    scene.objects.active = cam
    cam.select = True

    if 'Track To' not in cam.constraints:
        bpy.ops.object.constraint_add(type='TRACK_TO')

    cam.constraints['Track To'].target = origin
    cam.constraints['Track To'].track_axis = 'TRACK_NEGATIVE_Z'
    cam.constraints['Track To'].up_axis = 'UP_Y'


def move_camera(coord):
    def deg2rad(deg):
        return deg * math.pi / 180.

    r = 3.
    theta, phi = deg2rad(coord[0]), deg2rad(coord[1])
    loc_x = r * math.sin(theta) * math.cos(phi)
    loc_y = r * math.sin(theta) * math.sin(phi)
    loc_z = r * math.cos(theta)

    D.objects['Camera'].location = (loc_x, loc_y, loc_z)


def save(image_dir, name):
    path = os.path.join(image_dir, name + '.png')
    D.images['Render Result'].save_render(filepath=path)
    print('save to ' + path)


def main():
    argv = sys.argv
    argv = argv[argv.index('--') + 1:]

    if len(argv) != 2:
        print('phong.py args: <3d mesh path> <image dir>')
        exit(-1)

    model = argv[0]
    image_dir = argv[1]

    init_camera()
    fix_camera_to_origin()

    name = load_model(model)
    center_model(name)
    normalize_model(name)
    image_subdir = os.path.join(image_dir, name)
    ii = 0

    # Load model
    name = load_model(model)
    center_model(name)
    normalize_model(name)
    mat1 = bpy.data.materials.new("Mat1")
    mat1.diffuse_color = 0.2, 0.2, 0.2


    # bpy.ops.material.new()
    # mat1 = bpy.data.materials['Mat1']
    # mat1.diffuse_color = (0.5, 0.5, 0.5)
    #
    # bpy.data.objects[name].data.materials.append(mat1)

    for ii, c in enumerate(cameras):
        # # Clear data from previous scenes
        # for material in bpy.data.materials:
        #     material.user_clear();
        #     bpy.data.materials.remove(material);
        #
        # for texture in bpy.data.textures:
        #     texture.user_clear();
        #     bpy.data.textures.remove(texture);

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # # clear default nodes
        # for n in tree.nodes:
        #     tree.nodes.remove(n)

        # setup lighting:
        # light = bpy.data.objects['Lamp']
        # light.data.use_shadow = False
        # light.data.energy = 3.0
        # light.select = False

        # setup camera:
        cam = D.objects['Camera']
        move_camera(c)
        # camera = D.objects['Camera']
        cam.select = True
        # camera.rotation_mode = 'XYZ'
        # angle1 = 1.3 + (0.5 - rand.random()) * 1
        # angle2 = (0.5 - rand.random()) * 1
        # angle3 = 0.75 + (0.5 - rand.random()) * 1
        # camera.rotation_euler = (angle1, angle2, angle3)
        # Cam_x = 10 + (0.5 - rand.random()) * 2
        # Cam_y = -3 + (0.5 - rand.random()) * 2
        # Cam_z = 3 + (0.5 - rand.random()) * 2
        # camera.location = (Cam_x, Cam_y, Cam_z)
        # cam.data.stereo.convergence_distance = 10000
        # cam.data.lens = 100  # (focal length)
        # cam.data.stereo.interocular_distance = 0.3
        # dist = ((camera.location[0] - (-3.22)) ** (2) + (camera.location[1] - (8.0)) ** (2) + (
        #         camera.location[2] - (-5.425)) ** (2)) ** (1 / 2)
        cam.select = False

        # Remove objects from previsous scenes
        # for item in bpy.data.objects:
        #     if item.type == "MESH":
        #         bpy.data.objects[item.name].select = True
        #         bpy.ops.object.delete()
        #
        # for item in bpy.data.meshes:
        #     bpy.data.meshes.remove(item)

        ##################
        # Create new scene:
        ##################

        scene = bpy.context.scene
        scene.render.use_multiview = True
        # scene.render.views_format = 'STEREO_3D'
        rl = tree.nodes.new(type="CompositorNodeRLayers")
        composite = tree.nodes.new(type="CompositorNodeComposite")
        # composite.location = 300, 0

        scene = bpy.context.scene

        # setup the depthmap calculation using blender's mist function:
        # scene.render.layers['RenderLayer'].use_pass_mist = True
        # the depthmap can be calculated as the distance between objects and camera ('LINEAR'), or square/inverse square of the distance ('QUADRATIC'/'INVERSEQUADRATIC'):
        scene.world.mist_settings.falloff = 'LINEAR'
        # minimum depth:
        scene.world.mist_settings.intensity = 0

        # maximum depth (can be changed depending on the scene geometry to normalize the depth map whatever the camera orientation and position is):
        dist = ((cam.location[0] - 0) ** (2) + (cam.location[1] - 0) ** (2) + (
                cam.location[2] - 0) ** (2)) ** (1 / 2)
        scene.world.mist_settings.depth = dist
        print("dist: " + str(dist))

        # magnitude of the random variation of object placements:

        # create input render layer node

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


        #################
        # Render the scene
        #################

        # ouput the depthmap:
        links.new(invert.outputs[0], composite.inputs['Image'])

        scene.render.use_multiview = False

        bpy.ops.render.render(write_still=True)
        save(image_subdir, 'depth/%s.%d' % (name, ii))
        # scene.render.filepath = image_subdir+'/DepthMap_' + str(ii) + '.png'

        # output the stereoscopic images:
        links.new(rl.outputs['Image'], composite.inputs['Image'])

        scene.render.use_multiview = True
        bpy.ops.render.render(write_still=True)
        save(image_subdir, 'stereo/%s.%d' % (name, ii))
        # scene.render.filepath = image_subdir+'/Stereoscopic_' + str(ii) + '.png'


if __name__ == '__main__':
    main()
