import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Ice Defense Simulator",
    page_icon="🧊",
    layout="wide",
)

components.html(
    r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {
        margin: 0;
        background: #0f172a;
        color: #e5e7eb;
        font-family: Inter, Arial, sans-serif;
    }

    .app {
        display: grid;
        grid-template-columns: 760px 1fr;
        gap: 22px;
        padding: 18px;
        box-sizing: border-box;
    }

    .panel {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
    }

    h1 {
        margin: 0 0 6px 0;
        font-size: 28px;
        color: #f8fafc;
    }

    h2 {
        margin: 18px 0 10px 0;
        font-size: 17px;
        color: #f8fafc;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 14px;
    }

    canvas {
        width: 720px;
        height: 720px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: #020617;
        display: block;
    }

    .buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }

    button {
        border: none;
        border-radius: 12px;
        padding: 10px 13px;
        color: #f8fafc;
        background: #2563eb;
        font-weight: 700;
        cursor: pointer;
    }

    button.secondary {
        background: #334155;
    }

    button.danger {
        background: #dc2626;
    }

    button.good {
        background: #059669;
    }

    button:hover {
        filter: brightness(1.08);
    }

    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }

    .metric {
        background: #020617;
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 14px;
        padding: 12px;
    }

    .metric .label {
        font-size: 12px;
        color: #94a3b8;
    }

    .metric .value {
        margin-top: 5px;
        font-size: 23px;
        font-weight: 800;
        color: #f8fafc;
    }

    .control {
        margin: 12px 0;
    }

    .control label {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #cbd5e1;
        margin-bottom: 6px;
    }

    input[type="range"] {
        width: 100%;
    }

    .legend {
        display: grid;
        gap: 8px;
        margin-top: 8px;
    }

    .legend-row {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #cbd5e1;
        font-size: 14px;
    }

    .swatch {
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.45);
    }

    .note {
        margin-top: 12px;
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.45;
    }

    .status {
        margin-top: 12px;
        padding: 12px;
        border-radius: 14px;
        background: #020617;
        border: 1px solid rgba(148, 163, 184, 0.25);
        color: #e5e7eb;
        line-height: 1.45;
    }
</style>
</head>
<body>
<div class="app">
    <div class="panel">
        <h1>Ice Defense Simulator</h1>
        <div class="subtitle">непрерывное распространение тепла, таяние льда и перетаскивание защитных объектов мышкой</div>
        <canvas id="field" width="720" height="720"></canvas>
        <div class="buttons">
            <button id="pauseBtn">Pause</button>
            <button id="resetBtn" class="secondary">Reset heat</button>
            <button id="goodBtn" class="good">Good defense</button>
            <button id="badBtn" class="danger">Bad defense</button>
            <button id="raceBtn" class="secondary">Race layout</button>
        </div>
    </div>

    <div class="panel">
        <h2>Simulation</h2>

        <div class="metric-grid">
            <div class="metric">
                <div class="label">Ice left</div>
                <div id="iceMetric" class="value">100%</div>
            </div>
            <div class="metric">
                <div class="label">Max temperature</div>
                <div id="tempMetric" class="value">-5 °C</div>
            </div>
            <div class="metric">
                <div class="label">Time</div>
                <div id="timeMetric" class="value">0.0 s</div>
            </div>
            <div class="metric">
                <div class="label">Status</div>
                <div id="statusMetric" class="value">Safe</div>
            </div>
        </div>

        <div class="control">
            <label>
                <span>Simulation speed</span>
                <span id="speedLabel">12</span>
            </label>
            <input id="speedInput" type="range" min="1" max="35" step="1" value="12">
        </div>

        <div class="control">
            <label>
                <span>Heat source power</span>
                <span id="powerLabel">42</span>
            </label>
            <input id="powerInput" type="range" min="10" max="90" step="1" value="42">
        </div>

        <div class="control">
            <label>
                <span>Base conductivity</span>
                <span id="alphaLabel">0.34</span>
            </label>
            <input id="alphaInput" type="range" min="0.08" max="0.75" step="0.01" value="0.34">
        </div>

        <h2>Objects</h2>
        <div class="legend">
            <div class="legend-row"><div class="swatch" style="background:#38bdf8"></div>Ice block. It loses mass when heated above 0 °C.</div>
            <div class="legend-row"><div class="swatch" style="background:#ef4444"></div>Heat source. It continuously injects heat.</div>
            <div class="legend-row"><div class="swatch" style="background:#8b5cf6"></div>Insulator. It slows down heat transfer.</div>
            <div class="legend-row"><div class="swatch" style="background:#f59e0b"></div>Conductor. It spreads heat faster.</div>
            <div class="legend-row"><div class="swatch" style="background:#06b6d4"></div>Cooler. It removes heat locally.</div>
        </div>

        <div class="status" id="adviceBox">
            Drag objects directly on the field. Place insulators between the heat source and the ice to protect it.
        </div>

        <div class="note">
            Управление: перетаскивай объекты мышкой. Симуляция идёт непрерывно и не ограничена временем.
            Если лёд не тает, увеличь скорость или мощность источника. Если всё происходит слишком быстро, уменьши скорость.
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById("field");
const ctx = canvas.getContext("2d");

const N = 90;
const S = canvas.width / N;
const ambient = -5.0;
const dt = 0.055;

let temperature = new Float32Array(N * N);
let nextTemperature = new Float32Array(N * N);
let iceMass = 1.0;
let simulatedTime = 0.0;
let paused = false;
let dragging = null;
let dragOffsetX = 0;
let dragOffsetY = 0;

let objects = [];

const typeStyle = {
    ice: { fill: "#38bdf8", stroke: "#e0f2fe", label: "ICE" },
    heater: { fill: "#ef4444", stroke: "#fee2e2", label: "HEAT" },
    insulator: { fill: "#8b5cf6", stroke: "#ede9fe", label: "INSULATOR" },
    conductor: { fill: "#f59e0b", stroke: "#fffbeb", label: "CONDUCTOR" },
    cooler: { fill: "#06b6d4", stroke: "#cffafe", label: "COOLER" }
};

function idx(x, y) {
    return y * N + x;
}

function resetTemperature() {
    for (let i = 0; i < temperature.length; i++) {
        temperature[i] = ambient;
        nextTemperature[i] = ambient;
    }
    iceMass = 1.0;
    simulatedTime = 0.0;
}

function setGoodDefense() {
    objects = [
        { type: "ice", x: 10, y: 34, w: 13, h: 20 },
        { type: "heater", x: 76, y: 42, w: 6, h: 6 },
        { type: "insulator", x: 39, y: 23, w: 8, h: 43 },
        { type: "insulator", x: 28, y: 31, w: 7, h: 30 },
        { type: "cooler", x: 22, y: 12, w: 20, h: 8 },
        { type: "conductor", x: 62, y: 37, w: 11, h: 15 }
    ];
    resetTemperature();
}

function setBadDefense() {
    objects = [
        { type: "ice", x: 10, y: 34, w: 13, h: 20 },
        { type: "heater", x: 76, y: 42, w: 6, h: 6 },
        { type: "insulator", x: 66, y: 15, w: 8, h: 36 },
        { type: "conductor", x: 34, y: 38, w: 36, h: 8 },
        { type: "cooler", x: 68, y: 64, w: 16, h: 8 }
    ];
    resetTemperature();
}

function setRaceLayout() {
    objects = [
        { type: "ice", x: 10, y: 20, w: 12, h: 16 },
        { type: "ice", x: 10, y: 54, w: 12, h: 16 },
        { type: "heater", x: 77, y: 42, w: 6, h: 6 },
        { type: "insulator", x: 39, y: 12, w: 7, h: 32 },
        { type: "conductor", x: 39, y: 52, w: 7, h: 28 },
        { type: "cooler", x: 24, y: 6, w: 15, h: 8 }
    ];
    resetTemperature();
}

function getValue(id) {
    return Number(document.getElementById(id).value);
}

function objectAtCell(cx, cy) {
    for (let i = objects.length - 1; i >= 0; i--) {
        const o = objects[i];
        if (cx >= o.x && cx <= o.x + o.w && cy >= o.y && cy <= o.y + o.h) {
            return o;
        }
    }
    return null;
}

function pointerToCell(event) {
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width * N;
    const y = (event.clientY - rect.top) / rect.height * N;
    return { x, y };
}

canvas.addEventListener("pointerdown", (event) => {
    const p = pointerToCell(event);
    const selected = objectAtCell(p.x, p.y);
    if (selected) {
        dragging = selected;
        dragOffsetX = p.x - selected.x;
        dragOffsetY = p.y - selected.y;
        canvas.setPointerCapture(event.pointerId);
    }
});

canvas.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const p = pointerToCell(event);
    dragging.x = Math.max(0, Math.min(N - dragging.w, p.x - dragOffsetX));
    dragging.y = Math.max(0, Math.min(N - dragging.h, p.y - dragOffsetY));
});

canvas.addEventListener("pointerup", () => {
    dragging = null;
});

function buildFields() {
    const alpha = new Float32Array(N * N);
    const cooling = new Float32Array(N * N);
    const source = new Float32Array(N * N);

    const baseAlpha = getValue("alphaInput");
    const heaterPower = getValue("powerInput");

    for (let i = 0; i < alpha.length; i++) {
        alpha[i] = baseAlpha;
        cooling[i] = 0.0008;
        source[i] = 0.0;
    }

    for (const o of objects) {
        const x0 = Math.floor(o.x);
        const y0 = Math.floor(o.y);
        const x1 = Math.ceil(o.x + o.w);
        const y1 = Math.ceil(o.y + o.h);

        if (o.type === "insulator") {
            for (let y = y0; y < y1; y++) {
                for (let x = x0; x < x1; x++) {
                    if (x >= 0 && x < N && y >= 0 && y < N) {
                        alpha[idx(x, y)] *= 0.025;
                    }
                }
            }
        }

        if (o.type === "conductor") {
            for (let y = y0; y < y1; y++) {
                for (let x = x0; x < x1; x++) {
                    if (x >= 0 && x < N && y >= 0 && y < N) {
                        alpha[idx(x, y)] = Math.max(alpha[idx(x, y)], 1.05);
                    }
                }
            }
        }

        if (o.type === "cooler") {
            for (let y = y0; y < y1; y++) {
                for (let x = x0; x < x1; x++) {
                    if (x >= 0 && x < N && y >= 0 && y < N) {
                        cooling[idx(x, y)] += 0.095;
                    }
                }
            }
        }

        if (o.type === "heater") {
            const cx = o.x + o.w / 2;
            const cy = o.y + o.h / 2;
            const radius = 15.0;
            for (let y = 0; y < N; y++) {
                for (let x = 0; x < N; x++) {
                    const dx = x - cx;
                    const dy = y - cy;
                    const d2 = dx * dx + dy * dy;
                    if (d2 < radius * radius * 5.5) {
                        source[idx(x, y)] += heaterPower * Math.exp(-d2 / (2.0 * radius * radius));
                    }
                }
            }
        }
    }

    return { alpha, cooling, source };
}

function stepSimulation() {
    const fields = buildFields();
    let meltSignal = 0.0;
    let iceCellCount = 0;

    for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) {
            const i = idx(x, y);
            const xl = Math.max(0, x - 1);
            const xr = Math.min(N - 1, x + 1);
            const yd = Math.max(0, y - 1);
            const yu = Math.min(N - 1, y + 1);

            const lap =
                temperature[idx(xl, y)] +
                temperature[idx(xr, y)] +
                temperature[idx(x, yd)] +
                temperature[idx(x, yu)] -
                4.0 * temperature[i];

            let t =
                temperature[i] +
                fields.alpha[i] * lap * dt +
                fields.source[i] * dt -
                fields.cooling[i] * (temperature[i] - ambient) * dt;

            nextTemperature[i] = t;
        }
    }

    for (const o of objects) {
        if (o.type !== "ice") continue;

        const x0 = Math.floor(o.x);
        const y0 = Math.floor(o.y);
        const x1 = Math.ceil(o.x + o.w);
        const y1 = Math.ceil(o.y + o.h);

        for (let y = y0; y < y1; y++) {
            for (let x = x0; x < x1; x++) {
                if (x >= 0 && x < N && y >= 0 && y < N) {
                    const i = idx(x, y);
                    iceCellCount += 1;
                    if (iceMass > 0 && nextTemperature[i] > 0) {
                        meltSignal += nextTemperature[i];
                        nextTemperature[i] = Math.min(nextTemperature[i], 0.0);
                    }
                }
            }
        }
    }

    if (iceCellCount > 0 && iceMass > 0) {
        const averageHeatOnIce = meltSignal / iceCellCount;
        iceMass = Math.max(0.0, iceMass - averageHeatOnIce * 0.0065 * dt);
    }

    const tmp = temperature;
    temperature = nextTemperature;
    nextTemperature = tmp;
    simulatedTime += dt;
}

function mix(a, b, t) {
    return Math.round(a + (b - a) * t);
}

function colorForTemperature(temp) {
    const v = Math.max(0, Math.min(1, (temp + 5) / 90));

    const stops = [
        [0.00, [30, 64, 175]],
        [0.26, [34, 211, 238]],
        [0.50, [250, 204, 21]],
        [0.72, [249, 115, 22]],
        [1.00, [220, 38, 38]]
    ];

    for (let i = 0; i < stops.length - 1; i++) {
        const a = stops[i];
        const b = stops[i + 1];
        if (v >= a[0] && v <= b[0]) {
            const t = (v - a[0]) / (b[0] - a[0]);
            return [
                mix(a[1][0], b[1][0], t),
                mix(a[1][1], b[1][1], t),
                mix(a[1][2], b[1][2], t)
            ];
        }
    }

    return stops[stops.length - 1][1];
}

function drawHeatMap() {
    const image = ctx.createImageData(N, N);
    for (let y = 0; y < N; y++) {
        for (let x = 0; x < N; x++) {
            const i = idx(x, y);
            const c = colorForTemperature(temperature[i]);
            const p = i * 4;
            image.data[p + 0] = c[0];
            image.data[p + 1] = c[1];
            image.data[p + 2] = c[2];
            image.data[p + 3] = 255;
        }
    }

    const tiny = document.createElement("canvas");
    tiny.width = N;
    tiny.height = N;
    const tctx = tiny.getContext("2d");
    tctx.putImageData(image, 0, 0);

    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(tiny, 0, 0, canvas.width, canvas.height);
}

function drawObject(o) {
    const style = typeStyle[o.type];
    const x = o.x * S;
    const y = o.y * S;
    const w = o.w * S;
    const h = o.h * S;

    ctx.save();
    ctx.shadowColor = "rgba(0, 0, 0, 0.45)";
    ctx.shadowBlur = 14;
    ctx.shadowOffsetY = 5;

    if (o.type === "heater") {
        ctx.beginPath();
        ctx.arc(x + w / 2, y + h / 2, Math.max(w, h) * 0.68, 0, Math.PI * 2);
        ctx.fillStyle = style.fill;
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = style.stroke;
        ctx.stroke();
    } else {
        ctx.fillStyle = o.type === "ice"
            ? `rgba(56, 189, 248, ${0.25 + 0.65 * iceMass})`
            : style.fill;

        ctx.strokeStyle = style.stroke;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.roundRect(x, y, w, h, 10);
        ctx.fill();
        ctx.stroke();
    }

    ctx.shadowBlur = 0;
    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 13px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    let label = style.label;
    if (o.type === "ice") {
        label = `ICE ${Math.round(iceMass * 100)}%`;
    }

    ctx.fillText(label, x + w / 2, y + h / 2);
    ctx.restore();
}

function drawGrid() {
    ctx.save();
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = 1;
    for (let k = 0; k <= N; k += 10) {
        ctx.beginPath();
        ctx.moveTo(k * S, 0);
        ctx.lineTo(k * S, canvas.height);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(0, k * S);
        ctx.lineTo(canvas.width, k * S);
        ctx.stroke();
    }
    ctx.restore();
}

function updateMetrics() {
    let maxT = -1000;
    for (let i = 0; i < temperature.length; i++) {
        if (temperature[i] > maxT) maxT = temperature[i];
    }

    document.getElementById("iceMetric").textContent = `${(iceMass * 100).toFixed(1)}%`;
    document.getElementById("tempMetric").textContent = `${maxT.toFixed(1)} °C`;
    document.getElementById("timeMetric").textContent = `${simulatedTime.toFixed(1)} s`;

    let status = "Safe";
    let advice = "The ice is still protected. Try moving the insulator to see how the heat path changes.";

    if (iceMass < 0.75) {
        status = "Melting";
        advice = "The ice is melting. Put an insulator between the heat source and the ice or move the conductor away from the ice.";
    }

    if (iceMass < 0.25) {
        status = "Critical";
        advice = "The defense is weak. The heat path reaches the ice too directly.";
    }

    if (iceMass <= 0.001) {
        status = "Melted";
        advice = "The ice has melted. Press Reset heat or choose Good defense to test a better layout.";
    }

    document.getElementById("statusMetric").textContent = status;
    document.getElementById("adviceBox").textContent = advice;
}

function draw() {
    drawHeatMap();
    drawGrid();
    for (const o of objects) {
        drawObject(o);
    }
}

function loop() {
    document.getElementById("speedLabel").textContent = String(getValue("speedInput"));
    document.getElementById("powerLabel").textContent = String(getValue("powerInput"));
    document.getElementById("alphaLabel").textContent = getValue("alphaInput").toFixed(2);

    if (!paused && iceMass > 0) {
        const speed = getValue("speedInput");
        for (let k = 0; k < speed; k++) {
            stepSimulation();
        }
    }

    draw();
    updateMetrics();
    requestAnimationFrame(loop);
}

document.getElementById("pauseBtn").addEventListener("click", () => {
    paused = !paused;
    document.getElementById("pauseBtn").textContent = paused ? "Resume" : "Pause";
});

document.getElementById("resetBtn").addEventListener("click", () => {
    resetTemperature();
});

document.getElementById("goodBtn").addEventListener("click", () => {
    setGoodDefense();
});

document.getElementById("badBtn").addEventListener("click", () => {
    setBadDefense();
});

document.getElementById("raceBtn").addEventListener("click", () => {
    setRaceLayout();
});

if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r) {
        this.beginPath();
        this.moveTo(x + r, y);
        this.lineTo(x + w - r, y);
        this.quadraticCurveTo(x + w, y, x + w, y + r);
        this.lineTo(x + w, y + h - r);
        this.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        this.lineTo(x + r, y + h);
        this.quadraticCurveTo(x, y + h, x, y + h - r);
        this.lineTo(x, y + r);
        this.quadraticCurveTo(x, y, x + r, y);
        this.closePath();
        return this;
    };
}

setGoodDefense();
loop();
</script>
</body>
</html>
    """,
    height=890,
    scrolling=False,
)
