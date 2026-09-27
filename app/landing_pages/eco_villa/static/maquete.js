import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { BASIC, buildBasicChalet } from './basic-chalet.js';

// Concept dimensions in metres, not a surveyed site or a confirmed Basic unit.
export const LAYOUT = Object.freeze({ width: 52, depth: 24, cabinWidth: BASIC.width, cabinDepth: BASIC.depth, cabinHeight: BASIC.ridge, cabinCenters: [-20, -12, -4, 4, 12, 20], cabinZ: -3.6 });
const $ = selector => document.querySelector(selector);
const viewport = $('#viewport');
const landingMode = viewport.dataset.landing === 'true';
const sceneDayColor = getComputedStyle(document.body).getPropertyValue('--villa-scene-background').trim() || '#e5e9df';
const scene = new THREE.Scene();
scene.background = new THREE.Color(sceneDayColor);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'low-power' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.7));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
viewport.append(renderer.domElement);
renderer.domElement.setAttribute('role', 'img');
renderer.domElement.setAttribute('aria-label', 'Maquete dos seis chalés Basic fixos no chão. Use os botões para selecionar uma unidade e mudar a vista, ou arraste para girar.');
const camera = new THREE.PerspectiveCamera(39, 1, .1, 320);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enabled = !landingMode;
if (landingMode) renderer.domElement.style.touchAction = 'pan-y';
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 8;
controls.maxDistance = 240;
controls.maxPolarAngle = Math.PI * .48;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const ambient = new THREE.HemisphereLight(0xfff9e6, 0x647159, 2.4);
const sun = new THREE.DirectionalLight(0xffedcf, 3.2);
sun.position.set(-12, 25, 14); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -36, right: 36, top: 30, bottom: -30, near: 1, far: 90 });
sun.shadow.bias = -.0005;
scene.add(ambient, sun);
const world = new THREE.Group(); scene.add(world);
const material = (color, options = {}) => new THREE.MeshStandardMaterial({ color, roughness: .85, ...options });
const palette = {
 grass: material('#81916a'), soil: material('#78644c'), timber: material('#a37649'), trim: material('#313d38'),
 roof: material('#424c48', { metalness: .25, roughness: .6 }), path: material('#b9b5a2'), gravel: material('#aaa695'),
 cream: material('#e5dfcb'), fabric: material('#c6c3ab'), leaf: material('#405c3c'), leafLight: material('#6d8151'),
 glass: material('#a0c0bb', { transparent: true, opacity: .19, roughness: .15, depthWrite: false }),
 light: material('#ffe2a1', { emissive: '#ffc15e', emissiveIntensity: .6 }), water: material('#dddcd0'),
};
const unitGeo = new THREE.BoxGeometry(1, 1, 1);
const foliageGeo = new THREE.IcosahedronGeometry(1, 1);
const roofs = [], upperWalls = [], lofts = [], cabins = [], targets = [], lamps = [];
function box(parent, mat, x, y, z, w, h, d) {
 const mesh = new THREE.Mesh(unitGeo, mat); mesh.position.set(x,y,z); mesh.scale.set(w,h,d);
 mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function cylinder(parent, mat, x,y,z, radius, height, segments = 16) {
 const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,height,segments),mat);
 mesh.position.set(x,y,z); mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function bush(x,z,size=1) {
 const mesh = new THREE.Mesh(foliageGeo, ((Math.round(x*11+z*7)&1) ? palette.leaf : palette.leafLight));
 mesh.position.set(x,.35+size*.45,z); mesh.scale.set(size*.7,size*.65,size*.65); world.add(mesh); mesh.castShadow=true;
}
function tree(x,z,size) {
 cylinder(world,palette.timber,x,size*.6,z,.12,size*1.2,6);
 const mesh = new THREE.Mesh(foliageGeo,palette.leaf); mesh.position.set(x,size*1.2,z); mesh.scale.set(size*.65,size*.82,size*.65); world.add(mesh); mesh.castShadow=true;
}
box(world,palette.soil,0,-.45,0,LAYOUT.width,.8,LAYOUT.depth);
box(world,palette.grass,0,-.01,0,LAYOUT.width,.12,LAYOUT.depth);
box(world,palette.gravel,0,.07,7.6,49,.12,5.5);
box(world,palette.path,-24.8,.12,0,1.2,.12,23.8);
box(world,palette.path,0,.14,4,50,.12,1);
for(let x=-25;x<=25;x+=1.5) { bush(x,-11.3,.8); if(Math.abs(x)>3) bush(x,11.3,.6); }
for(let z=-10;z<=10;z+=1.6) { bush(25.3,z,.8); bush(-25.7,z,.5); }
for (const x of [-23.5,-16,-8,0,8,16,23.5]) {
 for(let z=-9;z<3;z+=1.3) bush(x,z,.65);
 tree(x,-10.2,1.8); tree(x,2.3,1.35);
}
function chair(parent,x,z,rotation=0) {
 const g = new THREE.Group(); g.position.set(x,0,z); g.rotation.y=rotation; parent.add(g);
 box(g,palette.timber,0,.48,0,.68,.13,.65); box(g,palette.cream,0,.59,0,.55,.12,.52);
 box(g,palette.timber,0,.92,-.28,.68,.75,.1);
 for(const a of [-.25,.25]) for(const b of [-.22,.22]) box(g,palette.trim,a,.24,b,.06,.45,.06);
}
function cabin(x,index) {
 const basic = buildBasicChalet(palette);
 const g = basic.root; g.position.set(x,.16,LAYOUT.cabinZ); g.userData.unit=index;
 world.add(g); cabins.push(g); roofs.push(basic.roof); upperWalls.push(basic.shell); lofts.push(basic.loft);
 for(let z=2.9;z<3.7;z+=.5) box(world,palette.path,x,.14,z,.85,.12,.36);
 const hit = box(g,new THREE.MeshBasicMaterial({visible:false}),0,BASIC.ridge/2,0,BASIC.width,BASIC.ridge,BASIC.depth);
 targets.push(hit);
}
LAYOUT.cabinCenters.forEach(cabin);
// Central gathering space, facing seats, four stylized parked cars.
cylinder(world,palette.path,0,.16,7,2.3,.15,48);
cylinder(world,palette.trim,0,.42,7,.7,.45,24);
cylinder(world,palette.soil,0,.67,7,.55,.08,24);
const fire = new THREE.Mesh(new THREE.ConeGeometry(.31,.7,7),palette.light); fire.position.set(0,.95,7); world.add(fire);
const fireLight = new THREE.PointLight(0xffa34a,0,7,2); fireLight.position.set(0,1.5,7); scene.add(fireLight);
for(let i=0;i<6;i++) { const a=i*Math.PI/3; chair(world,Math.sin(a)*1.72,7+Math.cos(a)*1.72,a); }
for(const [i,x] of [-20,-12,12,20].entries()) {
 const g=new THREE.Group();g.position.set(x,0,7);world.add(g);
 const paint=material(i%2?'#d4d4c7':'#384b4e',{metalness:.3,roughness:.35});
 box(g,paint,0,.75,0,1.6,.65,3.7);box(g,palette.trim,0,1.25,-.15,1.4,.6,2);
 box(g,paint,0,1.57,-.15,1.42,.1,1.5);
 for(const a of [-.81,.81]) for(const b of [-1.2,1.2]) {const tire=cylinder(g,palette.trim,a,.45,b,.35,.18,12);tire.rotation.z=Math.PI/2;}
 box(world,palette.cream,x-1.08,.16,7,.045,.02,4.5);
}
for(let x=-23;x<=23;x+=3) {
 cylinder(world,palette.trim,x,.38,3.3,.06,.65,6);
 const lamp=cylinder(world,palette.light,x,.73,3.3,.11,.12,8); lamps.push(lamp);
}
const selectionRing = new THREE.Mesh(new THREE.RingGeometry(1,1.025,64),new THREE.MeshBasicMaterial({color:'#c69655',side:THREE.DoubleSide}));
selectionRing.rotation.x=-Math.PI/2;selectionRing.scale.set(2.7,4.9,1);selectionRing.position.y=.19;selectionRing.visible=false;world.add(selectionRing);
let selected=null, tween=null, raf=0, visible=true, night=false;
const views={overview:[-30,33,44],top:[0,65,.01],front:[0,14,63]};
function invalidate(){if(!raf&&visible&&!document.hidden)raf=requestAnimationFrame(frame);}
function move(position,target){
 tween={from:camera.position.clone(),to:new THREE.Vector3(...position),targetFrom:controls.target.clone(),targetTo:new THREE.Vector3(...target),start:performance.now()};
 if(reducedMotion.matches){camera.position.copy(tween.to);controls.target.copy(tween.targetTo);tween=null;controls.update();}
 invalidate();
}
function markView(name){document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));}
function overview(name='overview'){
 selected=null;selectionRing.visible=false;markView(name);
 document.querySelectorAll('[data-unit]').forEach(b=>b.setAttribute('aria-pressed','false'));
 $('#selection-kicker').textContent='A VILLA';$('#selection-title').textContent='Um conjunto acolhedor.';
 $('#selection-description').textContent='Selecione um chalé Basic para se aproximar e conhecer seus ambientes.';
 $('#view-label').textContent=({overview:'VISTA GERAL',top:'VISTA SUPERIOR',front:'FACHADAS'})[name];
 // Fit the full plot even in a narrow, portrait viewport.
 const scale=Math.max(1,1.2/camera.aspect);
 move(views[name].map(n=>n*scale),[0,0,0]);
}
function select(index){
 selected=index;const x=LAYOUT.cabinCenters[index];selectionRing.visible=true;selectionRing.position.set(x,.19,LAYOUT.cabinZ);markView('');
 document.querySelectorAll('[data-unit]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.unit)===index)));
 $('#selection-kicker').textContent='SEU REFÚGIO';$('#selection-title').textContent=`Basic 0${index+1}`;
 $('#selection-description').textContent='Dormitório no mezanino, sala e cozinha no térreo e banheiro ao fundo. Base fixa no chão. Explore os dois níveis em “Ver interiores”.';
 $('#view-label').textContent=`CHALÉ BASIC 0${index+1}`;
 const distance=camera.aspect<1?1.45:1;move([x-9*distance,10*distance,LAYOUT.cabinZ+14*distance],[x,0,LAYOUT.cabinZ]);
}
document.querySelectorAll('[data-unit]').forEach(b=>b.addEventListener('click',()=>select(Number(b.dataset.unit))));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>overview(b.dataset.view)));
$('#reset').addEventListener('click',()=>overview());
$('#cutaway').addEventListener('click',()=>{
 const open=$('#cutaway').getAttribute('aria-pressed')!=='true';
 $('.viewer').classList.toggle('cutaway',open);
 roofs.forEach(o=>o.visible=!open);upperWalls.forEach(o=>o.visible=!open);
 lofts.forEach(o=>o.visible=true);$('#loft').hidden=!open;$('#loft').setAttribute('aria-pressed','false');$('#loft').textContent='Ver térreo';
 $('#cutaway').setAttribute('aria-pressed',String(open));$('#cutaway').textContent=open?'Recolocar telhados':'Ver interiores';invalidate();
});
$('#loft').addEventListener('click',()=>{
 const hidden=$('#loft').getAttribute('aria-pressed')!=='true';
 lofts.forEach(o=>o.visible=!hidden);$('#loft').setAttribute('aria-pressed',String(hidden));$('#loft').textContent=hidden?'Mostrar mezanino':'Ver térreo';invalidate();
});
$('#night').addEventListener('click',()=>{
 night=!night;$('.viewer').classList.toggle('dusk',night);$('#night').setAttribute('aria-pressed',String(night));$('#night').textContent=night?'Voltar à luz do dia':'Luz do entardecer';
 scene.background.set(night?'#344a4b':sceneDayColor);ambient.intensity=night?1.2:2.4;sun.intensity=night?1.6:3.2;
 sun.color.set(night?'#ffb36a':'#ffedcf');palette.light.emissiveIntensity=night?3:.6;fireLight.intensity=night?18:0;invalidate();
});
function zoom(factor){tween=null;const offset=camera.position.clone().sub(controls.target);offset.setLength(THREE.MathUtils.clamp(offset.length()*factor,controls.minDistance,controls.maxDistance));camera.position.copy(controls.target).add(offset);controls.update();invalidate();}
$('#zoom-in').addEventListener('click',()=>zoom(.8));$('#zoom-out').addEventListener('click',()=>zoom(1.25));
if(!document.fullscreenEnabled)$('#fullscreen').hidden=true;
$('#fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('.viewer').requestFullscreen();}catch{ $('#fullscreen').hidden=true; }});
document.addEventListener('fullscreenchange',()=>$('#fullscreen').setAttribute('aria-label',document.fullscreenElement?'Sair da tela cheia':'Abrir em tela cheia'));
controls.addEventListener('start',()=>{tween=null;});controls.addEventListener('change',invalidate);
let down=null;const raycaster=new THREE.Raycaster();
renderer.domElement.addEventListener('pointerdown',e=>{down=e.isPrimary?{x:e.clientX,y:e.clientY}:null;});
renderer.domElement.addEventListener('pointercancel',()=>{down=null;});
renderer.domElement.addEventListener('pointerup',e=>{
 if(!controls.enabled){down=null;return;}
 if(!down||Math.hypot(e.clientX-down.x,e.clientY-down.y)>6){down=null;return;} down=null;
 const rect=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);
 const hit=raycaster.intersectObjects(targets,false)[0];if(hit)select(hit.object.parent.userData.unit);
});
function resize(){
 const w=viewport.clientWidth,h=viewport.clientHeight;if(!w||!h)return;
 camera.aspect=w/h;
 // Keep the first chalet clear of the information card on wide screens.
 if(w>800)camera.setViewOffset(w,h,-Math.min(110,w*.085),0,w,h);else camera.clearViewOffset();
 camera.updateProjectionMatrix();renderer.setSize(w,h);invalidate();
}
new ResizeObserver(resize).observe(viewport);
new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)invalidate();}).observe(viewport);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)invalidate();});
renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();viewport.classList.remove('ready');renderer.domElement.style.display='none';window.dispatchEvent(new Event('villa-viewer-error'));});
function frame(now){
 raf=0;if(!visible||document.hidden)return;
 if(tween){const t=Math.min((now-tween.start)/750,1),ease=1-Math.pow(1-t,3);camera.position.lerpVectors(tween.from,tween.to,ease);controls.target.lerpVectors(tween.targetFrom,tween.targetTo,ease);if(t===1)tween=null;}
 const changed=controls.update();renderer.render(scene,camera);if(tween||changed)invalidate();
}
if (landingMode) {
 let exploring = false;
 window.addEventListener('villa:explore', event => {
  exploring = Boolean(event.detail.enabled);
  controls.enabled = exploring;
  renderer.domElement.style.touchAction = exploring ? 'none' : 'pan-y';
  if (!exploring) {
   if ($('#cutaway').getAttribute('aria-pressed') === 'true') $('#cutaway').click();
   if (night) $('#night').click();
  }
  overview();
 });
 window.addEventListener('villa:scroll', event => {
  if (exploring) return;
  const progress = reducedMotion.matches ? 0 : THREE.MathUtils.clamp(event.detail.progress, 0, 1);
  const start = new THREE.Vector3(...views.overview);
  const end = new THREE.Vector3(-5, 55, 40);
  const scale = Math.max(1, 1.2 / camera.aspect) * 1.16;
  tween = null;
  camera.position.copy(start.lerp(end, progress * progress * (3 - 2 * progress)).multiplyScalar(scale));
  controls.target.set(0,0,0);controls.update();invalidate();
 });
}
resize();camera.position.set(...views.overview);controls.target.set(0,0,0);controls.update();overview();
$('#loading').hidden=true;viewport.classList.add('ready');invalidate();
window.dispatchEvent(new Event('villa:ready'));
