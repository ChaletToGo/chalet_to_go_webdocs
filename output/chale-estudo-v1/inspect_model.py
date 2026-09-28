import bpy, json, math
from mathutils import Vector
from pathlib import Path
OUT=Path(r'C:/Users/rafae/Documents/chalet_to_go_webdocs/output/chale-estudo-v1')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r'D:/Cursos/Meshy_AI_Exploded_Tiny_House_T_0915232056_generate.glb')
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.context.view_layer.objects.active=obj
obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
data=[]
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  coords=[o.matrix_world@Vector(c) for c in o.bound_box]
  data.append({'name':o.name,'faces':len(o.data.polygons),'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]})
(OUT/'mesh-inspection.json').write_text(json.dumps(data,indent=2))
print('PARTS',len(data),json.dumps(sorted(data,key=lambda d:-d['faces'])[:30]))
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.world=bpy.data.worlds.new('World'); scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.65,.65,1)
bpy.ops.object.camera_add(location=(2.7,-3.5,2.4)); camera=bpy.context.object; camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=2.8; scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(0,-2,4)); bpy.context.object.data.energy=450; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=4
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'mesh-before.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'chale-inspecao.blend'))
bpy.ops.render.render(write_still=True)
