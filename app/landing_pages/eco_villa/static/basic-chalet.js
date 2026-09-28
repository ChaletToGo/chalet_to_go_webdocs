import * as THREE from 'three';

// Proportions inferred from the Basic reference images, not construction dimensions.
export const BASIC = Object.freeze({ width: 3.8, depth: 8, floor: .28, eave: 3.25, ridge: 5.15, loft: 2.65 });
const cube = new THREE.BoxGeometry(1, 1, 1);
const wood = new THREE.MeshStandardMaterial({ color: '#c29159', roughness: .82 });
const woodLight = wood.clone(); woodLight.color.set('#cfa36c');
const woodDark = wood.clone(); woodDark.color.set('#b0804e');
const concrete = new THREE.MeshStandardMaterial({ color: '#aaa595', roughness: 1 });
const windowGlass = new THREE.MeshStandardMaterial({ color: '#70918c', metalness: .3, roughness: .25 });
const planks = [wood, woodLight, wood, woodDark];

function box(parent, mat, x, y, z, w, h, d, rotation = 0) {
  const mesh = new THREE.Mesh(cube, mat);
  mesh.position.set(x, y, z); mesh.scale.set(w, h, d); mesh.rotation.z = rotation;
  mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}

// Batch repeated boards and frames. Each removable section stays independent.
function batch(group) {
  group.updateMatrixWorld(true);
  const inverse = group.matrixWorld.clone().invert(), batches = new Map();
  group.traverse(mesh => {
    if (!mesh.isMesh) return;
    const key = mesh.geometry.uuid + mesh.material.uuid;
    if (!batches.has(key)) batches.set(key, { geometry: mesh.geometry, material: mesh.material, matrices: [] });
    batches.get(key).matrices.push(inverse.clone().multiply(mesh.matrixWorld));
  });
  group.clear();
  for (const { geometry, material, matrices } of batches.values()) {
    const mesh = new THREE.InstancedMesh(geometry, material, matrices.length);
    matrices.forEach((matrix, index) => mesh.setMatrixAt(index, matrix));
    mesh.castShadow = true; mesh.receiveShadow = true;
    mesh.computeBoundingSphere(); group.add(mesh);
  }
}

// Horizontal siding with actual openings, rather than windows on solid walls.
function siding(parent, width, bottom, top, openings = []) {
  for (let y = bottom, row = 0; y < top - .001; y += .19, row++) {
    const h = Math.min(.182, top - y);
    let segments = [[-width / 2, width / 2]];
    for (const opening of openings) {
      if (y + h <= opening.bottom || y >= opening.top) continue;
      const left = opening.x - opening.width / 2, right = opening.x + opening.width / 2;
      segments = segments.flatMap(([a, b]) => {
        if (right <= a || left >= b) return [[a, b]];
        return [[a, Math.min(b, left)], [Math.max(a, right), b]].filter(([l, r]) => r - l > .01);
      });
    }
    segments.forEach(([a, b]) => box(parent, planks[row % planks.length], (a + b) / 2, y + h / 2, 0, b - a, h, .15));
  }
}

function windowFrame(parent, palette, x, y, width, height) {
  box(parent, windowGlass, x, y, .025, width - .1, height - .1, .045);
  for (const sign of [-1, 1]) {
    box(parent, palette.trim, x + sign * width / 2, y, .07, .075, height + .075, .1);
    box(parent, palette.trim, x, y + sign * height / 2, .07, width + .075, .075, .1);
  }
  box(parent, palette.trim, x, y, .085, width, .045, .07);
  box(parent, palette.trim, x, y, .085, .035, height, .07);
  box(parent, woodDark, x, y - height / 2 - .08, .09, width + .2, .075, .21);
}

function wall(root, x, z, angle = 0) {
  const group = new THREE.Group(); group.position.set(x, 0, z); group.rotation.y = angle; root.add(group); return group;
}

export function buildBasicChalet(palette) {
  const root = new THREE.Group(); root.name = 'basic-fixed';
  const fixed = new THREE.Group(), shell = new THREE.Group(), roof = new THREE.Group(), loft = new THREE.Group();
  root.add(fixed, shell, roof, loft);
  // Continuous fixed plinth meets the ground. No trailer, chassis, wheels or axle.
  box(fixed, concrete, 0, .04, 0, BASIC.width, .32, BASIC.depth);
  box(fixed, wood, 0, .23, 0, BASIC.width, .1, BASIC.depth);
  for (let z = -3.9; z < 4; z += .22) box(fixed, woodLight, 0, .295, z, 3.6, .035, .2);
  box(fixed, concrete, 0, .045, 5.02, 4.25, .22, 2.05);
  for (let z = 4.08; z < 6.05; z += .2) box(fixed, wood, 0, .18, z, 4.25, .08, .185);
  box(fixed, concrete, 0, -.015, 6.2, 1.35, .1, .42);

  const front = wall(shell, 0, 4);
  const frontOpenings = [
    { x: 0, width: 1.03, bottom: .28, top: 2.75 },
    ...[-1.2, 1.2].map(x => ({ x, width: .63, bottom: 1.06, top: 2.73 })),
  ];
  siding(front, BASIC.width, .28, BASIC.eave, frontOpenings);
  windowFrame(front, palette, -1.2, 1.9, .63, 1.67);
  windowFrame(front, palette, 1.2, 1.9, .63, 1.67);
  box(front, palette.trim, 0, 1.5, .02, .97, 2.42, .1);
  windowFrame(front, palette, 0, 1.93, .76, 1.4);
  for (const x of [-.23, .23]) box(front, palette.trim, x, .78, .09, .36, .62, .06);
  box(front, palette.trim, .36, 1.3, .18, .1, .07, .16);
  for (const x of [-.57, .57]) box(front, woodLight, x, 1.53, .085, .11, 2.6, .2);
  box(front, woodLight, 0, 2.87, .08, 1.28, .16, .2);
  // Reference side windows: three downstairs; three smaller windows in the dormer.
  for (const side of [-1, 1]) {
    const sideWall = wall(shell, side * 1.9, 0, side * Math.PI / 2);
    const windows = [
      { x: -2.5, width: .83, bottom: .98, top: 2.62 },
      { x: 0, width: .65, bottom: 1.07, top: 2.62 },
      { x: 2.65, width: .72, bottom: 1.42, top: 2.46 },
    ];
    // Mirror coordinates on the right, keeping the bathroom window at the rear.
    const openings = windows.map(o => ({ ...o, x: o.x * side }));
    siding(sideWall, BASIC.depth, .28, BASIC.eave, openings);
    openings.forEach(o => windowFrame(sideWall, palette, o.x, (o.top + o.bottom) / 2, o.width, o.top - o.bottom));
  }
  const rear = wall(shell, 0, -4, Math.PI);
  siding(rear, BASIC.width, .28, BASIC.eave);
  for (const x of [-1.85, 1.85]) for (const z of [-4.02, 4.02]) box(shell, woodLight, x, 1.77, z, .17, 3.08, .2);

  // Timber gables, roof pitches, standing seams and exposed fascia.
  const slope = (BASIC.ridge - BASIC.eave) / (BASIC.width / 2);
  const angle = Math.atan(slope), half = 2.16, pitchWidth = half / Math.cos(angle);
  for (const z of [-4, 4]) {
    for (let y = BASIC.eave; y < BASIC.ridge - .05; y += .18) {
      const width = Math.max(.02, 2 * (BASIC.ridge - y - .08) / slope);
      box(roof, wood, 0, y + .085, z, width, .17, .16);
    }
    for (const sign of [-1, 1]) box(roof, woodLight, sign * half / 2, BASIC.ridge - slope * half / 2, z + Math.sign(z) * .27, pitchWidth + .15, .2, .18, -sign * angle);
  }
  for (const sign of [-1, 1]) {
    box(roof, palette.roof, sign * half / 2, BASIC.ridge - slope * half / 2 + .03, 0, pitchWidth, .11, 8.65, -sign * angle);
    for (let z = -4.2; z <= 4.2; z += .4) box(roof, palette.trim, sign * half / 2, BASIC.ridge - slope * half / 2 + .11, z, pitchWidth, .05, .035, -sign * angle);
  }
  box(roof, palette.trim, 0, BASIC.ridge + .12, 0, .16, .14, 8.7);
  // Raised shed dormer, visible on the left side in the supplied exterior image.
  const dormer = wall(roof, -1.66, -1.2, -Math.PI / 2);
  const dormerWindows = [-1.35, 0, 1.35].map(x => ({ x, width: .48, bottom: 3.73, top: 4.47 }));
  siding(dormer, 4.35, 3.48, 4.67, dormerWindows);
  dormerWindows.forEach(o => windowFrame(dormer, palette, o.x, 4.1, o.width, .74));
  for (const z of [-3.38, .98]) box(roof, wood, -.88, 4.1, z, 1.55, 1.15, .12);
  box(roof, palette.roof, -.86, 4.88, -1.2, 1.93, .1, 4.65, .2);
  for (let z = -3.4; z <= 1; z += .4) box(roof, palette.trim, -.86, 4.95, z, 1.93, .04, .035, .2);
  // Entrance wall lantern attached to the gable.
  box(roof, palette.trim, 0, 3.72, 4.15, .1, .36, .15);
  box(roof, palette.light, 0, 3.57, 4.25, .16, .2, .16);
  box(roof, palette.trim, 0, 3.7, 4.25, .27, .06, .27);

  // Ground floor from planta_chale_basico.jpg: lounge front left, kitchen left,
  // stairs right, full-width bathroom at the rear, sleeping loft above the rear.
  box(fixed, palette.fabric, -.75, .32, 2.27, 1.7, .035, 2.2);
  box(fixed, palette.fabric, -1.29, .66, 2.13, .86, .66, 1.95);
  box(fixed, palette.cream, -1.68, 1, 2.13, .18, 1.03, 2.02);
  for (const z of [1.13, 3.13]) box(fixed, palette.cream, -1.28, .88, z, .96, .45, .17);
  box(fixed, wood, -.27, .56, 2.13, .54, .46, .72);
  box(fixed, wood, -1.43, .8, -.66, .63, 1, 2.55);
  box(fixed, palette.cream, -1.43, 1.34, -.66, .75, .09, 2.62);
  box(fixed, palette.trim, -1.43, 1.4, -.1, .53, .025, .62);
  box(fixed, palette.water, -1.43, 1.4, -1.2, .5, .025, .49);
  box(fixed, palette.trim, -1.73, 1.56, -1.2, .045, .32, .045);
  box(fixed, palette.cream, -1.44, .81, -1.77, .58, .9, .47);
  box(fixed, palette.path, 0, .31, -3.17, 3.57, .06, 1.5);
  box(fixed, palette.cream, -.55, .7, -2.36, 2.6, .8, .1);
  box(shell, palette.cream, -.55, 1.82, -2.36, 2.6, 1.44, .1);
  box(fixed, palette.water, -1.21, .38, -3.18, 1.06, .12, 1.28);
  box(shell, palette.glass, -.65, 1.36, -3.2, .025, 2, 1.3);
  box(fixed, palette.cream, .05, .6, -3.55, .45, .6, .65);
  box(fixed, palette.cream, 1.26, .99, -3.55, .75, .2, .49);
  // Stairs rise from front to rear along the right wall.
  for (let i = 0; i < 12; i++) {
    const height = (BASIC.loft - .3) * (i + 1) / 12;
    box(fixed, wood, 1.22, .3 + height / 2, 2.5 - i * .29, .86, height, .29);
  }
  box(loft, wood, 0, BASIC.loft, -2.13, 3.6, .16, 3.58);
  box(loft, palette.fabric, -.2, BASIC.loft + .12, -2.35, 2.5, .03, 2.8);
  box(loft, woodDark, -.2, BASIC.loft + .28, -2.35, 1.9, .3, 2.25);
  box(loft, palette.cream, -.2, BASIC.loft + .5, -2.35, 1.86, .2, 2.2);
  box(loft, palette.fabric, -.2, BASIC.loft + .62, -1.85, 1.87, .045, 1.1);
  for (const x of [-.68, .28]) box(loft, palette.cream, x, BASIC.loft + .68, -3.1, .74, .15, .43);
  for (let x = -1.7; x < .7; x += .35) box(loft, woodLight, x, BASIC.loft + .48, -.37, .05, .87, .05);
  box(loft, woodLight, -.5, BASIC.loft + .93, -.37, 2.6, .07, .09);
  // Compact terrace keeps the common landscape language of the supplied site plan.
  for (const x of [-1.35, 1.35]) {
    box(fixed, wood, x, .53, 5.1, .6, .13, .67);
    box(fixed, palette.cream, x, .62, 5.1, .51, .1, .55);
    box(fixed, wood, x, .91, 4.8, .6, .67, .09);
    for (const z of [4.88, 5.34]) box(fixed, wood, x, .35, z, .48, .3, .055);
  }
  for (const group of [fixed, shell, roof, loft]) batch(group);
  return { root, shell, roof, loft };
}
