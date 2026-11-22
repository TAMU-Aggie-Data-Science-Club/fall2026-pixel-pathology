// "Follow an image through the model": animated, interactive replay of one inference result.
// All data arrives as JSON from Python (flow_payload.py). It is validated here and written to the
// page only with textContent or as validated data-URL images, never as HTML.
// The animation is a replay: it never runs the model and never talks back to Streamlit.

export default function (component) {
  const { data, parentElement: root } = component;
  const $ = (selector) => root.querySelector(selector);

  // ---- small helpers --------------------------------------------------------------------
  const clamp = (x, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, x));
  const ease = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const lerp = (a, b, t) => a + (b - a) * t;
  const SAFE_URL = /^data:image\/(png|jpeg);base64,[A-Za-z0-9+/=]+$/;
  const safeUrl = (u) => (typeof u === "string" && SAFE_URL.test(u) ? u : null);
  const str = (v) => (typeof v === "string" ? v : "");
  const num = (v) => (typeof v === "number" && Number.isFinite(v) ? v : 0);
  const SVG_NS = "http://www.w3.org/2000/svg";

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function svg(tag, attrs, text) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const key of Object.keys(attrs || {})) node.setAttribute(key, String(attrs[key]));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function picture(url, alt, className) {
    const img = el("img", className);
    const safe = safeUrl(url);
    if (safe) img.src = safe;
    img.alt = alt;
    img.draggable = false;
    return img;
  }

  // ---- data -----------------------------------------------------------------------------
  const payload = data || {};
  const hasImage = payload.hasImage === true;
  const ready = payload.ready === true;
  const heatmapReady = payload.heatmapReady === true;
  const images = payload.images || {};
  const sizes = payload.sizes || {};
  const classes = Array.isArray(payload.classes) ? payload.classes : [];
  const copy = payload.copy || {};
  const message = str(payload.message);
  const topIndex = Number.isInteger(payload.top) ? payload.top : -1;

  const STAGES = [
    { id: "A", label: "Input" },
    { id: "B", label: "Prepare" },
    { id: "C", label: "Model" },
    { id: "D", label: "Prediction" },
    { id: "E", label: "Grad-CAM" },
  ];
  // How long each stage takes to play, in milliseconds.
  const DURATIONS = { A: 3200, B: 5200, C: 6800, D: 5600, E: 6000 };
  // With no image, only the conceptual sketch is available.
  const enabledIds = hasImage ? STAGES.map((s) => s.id) : ["C"];

  const flow = $("#flow");
  const tabsEl = $("#tabs");
  const canvas = $("#canvas");
  const progEl = $("#prog");
  const playBtn = $("#play");
  const replayBtn = $("#replay");
  const prevBtn = $("#prev");
  const nextBtn = $("#next");
  const kickerEl = $("#kicker");
  const titleEl = $("#title");
  const textEl = $("#text");
  const text2El = $("#text2");
  const factsEl = $("#facts");
  const tagEl = $("#tag");
  $("#barTitle").textContent = str(payload.barTitle);

  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  let reduced = motionQuery.matches;
  flow.classList.toggle("reduced", reduced);

  // ---- scenes ---------------------------------------------------------------------------
  function unavailableScene(text) {
    const scene = el("div", "scene");
    scene.append(el("div", "notice", text || "This stage is unavailable for this image."));
    return { node: scene, render() {} };
  }

  // A: the original image.
  function buildA() {
    const url = safeUrl(images.original);
    if (!url) return unavailableScene(message);
    const scene = el("div", "scene");
    const frame = el("div", "a-frame");
    frame.append(picture(url, "Your selected image", ""));
    const size = sizes.original || [0, 0];
    const chip = el("div", "chip tl live", `YOUR IMAGE · ${num(size[0])} × ${num(size[1])} px`);
    scene.append(chip, frame);
    return {
      node: scene,
      render(t) {
        const k = ease(t / 0.45);
        frame.style.opacity = String(k);
        frame.style.transform = `scale(${lerp(0.96, 1, k)})`;
        chip.style.opacity = String(clamp((t - 0.4) / 0.3));
      },
    };
  }

  // B: from the original to the real crop produced by the shared preprocessing.
  function buildB() {
    const original = safeUrl(images.original);
    const crop = safeUrl(images.crop);
    if (!original || !crop) return unavailableScene(message);
    const [ow, oh] = (sizes.original || [1, 1]).map(num);
    const [cw, ch] = (sizes.crop || [1, 1]).map(num);
    const aspect = ow > 0 && oh > 0 ? ow / oh : 1;

    const scene = el("div", "scene");
    const label = el("div", "chip tl live", "");
    const frame = el("div", "b-frame");
    const origImg = picture(original, "Your image", "fill");
    const cropImg = picture(crop, "The crop the model receives", "fill crop");
    frame.append(origImg, cropImg);
    const steps = el("div", "steps");
    const stepEls = ["1 Original", "2 Resize and center crop", "3 Model input"].map((text) => el("span", "step", text));
    steps.append(...stepEls);
    scene.append(label, frame, steps);

    return {
      node: scene,
      render(t) {
        // The frame morphs from the original's shape to a square (the cover fit looks like a center crop),
        // then crossfades to the actual prepared crop, which is the model's real input.
        const k = ease((t - 0.25) / 0.45);
        const base = 300;
        const maxWidth = Math.max(160, scene.clientWidth - 56);
        const rawWidth = base * lerp(aspect, 1, k);
        const scale = Math.min(1, maxWidth / Math.max(rawWidth, base * aspect));
        frame.style.width = `${rawWidth * scale}px`;
        frame.style.height = `${base * scale}px`;
        cropImg.style.opacity = String(clamp((t - 0.72) / 0.2));
        frame.classList.toggle("cropped", t >= 0.9);
        const phase = t < 0.25 ? 0 : t < 0.72 ? 1 : 2;
        stepEls.forEach((node, i) => node.classList.toggle("on", i === phase));
        const text = phase < 2 ? `ORIGINAL · ${ow} × ${oh} px` : `MODEL INPUT · ${cw} × ${ch} px`;
        if (label.textContent !== text) label.textContent = text;
      },
    };
  }

  // C: conceptual illustration of a neural network. Decorative geometry only: no feature maps,
  // no claim about what any layer computes.
  function buildC() {
    const scene = el("div", "scene");
    scene.append(el("div", "chip tl concept", "CONCEPTUAL ILLUSTRATION · NOT THE MODEL'S REAL INTERNAL ACTIVITY"));
    const net = svg("svg", {
      viewBox: "0 0 940 380",
      class: "net",
      role: "img",
      "aria-label": "Simplified sketch: an image passes through many layers and ends in seven scores. Conceptual illustration.",
    });
    const cy = 200;
    const inX = 24, inY = cy - 60, inW = 120;
    const bx = [196, 308, 420, 532, 644], bw = 64, heights = [210, 184, 150, 118, 88];
    const headX = 724, headW = 46, headH = 120;
    const outX = 860;
    const codes = classes.length ? classes.map((c) => str(c.code)) : ["", "", "", "", "", "", ""];
    const outY = codes.map((_, j) => cy + (j - (codes.length - 1) / 2) * 38);

    // connectors first, so shapes sit on top
    const link = (x1, y1, x2, y2) => net.append(svg("line", { x1, y1, x2, y2, class: "link" }));
    link(inX + inW, cy, bx[0], cy);
    for (let i = 0; i < bx.length - 1; i++) link(bx[i] + bw, cy, bx[i + 1], cy);
    link(bx[bx.length - 1] + bw, cy, headX, cy);
    outY.forEach((y) => link(headX + headW, cy, outX, y));

    // input thumbnail: the real prepared crop when there is one, a neutral placeholder otherwise
    const cropUrl = ready ? safeUrl(images.crop) : null;
    if (cropUrl) {
      const thumb = svg("image", { x: inX, y: inY, width: inW, height: 120, preserveAspectRatio: "xMidYMid slice" });
      thumb.setAttribute("href", cropUrl);
      net.append(thumb);
    } else {
      net.append(svg("rect", { x: inX, y: inY, width: inW, height: 120, rx: 10, class: "ph" }));
    }
    net.append(svg("rect", { x: inX, y: inY, width: inW, height: 120, rx: 10, class: "frame" }));
    net.append(svg("text", { x: inX + inW / 2, y: inY + 146, "text-anchor": "middle" }, cropUrl ? "prepared image" : "your image"));

    // layers (decorative)
    const glows = bx.map((x, i) => {
      const h = heights[i];
      net.append(svg("rect", { x: x + 10, y: cy - h / 2 - 8, width: bw, height: h, rx: 8, class: "blk ghost" }));
      net.append(svg("rect", { x: x + 5, y: cy - h / 2 - 4, width: bw, height: h, rx: 8, class: "blk ghost" }));
      net.append(svg("rect", { x, y: cy - h / 2, width: bw, height: h, rx: 8, class: "blk" }));
      const glow = svg("rect", { x, y: cy - h / 2, width: bw, height: h, rx: 8, class: "glow" });
      glow.style.opacity = "0";
      net.append(glow);
      return glow;
    });

    // new final layer
    net.append(svg("rect", { x: headX, y: cy - headH / 2, width: headW, height: headH, rx: 8, class: "head" }));
    const headGlow = svg("rect", { x: headX, y: cy - headH / 2, width: headW, height: headH, rx: 8, class: "headglow" });
    headGlow.style.opacity = "0";
    net.append(headGlow);

    // seven output nodes (unlabeled by value: this sketch carries no numbers)
    const outs = outY.map((y, j) => {
      net.append(svg("circle", { cx: outX, cy: y, r: 10, class: "out" }));
      const glow = svg("circle", { cx: outX, cy: y, r: 10, class: "outglow" });
      glow.style.opacity = "0";
      net.append(glow);
      net.append(svg("text", { x: outX + 18, y: y + 4, class: "code" }, codes[j]));
      return glow;
    });

    // labels
    const midBlocks = (bx[0] + bx[bx.length - 1] + bw) / 2;
    net.append(svg("path", { d: `M${bx[0]} 76 V68 H${bx[bx.length - 1] + bw} V76`, class: "brace" }));
    net.append(svg("text", { x: midBlocks, y: 48, "text-anchor": "middle" }, "Pre-trained layers (ResNet-50, simplified)"));
    net.append(svg("text", { x: midBlocks, y: 30, "text-anchor": "middle" }, "already learned general visual patterns"));
    net.append(svg("text", { x: headX + headW / 2, y: cy + 90, "text-anchor": "middle" }, "New final layer"));
    net.append(svg("text", { x: headX + headW / 2, y: cy + 108, "text-anchor": "middle" }, "trained for 7 categories"));
    net.append(svg("text", { x: outX - 30, y: 352, "text-anchor": "middle" }, "seven scores, one per category"));

    const pulses = [0, 1, 2].map((k) => {
      const dot = svg("circle", { r: 5 - k, class: "pulse" });
      dot.style.opacity = "0";
      net.append(dot);
      return dot;
    });
    const fan = outY.map(() => {
      const dot = svg("circle", { r: 4, class: "pulse" });
      dot.style.opacity = "0";
      net.append(dot);
      return dot;
    });
    scene.append(net);

    const x0 = inX + inW;
    const headCenter = headX;
    return {
      node: scene,
      render(t) {
        const travel = clamp(t / 0.8);
        const x = lerp(x0, headCenter, travel);
        glows.forEach((glow, i) => {
          const lit = ease((x - (bx[i] - 40)) / 90);
          const settle = 1 - 0.45 * clamp((t - 0.9) / 0.1);
          glow.style.opacity = String(0.6 * lit * settle);
        });
        pulses.forEach((dot, k) => {
          const px = x - k * 20;
          const visible = t < 0.8 && px >= x0;
          dot.setAttribute("cx", String(px));
          dot.setAttribute("cy", String(cy));
          dot.style.opacity = visible ? String(1 - k * 0.3) : "0";
        });
        headGlow.style.opacity = String(0.55 * ease((t - 0.74) / 0.12));
        const spread = ease((t - 0.8) / 0.18);
        fan.forEach((dot, j) => {
          dot.setAttribute("cx", String(lerp(headX + headW, outX, spread)));
          dot.setAttribute("cy", String(lerp(cy, outY[j], spread)));
          dot.style.opacity = t > 0.8 && t < 0.98 ? "1" : "0";
        });
        const outLit = ease((t - 0.9) / 0.1);
        outs.forEach((glow) => { glow.style.opacity = String(0.55 * outLit); });
      },
    };
  }

  // D: the real seven probabilities, revealed to their computed values.
  function buildD() {
    if (!ready || classes.length === 0) return unavailableScene(message);
    const scene = el("div", "scene");
    const wrap = el("div", "d-wrap");
    const thumb = el("figure", "d-thumb");
    thumb.append(picture(images.crop, "The model's input crop", ""), el("figcaption", "", "model input"));
    const list = el("div", "d-bars");
    const head = el("div", "d-head");
    head.append(el("span", "", "Model probability"), el("span", "", "adds up to 100%"));
    list.append(head);
    const order = classes.map((c, i) => ({ code: str(c.code), name: str(c.name), p: num(c.p), i })).sort((a, b) => b.p - a.p);
    const rows = order.map((c) => {
      const row = el("div", c.i === topIndex ? "d-row top" : "d-row");
      const label = el("span", "lbl", c.name);
      label.append(el("i", "", c.code));
      const track = el("div", "trk");
      const fill = el("div", "fil");
      track.append(fill);
      const value = el("span", "val", "0%");
      row.append(label, track, value);
      list.append(row);
      return { fill, value, pct: c.p * 100 };
    });
    wrap.append(thumb, list);
    scene.append(el("div", "chip tl live", "ACTUAL OUTPUTS · REPLAYED"), wrap);
    return {
      node: scene,
      render(t) {
        rows.forEach((row, k) => {
          const done = ease((t * 1.3 - k * 0.08) / 0.6);
          const shown = row.pct * done;
          row.fill.style.width = `${shown.toFixed(2)}%`;
          row.value.textContent = `${shown.toFixed(2)}%`;
        });
      },
    };
  }

  // E: the real Grad-CAM heatmap over the real crop, with an opacity slider.
  function buildE() {
    const cropUrl = safeUrl(images.crop);
    const layerUrl = safeUrl(images.colorLayer);
    if (!heatmapReady || !cropUrl || !layerUrl) return unavailableScene(message);
    const scene = el("div", "scene");
    const wrap = el("div", "e-wrap");
    const frame = el("div", "e-frame");
    const layer = picture(layerUrl, "Grad-CAM heatmap colors", "layer");
    frame.append(picture(cropUrl, "The image the model sees", ""), layer);

    const legend = el("div", "legend");
    const bar = el("div", "lbar");
    const stops = (Array.isArray(payload.legend) ? payload.legend : [])
      .filter((s) => Array.isArray(s) && s.length === 4)
      .map((s) => `rgb(${Math.round(num(s[0]))},${Math.round(num(s[1]))},${Math.round(num(s[2]))}) ${Math.round(num(s[3]))}%`);
    if (stops.length) bar.style.background = `linear-gradient(90deg, ${stops.join(", ")})`;
    legend.append(el("span", "", "less contribution"), bar, el("span", "", "more contribution"));

    const sliderRow = el("label", "slider");
    const input = el("input", "");
    input.type = "range";
    input.min = "0";
    input.max = "100";
    input.value = "50";
    input.setAttribute("aria-label", "Heatmap opacity");
    const readout = el("output", "", "50%");
    sliderRow.append(el("span", "", "heatmap opacity"), input, readout);
    const note = el("div", "e-note", "Warmer = contributed more to this prediction. Not disease severity.");

    wrap.append(frame, legend, sliderRow, note);
    scene.append(el("div", "chip tl live", `ACTUAL HEATMAP · ${str(payload.heatmapLabel).toUpperCase()}`), wrap);

    let opacity = 0.5;
    let reveal = 1;
    const apply = () => { layer.style.opacity = String(opacity * reveal); };
    input.addEventListener("input", () => {
      opacity = clamp(Number(input.value) / 100);
      readout.textContent = `${Math.round(opacity * 100)}%`;
      apply();
    });
    return {
      node: scene,
      render(t) {
        reveal = ease(t / 0.6);
        apply();
      },
    };
  }

  const builders = { A: buildA, B: buildB, C: buildC, D: buildD, E: buildE };
  const scenes = {};
  for (const id of enabledIds) {
    scenes[id] = builders[id]();
    canvas.append(scenes[id].node);
  }

  // ---- stage tabs and progress segments ---------------------------------------------------
  const state = { index: 0, local: 1, playing: false };
  let raf = 0;
  let last = null;

  const tabButtons = STAGES.map((stage) => {
    const button = el("button", "");
    button.type = "button";
    button.setAttribute("role", "tab");
    button.append(el("span", "tl", stage.id), document.createTextNode(stage.label));
    button.disabled = !enabledIds.includes(stage.id);
    button.addEventListener("click", () => goTo(enabledIds.indexOf(stage.id)));
    tabsEl.append(button);
    return button;
  });
  const progButtons = enabledIds.map((id, i) => {
    const button = el("button", "pseg");
    button.type = "button";
    button.setAttribute("aria-label", `Go to stage ${id}: ${STAGES.find((s) => s.id === id).label}`);
    button.append(el("i", ""));
    button.addEventListener("click", () => goTo(i));
    progEl.append(button);
    return button;
  });

  function showStage() {
    const id = enabledIds[state.index];
    for (const key of Object.keys(scenes)) scenes[key].node.classList.toggle("on", key === id);
    const stage = STAGES.find((s) => s.id === id);
    const c = copy[id] || {};
    kickerEl.textContent = str(c.kicker) || `${id} · ${stage.label}`;
    titleEl.textContent = str(c.title) || stage.label;
    textEl.textContent = str(c.body) || message;
    text2El.textContent = str(c.body2);
    text2El.hidden = !c.body2;
    factsEl.replaceChildren();
    for (const row of Array.isArray(c.facts) ? c.facts : []) {
      if (!Array.isArray(row) || row.length < 2) continue;
      const wrapper = el("div", "fact");
      wrapper.append(el("dt", "", str(row[0])), el("dd", "", str(row[1])));
      factsEl.append(wrapper);
    }
    tagEl.textContent = str(c.tag);
    tabButtons.forEach((button, i) => button.setAttribute("aria-selected", String(STAGES[i].id === id)));
  }

  function render() {
    const id = enabledIds[state.index];
    // Reduced motion: always show the finished state of the stage.
    scenes[id].render(reduced ? 1 : state.local);
    progButtons.forEach((button, i) => {
      const fill = i < state.index ? 1 : i === state.index ? state.local : 0;
      button.firstChild.style.width = `${(fill * 100).toFixed(1)}%`;
    });
  }

  function updateControls() {
    const finished = state.index === enabledIds.length - 1 && state.local >= 1;
    playBtn.textContent = state.playing ? "❚❚ Pause" : finished ? "▶ Play again" : "▶ Play";
    flow.dataset.playing = String(state.playing);
    prevBtn.disabled = state.index === 0;
    nextBtn.disabled = state.index === enabledIds.length - 1;
  }

  function frame(timestamp) {
    raf = 0;
    if (!state.playing) { last = null; return; }
    if (last === null) last = timestamp;
    const dt = Math.min(timestamp - last, 100);
    last = timestamp;
    state.local += dt / DURATIONS[enabledIds[state.index]];
    if (state.local >= 1) {
      if (state.index < enabledIds.length - 1) {
        state.index += 1;
        state.local = 0;
        showStage();
      } else if (!hasImage) {
        state.local = 0; // loop the conceptual preview while no image is selected
      } else {
        state.local = 1;
        state.playing = false;
      }
    }
    render();
    updateControls();
    if (state.playing) raf = requestAnimationFrame(frame);
  }
  function startLoop() {
    if (!raf && state.playing) { last = null; raf = requestAnimationFrame(frame); }
  }

  function goTo(i) {
    state.index = Math.min(enabledIds.length - 1, Math.max(0, Math.round(i)));
    // Playing: animate the chosen stage from the start. Paused: show it fully drawn.
    state.local = state.playing ? 0 : 1;
    last = null;
    showStage();
    render();
    updateControls();
  }

  playBtn.addEventListener("click", () => {
    if (state.playing) {
      state.playing = false; // pause: freeze where we are
    } else {
      if (state.local >= 1) {
        state.index = state.index < enabledIds.length - 1 ? state.index + 1 : 0;
        state.local = 0;
        showStage();
      }
      state.playing = true;
      startLoop();
    }
    render();
    updateControls();
  });
  replayBtn.addEventListener("click", () => {
    state.index = 0;
    state.local = 0;
    state.playing = true;
    showStage();
    render();
    updateControls();
    startLoop();
  });
  prevBtn.addEventListener("click", () => goTo(state.index - 1));
  nextBtn.addEventListener("click", () => goTo(state.index + 1));

  function onKey(event) {
    if (event.target && event.target.type === "range") return;
    if (event.key === "ArrowRight") { event.preventDefault(); goTo(state.index + 1); }
    if (event.key === "ArrowLeft") { event.preventDefault(); goTo(state.index - 1); }
  }
  flow.addEventListener("keydown", onKey);

  const onMotionChange = (event) => {
    reduced = event.matches;
    flow.classList.toggle("reduced", reduced);
    render();
  };
  motionQuery.addEventListener("change", onMotionChange);

  const resizeObserver = new ResizeObserver(() => render());
  resizeObserver.observe(canvas);

  // ---- start ------------------------------------------------------------------------------
  if (!hasImage) {
    state.local = 0;
    state.playing = !reduced; // a looping conceptual preview, unless motion is reduced
  }
  showStage();
  render();
  updateControls();
  startLoop();

  return () => {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    state.playing = false;
    resizeObserver.disconnect();
    motionQuery.removeEventListener("change", onMotionChange);
    flow.removeEventListener("keydown", onKey);
  };
}
