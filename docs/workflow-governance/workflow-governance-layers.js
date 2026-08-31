const root = document.getElementById("workflow-governance-layers");
const failDataLoad = (message, error) => {
  console.error(error);
  const status = document.createElement("p");
  status.className = "wgl-render-status text-small text-destructive";
  status.setAttribute("role", "alert");
  status.textContent = message;
  root.replaceChildren(status);
};

const isPlainObject = (value) =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const assertSetEquals = (actual, expected, label) => {
  const missing = [...expected].filter((item) => !actual.has(item));
  const unexpected = [...actual].filter((item) => !expected.has(item));
  if (missing.length || unexpected.length) {
    throw new Error(
      `${label} 不一致；缺少：${missing.join(", ") || "無"}；多出：${unexpected.join(", ") || "無"}`
    );
  }
};

const validateModel = (model) => {
  if (!isPlainObject(model) || model.schema_version !== 1) {
    throw new Error("YAML schema_version 必須是 1。");
  }
  if (!isPlainObject(model.document) || typeof model.document.title !== "string") {
    throw new Error("YAML 缺少 document.title。");
  }
  if (!isPlainObject(model.document.sections_html)) {
    throw new Error("YAML 缺少 document.sections_html。");
  }
  ["header_html"].forEach((key) => {
    if (typeof model.document[key] !== "string") {
      throw new Error(`YAML 缺少 document.${key}。`);
    }
  });
  ["a1", "a1_2", "a1_3"].forEach((key) => {
    if (typeof model.document.sections_html[key] !== "string") {
      throw new Error(`YAML 缺少 document.sections_html.${key}。`);
    }
  });
  if (!isPlainObject(model.presentation)) {
    throw new Error("YAML 缺少 presentation 設定。");
  }
  if (!isPlainObject(model.a1_details) || !isPlainObject(model.diagram_aria_labels)) {
    throw new Error("YAML 缺少 A1 details 或圖表 ARIA 說明。");
  }
  if (!isPlainObject(model.render_status) || !isPlainObject(model.validation)) {
    throw new Error("YAML 缺少 render_status 或 validation。");
  }
};

const validateRenderedModel = (model) => {
  const renderedDiagramIds = new Set(
    [...root.querySelectorAll("[data-diagram]")].map((diagram) => diagram.dataset.diagram)
  );
  assertSetEquals(
    renderedDiagramIds,
    new Set(model.validation.diagram_ids),
    "Mermaid diagram ID"
  );
  assertSetEquals(
    new Set(Object.keys(model.a1_details)),
    new Set(model.validation.a1_detail_node_ids),
    "A1 detail node ID"
  );
  const renderedActionIds = new Set(
    [...root.querySelectorAll('[data-diagram^="a1-2"]')]
      .flatMap((diagram) => diagram.textContent.match(/\bA12-A\d+(?:[AB])?\b/g) || [])
  );
  assertSetEquals(
    renderedActionIds,
    new Set(model.validation.a1_2_action_ids),
    "A1-2 action ID"
  );

  const allIds = [...root.querySelectorAll("[id]")].map((element) => element.id);
  if (new Set(allIds).size !== allIds.length) {
    throw new Error("YAML 產生了重複的 DOM ID。");
  }
  for (const element of root.querySelectorAll(
    "[aria-controls], [aria-labelledby], [aria-describedby]"
  )) {
    for (const attribute of ["aria-controls", "aria-labelledby", "aria-describedby"]) {
      for (const id of (element.getAttribute(attribute) || "").split(/\s+/).filter(Boolean)) {
        if (!document.getElementById(id)) {
          throw new Error(`${attribute} 指向不存在的 DOM ID：${id}`);
        }
      }
    }
  }
};

let model;
try {
  const [{ load }, response] = await Promise.all([
    import("https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/+esm"),
    fetch(new URL("./workflow-governance-layers.yaml", import.meta.url), {
      cache: "no-store"
    })
  ]);
  if (!response.ok) {
    throw new Error(`YAML HTTP ${response.status} ${response.statusText}`);
  }
  model = load(await response.text());
  validateModel(model);
  document.title = model.document.title;
  root.innerHTML = [
    model.document.header_html,
    model.document.sections_html.a1,
    model.document.sections_html.a1_2,
    model.document.sections_html.a1_3
  ].join("\n");
  validateRenderedModel(model);
} catch (error) {
  failDataLoad(
    "治理資料載入失敗。請確認已透過本機 HTTP server 開啟此頁面，且 YAML 格式正確。",
    error
  );
  throw error;
}

    const a1Status = root.querySelector("#wgl-mermaid-status");
    const a13Status = root.querySelector("#wgl-a13-mermaid-status");
    const a12Statuses = new Map(
      [...root.querySelectorAll("[data-mermaid-status]")].map((status) => [
        status.dataset.mermaidStatus,
        status
      ])
    );
    const isMobileLayout = window.matchMedia("(max-width: 520px)").matches;
    const isTwoColumnLayout = window.matchMedia("(min-width: 900px)").matches;
    const a12ZoomControlsEnabled = model.presentation.a1_2_zoom_controls_enabled;
    const diagrams = [...root.querySelectorAll(".wgl-mermaid")];
    const detailSelect = root.querySelector("#wgl-a1-detail-select");
    const detailTitle = root.querySelector("#wgl-a1-detail-title");
    const detailSummary = root.querySelector("#wgl-a1-detail-summary");
    const detailType = root.querySelector("#wgl-a1-detail-type");
    const detailInput = root.querySelector("#wgl-a1-detail-input");
    const detailNext = root.querySelector("#wgl-a1-detail-next");
    const detailGuard = root.querySelector("#wgl-a1-detail-guard");
    const detailPanel = root.querySelector("#wgl-a1-detail-panel");
    const decisionNodes = new Set(model.presentation.a1_decision_node_ids);
    const nodeTypes = model.presentation.a1_node_types;

    const details = model.a1_details;

    const createZoomPanController = (panel) => {
      const diagram = panel.querySelector(".wgl-zoom-canvas");
      const viewport = panel.querySelector(".wgl-zoom-viewport");
      const controls = panel.querySelector(".wgl-zoom-controls");
      const help = panel.querySelector(".wgl-fsm-notation");
      const zoomOut = panel.querySelector(".wgl-zoom-out");
      const zoomReset = panel.querySelector(".wgl-zoom-reset");
      const zoomIn = panel.querySelector(".wgl-zoom-in");
      const announcement = panel.querySelector(".wgl-zoom-announcement");
      const label = panel.dataset.zoomLabel || "圖表";
      const zoomMin = 75;
      const zoomMax = 200;
      const zoomStep = 25;
      let zoom = 100;
      let panPointerId = null;
      let panStartX = 0;
      let panStartY = 0;
      let panStartScrollLeft = 0;
      let panStartScrollTop = 0;

      controls.hidden = !a12ZoomControlsEnabled;
      if (!a12ZoomControlsEnabled) {
        help.textContent = "圖表維持 100%；縮放控制目前隱藏。";
      }

      const refresh = () => {
        const isPannable =
          viewport.scrollWidth > viewport.clientWidth + 1 ||
          viewport.scrollHeight > viewport.clientHeight + 1;
        viewport.classList.toggle("is-pannable", isPannable);
      };

      const applyZoom = (nextZoom) => {
        const previousScrollableWidth = viewport.scrollWidth;
        const previousScrollableHeight = viewport.scrollHeight;
        const previousCenter = viewport.scrollLeft + viewport.clientWidth / 2;
        const previousMiddle = viewport.scrollTop + viewport.clientHeight / 2;
        const previousCenterRatio = previousScrollableWidth
          ? previousCenter / previousScrollableWidth
          : 0.5;
        const previousMiddleRatio = previousScrollableHeight
          ? previousMiddle / previousScrollableHeight
          : 0.5;
        zoom = Math.min(zoomMax, Math.max(zoomMin, nextZoom));
        diagram.style.width = `${zoom}%`;
        viewport.classList.toggle("is-zoomed", zoom > 100);
        zoomReset.textContent = `${zoom}%`;
        zoomReset.title = zoom === 100 ? "目前為 100%" : "重設為 100%";
        zoomOut.disabled = zoom === zoomMin;
        zoomIn.disabled = zoom === zoomMax;
        announcement.textContent = `${label} 圖表縮放 ${zoom}%`;
        requestAnimationFrame(() => {
          const nextCenter = previousCenterRatio * viewport.scrollWidth;
          const nextMiddle = previousMiddleRatio * viewport.scrollHeight;
          viewport.scrollLeft = Math.max(0, nextCenter - viewport.clientWidth / 2);
          viewport.scrollTop = Math.max(0, nextMiddle - viewport.clientHeight / 2);
          refresh();
        });
      };

      const stopPan = () => {
        if (panPointerId === null) return;
        if (viewport.hasPointerCapture(panPointerId)) {
          viewport.releasePointerCapture(panPointerId);
        }
        panPointerId = null;
        viewport.classList.remove("is-panning");
      };

      viewport.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "touch" || event.button !== 0) return;
        if (!viewport.classList.contains("is-pannable")) return;
        panPointerId = event.pointerId;
        panStartX = event.clientX;
        panStartY = event.clientY;
        panStartScrollLeft = viewport.scrollLeft;
        panStartScrollTop = viewport.scrollTop;
        viewport.setPointerCapture(event.pointerId);
        viewport.classList.add("is-panning");
      });

      viewport.addEventListener("pointermove", (event) => {
        if (event.pointerId !== panPointerId) return;
        event.preventDefault();
        viewport.scrollLeft = panStartScrollLeft - (event.clientX - panStartX);
        viewport.scrollTop = panStartScrollTop - (event.clientY - panStartY);
      });
      viewport.addEventListener("pointerup", stopPan);
      viewport.addEventListener("pointercancel", stopPan);
      viewport.addEventListener("lostpointercapture", () => {
        panPointerId = null;
        viewport.classList.remove("is-panning");
      });
      zoomOut.addEventListener("click", () => applyZoom(zoom - zoomStep));
      zoomReset.addEventListener("click", () => applyZoom(100));
      zoomIn.addEventListener("click", () => applyZoom(zoom + zoomStep));
      applyZoom(100);
      return { refresh };
    };

    const zoomPanControllers = [...root.querySelectorAll("[data-zoom-pan]")].map(
      createZoomPanController
    );
    window.addEventListener("resize", () => {
      zoomPanControllers.forEach(({ refresh }) => requestAnimationFrame(refresh));
    });

    const showDetail = (nodeId) => {
      const detail = details[nodeId];
      if (!detail) return;
      detailSelect.value = nodeId;
      detailTitle.textContent = detail.title;
      detailSummary.textContent = detail.summary;
      detailType.textContent = nodeTypes[nodeId].label;
      detailInput.textContent = detail.input;
      detailNext.textContent = detail.next;
      detailGuard.textContent = detail.guard;
    };

    detailSelect.addEventListener("change", (event) => showDetail(event.target.value));
    showDetail(detailSelect.value);

    const colorCanvas = document.createElement("canvas");
    colorCanvas.width = 1;
    colorCanvas.height = 1;
    const colorContext = colorCanvas.getContext("2d", { willReadFrequently: true });

    const normalizeColor = (value) => {
      colorContext.clearRect(0, 0, 1, 1);
      colorContext.fillStyle = value;
      colorContext.fillRect(0, 0, 1, 1);
      const [red, green, blue, alpha] = colorContext.getImageData(0, 0, 1, 1).data;
      return `rgba(${red}, ${green}, ${blue}, ${alpha / 255})`;
    };

    const readColor = (name) => {
      const resolver = document.createElement("span");
      resolver.style.color = `var(${name})`;
      resolver.hidden = true;
      root.appendChild(resolver);
      const resolved = normalizeColor(getComputedStyle(resolver).color);
      resolver.remove();
      return resolved;
    };

    const diagramAriaLabels = model.diagram_aria_labels;
    const a12NodeLayers = model.presentation.a1_2_node_layers;
    const a12SharedBoundaryNodes = new Set(
      model.presentation.a1_2_shared_boundary_node_ids
    );

    try {
      const module = await import("https://cdn.jsdelivr.net/npm/mermaid@11.12.0/+esm");
      const mermaid = module.default;
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: "base",
        themeVariables: {
          background: "transparent",
          primaryColor: readColor("--card"),
          primaryTextColor: readColor("--card-foreground"),
          primaryBorderColor: readColor("--border"),
          secondaryColor: readColor("--muted"),
          secondaryTextColor: readColor("--foreground"),
          secondaryBorderColor: readColor("--border"),
          tertiaryColor: readColor("--background"),
          tertiaryTextColor: readColor("--foreground"),
          tertiaryBorderColor: readColor("--border"),
          lineColor: readColor("--muted-foreground"),
          textColor: readColor("--foreground"),
          clusterBkg: readColor("--background"),
          clusterBorder: readColor("--border"),
          edgeLabelBackground: readColor("--background"),
          fontSize: "14px"
        },
        flowchart: {
          curve: "basis",
          htmlLabels: true,
          nodeSpacing: isMobileLayout ? 18 : 26,
          rankSpacing: isMobileLayout ? 28 : 34,
          padding: 10,
          useMaxWidth: true
        }
      });

      await mermaid.run({ nodes: diagrams });
      const svgs = diagrams.map((item) => item.querySelector("svg"));
      zoomPanControllers.forEach(({ refresh }) => requestAnimationFrame(refresh));
      svgs.forEach((svg, index) => {
        const diagram = diagrams[index].dataset.diagram;
        svg.setAttribute("role", "img");
        svg.setAttribute("aria-label", diagramAriaLabels[diagram] || "Workflow 治理圖");
        svg.removeAttribute("height");
        svg.querySelectorAll("g.cluster").forEach((cluster) => {
          const label = cluster.textContent.trim();
          if (label.startsWith("L1｜")) cluster.classList.add("wgl-cluster-l1");
          if (label.startsWith("L2｜")) cluster.classList.add("wgl-cluster-l2");
          if (label.startsWith("L3｜")) cluster.classList.add("wgl-cluster-l3");
        });
        if (diagram.startsWith("a1-2")) {
          svg.querySelectorAll("g.node").forEach((node) => {
            const nodeId = Object.keys(a12NodeLayers).find((candidate) =>
              node.id.startsWith(`flowchart-${candidate}-`)
            );
            if (!nodeId) return;
            node.classList.add(`wgl-a12-layer-${a12NodeLayers[nodeId]}`);
            if (a12SharedBoundaryNodes.has(nodeId)) {
              node.classList.add("wgl-a12-shared-boundary");
            }
            if (nodeId === "N03") node.classList.add("wgl-a12-conditional");
            if (nodeId.endsWith("PORT")) node.classList.add("wgl-a12-boundary-port");
          });
        }
      });

      Object.entries(details).forEach(([nodeId, detail]) => {
        const nodeType = nodeTypes[nodeId];
        const node = svgs
          .flatMap((svg) => [...svg.querySelectorAll("g.node")])
          .find((candidate) => candidate.id.startsWith(`flowchart-${nodeId}-`));
        if (!node) return;
        const link = document.createElementNS("http://www.w3.org/2000/svg", "a");
        link.setAttribute("href", "#wgl-a1-detail-panel");
        link.setAttribute("aria-label", `查看 ${detail.title} 的詳細說明；節點類型：${nodeType.label}`);
        link.setAttribute("data-tooltip", detail.summary);
        link.setAttribute("data-tooltip-placement", "top");
        link.classList.add("wgl-node-link");
        link.classList.add(`wgl-node-${nodeId.slice(0, 2).toLowerCase()}`);
        link.classList.add(`wgl-node-type-${nodeType.key}`);
        if (decisionNodes.has(nodeId)) link.classList.add("wgl-node-decision");
        node.parentNode.insertBefore(link, node);
        link.append(node);
        link.addEventListener("pointerenter", () => {
          if (window.matchMedia("(hover: hover)").matches) showDetail(nodeId);
        });
        link.addEventListener("focus", () => showDetail(nodeId));
        link.addEventListener("click", (event) => {
          event.preventDefault();
          showDetail(nodeId);
          if (!isTwoColumnLayout) detailPanel.scrollIntoView({ block: "start" });
        });
      });

      a1Status.textContent = !isTwoColumnLayout
        ? model.render_status.a1_mobile
        : model.render_status.a1_desktop;
      const a12RenderedMessages = model.render_status.a1_2;
      a12Statuses.forEach((status, diagram) => {
        const interactionStatus = a12ZoomControlsEnabled
          ? model.render_status.interaction_enabled
          : model.render_status.interaction_disabled;
        status.textContent = `${a12RenderedMessages[diagram]} ${interactionStatus}`;
      });
      a13Status.textContent = model.render_status.a1_3;
    } catch (error) {
      console.error(error);
      a1Status.textContent = model.render_status.load_errors.a1;
      a13Status.textContent = model.render_status.load_errors.a1_3;
      a1Status.classList.add("text-destructive");
      a12Statuses.forEach((status) => {
        status.textContent = model.render_status.load_errors.a1_2;
        status.classList.add("text-destructive");
      });
      a13Status.classList.add("text-destructive");
    }
