
// Shared Three.js helpers. Every frame is a pure function of the time passed in.
(function () {
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  function renderer(canvas) {
    const r = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
    r.setPixelRatio(1); r.setSize(canvas.width, canvas.height, false);
    return r;
  }

  // Gold particle field + slow wireframe rings (Option B cutaway backgrounds)
  function goldField(canvas, seed) {
    const r = renderer(canvas);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x081024);
    const cam = new THREE.PerspectiveCamera(50, canvas.width / canvas.height, 0.1, 100);
    cam.position.set(0, 0, 14);
    const rnd = mulberry32(seed + 7);
    const N = 900, pos = new Float32Array(N * 3), base = [];
    for (let i = 0; i < N; i++) { base.push([(rnd() - .5) * 18, (rnd() - .5) * 32, (rnd() - .5) * 14, rnd() * 6.28, 0.2 + rnd() * 0.6]); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xd4af6a, size: 0.09, transparent: true, opacity: 0.85 }));
    scene.add(pts);
    const ring1 = new THREE.Mesh(new THREE.TorusGeometry(5.2, 0.025, 8, 160), new THREE.MeshBasicMaterial({ color: 0xd4af6a, transparent: true, opacity: 0.35 }));
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(6.4, 0.018, 8, 160), new THREE.MeshBasicMaterial({ color: 0xf3d9a4, transparent: true, opacity: 0.22 }));
    const ico = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(3.2, 1)), new THREE.LineBasicMaterial({ color: 0xd4af6a, transparent: true, opacity: 0.18 }));
    [ring1, ring2, ico].forEach(m => { m.position.set(0, -1.5, -4); scene.add(m); });
    return function (t) {
      for (let i = 0; i < N; i++) { const b = base[i];
        pos[i * 3] = b[0] + Math.sin(t * 0.4 + b[3]) * 0.3; pos[i * 3 + 1] = ((b[1] + t * b[4] + 16) % 32) - 16; pos[i * 3 + 2] = b[2]; }
      geo.attributes.position.needsUpdate = true;
      ring1.rotation.set(1.1 + t * 0.12, t * 0.18, 0); ring2.rotation.set(0.6 - t * 0.1, -t * 0.14, 0.3);
      ico.rotation.set(t * 0.08, t * 0.15, 0);
      cam.position.x = Math.sin(t * 0.15) * 0.8;
      cam.lookAt(0, 0, 0);
      r.render(scene, cam);
    };
  }

  // Dotted globe turning from Brazil to the UAE with an arc between them.
  function globe(canvas, texUrl, accentHex, centerY) {
    const r = renderer(canvas);
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(30, canvas.width / canvas.height, 0.1, 100);
    // shift the globe vertically so it sits at centerY px
    const ndcY = 1 - 2 * (centerY / canvas.height);
    cam.position.set(0, 0, 20.5);
    cam.setViewOffset(canvas.width, canvas.height, 0, ndcY * canvas.height / 2, canvas.width, canvas.height);
    const accent = new THREE.Color(accentHex);
    const tex = new THREE.TextureLoader().load(texUrl, () => { ready = true; });
    let ready = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    const g = new THREE.Group(); scene.add(g);
    const sphere = new THREE.Mesh(new THREE.SphereGeometry(2, 96, 96), new THREE.MeshBasicMaterial({ map: tex }));
    g.add(sphere);
    const halo = new THREE.Mesh(new THREE.SphereGeometry(2.08, 64, 64), new THREE.MeshBasicMaterial({ color: accent, transparent: true, opacity: 0.08, side: THREE.BackSide }));
    scene.add(halo);
    function ll(lat, lon, rad) { const phi = (90 - lat) * Math.PI / 180, th = (lon + 180) * Math.PI / 180;
      return new THREE.Vector3(-rad * Math.sin(phi) * Math.cos(th), rad * Math.cos(phi), rad * Math.sin(phi) * Math.sin(th)); }
    const A = ll(-23.55, -46.63, 2.01), B = ll(25.2, 55.27, 2.01);
    const mid = A.clone().add(B).multiplyScalar(0.5).normalize().multiplyScalar(3.1);
    const curve = new THREE.QuadraticBezierCurve3(A, mid, B);
    const P = curve.getPoints(160);
    const arcGeo = new THREE.BufferGeometry().setFromPoints(P);
    const arc = new THREE.Line(arcGeo, new THREE.LineBasicMaterial({ color: accent, linewidth: 2 }));
    g.add(arc);
    const dotA = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    const dotB = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), new THREE.MeshBasicMaterial({ color: accent }));
    dotA.position.copy(A); dotB.position.copy(B); g.add(dotA); g.add(dotB);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), new THREE.MeshBasicMaterial({ color: accent }));
    g.add(head);
    // rotation so Brazil faces camera (+z), then the UAE
    const yawFor = lon => -((lon + 90) * Math.PI / 180);
    const y0 = yawFor(-46.6), y1 = yawFor(6);
    return function (p, a) {
      g.rotation.y = y0 + (y1 - y0) * p;
      g.rotation.x = 0.18 - 0.25 * p;
      const n = Math.max(2, Math.floor(a * P.length));
      arcGeo.setDrawRange(0, n);
      head.position.copy(P[Math.min(P.length - 1, n - 1)]);
      head.visible = a > 0.01 && a < 0.99;
      dotB.scale.setScalar(a > 0.98 ? 1.6 : 1);
      r.render(scene, cam);
    };
  }
  window.CaioFX = { goldField, globe };
})();
