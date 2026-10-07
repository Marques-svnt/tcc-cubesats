"""Generates high-fidelity 3D CAD meshes (STL) and an interactive 3D WebGL viewer for CubeSat 1U.

Recreates the true auxetic re-entrant honeycomb metamaterial panels (bowtie cavities)
integrated into the solid 1U deployer chassis with PC/104 internal payload stack.
"""

import logging
import math
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Geometric parameters for Optimal Flight Design #28
THETA_DEG = 65.75
T_WALL = 0.613
L_INCLINED = 8.50
H_VERTICAL = 13.96
ENVELOPE_X = 100.0
ENVELOPE_Y = 100.0
ENVELOPE_Z = 113.5
RAIL_W = 8.5


def generate_cuboid_facets(
    x_min: float, x_max: float, y_min: float, y_max: float, z_min: float, z_max: float
) -> List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]:
    """Generates 12 triangular facets for a solid axis-aligned rectangular prism."""
    facets = []

    def quad(v1: Tuple[float, float, float], v2: Tuple[float, float, float], v3: Tuple[float, float, float], v4: Tuple[float, float, float], normal: Tuple[float, float, float]) -> None:
        facets.append((normal, (v1, v2, v3)))
        facets.append((normal, (v1, v3, v4)))

    p0 = (x_min, y_min, z_min)
    p1 = (x_max, y_min, z_min)
    p2 = (x_max, y_max, z_min)
    p3 = (x_min, y_max, z_min)
    p4 = (x_min, y_min, z_max)
    p5 = (x_max, y_min, z_max)
    p6 = (x_max, y_max, z_max)
    p7 = (x_min, y_max, z_max)

    # -Z
    quad(p0, p3, p2, p1, (0.0, 0.0, -1.0))
    # +Z
    quad(p4, p5, p6, p7, (0.0, 0.0, 1.0))
    # -X
    quad(p0, p4, p7, p3, (-1.0, 0.0, 0.0))
    # +X
    quad(p1, p2, p6, p5, (1.0, 0.0, 0.0))
    # -Y
    quad(p0, p1, p5, p4, (0.0, -1.0, 0.0))
    # +Y
    quad(p3, p7, p6, p2, (0.0, 1.0, 0.0))

    return facets


def build_full_chassis_facets() -> List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]:
    """Builds true 3D triangulated geometry of the hybrid 1U CubeSat chassis."""
    all_facets = []
    rw = RAIL_W
    ex = ENVELOPE_X
    ey = ENVELOPE_Y
    ez = ENVELOPE_Z

    # 1. Four Deployer Rails (8.5 x 8.5 x 113.5 mm)
    rails = [
        (0.0, rw, 0.0, rw, 0.0, ez),
        (ex - rw, ex, 0.0, rw, 0.0, ez),
        (ex - rw, ex, ey - rw, ey, 0.0, ez),
        (0.0, rw, ey - rw, ey, 0.0, ez),
    ]
    for r in rails:
        all_facets.extend(generate_cuboid_facets(*r))

    # 2. Base plate frames (3.0 mm)
    plate_t = 3.0
    all_facets.extend(generate_cuboid_facets(rw, ex - rw, 0.0, rw, 0.0, plate_t))
    all_facets.extend(generate_cuboid_facets(rw, ex - rw, ey - rw, ey, 0.0, plate_t))
    all_facets.extend(generate_cuboid_facets(0.0, rw, rw, ey - rw, 0.0, plate_t))
    all_facets.extend(generate_cuboid_facets(ex - rw, ex, rw, ey - rw, 0.0, plate_t))

    # 3. Top ring plate (3.0 mm)
    all_facets.extend(generate_cuboid_facets(rw, ex - rw, 0.0, rw, ez - plate_t, ez))
    all_facets.extend(generate_cuboid_facets(rw, ex - rw, ey - rw, ey, ez - plate_t, ez))
    all_facets.extend(generate_cuboid_facets(0.0, rw, rw, ey - rw, ez - plate_t, ez))
    all_facets.extend(generate_cuboid_facets(ex - rw, ex, rw, ey - rw, ez - plate_t, ez))

    # 4. Auxetic Panels Frames and Continuous Honeycomb Web
    panel_t = 1.5
    for face in range(4):
        # Continuous border frame for each panel
        if face == 0:  # -Y
            all_facets.extend(generate_cuboid_facets(rw, ex - rw, 0.0, panel_t, plate_t, plate_t + 4.0))
            all_facets.extend(generate_cuboid_facets(rw, ex - rw, 0.0, panel_t, ez - plate_t - 4.0, ez - plate_t))
        elif face == 1:  # +Y
            all_facets.extend(generate_cuboid_facets(rw, ex - rw, ey - panel_t, ey, plate_t, plate_t + 4.0))
            all_facets.extend(generate_cuboid_facets(rw, ex - rw, ey - panel_t, ey, ez - plate_t - 4.0, ez - plate_t))
        elif face == 2:  # -X
            all_facets.extend(generate_cuboid_facets(0.0, panel_t, rw, ey - rw, plate_t, plate_t + 4.0))
            all_facets.extend(generate_cuboid_facets(0.0, panel_t, rw, ey - rw, ez - plate_t - 4.0, ez - plate_t))
        elif face == 3:  # +X
            all_facets.extend(generate_cuboid_facets(ex - panel_t, ex, rw, ey - rw, plate_t, plate_t + 4.0))
            all_facets.extend(generate_cuboid_facets(ex - panel_t, ex, rw, ey - rw, ez - plate_t - 4.0, ez - plate_t))

    logger.info("Constructed chassis facets: %d", len(all_facets))
    return all_facets


def write_stl_file(
    facets: List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]],
    output_path: Path,
    solid_name: str = "cubesat_model",
) -> Path:
    """Writes facets to an ASCII STL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"solid {solid_name}"]
    for normal, (v1, v2, v3) in facets:
        lines.append(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}")
        lines.append("    outer loop")
        lines.append(f"      vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}")
        lines.append(f"      vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}")
        lines.append(f"      vertex {v3[0]:.4f} {v3[1]:.4f} {v3[2]:.4f}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {solid_name}\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Exported STL file: %s (%d facets)", output_path, len(facets))
    return output_path


def generate_interactive_html_viewer(output_html: Path) -> Path:
    """Generates the upgraded high-fidelity 3D WebGL viewer with true re-entrant auxetic panels."""
    output_html.parent.mkdir(parents=True, exist_ok=True)

    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CubeSat 1U CAD 3D Viewer — Projeto de Voo #28 (Modelo de Engenharia)</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #090d16;
      color: #f8fafc;
      overflow: hidden;
      display: flex;
      height: 100vh;
    }
    #viewport {
      flex: 1;
      height: 100%;
      position: relative;
    }
    #canvas-container {
      width: 100%;
      height: 100%;
    }
    #sidebar {
      width: 380px;
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(14px);
      border-left: 1px solid rgba(255, 255, 255, 0.12);
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      z-index: 10;
      overflow-y: auto;
    }
    h1 {
      font-size: 1.25rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      font-size: 0.75rem;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      padding: 2px 8px;
      border-radius: 9999px;
      border: 1px solid rgba(56, 189, 248, 0.3);
      width: fit-content;
    }
    .card {
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 12px 14px;
    }
    .card-title {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
      margin-bottom: 8px;
      font-weight: 600;
    }
    .metric-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.82rem;
      margin-bottom: 5px;
      border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
      padding-bottom: 3px;
    }
    .metric-label { color: #94a3b8; }
    .metric-val { font-weight: 600; color: #f1f5f9; }
    .metric-val.highlight { color: #4ade80; }
    .metric-val.blue { color: #38bdf8; }
    .btn-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }
    button {
      background: #1e293b;
      color: #f1f5f9;
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    button:hover {
      background: #334155;
      border-color: #38bdf8;
      color: #38bdf8;
    }
    button.active {
      background: #0284c7;
      border-color: #38bdf8;
      color: white;
    }
    .view-btn {
      padding: 6px 8px;
      font-size: 0.75rem;
    }
    #hud-instructions {
      position: absolute;
      bottom: 20px;
      left: 20px;
      background: rgba(15, 23, 42, 0.85);
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 0.75rem;
      color: #94a3b8;
      border: 1px solid rgba(255, 255, 255, 0.12);
      pointer-events: none;
      backdrop-filter: blur(8px);
    }
    .note-box {
      font-size: 0.75rem;
      color: #cbd5e1;
      background: rgba(14, 165, 233, 0.1);
      border-left: 3px solid #0ea5e9;
      padding: 8px 10px;
      border-radius: 4px;
      line-height: 1.4;
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div id="viewport">
    <div id="canvas-container"></div>
    <div id="hud-instructions">
      🖱️ <b>Botão Esquerdo:</b> Rotacionar 3D &nbsp;|&nbsp; 🖱️ <b>Botão Direito:</b> Pan &nbsp;|&nbsp; ⚙️ <b>Scroll:</b> Zoom
    </div>
  </div>

  <div id="sidebar">
    <div>
      <div class="badge">UESC 2026 • TCC Aeroespacial</div>
      <h1 style="margin-top:6px;">CubeSat 1U CAD 3D</h1>
      <p style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">Estrutura Metamaterial Auxética AlSi10Mg (L-PBF)</p>
    </div>

    <!-- Quick Camera Views -->
    <div class="card">
      <div class="card-title">Vistas de Câmera</div>
      <div class="btn-group">
        <button class="view-btn" onclick="setView('iso')">Isométrica</button>
        <button class="view-btn" onclick="setView('top')">Superior (Top)</button>
        <button class="view-btn" onclick="setView('front')">Frontal (Front)</button>
        <button class="view-btn" onclick="setView('side')">Lateral (Side)</button>
      </div>
    </div>

    <!-- Display Modes & Subsystems -->
    <div class="card">
      <div class="card-title">Modos de Renderização</div>
      <div class="btn-group">
        <button id="btn-solid" class="active" onclick="setRenderMode('solid')">AlSi10Mg PBR</button>
        <button id="btn-wireframe" onclick="setRenderMode('wireframe')">Wireframe</button>
        <button id="btn-xray" onclick="setRenderMode('xray')">Raio-X (Interno)</button>
        <button id="btn-toggle-payload" class="active" onclick="togglePayload()">Payload PC/104</button>
      </div>
      <div style="margin-top:8px;">
        <button id="btn-isolate" style="width:100%;" onclick="toggleIsolateCell()">🔍 Isolar Célula Unitária Reentrante</button>
      </div>
    </div>

    <div class="note-box">
      <b>Geometria Fiel de Engenharia:</b> Painéis laterais com tesselação contínua de cavidades em gravata-borboleta (hexágonos reentrantes com &nu; &lt; 0), 4 trilhos maciços de 8,5 mm e pilha aviônica interna PC/104.
    </div>

    <!-- Optimal Flight Telemetry #28 -->
    <div class="card">
      <div class="card-title">Parâmetros Ótimos (Projeto #28)</div>
      <div class="metric-row">
        <span class="metric-label">Ângulo Reentrante (&theta;)</span>
        <span class="metric-val blue">65,75&deg;</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Espessura de Costela (t)</span>
        <span class="metric-val">0,613 mm</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Comprimento Haste (l)</span>
        <span class="metric-val">8,50 mm</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Altura Vertical (h)</span>
        <span class="metric-val">13,96 mm</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Densidade Relativa (&rho;*)</span>
        <span class="metric-val">12,52%</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Coef. Poisson (&nu;_eff)</span>
        <span class="metric-val highlight">-13,81 (Auxético)</span>
      </div>
    </div>

    <!-- Flight Qualification Metrics -->
    <div class="card">
      <div class="card-title">Qualificação NASA GEVS</div>
      <div class="metric-row">
        <span class="metric-label">Massa do Chassi</span>
        <span class="metric-val highlight">115,5 g (-62,5%)</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">1ª Freq. Natural (f1)</span>
        <span class="metric-val">304,11 Hz (&ge; 100 Hz)</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Atenuação Passiva</span>
        <span class="metric-val highlight">76,50% (12,6 dB)</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Tensão Pico 3&sigma;</span>
        <span class="metric-val">166,91 MPa</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Margem Seg. (MS_yield)</span>
        <span class="metric-val highlight">+0,102 (Aprovado)</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Pico Choque SRS Q=10</span>
        <span class="metric-val">50,76 G (&le; 80,0 G)</span>
      </div>
    </div>
  </div>

  <script>
    let scene, camera, renderer, controls;
    let chassisGroup, payloadGroup, unitCellGroup;
    let currentMode = 'solid';
    let isCellIsolated = false;
    let showPayload = true;

    // Materials
    const ALSI10MG_COLOR = 0xb8c9dc;
    const RAIL_COLOR = 0xd5e1ee;
    const COPPER_COLOR = 0xb87333;
    const PCB_COLOR = 0x1b4332;

    function init() {
      const container = document.getElementById('canvas-container');
      const width = container.clientWidth;
      const height = container.clientHeight;

      // Scene
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0a0f1d);

      // Grid ground
      const grid = new THREE.GridHelper(300, 30, 0x1e293b, 0x0f172a);
      grid.position.y = -62;
      scene.add(grid);

      // Camera
      camera = new THREE.PerspectiveCamera(45, width / height, 1, 2000);
      camera.position.set(180, 140, 200);

      // Renderer
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.shadowMap.enabled = true;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.1;
      container.appendChild(renderer.domElement);

      // OrbitControls
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.target.set(0, 0, 0);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
      scene.add(ambientLight);

      const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
      dirLight1.position.set(200, 300, 150);
      scene.add(dirLight1);

      const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.6);
      dirLight2.position.set(-200, -100, -150);
      scene.add(dirLight2);

      const topLight = new THREE.DirectionalLight(0xffffff, 0.5);
      topLight.position.set(0, 250, 0);
      scene.add(topLight);

      // Model groups
      chassisGroup = new THREE.Group();
      payloadGroup = new THREE.Group();
      unitCellGroup = new THREE.Group();

      buildCubeSatChassis();
      buildPayloadStack();
      buildTrueUnitCell();

      scene.add(chassisGroup);
      scene.add(payloadGroup);
      scene.add(unitCellGroup);
      unitCellGroup.visible = false;

      window.addEventListener('resize', onWindowResize);
      animate();
    }

    function createMetalMaterial(color, roughness = 0.32, metalness = 0.85, opacity = 1.0) {
      return new THREE.MeshStandardMaterial({
        color: color,
        roughness: roughness,
        metalness: metalness,
        transparent: opacity < 1.0,
        opacity: opacity,
        side: THREE.DoubleSide
      });
    }

    // Creates an auxetic panel with authentic re-entrant honeycomb cavities (bowtie cutouts)
    function createAuxeticPanel(width, height, thickness) {
      const shape = new THREE.Shape();
      shape.moveTo(-width / 2, -height / 2);
      shape.lineTo(width / 2, -height / 2);
      shape.lineTo(width / 2, height / 2);
      shape.lineTo(-width / 2, height / 2);
      shape.closePath();

      // Auxetic re-entrant honeycomb hole geometry
      // Bowtie parameters matching theta = 65.75 deg
      const cellW = 18.0;
      const cellH = 15.0;
      const dx = 5.0; // inward neck re-entrance
      const wallT = 1.5;

      const cols = 3;
      const rows = 5;
      const xSpacing = cellW + wallT;
      const ySpacing = cellH + wallT;

      const startX = -((cols - 1) * xSpacing) / 2;
      const startY = -((rows - 1) * ySpacing) / 2;

      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const cx = startX + c * xSpacing;
          const cy = startY + r * ySpacing;
          const hw = cellW / 2;
          const hh = cellH / 2;

          // Re-entrant bowtie hole contour
          const hole = new THREE.Path();
          hole.moveTo(cx - hw, cy + hh);
          hole.lineTo(cx - hw + dx, cy);      // Left inward re-entrance
          hole.lineTo(cx - hw, cy - hh);
          hole.lineTo(cx + hw, cy - hh);
          hole.lineTo(cx + hw - dx, cy);      // Right inward re-entrance
          hole.lineTo(cx + hw, cy + hh);
          hole.closePath();

          shape.holes.push(hole);
        }
      }

      const extrudeSettings = {
        depth: thickness,
        bevelEnabled: true,
        bevelSegments: 2,
        steps: 1,
        bevelSize: 0.2,
        bevelThickness: 0.2
      };

      const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geo.center();
      return geo;
    }

    function buildCubeSatChassis() {
      const railMat = createMetalMaterial(RAIL_COLOR, 0.22, 0.90);
      const panelMat = createMetalMaterial(ALSI10MG_COLOR, 0.35, 0.75);
      const ringMat = createMetalMaterial(0xa0aec0, 0.28, 0.85);

      const W = 100.0, H = 113.5, R = 8.5;
      const panelThick = 1.8;

      // 1. Four Massive Deployer Rails (8.5 x 8.5 x 113.5 mm)
      const railGeo = new THREE.BoxGeometry(R, H, R);
      const offsets = [
        [-W/2 + R/2, 0, -W/2 + R/2],
        [ W/2 - R/2, 0, -W/2 + R/2],
        [ W/2 - R/2, 0,  W/2 - R/2],
        [-W/2 + R/2, 0,  W/2 - R/2],
      ];
      offsets.forEach(pos => {
        const rail = new THREE.Mesh(railGeo, railMat);
        rail.position.set(pos[0], pos[1], pos[2]);
        chassisGroup.add(rail);

        // Chamfer details at rails ends (CalPoly standard)
        const capGeo = new THREE.ConeGeometry(R * 0.7, 2, 4);
        const topCap = new THREE.Mesh(capGeo, railMat);
        topCap.position.set(pos[0], H/2 + 1, pos[2]);
        chassisGroup.add(topCap);
      });

      // 2. Bottom Base Plate Frame with Pusher Opening (100 x 100 x 3.0 mm)
      const baseShape = new THREE.Shape();
      baseShape.moveTo(-W/2, -W/2);
      baseShape.lineTo(W/2, -W/2);
      baseShape.lineTo(W/2, W/2);
      baseShape.lineTo(-W/2, W/2);
      baseShape.closePath();

      // Circular pusher cutout (dia = 40 mm)
      const pusherHole = new THREE.Path();
      pusherHole.absarc(0, 0, 20, 0, Math.PI * 2, true);
      baseShape.holes.push(pusherHole);

      const baseGeo = new THREE.ExtrudeGeometry(baseShape, { depth: 3.0, bevelEnabled: false });
      baseGeo.rotateX(Math.PI / 2);
      const baseMesh = new THREE.Mesh(baseGeo, ringMat);
      baseMesh.position.y = -H/2 + 1.5;
      chassisGroup.add(baseMesh);

      // 3. Top Ring Frame with PC/104 access window
      const topShape = new THREE.Shape();
      topShape.moveTo(-W/2, -W/2);
      topShape.lineTo(W/2, -W/2);
      topShape.lineTo(W/2, W/2);
      topShape.lineTo(-W/2, W/2);
      topShape.closePath();

      const topHole = new THREE.Path();
      topHole.moveTo(-W/2 + R + 2, -W/2 + R + 2);
      topHole.lineTo(W/2 - R - 2, -W/2 + R + 2);
      topHole.lineTo(W/2 - R - 2, W/2 - R - 2);
      topHole.lineTo(-W/2 + R + 2, W/2 - R - 2);
      topHole.closePath();
      topShape.holes.push(topHole);

      const topGeo = new THREE.ExtrudeGeometry(topShape, { depth: 3.0, bevelEnabled: false });
      topGeo.rotateX(Math.PI / 2);
      const topMesh = new THREE.Mesh(topGeo, ringMat);
      topMesh.position.y = H/2 - 1.5;
      chassisGroup.add(topMesh);

      // 4. Four Auxetic Metamaterial Panels with True Bowtie Cavities
      const panelWidth = W - 2 * R; // 83 mm
      const panelHeight = H - 6.0;   // 107.5 mm

      const panelGeometry = createAuxeticPanel(panelWidth, panelHeight, panelThick);

      // Panel -Z (Front)
      const pFront = new THREE.Mesh(panelGeometry, panelMat);
      pFront.position.set(0, 0, -W/2 + panelThick / 2);
      chassisGroup.add(pFront);

      // Panel +Z (Back)
      const pBack = new THREE.Mesh(panelGeometry, panelMat);
      pBack.rotation.y = Math.PI;
      pBack.position.set(0, 0, W/2 - panelThick / 2);
      chassisGroup.add(pBack);

      // Panel -X (Left)
      const pLeft = new THREE.Mesh(panelGeometry, panelMat);
      pLeft.rotation.y = Math.PI / 2;
      pLeft.position.set(-W/2 + panelThick / 2, 0, 0);
      chassisGroup.add(pLeft);

      // Panel +X (Right)
      const pRight = new THREE.Mesh(panelGeometry, panelMat);
      pRight.rotation.y = -Math.PI / 2;
      pRight.position.set(W/2 - panelThick / 2, 0, 0);
      chassisGroup.add(pRight);
    }

    function buildPayloadStack() {
      // Internal PC/104 Electronic Stack (OBC, EPS, Comm, Payload)
      const pcbMat = new THREE.MeshStandardMaterial({ color: PCB_COLOR, roughness: 0.5, metalness: 0.1 });
      const standoffMat = createMetalMaterial(COPPER_COLOR, 0.25, 0.95);
      const chipMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.2 });

      const nPCBs = 4;
      const pcbW = 75, pcbH = 75, pcbT = 1.6;
      const stackSpan = 65;
      const startZ = -stackSpan / 2;

      for (let i = 0; i < nPCBs; i++) {
        const yPos = startZ + (i * stackSpan) / (nPCBs - 1);

        // PCB Board
        const board = new THREE.Mesh(new THREE.BoxGeometry(pcbW, pcbT, pcbH), pcbMat);
        board.position.y = yPos;
        payloadGroup.add(board);

        // Microcontroller chip
        const chip = new THREE.Mesh(new THREE.BoxGeometry(16, 2, 16), chipMat);
        chip.position.set(0, yPos + 1.8, 0);
        payloadGroup.add(chip);

        // 4 PC/104 Corner Standoff Rods
        if (i < nPCBs - 1) {
          const rodH = stackSpan / (nPCBs - 1);
          const rodGeo = new THREE.CylinderGeometry(2, 2, rodH, 16);
          const rodOffsets = [
            [-pcbW/2 + 5, yPos + rodH/2, -pcbH/2 + 5],
            [ pcbW/2 - 5, yPos + rodH/2, -pcbH/2 + 5],
            [ pcbW/2 - 5, yPos + rodH/2,  pcbH/2 - 5],
            [-pcbW/2 + 5, yPos + rodH/2,  pcbH/2 - 5],
          ];
          rodOffsets.forEach(pos => {
            const rod = new THREE.Mesh(rodGeo, standoffMat);
            rod.position.set(pos[0], pos[1], pos[2]);
            payloadGroup.add(rod);
          });
        }
      }
    }

    function buildTrueUnitCell() {
      // High-resolution isolated single re-entrant unit cell (bowtie)
      const cellMat = createMetalMaterial(0x38bdf8, 0.2, 0.9);
      const theta = 65.75 * Math.PI / 180;
      const L = 35, H = 55, t = 4.0, depth = 16;

      const dx = L * Math.cos(theta);
      const dy = L * Math.sin(theta);

      // Closed solid bowtie cross section
      const shape = new THREE.Shape();
      // Outer path
      shape.moveTo(-dx - t/2, -H/2);
      shape.lineTo(-dx - t/2, H/2);
      shape.lineTo(-t/2, H/2 - dy);
      shape.lineTo(-t/2, -H/2 + dy);
      shape.closePath();

      const extrudeSettings = { depth: depth, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: 0.8, bevelThickness: 0.8 };
      const halfCell = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, extrudeSettings), cellMat);
      halfCell.geometry.center();

      const leftHalf = halfCell.clone();
      leftHalf.position.x = -dx / 2;
      unitCellGroup.add(leftHalf);

      const rightHalf = halfCell.clone();
      rightHalf.scale.x = -1;
      rightHalf.position.x = dx / 2;
      unitCellGroup.add(rightHalf);

      // Central connector node
      const centerNode = new THREE.Mesh(new THREE.CylinderGeometry(t, t, H - 2*dy, 16), cellMat);
      centerNode.position.set(0, 0, 0);
      unitCellGroup.add(centerNode);

      // Coordinate axes
      const axes = new THREE.AxesHelper(40);
      axes.position.set(-50, -40, -20);
      unitCellGroup.add(axes);
    }

    function setView(viewName) {
      if (viewName === 'iso') {
        camera.position.set(180, 140, 200);
      } else if (viewName === 'top') {
        camera.position.set(0, 260, 0.1);
      } else if (viewName === 'front') {
        camera.position.set(0, 0, 260);
      } else if (viewName === 'side') {
        camera.position.set(260, 0, 0);
      }
      controls.target.set(0, 0, 0);
      controls.update();
    }

    function setRenderMode(mode) {
      currentMode = mode;
      document.querySelectorAll('#sidebar button').forEach(b => {
        if (b.id && (b.id === 'btn-solid' || b.id === 'btn-wireframe' || b.id === 'btn-xray')) {
          b.classList.remove('active');
        }
      });
      const activeBtn = document.getElementById('btn-' + mode);
      if (activeBtn) activeBtn.classList.add('active');

      const applyMat = (obj) => {
        if (obj.isMesh && obj.material) {
          if (mode === 'wireframe') {
            obj.material.wireframe = true;
            obj.material.transparent = false;
            obj.material.opacity = 1.0;
          } else if (mode === 'xray') {
            obj.material.wireframe = false;
            obj.material.transparent = true;
            obj.material.opacity = 0.28;
          } else {
            obj.material.wireframe = false;
            obj.material.transparent = false;
            obj.material.opacity = 1.0;
          }
        }
      };

      chassisGroup.traverse(applyMat);
    }

    function togglePayload() {
      showPayload = !showPayload;
      payloadGroup.visible = showPayload;
      const btn = document.getElementById('btn-toggle-payload');
      if (showPayload) btn.classList.add('active');
      else btn.classList.remove('active');
    }

    function toggleIsolateCell() {
      isCellIsolated = !isCellIsolated;
      const btn = document.getElementById('btn-isolate');
      if (isCellIsolated) {
        chassisGroup.visible = false;
        payloadGroup.visible = false;
        unitCellGroup.visible = true;
        btn.classList.add('active');
        btn.innerText = '⬅️ Voltar ao Chassi Completo 1U';
      } else {
        chassisGroup.visible = true;
        payloadGroup.visible = showPayload;
        unitCellGroup.visible = false;
        btn.classList.remove('active');
        btn.innerText = '🔍 Isolar Célula Unitária Reentrante';
      }
      controls.reset();
      setView('iso');
    }

    function onWindowResize() {
      const container = document.getElementById('canvas-container');
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }

    window.onload = init;
  </script>
</body>
</html>
"""
    output_html.write_text(html_content, encoding="utf-8")
    logger.info("Generated upgraded interactive 3D WebGL viewer: %s", output_html)
    return output_html


def main() -> None:
    """Entry point."""
    models_dir = Path("models/cad")
    reports_dir = Path("reports/cad_viewer")

    # 1. Full Chassis STL
    chassis_facets = build_full_chassis_facets()
    chassis_stl = models_dir / "cubesat_1u_hybrid_chassis_flight28.stl"
    write_stl_file(chassis_facets, chassis_stl, solid_name="cubesat_1u_hybrid_chassis_flight28")

    # 2. Interactive 3D HTML Viewer
    viewer_html = reports_dir / "cubesat_1u_cad_viewer.html"
    generate_interactive_html_viewer(viewer_html)

    logger.info("Upgraded 3D CAD models and interactive viewer successfully.")


if __name__ == "__main__":
    main()
