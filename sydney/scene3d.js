import * as THREE from "./vendor/three.module.js";

const W = 1080, H = 1920, GOLD = 0xd4af6a, CREAM = 0xf0ebd8;
const canvas = document.getElementById("three-layer");
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false);
renderer.setPixelRatio(1);
renderer.setClearColor(0x000000, 0);

const scene = new THREE.Scene();
// pixel-space orthographic camera, origin top-left
const camera = new THREE.OrthographicCamera(0, W, 0, -H, -1000, 1000);
camera.position.z = 500;

// ---- seeded RNG (deterministic) ----
let seed = 20261013;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);

// ---- helpers ----
const ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const P = (lat, lon, r = 1) => {
  const la = (lat * Math.PI) / 180, lo = (lon * Math.PI) / 180;
  return new THREE.Vector3(Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)).multiplyScalar(r);
};

// ---- gold dust particles ----
const N = 140;
const pPos = new Float32Array(N * 3), pBase = [];
for (let i = 0; i < N; i++) pBase.push({ x: rnd() * W, y: rnd() * H, z: rnd() * 200 - 100, sp: 12 + rnd() * 30, ph: rnd() * 6.283 });
const pGeo = new THREE.BufferGeometry();
pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
const dot = document.createElement("canvas"); dot.width = dot.height = 64;
const dc = dot.getContext("2d"); const g = dc.createRadialGradient(32, 32, 0, 32, 32, 32);
g.addColorStop(0, "rgba(255,236,190,1)"); g.addColorStop(1, "rgba(212,175,106,0)"); dc.fillStyle = g; dc.fillRect(0, 0, 64, 64);
const particles = new THREE.Points(pGeo, new THREE.PointsMaterial({ map: new THREE.CanvasTexture(dot), size: 16, transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending }));
scene.add(particles);

// ---- globe ----
const R = 128, CX = 915, CY = 345;
const globe = new THREE.Group();            // positioned in screen space, flipped Y (ortho origin top-left, y down)
globe.position.set(CX, -CY, 0);
globe.scale.set(R, R, R);
scene.add(globe);
const tilt = new THREE.Group(); tilt.rotation.x = 0.38; globe.add(tilt);
const spin = new THREE.Group(); tilt.add(spin);

spin.add(new THREE.Mesh(new THREE.SphereGeometry(0.985, 48, 32), new THREE.MeshBasicMaterial({ color: 0x0d1321, transparent: true, opacity: 0.88 })));
// lat/lon grid
const lines = [];
for (let lat = -60; lat <= 60; lat += 30) { for (let lo = 0; lo < 360; lo += 6) lines.push(P(lat, lo), P(lat, lo + 6)); }
for (let lon = 0; lon < 360; lon += 30) { for (let la = -84; la < 84; la += 6) lines.push(P(la, lon), P(la + 6, lon)); }
spin.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(lines), new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0.6 })));
// fibonacci dot cloud on the surface
const fp = []; for (let i = 0; i < 520; i++) { const y = 1 - (i / 519) * 2, r = Math.sqrt(1 - y * y), a = i * 2.399963; fp.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r)); }
spin.add(new THREE.Points(new THREE.BufferGeometry().setFromPoints(fp), new THREE.PointsMaterial({ color: CREAM, size: 3.2, sizeAttenuation: false, transparent: true, opacity: 0.85 })));
// atmosphere rim
const rim = new THREE.Mesh(new THREE.RingGeometry(1.0, 1.06, 64), new THREE.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0.7, side: THREE.DoubleSide }));
rim.position.z = 1.2; globe.add(rim);

// cities + flight arc
const DXB = { lat: 25.2, lon: 55.3 }, SYD = { lat: -33.87, lon: 151.2 };
const markerMat = (c) => new THREE.MeshBasicMaterial({ color: c });
const dxb = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), markerMat(CREAM)); dxb.position.copy(P(DXB.lat, DXB.lon, 1.0)); spin.add(dxb);
const syd = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 12), markerMat(GOLD)); syd.position.copy(P(SYD.lat, SYD.lon, 1.0)); spin.add(syd);
const ringMat = new THREE.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
const ring = new THREE.Mesh(new THREE.RingGeometry(0.9, 1, 48), ringMat);
ring.position.copy(P(SYD.lat, SYD.lon, 1.01)); ring.lookAt(ring.position.clone().multiplyScalar(2)); spin.add(ring);

const a = P(DXB.lat, DXB.lon), b = P(SYD.lat, SYD.lon), ang = a.angleTo(b);
const arcPts = [];
for (let i = 0; i <= 80; i++) { const t = i / 80; const v = new THREE.Vector3().copy(a).multiplyScalar(Math.sin((1 - t) * ang)).add(b.clone().multiplyScalar(Math.sin(t * ang))).multiplyScalar(1 / Math.sin(ang)); v.normalize().multiplyScalar(1.01 + 0.28 * Math.sin(Math.PI * t)); arcPts.push(v); }
const arcMat = new THREE.MeshBasicMaterial({ color: GOLD });
let arcMesh = null;
const setArc = (p) => {
  if (arcMesh) { spin.remove(arcMesh); arcMesh.geometry.dispose(); arcMesh = null; }
  const n = Math.floor(p * 80); if (n < 2) return;
  arcMesh = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(arcPts.slice(0, n + 1)), n * 2, 0.024, 8, false), arcMat);
  spin.add(arcMesh);
};
const plane = new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 8), markerMat(0xffffff)); spin.add(plane);

// ---- timeline of the 3D layer ----
function renderAt(t) {
  // particles drift upward
  for (let i = 0; i < N; i++) {
    const q = pBase[i];
    pPos[i * 3] = q.x + Math.sin(t * 0.6 + q.ph) * 24;
    pPos[i * 3 + 1] = -(((q.y - t * q.sp) % H + H) % H);
    pPos[i * 3 + 2] = q.z;
  }
  pGeo.attributes.position.needsUpdate = true;
  particles.material.opacity = 0.35 + 0.2 * Math.sin(t * 1.3);

  // globe entrance (0.1-0.7s) and camera-facing longitude
  const enter = ss(0.1, 0.8, t);
  globe.scale.setScalar(R * (0.2 + 0.8 * enter) * (1 + 0.1 * Math.max(0, Math.sin(Math.PI * ss(25.8, 26.5, t)) )));
  globe.visible = enter > 0.001;
  rim.material.opacity = 0.7 * enter;
  let lon = 103 + 0 * t;                                            // midpoint: whole route visible
  lon = lon + (SYD.lon - 103) * ss(3.2, 4.4, t);                     // swing round to Sydney
  lon += (t > 9.9 ? (t - 9.9) * 6 : 0) * ss(9.9, 11, t);             // gentle spin afterwards
  lon += (-(t > 20.1 ? 1 : 0)) * 0;                                  // keep deterministic
  const back = ss(20.1, 21.2, t);                                    // re-centre on Sydney for "come meet us"
  const spinLon = lon * (1 - back) + (SYD.lon + 360 * Math.round((lon - SYD.lon) / 360)) * back;
  spin.rotation.y = -(spinLon * Math.PI) / 180;

  // flight arc draws on during "why fly 12,000 km"
  const p = ss(0.5, 3.0, t); setArc(p);
  const idx = Math.min(80, Math.max(0, Math.floor(p * 80)));
  plane.visible = p > 0.01 && p < 0.99; plane.position.copy(arcPts[idx]);
  dxb.scale.setScalar(1 + 0.4 * Math.sin(t * 4));

  // Sydney pulse rings: "right here in Sydney", "permanent office", "come meet us", CTA
  let rp = 0; [[3.4, 5.4], [5.6, 9.6], [20.1, 22.2], [25.8, 28.4]].forEach(([s, e]) => { if (t >= s && t < e) rp = ((t - s) % 1.1) / 1.1; });
  const live = [[3.4, 9.6], [20.1, 22.2], [25.8, 28.4]].some(([s, e]) => t >= s && t < e);
  ring.scale.setScalar(0.05 + 0.2 * rp); ringMat.opacity = live ? 0.9 * (1 - rp) : 0;
  syd.scale.setScalar(live ? 1.3 + 0.3 * Math.sin(t * 6) : 1);

  renderer.render(scene, camera);
}
window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
renderAt(window.__hfThreeTime || 0);
