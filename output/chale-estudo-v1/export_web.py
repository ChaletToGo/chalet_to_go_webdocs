import bpy
from pathlib import Path
p=Path(r'C:/Users/rafae/Documents/chalet_to_go_webdocs/output/chale-estudo-v1')
bpy.ops.wm.open_mainfile(filepath=str(p/'chale-texturizado.blend'))
for o in bpy.context.scene.objects:
 o.select_set(o.type=='MESH')
 if o.type=='MESH':
  m=o.modifiers.new('Web 45 por cento','DECIMATE'); m.ratio=.45
bpy.ops.export_scene.gltf(filepath=str(p/'chale-texturizado-web-draco.glb'),export_format='GLB',use_selection=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
