import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = (s) => document.querySelector(s);
const viewport = $('#viewport');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const announce = (text) => { $('#announcement').textContent = text; };
let renderer;
function fail(message) {
  $('#loading').hidden = false;
  $('#loading-title').textContent = 'O estúdio não pôde ser aberto';
  $('#loading-text').textContent = message;
  $('#progress').hidden = true;
  $('#retry').hidden = false;
  document.querySelectorAll('.experience button, .experience input').forEach(el => { if (el.id !== 'retry' && !el.hasAttribute('data-model-id')) el.disabled = true; });
}
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.localClippingEnabled = true;
  viewport.prepend(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'Modelo 3D do chalé. Arraste para girar, use a roda para aproximar. As vistas também estão disponíveis nos botões abaixo.');
  renderer.domElement.setAttribute('role', 'img');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#ecebe5');
  const camera = new THREE.PerspectiveCamera(36, 1, .01, 200);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = .075;
  controls.minDistance = 2;
  controls.maxDistance = 15;
  controls.maxPolarAngle = Math.PI * .49;
  controls.autoRotateSpeed = .65;
  controls.enablePan = false;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room).texture;
  scene.environment = environment;
  room.dispose();
  pmrem.dispose();
  const ambient = new THREE.HemisphereLight(0xfffaf0, 0x6b7564, 2);
  const sun = new THREE.DirectionalLight(0xffefd6, 3);
  sun.position.set(4, 7, 5);
  scene.add(ambient, sun);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(20, 96), new THREE.MeshStandardMaterial({ color: '#e8e8df', roughness: 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -.025;
  scene.add(ground);
  const grid = new THREE.GridHelper(30, 70, 0xcbd0c0, 0xd9dccf);
  grid.position.y = -.02;
  grid.material.transparent = true;
  grid.material.opacity = .32;
  scene.add(grid);
  const clip = new THREE.Plane(new THREE.Vector3(0, -1, 0), 10);
  let model, bounds, height = 3, distance = 7, tween = null, tourTimer = null;
  const materials = new Set();
  const views = { perspective: [1, .65, 1.25], front: [0, .25, 1.6], side: [1.6, .25, 0], top: [0, 1.7, .001] };
  function stopTour() {
    clearInterval(tourTimer); tourTimer = null;
    $('#tour').innerHTML = '<span>▷ &nbsp; Fazer um tour</span><small>4 perspectivas</small>';
    $('#tour').setAttribute('aria-pressed', 'false');
  }
  function setView(name) {
    controls.autoRotate = false; $('#rotate').checked = false;
    const target = new THREE.Vector3(0, height * .45, 0);
    const offset = new THREE.Vector3(...views[name]).normalize().multiplyScalar(distance);
    tween = { start: performance.now(), from: camera.position.clone(), to: target.clone().add(offset), targetFrom: controls.target.clone(), target };
    if (reduced.matches) { camera.position.copy(tween.to); controls.target.copy(target); tween = null; }
    document.querySelectorAll('[data-view]').forEach(b => { b.classList.toggle('active', b.dataset.view === name); b.setAttribute('aria-pressed', String(b.dataset.view === name)); });
  }
  controls.addEventListener('start', () => {
    tween = null; stopTour(); controls.autoRotate = false; $('#rotate').checked = false;
    document.querySelectorAll('[data-view]').forEach(b => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
  });
  function resize() {
    const w = viewport.clientWidth, h = viewport.clientHeight;
    renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
    if (model) {
      const size = bounds.getSize(new THREE.Vector3());
      const vfov = THREE.MathUtils.degToRad(camera.fov);
      const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
      distance = Math.max(size.length() / (2 * Math.sin(Math.min(vfov, hfov) / 2)) * 1.18, 4);
      controls.maxDistance = distance * 2.5;
    }
  }
  new ResizeObserver(resize).observe(viewport);
  resize();
  const loader = new GLTFLoader();
  let loadVersion = 0;
  function disposeModel(root) {
    const textures = new Set(), geometries = new Set(), mats = new Set();
    root.traverse(obj => { if (!obj.isMesh) return; geometries.add(obj.geometry); for (const mat of (Array.isArray(obj.material) ? obj.material : [obj.material])) { mats.add(mat); for (const value of Object.values(mat)) if (value?.isTexture) textures.add(value); } });
    geometries.forEach(x => x.dispose()); mats.forEach(x => x.dispose()); textures.forEach(x => x.dispose());
  }
  function loadModel(button) {
    const url = button?.dataset.modelUrl;
    const version = ++loadVersion;
    stopTour(); tween = null; controls.autoRotate = false; controls.enabled = false;
    $('#rotate').checked = false;
    $('#loading').hidden = false; $('#retry').hidden = true;
    $('#loading-title').textContent = 'Preparando ' + (button?.textContent || 'modelo').toLowerCase();
    $('#loading-text').textContent = 'Carregando modelo 3D…';
    $('#progress').hidden = false; $('#progress').value = 0;
    document.querySelectorAll('.experience button, .experience input').forEach(el => { if (!el.hasAttribute('data-model-id') && el.id !== 'retry') el.disabled = true; });
    document.querySelectorAll('[data-model-id]').forEach(el => { const selected = el === button; el.classList.toggle('selected', selected); el.setAttribute('aria-pressed', String(selected)); });
    if (!url) { fail('Este modelo ainda não está disponível. Selecione outra opção.'); return; }
    const timeout = setTimeout(() => { if (version === loadVersion) { loadVersion++; fail('O carregamento demorou mais que o esperado. Selecione o modelo para tentar novamente.'); } }, 120000);
    loader.load(url, gltf => {
      clearTimeout(timeout);
      if (version !== loadVersion) { disposeModel(gltf.scene); return; }
      try {
        if (model) { scene.remove(model); disposeModel(model); }
        materials.clear(); model = gltf.scene;
        const original = new THREE.Box3().setFromObject(model);
        const size = original.getSize(new THREE.Vector3());
        model.scale.multiplyScalar(3.6 / Math.max(size.x, size.y, size.z));
        bounds = new THREE.Box3().setFromObject(model);
        const center = bounds.getCenter(new THREE.Vector3());
        model.position.sub(new THREE.Vector3(center.x, bounds.min.y, center.z));
        scene.add(model); bounds = new THREE.Box3().setFromObject(model); height = bounds.max.y;
        model.traverse(obj => { if (obj.isMesh) for (const mat of (Array.isArray(obj.material) ? obj.material : [obj.material])) { materials.add(mat); mat.clippingPlanes = [clip]; mat.side = THREE.DoubleSide; mat.wireframe = false; } });
        clip.constant = height + .1;
        $('#wireframe').checked = false; $('#section').value = 100; $('#section-value').textContent = 'Inteiro';
        resize(); camera.position.set(distance, distance * .7, distance); setView('perspective');
        controls.enabled = true; $('#loading').hidden = true;
        document.querySelectorAll('.experience button, .experience input').forEach(el => { el.disabled = el.hasAttribute('data-model-id') && !el.dataset.modelUrl; });
        if (!document.fullscreenEnabled) $('#fullscreen').hidden = true;
        $('#model-caption').textContent = button.dataset.modelId === 'structure' ? 'Estrutura · estudo construtivo em madeira' : 'Exterior · acabamentos e volumetria';
        announce(button.textContent + ' carregado. Explore as vistas e os controles.');
      } catch (error) { console.error(error); fail('Não foi possível preparar este modelo. Selecione outra opção.'); }
    }, event => {
      if (version !== loadVersion) return;
      if (event.total) { const n = Math.round(event.loaded / event.total * 100); $('#progress').value = n; $('#loading-text').textContent = n < 100 ? `Carregando o modelo · ${n}%` : 'Preparando materiais e iluminação…'; }
    }, () => { clearTimeout(timeout); if (version === loadVersion) fail('Não foi possível carregar este modelo. Selecione uma opção para tentar novamente.'); });
  }
  document.querySelectorAll('[data-model-id]').forEach(button => button.onclick = () => loadModel(button));
  loadModel(document.querySelector('[data-model-id="exterior"]'));
  document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => { stopTour(); setView(b.dataset.view); });
  $('#reset').onclick = () => { stopTour(); setView('perspective'); };
  $('#rotate').onchange = (e) => { stopTour(); tween = null; controls.autoRotate = e.target.checked; };
  $('#wireframe').onchange = (e) => { materials.forEach(mat => { mat.wireframe = e.target.checked; }); };
  $('#section').oninput = (e) => { const fraction = Number(e.target.value) / 100; clip.constant = fraction === 1 ? height + .1 : height * fraction; $('#section-value').textContent = fraction === 1 ? 'Inteiro' : `${e.target.value}%`; };
  const atmospheres = {
    studio: { bg: '#ecebe5', ground: '#e8e8df', sun: '#ffefd6', intensity: 3, ambient: 2, exposure: 1.1, env: 1 },
    sunset: { bg: '#e9d3b8', ground: '#d8bd9b', sun: '#ffac59', intensity: 4, ambient: 1.2, exposure: 1.05, env: .6 },
    night: { bg: '#253544', ground: '#304350', sun: '#a6cbff', intensity: 2, ambient: .7, exposure: .85, env: .35 },
  };
  document.querySelectorAll('[data-light]').forEach(b => b.onclick = () => {
    const a = atmospheres[b.dataset.light];
    scene.background.set(a.bg); ground.material.color.set(a.ground); sun.color.set(a.sun); sun.intensity = a.intensity; ambient.intensity = a.ambient; renderer.toneMappingExposure = a.exposure; scene.environmentIntensity = a.env;
    viewport.style.color = b.dataset.light === 'night' ? '#e1e7df' : '';
    document.querySelectorAll('[data-light]').forEach(el => { el.classList.toggle('selected', el === b); el.setAttribute('aria-pressed', String(el === b)); });
  });
  $('#tour').onclick = () => {
    if (tourTimer) { stopTour(); return; }
    const steps = Object.keys(views); let index = 0;
    setView(steps[index]);
    $('#tour').innerHTML = '<span>Ⅱ &nbsp; Parar tour</span><small>4 perspectivas</small>';
    $('#tour').setAttribute('aria-pressed', 'true');
    tourTimer = setInterval(() => { index++; if (index === steps.length) { stopTour(); return; } setView(steps[index]); announce(`Tour: vista ${document.querySelector(`[data-view="${steps[index]}"]`).textContent}`); }, 4000);
  };
  $('#fullscreen').onclick = async () => { try { if (document.fullscreenElement) await document.exitFullscreen(); else await viewport.requestFullscreen(); } catch { announce('Tela cheia indisponível neste navegador.'); } };
  $('#capture').onclick = () => {
    renderer.render(scene, camera);
    renderer.domElement.toBlob(blob => {
      if (!blob) { announce('Não foi possível salvar a imagem.'); return; }
      const url = URL.createObjectURL(blob), a = document.createElement('a');
      a.href = url; a.download = 'chalet-to-go-estudio.png'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 10000); announce('Imagem do chalé salva.');
    });
  };
  let visible = true, previous = performance.now();
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; }).observe(viewport);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopTour(); });
  renderer.domElement.addEventListener('webglcontextlost', (event) => { event.preventDefault(); renderer.setAnimationLoop(null); stopTour(); fail('A conexão com o renderizador foi interrompida. Recarregue para continuar.'); });
  renderer.setAnimationLoop(now => {
    const delta = Math.min((now - previous) / 1000, .1); previous = now;
    if (document.hidden || !visible) return;
    if (tween) { const t = Math.min((now - tween.start) / 1100, 1), eased = t * t * (3 - 2 * t); camera.position.lerpVectors(tween.from, tween.to, eased); controls.target.lerpVectors(tween.targetFrom, tween.target, eased); if (t === 1) tween = null; }
    controls.update(delta); renderer.render(scene, camera);
  });
} catch (error) {
  renderer?.dispose();
  fail('A visualização precisa de WebGL e de um navegador atualizado. Tente novamente em outro navegador.');
  console.error('Showroom initialization:', error);
}
