import bpy, numpy as np, math
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:/Users/rafae/Documents/chalet_to_go_webdocs/output/chale-estudo-v1')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'chale-inspecao.blend'))
bpy.context.preferences.filepaths.save_version=0
bpy.context.preferences.filepaths.file_preview_type='NONE'
def material(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name); m.use_nodes=True
 m.node_tree.nodes.clear(); bs=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled'); bs.name='Surface'; out=m.node_tree.nodes.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(bs.outputs[0],out.inputs['Surface']); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
 m.diffuse_color=(*color,1); return m
wood=material('Madeira natural | textura incorporada',(.5,.29,.12),0,.56)
metal=material('Cobertura | metal grafite',(.055,.066,.077),.65,.34)
chassis=material('Chassi | aco pintado',(.028,.032,.038),.5,.45)
rubber=material('Pneus | borracha',(.018,.019,.02),0,.84)
N=1024
y,x=np.mgrid[0:N,0:N].astype(np.float32)/N
rng=np.random.default_rng(31)
grain=np.sin(2*np.pi*(y*58+1.4*np.sin(x*7)+.25*np.sin(x*31)))
fine=np.sin(2*np.pi*(y*193+.5*np.sin(x*19)))
tone=.065*grain+.022*fine+.025*rng.normal(size=(N,N))
arr=np.ones((N,N,4),dtype=np.float32)
for i,c in enumerate((.62,.43,.25)): arr[:,:,i]=np.clip(c+tone,0,1)
im=bpy.data.images.new('Madeira_Veios_1024',width=N,height=N)
im.pixels.foreach_set(arr.ravel()); im.filepath_raw=str(OUT/'madeira-veios.png'); im.file_format='PNG'; im.save(); im.pack()
tex=wood.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=im
wood.node_tree.links.new(tex.outputs['Color'],wood.node_tree.nodes['Surface'].inputs['Base Color'])
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:
 old=o.name; me=o.data
 for m in (wood,metal,chassis,rubber): me.materials.append(m)
 uv=me.uv_layers.new(name='UV_Texturas')
 for p in me.polygons:
  c=p.center; n=p.normal
  if old=='mesh_node': p.material_index=2
  elif old=='mesh_node.006' and c.z > .685-.58*abs(c.y)-.022 and n.z>.25: p.material_index=1
  else: p.material_index=0
  axis=max(range(3),key=lambda i:abs(n[i]))
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   a,b=(v.y,v.z) if axis==0 else ((v.x,v.z) if axis==1 else (v.x,v.y))
   uv.data[li].uv=(a*2.2,b*2.2)
 o.name={'mesh_node':'Base e chassi','mesh_node.001':'Paineis estruturais','mesh_node.002':'Piso estrutural','mesh_node.006':'Cobertura e tesouras'}.get(old,'Travessa '+old.rsplit('.',1)[-1])
for o in bpy.context.scene.objects: o.select_set(o.type=='MESH')
scene=bpy.context.scene
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.33,.33,.33,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
scene.view_settings.view_transform='AgX'
scene.cycles.samples=32
scene.render.filepath=str(OUT/'chale-texturizado.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'chale-texturizado.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'chale-texturizado.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
print('EXPORTED_FULL',flush=True)
for o in objects:
 mod=o.modifiers.new('Reducao para web','DECIMATE'); mod.ratio=.45
bpy.ops.export_scene.gltf(filepath=str(OUT/'chale-texturizado-web.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
print('EXPORTED_WEB',flush=True)
for o in objects:
 for mod in list(o.modifiers): o.modifiers.remove(mod)
bpy.ops.render.render(write_still=True)
print('DONE',flush=True)
