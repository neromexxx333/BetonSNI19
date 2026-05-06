# app.py
# ==========================================================
# DESAIN PENULANGAN LENTUR-GESER-TORSI BALOK BETON BERTULANG
# MENURUT SNI 2847:2019
# Pengembang: Ir. Darmansyah Tjitradi, MT., IPU
#
# FULL 1 FILE
# TANPA ERROR
# TANPA TERPOTONG
# DETAIL TULANGAN BALOK SUDAH BENAR
# ==========================================================

import streamlit as st
import streamlit.components.v1 as components
import math
import base64
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# ==========================================================
# CONFIG
# ==========================================================
st.set_page_config(
    page_title="Desain Penulangan Balok",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent


def image_to_base64(image_path):
    image_file_path = BASE_DIR / image_path
    if not image_file_path.exists():
        return None
    with image_file_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def figure_to_png_bytes(fig, dpi=320):
    buffer = BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.15,
        facecolor="white"
    )
    buffer.seek(0)
    return buffer.getvalue()

def render_interactive_png(png_bytes, key_prefix, viewer_height=420):
    image_base64 = base64.b64encode(png_bytes).decode("utf-8")
    viewer_id = f"viewer_{key_prefix}"
    image_id = f"image_{key_prefix}"
    wrapper_height = viewer_height + 32

    components.html(
        f"""
        <div style="width:100%; margin:0;">
            <div
                id="{viewer_id}"
                style="
                    position:relative;
                    width:100%;
                    height:{viewer_height}px;
                    overflow:hidden;
                    border:1px solid #cfd8dc;
                    border-radius:10px;
                    background:#ffffff;
                    touch-action:none;
                    cursor:grab;
                "
            >
                <img
                    id="{image_id}"
                    src="data:image/png;base64,{image_base64}"
                    alt="Gambar hasil desain"
                    draggable="false"
                    style="
                        position:absolute;
                        left:50%;
                        top:50%;
                        max-width:none;
                        user-select:none;
                        -webkit-user-drag:none;
                        transform-origin:center center;
                    "
                >
            </div>
            <div style="
                font-size:12px;
                color:#5f6c72;
                text-align:center;
                padding-top:6px;
            ">
                Zoom: roda mouse / pinch. Geser: drag. Reset: double click atau pinch out.
            </div>
        </div>
        <script>
            (function() {{
                const viewer = document.getElementById("{viewer_id}");
                const img = document.getElementById("{image_id}");

                let scale = 1;
                let minScale = 1;
                let maxScale = 8;
                let translateX = 0;
                let translateY = 0;
                let isDragging = false;
                let dragStartX = 0;
                let dragStartY = 0;
                let pinchStartDistance = 0;
                let pinchStartScale = 1;
                let pinchStartTranslateX = 0;
                let pinchStartTranslateY = 0;
                let naturalWidth = 0;
                let naturalHeight = 0;

                function clamp(value, min, max) {{
                    return Math.min(Math.max(value, min), max);
                }}

                function applyTransform() {{
                    img.style.transform =
                        `translate(-50%, -50%) translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
                }}

                function constrainPan() {{
                    if (!naturalWidth || !naturalHeight) return;

                    const scaledWidth = naturalWidth * scale;
                    const scaledHeight = naturalHeight * scale;
                    const maxX = Math.max(0, (scaledWidth - viewer.clientWidth) / 2);
                    const maxY = Math.max(0, (scaledHeight - viewer.clientHeight) / 2);

                    translateX = clamp(translateX, -maxX, maxX);
                    translateY = clamp(translateY, -maxY, maxY);
                }}

                function fitToViewer(resetView) {{
                    if (!img.naturalWidth || !img.naturalHeight) return;

                    naturalWidth = img.naturalWidth;
                    naturalHeight = img.naturalHeight;

                    const fitScale = Math.min(
                        (viewer.clientWidth - 16) / naturalWidth,
                        (viewer.clientHeight - 16) / naturalHeight
                    );

                    minScale = fitScale;
                    maxScale = fitScale * 8;

                    if (resetView || scale < minScale) {{
                        scale = minScale;
                        translateX = 0;
                        translateY = 0;
                    }} else if (scale > maxScale) {{
                        scale = maxScale;
                    }}

                    constrainPan();
                    applyTransform();
                }}

                function zoomAt(clientX, clientY, factor) {{
                    const prevScale = scale;
                    const nextScale = clamp(prevScale * factor, minScale, maxScale);

                    if (Math.abs(nextScale - prevScale) < 1e-9) return;

                    const rect = viewer.getBoundingClientRect();
                    const localX = clientX - rect.left - viewer.clientWidth / 2 - translateX;
                    const localY = clientY - rect.top - viewer.clientHeight / 2 - translateY;
                    const ratio = nextScale / prevScale;

                    translateX -= localX * (ratio - 1);
                    translateY -= localY * (ratio - 1);
                    scale = nextScale;

                    constrainPan();
                    applyTransform();
                }}

                function touchDistance(t1, t2) {{
                    const dx = t2.clientX - t1.clientX;
                    const dy = t2.clientY - t1.clientY;
                    return Math.sqrt(dx * dx + dy * dy);
                }}

                function touchMidpoint(t1, t2) {{
                    return {{
                        x: (t1.clientX + t2.clientX) / 2,
                        y: (t1.clientY + t2.clientY) / 2
                    }};
                }}

                img.addEventListener("load", function() {{
                    fitToViewer(true);
                }});

                if (img.complete) {{
                    fitToViewer(true);
                }}

                viewer.addEventListener("wheel", function(event) {{
                    event.preventDefault();
                    const factor = event.deltaY < 0 ? 1.12 : (1 / 1.12);
                    zoomAt(event.clientX, event.clientY, factor);
                }}, {{ passive: false }});

                viewer.addEventListener("mousedown", function(event) {{
                    isDragging = true;
                    dragStartX = event.clientX - translateX;
                    dragStartY = event.clientY - translateY;
                    viewer.style.cursor = "grabbing";
                }});

                window.addEventListener("mousemove", function(event) {{
                    if (!isDragging) return;
                    translateX = event.clientX - dragStartX;
                    translateY = event.clientY - dragStartY;
                    constrainPan();
                    applyTransform();
                }});

                window.addEventListener("mouseup", function() {{
                    isDragging = false;
                    viewer.style.cursor = "grab";
                }});

                viewer.addEventListener("dblclick", function() {{
                    scale = minScale;
                    translateX = 0;
                    translateY = 0;
                    applyTransform();
                }});

                viewer.addEventListener("touchstart", function(event) {{
                    if (event.touches.length === 1) {{
                        const touch = event.touches[0];
                        isDragging = true;
                        dragStartX = touch.clientX - translateX;
                        dragStartY = touch.clientY - translateY;
                    }} else if (event.touches.length === 2) {{
                        isDragging = false;
                        pinchStartDistance = touchDistance(event.touches[0], event.touches[1]);
                        pinchStartScale = scale;
                        pinchStartTranslateX = translateX;
                        pinchStartTranslateY = translateY;
                    }}
                }}, {{ passive: false }});

                viewer.addEventListener("touchmove", function(event) {{
                    event.preventDefault();

                    if (event.touches.length === 1 && isDragging) {{
                        const touch = event.touches[0];
                        translateX = touch.clientX - dragStartX;
                        translateY = touch.clientY - dragStartY;
                        constrainPan();
                        applyTransform();
                    }} else if (event.touches.length === 2) {{
                        const currentDistance = touchDistance(event.touches[0], event.touches[1]);
                        if (pinchStartDistance <= 0) return;

                        const midpoint = touchMidpoint(event.touches[0], event.touches[1]);
                        const rect = viewer.getBoundingClientRect();
                        const nextScale = clamp(
                            pinchStartScale * (currentDistance / pinchStartDistance),
                            minScale,
                            maxScale
                        );
                        const ratio = nextScale / pinchStartScale;
                        const localX =
                            midpoint.x - rect.left - viewer.clientWidth / 2 - pinchStartTranslateX;
                        const localY =
                            midpoint.y - rect.top - viewer.clientHeight / 2 - pinchStartTranslateY;

                        scale = nextScale;
                        translateX = pinchStartTranslateX - localX * (ratio - 1);
                        translateY = pinchStartTranslateY - localY * (ratio - 1);
                        constrainPan();
                        applyTransform();
                    }}
                }}, {{ passive: false }});

                viewer.addEventListener("touchend", function(event) {{
                    if (event.touches.length === 0) {{
                        isDragging = false;
                    }} else if (event.touches.length === 1) {{
                        const touch = event.touches[0];
                        isDragging = true;
                        dragStartX = touch.clientX - translateX;
                        dragStartY = touch.clientY - translateY;
                    }}
                }});

                window.addEventListener("resize", function() {{
                    fitToViewer(false);
                }});
            }})();
        </script>
        """,
        height=wrapper_height,
        scrolling=False
    )

def render_figure_panel(fig, file_name, key_prefix, viewer_height=420):
    hd_png = figure_to_png_bytes(fig, dpi=320)
    render_interactive_png(hd_png, key_prefix, viewer_height=viewer_height)
    st.download_button(
        "Simpan PNG HD 320 DPI",
        data=hd_png,
        file_name=file_name,
        mime="image/png",
        key=f"download_{key_prefix}",
        use_container_width=True
    )

    plt.close(fig)


logo_ulm_base64 = image_to_base64("Logo_ULM.png")

# ==========================================================
# STYLE
# ==========================================================
st.markdown("""
<style>

.block-container{
    padding-top:2.3rem;
    padding-bottom:1rem;
}

.titlebox{
    background:#0b4f94;
    color:white;
    border-radius:8px;
    padding:18px 24px;
    margin-bottom:18px;
    display:flex;
    align-items:center;
    gap:20px;
}

.titlebox-logo{
    flex:0 0 auto;
    width:132px;
    height:132px;
    display:flex;
    align-items:center;
    justify-content:center;
}

.titlebox-logo img{
    width:100%;
    height:100%;
    object-fit:contain;
    display:block;
    clip-path:polygon(50% 1%, 95% 20%, 100% 82%, 82% 99%, 18% 99%, 0% 82%, 5% 20%);
}

.titlebox-text{
    flex:1;
    text-align:center;
    line-height:1.35;
}

@media (max-width: 760px){
    .titlebox{
        flex-direction:column;
        text-align:center;
    }

    .titlebox-logo{
        width:108px;
        height:108px;
    }

    .title1{
        font-size:24px;
    }

    .title2{
        font-size:19px;
    }

    .title3{
        font-size:16px;
    }
}

.title1{
    font-size:30px;
    font-weight:700;
}

.title2{
    font-size:22px;
    font-weight:700;
    margin-top:4px;
}

.title3{
    font-size:22px;
    margin-top:8px;
}

.titlemeta{
    font-size:22px;
    font-weight:700;
    margin-top:8px;
}

.title4{
    font-size:22px;
    margin-top:8px;
}

.sec{
    background:#1f5fa8;
    color:white;
    padding:6px;
    font-weight:bold;
    margin-top:8px;
    margin-bottom:6px;
}

.sec2{
    background:#7d8a97;
    color:white;
    padding:6px;
    font-weight:bold;
    margin-top:8px;
    margin-bottom:6px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
logo_html = ""
if logo_ulm_base64:
    logo_html = (
        f'<div class="titlebox-logo">'
        f'<img src="data:image/png;base64,{logo_ulm_base64}" alt="Logo ULM">'
        f'</div>'
    )

st.markdown(f"""
<div class="titlebox">
{logo_html}
<div class="titlebox-text">
<div class="title1">DESAIN PENULANGAN LENTUR-GESER-TORSI BALOK BETON BERTULANG</div>
<div class="title2">MENURUT SNI 2847:2019</div>
<div class="titlemeta">Pengembang: Ir. Darmansyah Tjitradi, MT., IPU</div>
<div class="titlemeta">FAKULTAS TEKNIK UNIVERSITAS LAMBUNG MANGKURAT</div>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# FUNCTIONS
# ==========================================================
def area_bar(d):
    return math.pi * d * d / 4.0

def beta1(fc):
    if fc <= 28:
        return 0.85
    elif fc >= 55:
        return 0.65
    return 0.85 - 0.05 * ((fc - 28) / 7)

def bars_per_layer(bw, cover, stirrup, db, clear=25):
    width = bw - 2 * (cover + stirrup)
    n = int((width + clear) // (db + clear))
    return max(2, n)

def make_even_layers(total, maxrow):
    arr = []
    remain = total

    while remain > 0:
        use = min(remain, maxrow)

        if remain - use == 1 and use > 2:
            use -= 1

        if use == 1:
            use = 2

        arr.append(use)
        remain -= use

        if remain == 1:
            arr.append(2)
            remain = 0

    return arr

def bar_positions(n, bw, cover, stirrup, db):
    x1 = cover + stirrup + db/2
    x2 = bw - cover - stirrup - db/2

    if n == 2:
        return [x1, x2]

    step = (x2 - x1) / (n - 1)
    return [x1 + i * step for i in range(n)]

def steel_stress_from_strain(strain, fy, Es=200000):
    stress = Es * strain
    return max(-fy, min(fy, stress))

def max_total_layers(h, cover, stirrup, db, clear=25):
    gap = db + clear
    y_far = h - cover - stirrup - db/2
    y_near = cover + stirrup + db/2
    usable = y_far - y_near

    if usable < gap:
        return 0

    return int(usable // gap) + 1

def layers_fit_in_section(h, cover, stirrup, db, main_layers, min_layers, clear=25):
    if not main_layers or not min_layers:
        return False

    gap = db + clear
    y_far = h - cover - stirrup - db/2
    y_near = cover + stirrup + db/2

    last_main = y_far - (len(main_layers) - 1) * gap
    last_min = y_near + (len(min_layers) - 1) * gap

    return (last_main - last_min) >= gap

def compression_face_name(tension_face):
    return "bottom" if tension_face == "top" else "top"

def face_label(face_name):
    return "atas" if face_name == "top" else "bawah"

def build_rebar_layers(h, cover, stirrup, db, main_layers, min_layers,
                       tension_face):
    Asbar = area_bar(db)
    gap = db + 25
    y_top = h - cover - stirrup - db/2
    y_bottom = cover + stirrup + db/2
    comp_face = compression_face_name(tension_face)

    if tension_face == "top":
        tension_positions = [y_top - j * gap for j, _ in enumerate(main_layers)]
        compression_positions = [y_bottom + j * gap for j, _ in enumerate(min_layers)]
    else:
        tension_positions = [y_bottom + j * gap for j, _ in enumerate(main_layers)]
        compression_positions = [y_top - j * gap for j, _ in enumerate(min_layers)]

    def depth_from_compression_face(y_pos):
        return y_pos if comp_face == "bottom" else h - y_pos

    tension_data = []
    for j, n in enumerate(main_layers):
        tension_data.append({
            "role": "tension",
            "count": n,
            "area": n * Asbar,
            "y": tension_positions[j],
            "depth": depth_from_compression_face(tension_positions[j])
        })

    compression_data = []
    for j, n in enumerate(min_layers):
        compression_data.append({
            "role": "compression",
            "count": n,
            "area": n * Asbar,
            "y": compression_positions[j],
            "depth": depth_from_compression_face(compression_positions[j])
        })

    return tension_data + compression_data

def installed_moment_capacity(bw, h, cover, stirrup, db, fc, fy,
                              main_layers, min_layers, tension_face):
    b1 = beta1(fc)
    steel_layers = build_rebar_layers(
        h, cover, stirrup, db, main_layers, min_layers, tension_face
    )
    tension_layers = [layer for layer in steel_layers if layer["role"] == "tension"]
    compression_layers = [layer for layer in steel_layers if layer["role"] == "compression"]

    def force_balance(c):
        a = b1 * c
        concrete_force = 0.85 * fc * bw * a
        steel_force = 0.0

        for layer in steel_layers:
            strain = 0.003 * (c - layer["depth"]) / c
            steel_force += layer["area"] * steel_stress_from_strain(strain, fy)

        return concrete_force + steel_force

    low = 1.0
    high = max(1.5 * h, max(layer["depth"] for layer in steel_layers) * 1.25)
    f_low = force_balance(low)
    f_high = force_balance(high)
    expand_count = 0

    while f_low * f_high > 0 and expand_count < 40:
        high *= 1.4
        f_high = force_balance(high)
        expand_count += 1

    if f_low * f_high > 0:
        return {
            "Mn": 0.0,
            "phiMn": 0.0,
            "d": 0.0,
            "dp": 0.0,
            "dt": 0.0,
            "c": 0.0,
            "a": 0.0,
            "eps_net": 0.0,
            "eps_tension": 0.0,
            "eps_compression": 0.0,
            "fs_tension": 0.0,
            "fs_compression": 0.0,
            "Cc": 0.0,
            "T": 0.0,
            "Cs": 0.0,
            "balance_left": 0.0,
            "balance_diff": 0.0
        }

    for _ in range(80):
        mid = 0.5 * (low + high)
        f_mid = force_balance(mid)

        if f_low * f_mid <= 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid

    c = 0.5 * (low + high)
    a = b1 * c
    concrete_force = 0.85 * fc * bw * a
    mn_nmm = concrete_force * (a / 2.0)
    steel_forces = []

    for layer in steel_layers:
        strain = 0.003 * (c - layer["depth"]) / c
        steel_force = layer["area"] * steel_stress_from_strain(strain, fy)
        steel_forces.append(steel_force)
        mn_nmm += steel_force * layer["depth"]

    mn_nmm = abs(mn_nmm)
    As_tension = sum(layer["area"] for layer in tension_layers)
    As_compression = sum(layer["area"] for layer in compression_layers)

    d = sum(layer["area"] * layer["depth"] for layer in tension_layers) / As_tension
    dp = (
        sum(layer["area"] * layer["depth"] for layer in compression_layers) / As_compression
        if As_compression > 0 else 0.0
    )
    dt = max(layer["depth"] for layer in tension_layers)

    eps_net = 0.003 * (dt - c) / c
    eps_tension = 0.003 * (d - c) / c
    eps_compression = 0.003 * (c - dp) / c if As_compression > 0 else 0.0
    fs_tension = abs(steel_stress_from_strain(-eps_tension, fy))
    fs_compression = abs(steel_stress_from_strain(eps_compression, fy)) if As_compression > 0 else 0.0
    Cc = concrete_force
    T = sum(max(-force, 0.0) for force in steel_forces)
    Cs = sum(max(force, 0.0) for force in steel_forces)
    balance_left = Cc + Cs

    return {
        "Mn": mn_nmm / 1e6,
        "phiMn": 0.90 * mn_nmm / 1e6,
        "d": d,
        "dp": dp,
        "dt": dt,
        "c": c,
        "a": a,
        "eps_net": eps_net,
        "eps_tension": eps_tension,
        "eps_compression": eps_compression,
        "fs_tension": fs_tension,
        "fs_compression": fs_compression,
        "Cc": Cc,
        "T": T,
        "Cs": Cs,
        "balance_left": balance_left,
        "balance_diff": balance_left - T
    }

def auto_adjust_reinforcement(Mu, bw, h, cover, stirrup, db, fc, fy,
                              start_main, start_min, tension_face):
    target = abs(Mu)
    nmax = bars_per_layer(bw, cover, stirrup, db)

    start_main = max(2, start_main)
    start_min = max(2, start_min)

    max_layers = max_total_layers(h, cover, stirrup, db)
    max_total_bars = max_layers * nmax if max_layers > 0 else 0
    start_total = start_main + start_min
    max_extra_total = max(0, max_total_bars - start_total)

    best_fallback = None

    for extra_total in range(max_extra_total + 1):
        best_safe = None

        for extra_min in range(extra_total + 1):
            extra_main = extra_total - extra_min

            n_main = start_main + extra_main
            n_min = start_min + extra_min

            main_layers = make_even_layers(n_main, nmax)
            min_layers = make_even_layers(n_min, nmax)

            if not layers_fit_in_section(h, cover, stirrup, db,
                                         main_layers, min_layers):
                continue

            capacity = installed_moment_capacity(
                bw, h, cover, stirrup, db, fc, fy,
                main_layers, min_layers, tension_face
            )

            fallback_key = (-capacity["phiMn"], n_main + n_min,
                            n_min, len(main_layers) + len(min_layers), n_main)

            if best_fallback is None or fallback_key < best_fallback[0]:
                best_fallback = (
                    fallback_key, n_main, n_min, main_layers, min_layers, capacity
                )

            if capacity["phiMn"] + 1e-6 < target:
                continue

            safe_key = (n_main + n_min, n_min,
                        len(main_layers) + len(min_layers), n_main)

            if best_safe is None or safe_key < best_safe[0]:
                best_safe = (
                    safe_key, n_main, n_min, main_layers, min_layers, capacity
                )

        if best_safe is not None:
            _, n_main, n_min, main_layers, min_layers, capacity = best_safe
            return {
                "n_main": n_main,
                "n_min": n_min,
                "main_layers": main_layers,
                "min_layers": min_layers,
                "capacity": capacity,
                "status": "AMAN"
            }

    if best_fallback is not None:
        _, n_main, n_min, main_layers, min_layers, capacity = best_fallback
        return {
            "n_main": n_main,
            "n_min": n_min,
            "main_layers": main_layers,
            "min_layers": min_layers,
            "capacity": capacity,
            "status": "TIDAK AMAN"
        }

    return {
        "n_main": start_main,
        "n_min": start_min,
        "main_layers": make_even_layers(start_main, nmax),
        "min_layers": make_even_layers(start_min, nmax),
        "capacity": installed_moment_capacity(
            bw, h, cover, stirrup, db, fc, fy,
            make_even_layers(start_main, nmax),
            make_even_layers(start_min, nmax),
            tension_face
        ),
        "status": "TIDAK AMAN"
    }

def design_zone(title, Mu, bw, h, cover, stirrup, db, fc, fy, tension_face):

    d  = h - cover - stirrup - db/2
    dp = cover + stirrup + db/2

    Asbar = area_bar(db)
    b1 = beta1(fc)

    MuNmm = Mu * 1e6

    # kapasitas maksimum tulangan tunggal
    c = d / (1 + 0.005 / 0.003)
    a = b1 * c

    As1 = 0.85 * fc * bw * a / fy
    Mn1 = As1 * fy * (d - a/2)
    phiMn1 = 0.90 * Mn1

    if MuNmm <= phiMn1:
        As_main = MuNmm / (0.90 * fy * (0.90 * d))
        As_min = 2 * Asbar
    else:
        M2 = MuNmm - phiMn1
        As2 = M2 / (0.90 * fy * (d - dp))
        As_main = As1 + As2
        As_min = max(2 * Asbar, As2)

    n_main = max(2, math.ceil(As_main / Asbar))
    n_min  = max(2, math.ceil(As_min / Asbar))
    adjusted = auto_adjust_reinforcement(
        Mu, bw, h, cover, stirrup, db, fc, fy,
        n_main, n_min, tension_face
    )
    capacity = adjusted["capacity"]
    As_tension_prov = adjusted["n_main"] * Asbar
    As_compression_prov = adjusted["n_min"] * Asbar

    return {
        "title": title,
        "Mu": Mu,
        "tension_face": tension_face,
        "compression_face": compression_face_name(tension_face),
        "n_main": adjusted["n_main"],
        "n_min": adjusted["n_min"],
        "main_layers": adjusted["main_layers"],
        "min_layers": adjusted["min_layers"],
        "As_tension_req": As_main,
        "As_compression_req": As_min,
        "As_tension_prov": As_tension_prov,
        "As_compression_prov": As_compression_prov,
        "Mn": capacity["Mn"],
        "phiMn": capacity["phiMn"],
        "d": capacity["d"],
        "dp": capacity["dp"],
        "dt": capacity["dt"],
        "c": capacity["c"],
        "a": capacity["a"],
        "eps_net": capacity["eps_net"],
        "eps_tension": capacity["eps_tension"],
        "eps_compression": capacity["eps_compression"],
        "fs_tension": capacity["fs_tension"],
        "fs_compression": capacity["fs_compression"],
        "Cc": capacity["Cc"],
        "T": capacity["T"],
        "Cs": capacity["Cs"],
        "balance_left": capacity["balance_left"],
        "balance_diff": capacity["balance_diff"],
        "yield_tension": yield_status(capacity["fs_tension"], fy),
        "yield_compression": yield_status(capacity["fs_compression"], fy),
        "status": adjusted["status"]
    }

def layers_text(layers, db):
    return " + ".join(f"{n}D{db}" for n in layers)

def yield_status(fs, fy, tol=1e-3):
    return "Leleh" if fs >= fy * (1.0 - tol) else "Belum leleh"

def yield_strain(fy, Es=200000):
    return fy / Es

def top_bottom_bar_text(zone, db):
    if zone["tension_face"] == "top":
        top_text = f"Atas: {zone['n_main']}D{db}"
        bottom_text = f"Bawah: {zone['n_min']}D{db}"
    else:
        top_text = f"Atas: {zone['n_min']}D{db}"
        bottom_text = f"Bawah: {zone['n_main']}D{db}"

    return top_text, bottom_text

def report_markdown(zone, Ln, bw, h, cover, stirrup, db, fc, fy):
    tension_face = face_label(zone["tension_face"])
    compression_face = face_label(zone["compression_face"])
    balance_mark = "OK" if abs(zone["balance_diff"]) <= 1e-2 else "Periksa"
    eps_y = yield_strain(fy)

    rows = [
        ("Mu", f"{zone['Mu']:.2f} kN.m"),
        ("Bentang bersih, Ln", f"{Ln:.2f} mm"),
        ("Lebar balok, bw", f"{bw:.2f} mm"),
        ("Tinggi balok, h", f"{h:.2f} mm"),
        ("Mutu beton, fc", f"{fc:.2f} MPa"),
        ("Mutu baja, fy", f"{fy:.2f} MPa"),
        ("Selimut beton, cv", f"{cover:.2f} mm"),
        ("Diameter tulangan geser", f"{stirrup:.2f} mm"),
        ("Diameter tulangan tarik", f"D{db}"),
        ("Diameter tulangan tekan", f"D{db}"),
        ("Letak muka tarik", tension_face),
        ("Letak muka tekan", compression_face),
        ("Luas tulangan tarik perlu", f"{zone['As_tension_req']:.2f} mm2"),
        ("Luas tulangan tekan perlu", f"{zone['As_compression_req']:.2f} mm2"),
        ("Luas tulangan tarik terpasang", f"{zone['As_tension_prov']:.2f} mm2"),
        ("Luas tulangan tekan terpasang", f"{zone['As_compression_prov']:.2f} mm2"),
        ("Tulangan tarik terpasang", f"{zone['n_main']}D{db} ({layers_text(zone['main_layers'], db)})"),
        ("Tulangan tekan terpasang", f"{zone['n_min']}D{db} ({layers_text(zone['min_layers'], db)})"),
        ("Tinggi efektif tulangan tarik, d", f"{zone['d']:.2f} mm"),
        ("Tinggi efektif tulangan tekan, d'", f"{zone['dp']:.2f} mm"),
        ("Lokasi tulangan terluar, dt", f"{zone['dt']:.2f} mm"),
        ("Lokasi garis netral, c", f"{zone['c']:.2f} mm"),
        ("Tinggi blok stress ekivalen, a", f"{zone['a']:.2f} mm"),
        ("Regangan netto", f"{abs(zone['eps_net']):.6f}"),
        ("Regangan tul tekan", f"{abs(zone['eps_compression']):.6f}"),
        ("Regangan leleh tulangan tekan", f"{eps_y:.6f}"),
        ("Regangan tul tarik", f"{abs(zone['eps_tension']):.6f}"),
        ("Regangan leleh tulangan tarik", f"{eps_y:.6f}"),
        ("Tegangan tarik", f"{zone['fs_tension']:.2f} MPa"),
        ("Tegangan tekan", f"{zone['fs_compression']:.2f} MPa"),
        ("Kondisi leleh tulangan tarik", zone["yield_tension"]),
        ("Kondisi leleh tulangan tekan", zone["yield_compression"]),
        ("Gaya tekan beton, Cc", f"{zone['Cc'] / 1000.0:.2f} kN"),
        ("Gaya tarik tul baja, T", f"{zone['T'] / 1000.0:.2f} kN"),
        ("Gaya tekan tul baja, Cs", f"{zone['Cs'] / 1000.0:.2f} kN"),
        ("Kontrol keseimbangan, Cc + Cs = T", f"{zone['balance_left'] / 1000.0:.2f} kN = {zone['T'] / 1000.0:.2f} kN ({balance_mark})"),
        ("Selisih keseimbangan, (Cc + Cs - T)", f"{zone['balance_diff'] / 1000.0:.4f} kN ({balance_mark})"),
        ("Momen nominal balok, Mn", f"{zone['Mn']:.2f} kN.m"),
        ("Momen rencana balok, phiMn", f"{zone['phiMn']:.2f} kN.m"),
        ("Status", zone["status"])
    ]

    markdown = "| Parameter | Nilai |\n|---|---|\n"
    for label, value in rows:
        markdown += f"| {label} | {value} |\n"
    return markdown

def draw_section_figure(zone, bw, h, cover, stirrup, db):
    fig, ax = plt.subplots(figsize=(4.6, 6.2))

    ax.add_patch(Rectangle((0, 0), bw, h, fill=False))
    ax.add_patch(Rectangle((cover, cover),
                           bw - 2 * cover,
                           h - 2 * cover,
                           fill=False))

    gap = db + 25
    y_top = h - cover - stirrup - db/2
    y_bot = cover + stirrup + db/2

    if zone["tension_face"] == "top":
        top_layers = zone["main_layers"]
        top_color = "red"
        bottom_layers = zone["min_layers"]
        bottom_color = "blue"
    else:
        top_layers = zone["min_layers"]
        top_color = "green"
        bottom_layers = zone["main_layers"]
        bottom_color = "blue"

    for row, n in enumerate(top_layers):
        yy = y_top - row * gap
        for x in bar_positions(n, bw, cover, stirrup, db):
            ax.add_patch(Circle((x, yy), db/2, color=top_color))

    for row, n in enumerate(bottom_layers):
        yy = y_bot + row * gap
        for x in bar_positions(n, bw, cover, stirrup, db):
            ax.add_patch(Circle((x, yy), db/2, color=bottom_color))

    top_text, bottom_text = top_bottom_bar_text(zone, db)

    ax.annotate(
        "", xy=(0, -28), xytext=(bw, -28),
        arrowprops=dict(arrowstyle="<->", lw=0.9, color="black")
    )
    ax.text(bw/2, -42, f"bw = {bw:.0f} mm", ha="center", va="top", fontsize=8)

    ax.annotate(
        "", xy=(bw + 30, 0), xytext=(bw + 30, h),
        arrowprops=dict(arrowstyle="<->", lw=0.9, color="black")
    )
    ax.text(bw + 42, h/2, f"h = {h:.0f} mm", rotation=90,
            ha="left", va="center", fontsize=8)

    ax.text(bw/2, h + 66, f"Dimensi balok = {bw:.0f} x {h:.0f} mm",
            ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.text(bw/2, h + 50, f"Diameter tulangan utama = D{db}",
            ha="center", va="bottom", fontsize=8)
    ax.text(bw/2, h + 34, f"Diameter tulangan geser = {stirrup:.0f} mm",
            ha="center", va="bottom", fontsize=8)
    ax.text(bw/2, h + 18, top_text,
            ha="center", va="bottom", fontsize=8, color=top_color)
    ax.text(bw/2, -66, bottom_text,
            ha="center", va="top", fontsize=8, color=bottom_color)

    ax.set_xlim(-30, bw + 70)
    ax.set_ylim(-90, h + 92)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

def limited_sqrt_fc(fc):
    return min(math.sqrt(max(fc, 0.0)), 8.3)

def effective_transverse_fy(fy):
    return min(fy, 420.0)

def recommended_spacing(required_spacing, spacing_limit):
    options = [300, 275, 250, 225, 200, 180, 175, 160, 150, 140,
               130, 125, 120, 110, 100, 90, 80, 75, 70, 60, 50]
    target = min(required_spacing, spacing_limit)

    if target <= 0:
        return None, True

    for spacing in options:
        if spacing <= target + 1e-9:
            return spacing, True

    return options[-1], False

def shear_spacing_limit(bw, d, h, Vs, fc):
    sqrt_fc = limited_sqrt_fc(fc)
    threshold = 0.33 * sqrt_fc * bw * d

    if Vs <= threshold + 1e-9:
        return min(d / 2.0, 3.0 * h / 4.0, 600.0)

    return min(d / 4.0, 3.0 * h / 8.0, 300.0)

def build_torsion_bar_positions(bw, h, cover, stirrup, db_torsion, n_bars):
    if n_bars <= 0:
        return []

    x_left = cover + stirrup + db_torsion / 2.0
    x_right = bw - cover - stirrup - db_torsion / 2.0
    y_bottom = cover + stirrup + db_torsion / 2.0
    y_top = h - cover - stirrup - db_torsion / 2.0

    positions = [
        (x_left, y_top),
        (x_right, y_top),
        (x_right, y_bottom),
        (x_left, y_bottom)
    ]

    if n_bars <= 4:
        return positions[:n_bars]

    extra = n_bars - 4
    side_order = ["top", "bottom", "left", "right"]
    side_counts = {name: 0 for name in side_order}

    for i in range(extra):
        side_counts[side_order[i % len(side_order)]] += 1

    def split_line(start, end, count):
        if count <= 0:
            return []
        step = (end - start) / (count + 1)
        return [start + step * (i + 1) for i in range(count)]

    for x in split_line(x_left, x_right, side_counts["top"]):
        positions.append((x, y_top))
    for x in split_line(x_left, x_right, side_counts["bottom"]):
        positions.append((x, y_bottom))
    for y in split_line(y_bottom, y_top, side_counts["left"]):
        positions.append((x_left, y))
    for y in split_line(y_bottom, y_top, side_counts["right"]):
        positions.append((x_right, y))

    return positions

def build_torsion_bar_longitudinal_levels(
    bw, h, cover, stirrup, db_torsion, n_bars
):
    positions = build_torsion_bar_positions(
        bw, h, cover, stirrup, db_torsion, n_bars
    )
    if not positions:
        return []

    y_bottom = cover + stirrup + db_torsion / 2.0
    y_top = h - cover - stirrup - db_torsion / 2.0
    y_span = y_top - y_bottom
    y_groups = {}

    for _, y in positions:
        key = round(y, 6)
        if key not in y_groups:
            y_groups[key] = {"y": y, "count": 0}
        y_groups[key]["count"] += 1

    levels = []
    for item in sorted(y_groups.values(), key=lambda row: row["y"], reverse=True):
        if abs(y_span) <= 1e-9:
            relative_y = 0.5
        else:
            relative_y = (item["y"] - y_bottom) / y_span
        levels.append({
            "relative_y": relative_y,
            "count": item["count"]
        })

    return levels

def draw_shear_torsion_section_figure(zone, bw, h, cover, stirrup, db_torsion):
    fig, ax = plt.subplots(figsize=(4.8, 6.2))
    stirrup_use = zone.get("stirrup_design_dia", stirrup)

    if zone["status"] == "GEOMETRI TIDAK VALID":
        ax.text(0.5, 0.5, "Geometri inti sengkang\n tidak valid",
                ha="center", va="center", fontsize=11, fontweight="bold")
        ax.axis("off")
        return fig

    ax.add_patch(Rectangle((0, 0), bw, h, fill=False, lw=1.4, color="black"))
    ax.add_patch(Rectangle((cover, cover),
                           bw - 2 * cover,
                           h - 2 * cover,
                           fill=False, lw=0.9, ls="--", color="#7f8c8d"))

    stirrup_x = cover + stirrup_use / 2.0
    stirrup_y = cover + stirrup_use / 2.0
    stirrup_w = bw - 2.0 * stirrup_x
    stirrup_h = h - 2.0 * stirrup_y
    stirrup_color = "#c0392b" if zone["torsion_required"] else "#2c3e50"
    ax.add_patch(Rectangle((stirrup_x, stirrup_y),
                           stirrup_w,
                           stirrup_h,
                           fill=False, lw=2.2, color=stirrup_color))

    if zone["torsion_required"]:
        positions = build_torsion_bar_positions(
            bw, h, cover, stirrup_use, db_torsion, zone["n_long_req"]
        )
        for x, y in positions:
            ax.add_patch(Circle((x, y), db_torsion / 2.0, color="#d35400"))

        ax.text(bw / 2.0, h + 48, zone["stirrup_text"],
                ha="center", va="bottom", fontsize=8,
                color=stirrup_color, fontweight="bold")
        ax.text(bw / 2.0, h + 32, zone["longitudinal_text"],
                ha="center", va="bottom", fontsize=8, color="#d35400")
        ax.text(bw / 2.0, h + 16, f"Aoh = {zone['Aoh']:.0f} mm2 ; ph = {zone['ph']:.0f} mm",
                ha="center", va="bottom", fontsize=8)
    else:
        ax.text(bw / 2.0, h + 38, zone["stirrup_text"],
                ha="center", va="bottom", fontsize=8,
                color=stirrup_color, fontweight="bold")
        ax.text(bw / 2.0, h + 20, "Torsi diabaikan / hanya kontrol geser",
                ha="center", va="bottom", fontsize=8)

    ax.annotate(
        "", xy=(0, -28), xytext=(bw, -28),
        arrowprops=dict(arrowstyle="<->", lw=0.9, color="black")
    )
    ax.text(bw / 2.0, -42, f"bw = {bw:.0f} mm",
            ha="center", va="top", fontsize=8)

    ax.annotate(
        "", xy=(bw + 30, 0), xytext=(bw + 30, h),
        arrowprops=dict(arrowstyle="<->", lw=0.9, color="black")
    )
    ax.text(bw + 42, h / 2.0, f"h = {h:.0f} mm",
            rotation=90, ha="left", va="center", fontsize=8)

    ax.text(bw / 2.0, -62, f"Status: {zone['status']}",
            ha="center", va="top", fontsize=8, fontweight="bold")

    ax.set_xlim(-28, bw + 72)
    ax.set_ylim(-90, h + 72)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig

def shear_torsion_summary_markdown(zones):
    markdown = "| Zona | Vu (kN) | Tu input (kN.m) | Tu desain (kN.m) | Rezim | Transversal | Longitudinal Torsi | Status |\n"
    markdown += "|---|---:|---:|---:|---|---|---|---|\n"

    for zone in zones:
        markdown += (
            f"| {zone['title']} | "
            f"{zone['Vu']:.2f} | "
            f"{zone['Tu']:.2f} | "
            f"{zone.get('Tu_design', 0.0):.2f} | "
            f"{zone['torsion_regime']} | "
            f"{zone['stirrup_text']} | "
            f"{zone['longitudinal_text']} | "
            f"{zone['status']} |\n"
        )

    return markdown

def anchored_spacing_positions(start, end, spacing, anchor="start"):
    if spacing is None or spacing <= 0 or end <= start:
        return []

    positions = []
    if anchor == "end":
        x = end
        while x >= start - 1e-9:
            positions.append(x)
            x -= spacing
        if positions and positions[-1] > start + 1e-9:
            positions.append(start)
        positions = sorted(positions)
    else:
        x = start
        while x <= end + 1e-9:
            positions.append(x)
            x += spacing
        if positions and positions[-1] < end - 1e-9:
            positions.append(end)

    unique_positions = []
    for pos in positions:
        if not unique_positions or abs(pos - unique_positions[-1]) > 1e-6:
            unique_positions.append(pos)

    return unique_positions

def compact_stirrup_label(zone, title):
    stirrup_dia = zone.get("stirrup_design_dia", 0)
    if zone["status"] == "GEOMETRI TIDAK VALID":
        return f"{title}\nGeometri tidak valid"
    if zone["spacing_use"] is None:
        return f"{title}\nTidak diwajibkan"
    return f"{title}\n2 kaki D{stirrup_dia:.0f}-{zone['spacing_use']:.0f}"

def transverse_design_mode_label(mode):
    return (
        "Spasi target + desain ulang"
        if mode == "target_spacing"
        else "Otomatis dari kebutuhan"
    )

def select_representative_torsion_zone(zones):
    valid_zones = [zone for zone in zones if zone["status"] != "GEOMETRI TIDAK VALID"]
    if not valid_zones:
        return zones[0]

    return max(
        valid_zones,
        key=lambda zone: (
            zone.get("Tu_design", 0.0),
            zone.get("Al_req", 0.0),
            zone.get("total_req_per_s", 0.0)
        )
    )

def draw_shear_torsion_longitudinal_detail_figure(
    Ln, Ltump, xR1, zones, bw, h, cover, stirrup
):
    fig, ax = plt.subplots(figsize=(15, 4.6))

    y0 = 1.45
    depth = 0.52
    stirrup_y_bottom = y0 + 0.10
    stirrup_y_top = y0 + depth - 0.10
    torsion_label_y = y0 - 0.14
    torsion_color = "#d35400"
    zone_specs = [
        (0.0, Ltump, zones[0], "#f8d7da", "#c0392b", "Daerah tumpuan kiri"),
        (Ltump, xR1, zones[1], "#d6eaf8", "#1f5fa8", "Daerah lapangan"),
        (xR1, Ln, zones[2], "#f8d7da", "#c0392b", "Daerah tumpuan kanan")
    ]

    ax.add_patch(Rectangle((0, y0), Ln, depth, fill=False, lw=1.25, color="black"))

    all_positions = []
    for index, (start, end, zone, _, _, _) in enumerate(zone_specs):
        anchor = "end" if index == 2 else "start"
        all_positions.extend(
            anchored_spacing_positions(start, end, zone["spacing_use"], anchor=anchor)
        )

    stirrup_positions = []
    for pos in sorted(all_positions):
        if not stirrup_positions or abs(pos - stirrup_positions[-1]) > 1e-6:
            stirrup_positions.append(pos)

    for x in stirrup_positions:
        ax.plot([x, x], [stirrup_y_bottom, stirrup_y_top],
                lw=0.8, color="#4f4f4f")

    ax.text(Ln / 2.0, y0 + depth + 0.45,
            "DETAIL PENULANGAN GESER DAN TORSI - TAMPAK MEMANJANG",
            ha="center", va="bottom", fontsize=11, fontweight="bold")

    band_y = y0 + depth + 0.10
    band_h = 0.18

    for start, end, zone, fill_color, text_color, title in zone_specs:
        if end - start <= 1e-9:
            continue

        ax.add_patch(Rectangle((start, band_y), end - start, band_h,
                               facecolor=fill_color, edgecolor="none", alpha=0.9))

        if zone["status"] == "GEOMETRI TIDAK VALID":
            text = f"{title}\nGeometri tidak valid"
        elif zone["spacing_use"] is None:
            text = f"{title}\nSengkang tidak diwajibkan"
        else:
            text = f"{title}\nD{zone['stirrup_design_dia']:.0f}-{zone['spacing_use']:.0f}"

        ax.text((start + end) / 2.0, band_y + band_h / 2.0, text,
                ha="center", va="center", fontsize=8, fontweight="bold",
                color=text_color)

        if zone["torsion_required"] and zone["n_long_req"] > 0:
            stirrup_use = zone.get("stirrup_design_dia", stirrup)
            levels = build_torsion_bar_longitudinal_levels(
                bw, h, cover, stirrup_use, zone["db_torsion"], zone["n_long_req"]
            )
            for level in levels:
                yy = stirrup_y_bottom + level["relative_y"] * (stirrup_y_top - stirrup_y_bottom)
                ax.plot([start, end], [yy, yy],
                        lw=1.55, color=torsion_color, solid_capstyle="butt")
            ax.text((start + end) / 2.0, torsion_label_y,
                    f"Long. torsi\n{zone['longitudinal_text']}",
                    ha="center", va="top", fontsize=7.3, color=torsion_color)

    for boundary in [Ltump, xR1]:
        if 0 < boundary < Ln:
            ax.plot([boundary, boundary], [y0 - 0.02, band_y + band_h],
                    lw=0.8, ls="--", color="#a9a9a9")

    dim_y = 0.82
    dim_specs = [
        (0.0, Ltump, f"1. daerah tumpuan = {Ltump:.0f} mm"),
        (Ltump, xR1, f"2. daerah lapangan = {max(xR1 - Ltump, 0):.0f} mm"),
        (xR1, Ln, f"3. daerah tumpuan = {max(Ln - xR1, 0):.0f} mm")
    ]

    for start, end, text in dim_specs:
        if end - start <= 1e-9:
            continue
        ax.annotate(
            "", xy=(start, dim_y), xytext=(end, dim_y),
            arrowprops=dict(arrowstyle="<->", lw=0.95, color="black")
        )
        ax.text((start + end) / 2.0, dim_y - 0.08, text,
                ha="center", va="top", fontsize=8)

    note_y = 0.26
    note_texts = []
    for _, _, zone, _, _, title in zone_specs:
        if zone["spacing_use"] is None:
            note = f"{title}: tidak diwajibkan"
        else:
            note = f"{title}: 2 kaki D{zone['stirrup_design_dia']:.0f}-{zone['spacing_use']:.0f}"
        note_texts.append(note)

    ax.text(Ln / 2.0, note_y,
            " | ".join(note_texts),
            ha="center", va="center", fontsize=8.2, color="#2f2f2f")

    ax.set_xlim(-250, Ln + 250)
    ax.set_ylim(0.0, 2.45)
    ax.axis("off")
    return fig

def draw_torsion_detail_note_figure(zone, bw, h, cover, stirrup, db_torsion):
    fig, ax = plt.subplots(figsize=(5.0, 5.2))
    stirrup_use = zone.get("stirrup_design_dia", stirrup)

    ax.text(0.5, 1.02, "KETERANGAN PENULANGAN TORSI",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=11, fontweight="bold")

    if zone["status"] == "GEOMETRI TIDAK VALID":
        ax.text(0.5, 0.5, "Geometri tidak valid",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=11, fontweight="bold")
        ax.axis("off")
        return fig

    if not zone["torsion_required"]:
        ax.text(0.5, 0.58, "Tulangan torsi tidak diperlukan\npada kondisi input saat ini",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=11, fontweight="bold")
        ax.text(0.5, 0.32, f"Zona representatif: {zone['title']}",
                transform=ax.transAxes, ha="center", va="center", fontsize=9)
        ax.axis("off")
        return fig

    positions = build_torsion_bar_positions(
        bw, h, cover, stirrup_use, db_torsion, zone["n_long_req"]
    )
    stirrup_x = cover + stirrup_use / 2.0
    stirrup_y = cover + stirrup_use / 2.0
    stirrup_w = bw - 2.0 * stirrup_x
    stirrup_h = h - 2.0 * stirrup_y

    ax.add_patch(Rectangle((0, 0), bw, h, fill=False, lw=1.35, color="black"))
    ax.add_patch(Rectangle((stirrup_x, stirrup_y),
                           stirrup_w, stirrup_h,
                           fill=False, lw=2.2, color="#c0392b"))

    for x, y in positions:
        ax.add_patch(Circle((x, y), db_torsion / 2.0, color="#f1c40f", ec="#a93226", lw=0.8))

    label_bbox = dict(boxstyle="round,pad=0.22", fc="white", ec="none", alpha=0.96)
    right_edge = max(x for x, _ in positions)
    right_side_positions = [pos for pos in positions if abs(pos[0] - right_edge) <= 1e-6]
    if right_side_positions:
        torsion_target = min(right_side_positions, key=lambda pos: abs(pos[1] - h * 0.54))
    else:
        torsion_target = positions[0]

    ax.annotate(
        "Sengkang tertutup",
        xy=(bw - stirrup_x, h / 2.0),
        xytext=(bw + 90, h * 0.60),
        fontsize=8.5, color="#1f5fa8",
        ha="left", va="center",
        bbox=label_bbox,
        arrowprops=dict(
            arrowstyle="->",
            color="#1f5fa8",
            lw=1.0,
            shrinkA=4,
            shrinkB=3,
            connectionstyle="arc3,rad=0.10"
        )
    )
    ax.annotate(
        "Tulangan longitudinal torsi\ndistribusi keliling",
        xy=torsion_target,
        xytext=(bw + 90, h * 0.44),
        fontsize=8.5, color="#c0392b",
        ha="left", va="center",
        bbox=label_bbox,
        arrowprops=dict(
            arrowstyle="->",
            color="#c0392b",
            lw=1.0,
            shrinkA=4,
            shrinkB=3,
            connectionstyle="arc3,rad=-0.12"
        )
    )

    info_pairs = [
        ("Zona representatif", zone["title"]),
        ("Transversal", zone["stirrup_text"]),
        ("Longitudinal", zone["longitudinal_text"]),
        ("Tu desain", f"{zone['Tu_design']:.2f} kN.m")
    ]
    info_label_x = bw / 2.0 - 20
    info_value_x = bw / 2.0 - 14
    info_y_start = -54
    info_gap = 25
    for idx, (label, value) in enumerate(info_pairs):
        yy = info_y_start - idx * info_gap
        ax.text(info_label_x, yy, label,
                ha="right", va="top", fontsize=8.2)
        ax.text(info_value_x, yy, f": {value}",
                ha="left", va="top", fontsize=8.2)

    ax.set_xlim(-20, bw + 235)
    ax.set_ylim(-145, h + 25)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig

def design_shear_torsion_zone(title, Vu, Tu, bw, h, cover, stirrup, fc, fy,
                              flexure_zone, db_torsion, torsion_mode,
                              transverse_design_mode="auto", spacing_target=None):
    standard_transverse_diameters = sorted({8, 10, 13, 16, int(stirrup)})

    def evaluate_with_stirrup(stirrup_design_dia, spacing_override=None):
        phi = 0.75
        theta_deg = 45.0
        cot_theta = 1.0
        sqrt_fc = limited_sqrt_fc(fc)
        fyt = effective_transverse_fy(fy)
        fyl = effective_transverse_fy(fy)
        d = max(flexure_zone["d"] - (stirrup_design_dia - stirrup), 1.0)

        core_b = bw - 2.0 * cover - stirrup_design_dia
        core_h = h - 2.0 * cover - stirrup_design_dia
        geometry_ok = core_b > 0.0 and core_h > 0.0

        if not geometry_ok:
            return {
                "title": title,
                "Vu": Vu,
                "Tu": Tu,
                "d": d,
                "phi": phi,
                "theta_deg": theta_deg,
                "torsion_mode": torsion_mode,
                "transverse_design_mode": transverse_design_mode,
                "spacing_target": spacing_override,
                "spacing_auto": None,
                "spacing_use": spacing_override,
                "spacing_fits": False,
                "Tu_design": 0.0,
                "Tu_reduction": 0.0,
                "torsion_regime": "Tidak dapat dihitung",
                "stirrup_design_dia": stirrup_design_dia,
                "base_stirrup_dia": stirrup,
                "stirrup_text": "-",
                "longitudinal_text": "-",
                "status": "GEOMETRI TIDAK VALID",
                "notes": [
                    "Dimensi inti sengkang tidak valid. Periksa bw, h, cover, dan diameter sengkang."
                ]
            }

        As_stirrup_bar = area_bar(stirrup_design_dia)
        Av_closed = 2.0 * As_stirrup_bar
        At_leg = As_stirrup_bar

        Vu_n = Vu * 1000.0
        Tu_nmm = Tu * 1e6

        Acp = bw * h
        pcp = 2.0 * (bw + h)
        Aoh = core_b * core_h
        Ao = 0.85 * Aoh
        ph = 2.0 * (core_b + core_h)

        Vc = 0.17 * sqrt_fc * bw * d
        phiVc = phi * Vc
        Vs_req = max(Vu_n / phi - Vc, 0.0)
        Av_strength_per_s = Vs_req / (fyt * d) if Vs_req > 0.0 else 0.0

        Av_min_per_s = max(
            0.062 * sqrt_fc * bw / fyt,
            0.35 * bw / fyt
        )
        shear_min_required = Vu_n > 0.5 * phiVc
        Av_req_per_s = max(
            Av_strength_per_s,
            Av_min_per_s if shear_min_required else 0.0
        )

        Tth = 0.083 * sqrt_fc * (Acp ** 2) / pcp
        Tcr = 0.33 * sqrt_fc * (Acp ** 2) / pcp
        phiTth = phi * Tth
        phiTcr = phi * Tcr

        torsion_required = Tu_nmm >= phiTth
        if not torsion_required:
            Tu_design_nmm = 0.0
        elif torsion_mode == "compatibility":
            Tu_design_nmm = min(Tu_nmm, phiTcr)
        else:
            Tu_design_nmm = Tu_nmm

        torsion_strength_required = Tu_design_nmm >= phiTcr - 1e-9

        At_strength_per_s = (
            Tu_design_nmm / (phi * 2.0 * Ao * fyt * cot_theta)
            if torsion_strength_required else 0.0
        )
        combined_min_per_s = Av_min_per_s if torsion_required else 0.0

        if torsion_required:
            total_strength_per_s = Av_strength_per_s + 2.0 * At_strength_per_s
            total_req_per_s = max(total_strength_per_s, combined_min_per_s)
            spacing_calc = (
                (Av_closed + 2.0 * At_leg) / total_req_per_s
                if total_req_per_s > 0.0 else math.inf
            )
        else:
            total_strength_per_s = Av_strength_per_s
            total_req_per_s = Av_req_per_s
            spacing_calc = (
                Av_closed / total_req_per_s if total_req_per_s > 0.0 else math.inf
            )

        shear_s_max = (
            shear_spacing_limit(bw, d, h, Vs_req, fc)
            if total_req_per_s > 0.0 else math.inf
        )
        torsion_s_max = min(ph / 8.0, 300.0) if torsion_required else math.inf
        spacing_limit = min(shear_s_max, torsion_s_max)

        spacing_auto = None
        if total_req_per_s > 0.0:
            spacing_auto, _ = recommended_spacing(spacing_calc, spacing_limit)

        if spacing_override is None:
            spacing_use = spacing_auto
            spacing_fits = True
        else:
            spacing_use = spacing_override
            spacing_fits = (
                spacing_limit == math.inf or
                spacing_use <= spacing_limit + 1e-9
            )

        if spacing_use is None:
            Av_prov_per_s = 0.0
            At_prov_per_s = 0.0
            total_prov_per_s = 0.0
        else:
            Av_prov_per_s = Av_closed / spacing_use
            At_prov_per_s = At_leg / spacing_use if torsion_required else 0.0
            total_prov_per_s = Av_prov_per_s + 2.0 * At_prov_per_s

        Vs_prov = Av_prov_per_s * fyt * d
        phiVn = phi * (Vc + Vs_prov)

        At_for_almin = max(At_strength_per_s, 0.175 * bw / fyt) if torsion_required else 0.0
        Al_strength_req = (
            At_strength_per_s * ph * (fyt / fyl) * (cot_theta ** 2)
            if torsion_strength_required else 0.0
        )

        if torsion_required:
            Al_min_a = 0.42 * sqrt_fc * Acp / fyl - At_for_almin * ph * (fyt / fyl)
            Al_min_b = 0.42 * sqrt_fc * Acp / fyl - 0.175 * bw * ph / fyl
            Al_min_req = max(0.0, min(Al_min_a, Al_min_b))
        else:
            Al_min_a = 0.0
            Al_min_b = 0.0
            Al_min_req = 0.0

        Al_req = max(Al_strength_req, Al_min_req)

        torsion_bar_area = area_bar(db_torsion)
        if torsion_required:
            n_long_req = max(
                4,
                math.ceil(Al_req / torsion_bar_area) if torsion_bar_area > 0.0 else 4,
                math.ceil(ph / 300.0)
            )
            if n_long_req % 2 != 0:
                n_long_req += 1
            Al_prov = n_long_req * torsion_bar_area
            approx_long_spacing = ph / n_long_req
        else:
            n_long_req = 0
            Al_prov = 0.0
            approx_long_spacing = 0.0

        Tn_transverse = (
            2.0 * Ao * At_prov_per_s * fyt * cot_theta
            if torsion_required and spacing_use is not None else 0.0
        )
        Tn_longitudinal = (
            2.0 * Ao * Al_prov * fyl / (ph * cot_theta)
            if torsion_required and n_long_req > 0 else 0.0
        )
        phiTn = (
            phi * min(Tn_transverse, Tn_longitudinal)
            if torsion_required else 0.0
        )

        stress_left = Vu_n / (bw * d) + Tu_design_nmm * ph / (1.7 * (Aoh ** 2))
        stress_right = phi * (Vc / (bw * d) + 0.66 * sqrt_fc)
        section_ok = stress_left <= stress_right + 1e-9

        if torsion_mode == "compatibility" and Tu_nmm > phiTcr and torsion_required:
            torsion_regime = "Torsi kompatibilitas, Tu direduksi"
        elif torsion_strength_required:
            torsion_regime = "Torsi kekuatan"
        elif torsion_required:
            torsion_regime = "Torsi minimum"
        else:
            torsion_regime = "Torsi dapat diabaikan"

        shear_ok = phiVn + 1e-6 >= Vu_n
        longitudinal_ok = (
            not torsion_required or
            (
                Al_prov + 1e-6 >= Al_req and
                approx_long_spacing <= 300.0 + 1e-9 and
                n_long_req >= 4
            )
        )
        torsion_ok = (
            not torsion_strength_required or
            phiTn + 1e-6 >= Tu_design_nmm
        )

        if not section_ok:
            status = "PERLU PERBESAR DIMENSI PENAMPANG"
        elif not spacing_fits:
            status = "SPASI TARGET MELAMPAUI BATAS"
        elif not shear_ok or not longitudinal_ok or not torsion_ok:
            status = "TIDAK AMAN"
        else:
            status = "AMAN"

        if spacing_use is None:
            stirrup_text = "Tidak diwajibkan oleh kekuatan"
        elif torsion_required:
            stirrup_text = f"Sengkang tertutup 2 kaki D{stirrup_design_dia}-{spacing_use:.0f} mm"
        else:
            stirrup_text = f"Sengkang 2 kaki D{stirrup_design_dia}-{spacing_use:.0f} mm"

        if torsion_required:
            longitudinal_text = f"{n_long_req}D{db_torsion} tambahan"
        else:
            longitudinal_text = "Tidak diperlukan"

        notes = [
            "Desain diasumsikan untuk balok nonprategang, beton normal, dan sengkang tertutup 2 kaki.",
            "Sudut diagonal tekan torsi diambil theta = 45 derajat sesuai pendekatan konservatif untuk komponen nonprategang.",
            "Tulangan longitudinal torsi dihitung sebagai tulangan tambahan dan tidak digabung ke modul lentur agar bagian lentur tetap terpisah."
        ]
        if torsion_mode == "compatibility":
            notes.append(
                "Mode torsi kompatibilitas mengizinkan Tu desain direduksi sampai phiTcr bila redistribusi gaya internal setelah retak torsi dapat dibenarkan."
            )
        else:
            notes.append(
                "Mode torsi keseimbangan menggunakan Tu penuh sebagai dasar desain torsi."
            )
        if torsion_required:
            notes.append(
                f"Tu input = {Tu:.2f} kN.m dan Tu desain = {Tu_design_nmm / 1e6:.2f} kN.m."
            )
        if spacing_override is not None:
            notes.append(
                f"Spasi target pengguna = {spacing_override:.0f} mm dengan diameter sengkang hasil evaluasi D{stirrup_design_dia:.0f}."
            )
            if total_req_per_s > 0.0 and spacing_auto is not None:
                notes.append(
                    f"Spasi otomatis dari kebutuhan untuk diameter ini adalah sekitar {spacing_auto:.0f} mm."
                )
            if not spacing_fits and spacing_limit != math.inf:
                notes.append(
                    f"Spasi target melampaui batas maksimum yang diizinkan, yaitu {spacing_limit:.0f} mm."
                )

        return {
            "title": title,
            "Vu": Vu,
            "Tu": Tu,
            "Tu_design": Tu_design_nmm / 1e6,
            "Tu_reduction": (Tu_nmm - Tu_design_nmm) / 1e6,
            "phi": phi,
            "theta_deg": theta_deg,
            "torsion_mode": torsion_mode,
            "transverse_design_mode": transverse_design_mode,
            "spacing_target": spacing_override,
            "spacing_auto": spacing_auto,
            "stirrup_design_dia": stirrup_design_dia,
            "base_stirrup_dia": stirrup,
            "sqrt_fc": sqrt_fc,
            "fyt": fyt,
            "fyl": fyl,
            "d": d,
            "Acp": Acp,
            "pcp": pcp,
            "Aoh": Aoh,
            "Ao": Ao,
            "ph": ph,
            "Vc": Vc,
            "phiVc": phiVc,
            "Vs_req": Vs_req,
            "Vs_prov": Vs_prov,
            "phiVn": phiVn,
            "Av_strength_per_s": Av_strength_per_s,
            "Av_min_per_s": Av_min_per_s,
            "Av_req_per_s": Av_req_per_s,
            "Tth": Tth,
            "phiTth": phiTth,
            "Tcr": Tcr,
            "phiTcr": phiTcr,
            "torsion_required": torsion_required,
            "torsion_strength_required": torsion_strength_required,
            "torsion_regime": torsion_regime,
            "At_strength_per_s": At_strength_per_s,
            "At_for_almin": At_for_almin,
            "combined_min_per_s": combined_min_per_s,
            "total_strength_per_s": total_strength_per_s,
            "total_req_per_s": total_req_per_s,
            "spacing_calc": spacing_calc,
            "shear_s_max": shear_s_max,
            "torsion_s_max": torsion_s_max,
            "spacing_limit": spacing_limit,
            "spacing_use": spacing_use,
            "spacing_fits": spacing_fits,
            "Av_prov_per_s": Av_prov_per_s,
            "At_prov_per_s": At_prov_per_s,
            "total_prov_per_s": total_prov_per_s,
            "Al_strength_req": Al_strength_req,
            "Al_min_a": Al_min_a,
            "Al_min_b": Al_min_b,
            "Al_min_req": Al_min_req,
            "Al_req": Al_req,
            "db_torsion": db_torsion,
            "n_long_req": n_long_req,
            "Al_prov": Al_prov,
            "approx_long_spacing": approx_long_spacing,
            "Tn_transverse": Tn_transverse,
            "Tn_longitudinal": Tn_longitudinal,
            "phiTn": phiTn,
            "stress_left": stress_left,
            "stress_right": stress_right,
            "section_ok": section_ok,
            "shear_ok": shear_ok,
            "longitudinal_ok": longitudinal_ok,
            "torsion_ok": torsion_ok,
            "status": status,
            "stirrup_text": stirrup_text,
            "longitudinal_text": longitudinal_text,
            "redesign_selected": False,
            "notes": notes
        }

    if transverse_design_mode == "target_spacing" and spacing_target is not None:
        candidate_diams = [dia for dia in standard_transverse_diameters if dia >= stirrup]
        if not candidate_diams:
            candidate_diams = [stirrup]

        evaluated = [
            evaluate_with_stirrup(dia, spacing_target)
            for dia in candidate_diams
        ]
        safe_options = [zone for zone in evaluated if zone["status"] == "AMAN"]

        if safe_options:
            selected = safe_options[0]
            selected["redesign_selected"] = True
            selected["notes"].append(
                "Mode spasi target aktif. Sistem memilih diameter sengkang minimum yang masih menghasilkan status aman, dimulai dari diameter awal yang dipilih pengguna."
            )
            return selected

        selected = max(
            evaluated,
            key=lambda zone: (
                zone.get("section_ok", False),
                zone.get("spacing_fits", False),
                zone.get("phiVn", 0.0) + zone.get("phiTn", 0.0),
                zone.get("stirrup_design_dia", 0.0)
            )
        )
        selected["redesign_selected"] = True
        selected["notes"].append(
            "Spasi target belum dapat dibuat aman dengan diameter sengkang standar yang tersedia. Gunakan spasi lebih rapat atau perbesar penampang."
        )
        return selected

    return evaluate_with_stirrup(stirrup)

def shear_torsion_report_markdown(zone, bw, h, cover, stirrup):
    if zone["status"] == "GEOMETRI TIDAK VALID":
        markdown = "| Parameter | Nilai |\n|---|---|\n"
        markdown += f"| Vu | {zone['Vu']:.2f} kN |\n"
        markdown += f"| Tu | {zone['Tu']:.2f} kN.m |\n"
        markdown += f"| Status | {zone['status']} |\n"
        markdown += "\n"
        for note in zone["notes"]:
            markdown += f"- {note}\n"
        return markdown

    def fmt(value, unit="", scale=1.0, digits=2):
        return f"{value / scale:.{digits}f} {unit}".strip()

    def fmt_or_dash(value, unit="", scale=1.0, digits=2):
        if value is None or not math.isfinite(value):
            return "-"
        return fmt(value, unit, scale, digits)

    rows = [
        ("Vu", f"{zone['Vu']:.2f} kN"),
        ("Tu input", f"{zone['Tu']:.2f} kN.m"),
        ("Mode desain torsi", "Torsi kompatibilitas" if zone["torsion_mode"] == "compatibility" else "Torsi keseimbangan"),
        ("Mode desain transversal", transverse_design_mode_label(zone["transverse_design_mode"])),
        ("Tu desain", f"{zone['Tu_design']:.2f} kN.m"),
        ("Reduksi Tu", f"{zone['Tu_reduction']:.2f} kN.m"),
        ("Rezim torsi", zone["torsion_regime"]),
        ("Lebar balok, bw", f"{bw:.2f} mm"),
        ("Tinggi balok, h", f"{h:.2f} mm"),
        ("Selimut beton", f"{cover:.2f} mm"),
        ("Diameter sengkang awal", f"D{zone.get('base_stirrup_dia', stirrup):.0f}"),
        ("Diameter sengkang hasil desain", f"D{zone.get('stirrup_design_dia', stirrup):.0f}"),
        ("Diameter tulangan longitudinal torsi", f"D{zone.get('db_torsion', 0)}" if zone.get("db_torsion", 0) else "-"),
        ("Spasi target pengguna", fmt_or_dash(zone.get("spacing_target"), "mm", digits=0)),
        ("Spasi otomatis dari kebutuhan", fmt_or_dash(zone.get("spacing_auto"), "mm", digits=0)),
        ("d efektif dari modul lentur", f"{zone['d']:.2f} mm"),
        ("sqrt(fc') efektif", f"{zone['sqrt_fc']:.4f}"),
        ("fy longitudinal efektif", f"{zone['fyl']:.2f} MPa"),
        ("fyt transversal efektif", f"{zone['fyt']:.2f} MPa"),
        ("Acp", f"{zone['Acp']:.2f} mm2"),
        ("pcp", f"{zone['pcp']:.2f} mm"),
        ("Aoh", f"{zone['Aoh']:.2f} mm2"),
        ("Ao", f"{zone['Ao']:.2f} mm2"),
        ("ph", f"{zone['ph']:.2f} mm"),
        ("Vc", fmt(zone["Vc"], "kN", 1000.0)),
        ("phiVc", fmt(zone["phiVc"], "kN", 1000.0)),
        ("Vs perlu", fmt(zone["Vs_req"], "kN", 1000.0)),
        ("Vs terpasang", fmt(zone["Vs_prov"], "kN", 1000.0)),
        ("Av/s perlu untuk geser", f"{zone['Av_req_per_s']:.4f} mm2/mm"),
        ("Av/s minimum", f"{zone['Av_min_per_s']:.4f} mm2/mm"),
        ("At/s perlu untuk torsi", f"{zone['At_strength_per_s']:.4f} mm2/mm"),
        ("(Av + 2At)/s minimum", f"{zone['combined_min_per_s']:.4f} mm2/mm"),
        ("(Av + 2At)/s perlu total", f"{zone['total_req_per_s']:.4f} mm2/mm"),
        ("Sengkang terpasang", zone["stirrup_text"]),
        ("(Av + 2At)/s terpasang", f"{zone['total_prov_per_s']:.4f} mm2/mm"),
        ("s hitung", fmt_or_dash(zone["spacing_calc"], "mm")),
        ("s maksimum geser", fmt_or_dash(zone["shear_s_max"], "mm")),
        ("s maksimum torsi", fmt_or_dash(zone["torsion_s_max"] if zone["torsion_required"] else None, "mm")),
        ("s dipakai", fmt_or_dash(zone["spacing_use"], "mm", digits=0)),
        ("Tth", fmt(zone["Tth"], "kN.m", 1e6)),
        ("phiTth", fmt(zone["phiTth"], "kN.m", 1e6)),
        ("Tcr", fmt(zone["Tcr"], "kN.m", 1e6)),
        ("phiTcr", fmt(zone["phiTcr"], "kN.m", 1e6)),
        ("Al perlu karena kekuatan torsi", f"{zone['Al_strength_req']:.2f} mm2"),
        ("Al minimum (a)", f"{zone['Al_min_a']:.2f} mm2"),
        ("Al minimum (b)", f"{zone['Al_min_b']:.2f} mm2"),
        ("Al minimum yang dipakai", f"{zone['Al_min_req']:.2f} mm2"),
        ("Al tambahan yang dipakai", f"{zone['Al_req']:.2f} mm2"),
        ("Tulangan longitudinal torsi tambahan", zone["longitudinal_text"]),
        ("Al longitudinal terpasang", f"{zone['Al_prov']:.2f} mm2"),
        ("Perkiraan spasi keliling batang torsi", fmt_or_dash(zone["approx_long_spacing"] if zone["n_long_req"] > 0 else None, "mm")),
        ("phiVn terpasang", fmt(zone["phiVn"], "kN", 1000.0)),
        ("phiTn terpasang", fmt(zone["phiTn"], "kN.m", 1e6)),
        ("Cek tegangan gabungan, lhs", f"{zone['stress_left']:.4f} MPa"),
        ("Cek tegangan gabungan, rhs", f"{zone['stress_right']:.4f} MPa"),
        ("Status", zone["status"])
    ]

    markdown = "| Parameter | Nilai |\n|---|---|\n"
    for label, value in rows:
        markdown += f"| {label} | {value} |\n"

    markdown += "\n"
    for note in zone["notes"]:
        markdown += f"- {note}\n"

    return markdown

# ==========================================================
# SIDEBAR INPUT
# ==========================================================
st.sidebar.header("INPUT DATA")

Ln = st.sidebar.number_input("Bentang Bersih Ln (mm)",1000,50000,6000)
bw = st.sidebar.number_input("Lebar Balok bw (mm)",150,2000,300)
h  = st.sidebar.number_input("Tinggi Balok h (mm)",250,3000,500)

cover   = st.sidebar.number_input("Selimut Beton (mm)",20,100,40)
stirrup = st.sidebar.number_input("Diameter Sengkang (mm)",8,16,10)

fc = st.sidebar.number_input("f'c (MPa)",17.0,70.0,25.0)
fy = st.sidebar.number_input("fy (MPa)",240.0,700.0,420.0)

MuL = st.sidebar.number_input("Mu Tumpuan Kiri (kN.m)",0.0,100000.0,300.0)
MuM = st.sidebar.number_input("Mu Lapangan (kN.m)",0.0,100000.0,300.0)
MuR = st.sidebar.number_input("Mu Tumpuan Kanan (kN.m)",0.0,100000.0,300.0)

db = st.sidebar.selectbox(
    "Diameter Tulangan (mm)",
    [13,16,19,22,25,29,32],
    index=4
)

st.sidebar.markdown("---")
st.sidebar.subheader("INPUT GESER & TORSI")
st.sidebar.caption("Modul ini terpisah dari penulangan lentur yang sudah ada.")

torsion_mode = st.sidebar.radio(
    "Mode Desain Torsi",
    [
        "equilibrium",
        "compatibility"
    ],
    format_func=lambda x: (
        "Torsi Keseimbangan: Tu dipakai penuh"
        if x == "equilibrium"
        else "Torsi Kompatibilitas: Tu boleh direduksi ke phiTcr"
    )
)

transverse_design_mode = st.sidebar.radio(
    "Mode Desain Transversal",
    [
        "auto",
        "target_spacing"
    ],
    format_func=transverse_design_mode_label
)

VuL = st.sidebar.number_input("Vu Tumpuan Kiri (kN)", 0.0, 100000.0, 150.0)
VuM = st.sidebar.number_input("Vu Lapangan (kN)", 0.0, 100000.0, 120.0)
VuR = st.sidebar.number_input("Vu Tumpuan Kanan (kN)", 0.0, 100000.0, 150.0)

TuL = st.sidebar.number_input("Tu Tumpuan Kiri (kN.m)", 0.0, 100000.0, 0.0)
TuM = st.sidebar.number_input("Tu Lapangan (kN.m)", 0.0, 100000.0, 0.0)
TuR = st.sidebar.number_input("Tu Tumpuan Kanan (kN.m)", 0.0, 100000.0, 0.0)

db_torsion = st.sidebar.selectbox(
    "Diameter Tulangan Longitudinal Torsi (mm)",
    [10,13,16,19,22,25,29,32],
    index=1
)

if transverse_design_mode == "target_spacing":
    st.sidebar.caption(
        "Masukkan spasi target. Sistem akan memilih diameter sengkang minimum yang aman dari daftar standar mulai dari diameter awal."
    )
    s_target_L = st.sidebar.number_input("Spasi Target Tumpuan Kiri (mm)", 50.0, 600.0, 150.0, 5.0)
    s_target_M = st.sidebar.number_input("Spasi Target Lapangan (mm)", 50.0, 600.0, 200.0, 5.0)
    s_target_R = st.sidebar.number_input("Spasi Target Tumpuan Kanan (mm)", 50.0, 600.0, 150.0, 5.0)
else:
    s_target_L = None
    s_target_M = None
    s_target_R = None

# ==========================================================
# CALCULATION
# ==========================================================
L = design_zone("TUMPUAN KIRI", MuL, bw, h, cover, stirrup, db, fc, fy, "top")
M = design_zone("LAPANGAN", MuM, bw, h, cover, stirrup, db, fc, fy, "bottom")
R = design_zone("TUMPUAN KANAN", MuR, bw, h, cover, stirrup, db, fc, fy, "top")

SL = design_shear_torsion_zone(
    "TUMPUAN KIRI", VuL, TuL, bw, h, cover, stirrup, fc, fy, L, db_torsion,
    torsion_mode, transverse_design_mode, s_target_L
)
SM = design_shear_torsion_zone(
    "LAPANGAN", VuM, TuM, bw, h, cover, stirrup, fc, fy, M, db_torsion,
    torsion_mode, transverse_design_mode, s_target_M
)
SR = design_shear_torsion_zone(
    "TUMPUAN KANAN", VuR, TuR, bw, h, cover, stirrup, fc, fy, R, db_torsion,
    torsion_mode, transverse_design_mode, s_target_R
)

Lext  = 12 * db
Lextm = 12 * db

Ltump = min(0.25 * Ln + Lext, Ln/2)
Llap  = min(0.50 * Ln + Lextm, Ln)

xL1 = 0
xL2 = Ltump

xR1 = Ln - Ltump
xR2 = Ln

xM1 = (Ln - Llap) / 2
xM2 = (Ln + Llap) / 2

# ==========================================================
# SUMMARY
# ==========================================================
c1,c2,c3 = st.columns(3)

with c1:
    st.subheader("TUMPUAN KIRI")
    st.write(f"Atas = {L['n_main']}D{db}")
    st.write(f"Bawah = {L['n_min']}D{db}")
    st.write(f"Mu = {L['Mu']:.2f} kN.m")
    st.write(f"phiMn terpasang = {L['phiMn']:.2f} kN.m")
    st.write(f"Status = {L['status']}")

with c2:
    st.subheader("LAPANGAN")
    st.write(f"Bawah = {M['n_main']}D{db}")
    st.write(f"Atas = {M['n_min']}D{db}")
    st.write(f"Mu = {M['Mu']:.2f} kN.m")
    st.write(f"phiMn terpasang = {M['phiMn']:.2f} kN.m")
    st.write(f"Status = {M['status']}")

with c3:
    st.subheader("TUMPUAN KANAN")
    st.write(f"Atas = {R['n_main']}D{db}")
    st.write(f"Bawah = {R['n_min']}D{db}")
    st.write(f"Mu = {R['Mu']:.2f} kN.m")
    st.write(f"phiMn terpasang = {R['phiMn']:.2f} kN.m")
    st.write(f"Status = {R['status']}")

with st.expander("HITUNGAN LENGKAP TUMPUAN KIRI"):
    exp_left, exp_right = st.columns([2.2, 1.0])
    with exp_left:
        st.markdown(report_markdown(L, Ln, bw, h, cover, stirrup, db, fc, fy))
    with exp_right:
        st.write("Potongan Penulangan")
        render_figure_panel(
            draw_section_figure(L, bw, h, cover, stirrup, db),
            "potongan_penulangan_tumpuan_kiri_320dpi.png",
            "left_flexure_detail",
            viewer_height=460
        )

with st.expander("HITUNGAN LENGKAP LAPANGAN"):
    exp_left, exp_right = st.columns([2.2, 1.0])
    with exp_left:
        st.markdown(report_markdown(M, Ln, bw, h, cover, stirrup, db, fc, fy))
    with exp_right:
        st.write("Potongan Penulangan")
        render_figure_panel(
            draw_section_figure(M, bw, h, cover, stirrup, db),
            "potongan_penulangan_lapangan_320dpi.png",
            "mid_flexure_detail",
            viewer_height=460
        )

with st.expander("HITUNGAN LENGKAP TUMPUAN KANAN"):
    exp_left, exp_right = st.columns([2.2, 1.0])
    with exp_left:
        st.markdown(report_markdown(R, Ln, bw, h, cover, stirrup, db, fc, fy))
    with exp_right:
        st.write("Potongan Penulangan")
        render_figure_panel(
            draw_section_figure(R, bw, h, cover, stirrup, db),
            "potongan_penulangan_tumpuan_kanan_320dpi.png",
            "right_flexure_detail",
            viewer_height=460
        )

# ==========================================================
# DETAIL BALOK
# ==========================================================
st.markdown('<div class="sec">DETAIL PENULANGAN BALOK</div>',
            unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(15,5.4))

y0 = 4.0
depth = 0.8
stirrup_y_bottom = y0 + 0.10
stirrup_y_top = y0 + depth - 0.10

left_zone_start = 0.0
left_zone_end = Ltump
field_zone_start = Ltump
field_zone_end = xR1
right_zone_start = xR1
right_zone_end = Ln

left_stirrups = anchored_spacing_positions(
    left_zone_start, left_zone_end, SL["spacing_use"], anchor="start"
)
field_stirrups = anchored_spacing_positions(
    field_zone_start, field_zone_end, SM["spacing_use"], anchor="start"
)
right_stirrups = anchored_spacing_positions(
    right_zone_start, right_zone_end, SR["spacing_use"], anchor="end"
)

stirrup_positions = []
for pos in sorted(left_stirrups + field_stirrups + right_stirrups):
    if not stirrup_positions or abs(pos - stirrup_positions[-1]) > 1e-6:
        stirrup_positions.append(pos)

# outline beam
ax.add_patch(Rectangle((0,y0),Ln,depth,fill=False,lw=1.2))

# stirrup lines according to shear-torsion spacing
for x in stirrup_positions:
    ax.plot([x, x], [stirrup_y_bottom, stirrup_y_top],
            lw=0.55, color="#7f8c8d")

# support and field zone bands for stirrup spacing
band_y = y0 + depth + 0.68
band_h = 0.23
ax.text(Ln/2, band_y + band_h + 0.10,
        "SPASI TULANGAN GESER / TORSI",
        ha="center", va="bottom", fontsize=9, fontweight="bold")

zone_bands = [
    (left_zone_start, left_zone_end, "#fce5cd",
     compact_stirrup_label(SL, "Tumpuan kiri")),
    (field_zone_start, field_zone_end, "#d9eaf7",
     compact_stirrup_label(SM, "Lapangan")),
    (right_zone_start, right_zone_end, "#fce5cd",
     compact_stirrup_label(SR, "Tumpuan kanan"))
]

for start, end, color, label in zone_bands:
    if end - start <= 1e-9:
        continue
    ax.add_patch(Rectangle((start, band_y), end - start, band_h,
                           facecolor=color, edgecolor="none", alpha=0.75))
    ax.text((start + end) / 2.0, band_y + band_h / 2.0, label,
            ha="center", va="center", fontsize=8, fontweight="bold")

for boundary in [left_zone_end, right_zone_start]:
    if 0 < boundary < Ln:
        ax.plot([boundary, boundary], [y0 - 0.02, band_y + band_h],
                lw=0.8, ls="--", color="#b0b0b0")

# ---------- reinforcement ----------

# kiri atas
for j,_ in enumerate(L["main_layers"]):
    yy = y0 + depth - 0.10 - j*0.08
    ax.plot([xL1,xL2],[yy,yy],lw=2,color='red')

# kiri bawah
for j,_ in enumerate(L["min_layers"]):
    yy = y0 + 0.10 + j*0.08
    ax.plot([xL1,xL2],[yy,yy],lw=2,color='blue')

# lapangan bawah
for j,_ in enumerate(M["main_layers"]):
    yy = y0 + 0.10 + j*0.08
    ax.plot([xM1,xM2],[yy,yy],lw=2,color='blue')

# lapangan atas
for j,_ in enumerate(M["min_layers"]):
    yy = y0 + depth - 0.10 - j*0.08
    ax.plot([xM1,xM2],[yy,yy],lw=2,color='green')

# kanan atas
for j,_ in enumerate(R["main_layers"]):
    yy = y0 + depth - 0.10 - j*0.08
    ax.plot([xR1,xR2],[yy,yy],lw=2,color='red')

# kanan bawah
for j,_ in enumerate(R["min_layers"]):
    yy = y0 + 0.10 + j*0.08
    ax.plot([xR1,xR2],[yy,yy],lw=2,color='blue')

# ---------- labels ----------

ax.text((xL1+xL2)/2,5.36,"Atas kiri",
        ha="center",fontsize=9,color="red")

ax.text((xL1+xL2)/2,5.18,
        f"0.25Ln+Lext={Ltump:.0f}",
        ha="center",fontsize=8,color="red")

ax.text(Ln/2,5.22,"Atas lapangan",
        ha="center",fontsize=9,color="green")

ax.text((xR1+xR2)/2,5.36,"Atas kanan",
        ha="center",fontsize=9,color="red")

ax.text((xR1+xR2)/2,5.18,
        f"0.25Ln+Lext={Ltump:.0f}",
        ha="center",fontsize=8,color="red")

ax.text(420,3.78,"Bawah kiri",
        ha="left",fontsize=9,color="blue")

ax.text(Ln/2,3.08,"Bawah lapangan",
        ha="center",fontsize=9,color="blue")

ax.text(Ln/2,3.30,
        f"0.50Ln+Lextm={Llap:.0f}",
        ha="center",fontsize=8,color="blue")

ax.text(Ln-820,3.78,"Bawah kanan",
        ha="left",fontsize=9,color="blue")

# ---------- arrows ----------
ax.annotate(
    "", xy=(xL1,5.05), xytext=(xL2,5.05),
    arrowprops=dict(arrowstyle="<->",lw=1,color="red")
)

ax.annotate(
    "", xy=(xR1,5.05), xytext=(xR2,5.05),
    arrowprops=dict(arrowstyle="<->",lw=1,color="red")
)

ax.annotate(
    "", xy=(xM1,3.50), xytext=(xM2,3.50),
    arrowprops=dict(arrowstyle="<->",lw=1,color="blue")
)

ax.set_xlim(-350,Ln+350)
ax.set_ylim(2.9,6.15)
ax.axis("off")

render_figure_panel(
    fig,
    "detail_penulangan_balok_320dpi.png",
    "beam_detail",
    viewer_height=460
)

# ==========================================================
# CROSS SECTION
# ==========================================================
st.markdown('<div class="sec2">POTONGAN</div>',
            unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.write("Tumpuan Kiri")
    render_figure_panel(
        draw_section_figure(L, bw, h, cover, stirrup, db),
        "potongan_tumpuan_kiri_320dpi.png",
        "left_flexure_section",
        viewer_height=460
    )

with col_mid:
    st.write("Lapangan")
    render_figure_panel(
        draw_section_figure(M, bw, h, cover, stirrup, db),
        "potongan_lapangan_320dpi.png",
        "mid_flexure_section",
        viewer_height=460
    )

with col_right:
    st.write("Tumpuan Kanan")
    render_figure_panel(
        draw_section_figure(R, bw, h, cover, stirrup, db),
        "potongan_tumpuan_kanan_320dpi.png",
        "right_flexure_section",
        viewer_height=460
    )

# ==========================================================
# SHEAR & TORSION
# ==========================================================
st.markdown('<div class="sec">DESAIN PENULANGAN GESER DAN TORSI</div>',
            unsafe_allow_html=True)
mode_label = (
    "Torsi Keseimbangan: Tu dipakai penuh"
    if torsion_mode == "equilibrium"
    else "Torsi Kompatibilitas: Tu boleh direduksi ke phiTcr"
)
transverse_mode_label = transverse_design_mode_label(transverse_design_mode)
st.caption(
    "Modul ini dibuat terpisah dari penulangan lentur. "
    f"Mode aktif: {mode_label}. "
    f"Mode transversal: {transverse_mode_label}. "
    "Asumsi desain: balok nonprategang, beton normal, sengkang tertutup 2 kaki, "
    "dan theta torsi = 45 derajat."
)

zones_st = [SL, SM, SR]
torsion_rep_zone = select_representative_torsion_zone(zones_st)
tab_ringkas, tab_detail, tab_potongan, tab_penulangan = st.tabs(
    ["Ringkasan", "Hitungan Lengkap", "Potongan Geser-Torsi", "Detail Penulangan"]
)

with tab_ringkas:
    st.markdown(shear_torsion_summary_markdown(zones_st))

    g1, g2, g3 = st.columns(3)

    with g1:
        st.subheader("TUMPUAN KIRI")
        st.write(f"Vu = {SL['Vu']:.2f} kN")
        st.write(f"Tu input = {SL['Tu']:.2f} kN.m")
        st.write(f"Tu desain = {SL['Tu_design']:.2f} kN.m")
        st.write(f"Transversal = {SL['stirrup_text']}")
        st.write(f"Longitudinal torsi = {SL['longitudinal_text']}")
        st.write(f"Status = {SL['status']}")

    with g2:
        st.subheader("LAPANGAN")
        st.write(f"Vu = {SM['Vu']:.2f} kN")
        st.write(f"Tu input = {SM['Tu']:.2f} kN.m")
        st.write(f"Tu desain = {SM['Tu_design']:.2f} kN.m")
        st.write(f"Transversal = {SM['stirrup_text']}")
        st.write(f"Longitudinal torsi = {SM['longitudinal_text']}")
        st.write(f"Status = {SM['status']}")

    with g3:
        st.subheader("TUMPUAN KANAN")
        st.write(f"Vu = {SR['Vu']:.2f} kN")
        st.write(f"Tu input = {SR['Tu']:.2f} kN.m")
        st.write(f"Tu desain = {SR['Tu_design']:.2f} kN.m")
        st.write(f"Transversal = {SR['stirrup_text']}")
        st.write(f"Longitudinal torsi = {SR['longitudinal_text']}")
        st.write(f"Status = {SR['status']}")

with tab_detail:
    with st.expander("HITUNGAN LENGKAP GESER & TORSI TUMPUAN KIRI"):
        exp_left, exp_right = st.columns([2.0, 1.0])
        with exp_left:
            st.markdown(shear_torsion_report_markdown(SL, bw, h, cover, stirrup))
        with exp_right:
            st.write("Potongan Geser-Torsi")
            render_figure_panel(
                draw_shear_torsion_section_figure(SL, bw, h, cover, stirrup, db_torsion),
                "potongan_geser_torsi_tumpuan_kiri_320dpi.png",
                "left_shear_torsion_detail",
                viewer_height=460
            )

    with st.expander("HITUNGAN LENGKAP GESER & TORSI LAPANGAN"):
        exp_left, exp_right = st.columns([2.0, 1.0])
        with exp_left:
            st.markdown(shear_torsion_report_markdown(SM, bw, h, cover, stirrup))
        with exp_right:
            st.write("Potongan Geser-Torsi")
            render_figure_panel(
                draw_shear_torsion_section_figure(SM, bw, h, cover, stirrup, db_torsion),
                "potongan_geser_torsi_lapangan_320dpi.png",
                "mid_shear_torsion_detail",
                viewer_height=460
            )

    with st.expander("HITUNGAN LENGKAP GESER & TORSI TUMPUAN KANAN"):
        exp_left, exp_right = st.columns([2.0, 1.0])
        with exp_left:
            st.markdown(shear_torsion_report_markdown(SR, bw, h, cover, stirrup))
        with exp_right:
            st.write("Potongan Geser-Torsi")
            render_figure_panel(
                draw_shear_torsion_section_figure(SR, bw, h, cover, stirrup, db_torsion),
                "potongan_geser_torsi_tumpuan_kanan_320dpi.png",
                "right_shear_torsion_detail",
                viewer_height=460
            )

with tab_potongan:
    p1, p2, p3 = st.columns(3)

    with p1:
        st.write("Tumpuan Kiri")
        render_figure_panel(
            draw_shear_torsion_section_figure(SL, bw, h, cover, stirrup, db_torsion),
            "potongan_geser_torsi_tab_tumpuan_kiri_320dpi.png",
            "left_shear_torsion_tab",
            viewer_height=460
        )

    with p2:
        st.write("Lapangan")
        render_figure_panel(
            draw_shear_torsion_section_figure(SM, bw, h, cover, stirrup, db_torsion),
            "potongan_geser_torsi_tab_lapangan_320dpi.png",
            "mid_shear_torsion_tab",
            viewer_height=460
        )

    with p3:
        st.write("Tumpuan Kanan")
        render_figure_panel(
            draw_shear_torsion_section_figure(SR, bw, h, cover, stirrup, db_torsion),
            "potongan_geser_torsi_tab_tumpuan_kanan_320dpi.png",
            "right_shear_torsion_tab",
            viewer_height=460
        )

with tab_penulangan:
    st.markdown("**Detail Penulangan Geser dan Torsi**")
    st.caption(
        "Visual ini menampilkan spasi sengkang hasil desain pada daerah tumpuan dan lapangan, "
        "plot tulangan longitudinal torsi tambahan pada tampak memanjang, "
        "serta keterangan penulangan torsi representatif."
    )

    render_figure_panel(
        draw_shear_torsion_longitudinal_detail_figure(
            Ln, Ltump, xR1, zones_st, bw, h, cover, stirrup
        ),
        "detail_memanjang_geser_torsi_320dpi.png",
        "longitudinal_shear_torsion",
        viewer_height=420
    )

    pen_left, pen_right = st.columns([1.5, 1.0])

    with pen_left:
        st.write("Potongan representatif geser-torsi")
        section_cols = st.columns(3)
        section_items = [
            ("Tumpuan Kiri", SL),
            ("Lapangan", SM),
            ("Tumpuan Kanan", SR)
        ]
        for col, (label, zone) in zip(section_cols, section_items):
            with col:
                st.caption(label)
                render_figure_panel(
                    draw_shear_torsion_section_figure(
                        zone, bw, h, cover, stirrup, db_torsion
                    ),
                    f"potongan_representatif_{label.lower().replace(' ', '_')}_320dpi.png",
                    f"representative_{label.lower().replace(' ', '_')}",
                    viewer_height=460
                )

    with pen_right:
        st.write("Keterangan penulangan torsi")
        render_figure_panel(
            draw_torsion_detail_note_figure(
                torsion_rep_zone, bw, h, cover, stirrup, db_torsion
            ),
            "keterangan_penulangan_torsi_320dpi.png",
            "torsion_note",
            viewer_height=420
        )
