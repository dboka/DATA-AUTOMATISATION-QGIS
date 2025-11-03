// =====================================================
// PATCH Leaflet.VectorGrid "fakeStop" kļūdai
// =====================================================
if (!L.DomEvent.fakeStop) {
  L.DomEvent.fakeStop = function (e) {
    if (e && e.stopPropagation) e.stopPropagation();
    if (e && e.preventDefault) e.preventDefault();
    e.cancelBubble = true;
    e.returnValue = false;
    return false;
  };
}

document.addEventListener("DOMContentLoaded", () => {
  // =====================================================
  //  KARTES INICIALIZĀCIJA
  // =====================================================
  const map = L.map("map", {
    preferCanvas: true,
    zoomSnap: 0.5,
    zoomDelta: 0.5,
    zoomAnimation: true,
    fadeAnimation: true,
    markerZoomAnimation: false
  }).setView([56.95, 24.1], 7);

  // Pane hierarhija
  map.createPane("background"); map.getPane("background").style.zIndex = 300;
  map.createPane("bottom");     map.getPane("bottom").style.zIndex = 400;
  map.createPane("middle");     map.getPane("middle").style.zIndex = 450;
  map.createPane("middle-top"); map.getPane("middle-top").style.zIndex = 460;
  map.createPane("top");        map.getPane("top").style.zIndex = 500;
  map.createPane("top-blue");   map.getPane("top-blue").style.zIndex = 520;

  // Pamatkarte
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 16,
    minZoom: 6,
    updateWhenIdle: true,
    updateWhenZooming: false,
    keepBuffer: 3,
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);

  // Latvijas robežas
  fetch("geojson/robeza.geojson")
    .then(res => res.json())
    .then(geojson => {
      L.geoJSON(geojson, {
        pane: "background",
        interactive: false,
        style: {
          fillColor: "#66bb6a",
          fillOpacity: 0.4,
          color: "#2e7d32",
          weight: 1
        }
      }).addTo(map);
    });

  // =====================================================
  //  PAMATSLĀŅI
  // =====================================================
  const layers = [
    { file: "geojson/VVD Atkritumu poligoni_optimized_dissolved.geojson", color: "#2e7d32", name: "Atkritumu poligoni (VVD)", pane: "bottom" },
    { file: "geojson/VVD Piesarnotas vietas_optimized_dissolved.geojson", color: "#e0b200", name: "Piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/VVD Potenciali piesarnotas vietas_optimized_dissolved.geojson", color: "#fff263", name: "Potenciāli piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/VMD_mezi_optimizeti_FAST.geojson.gz", color: "#d6cb3f", name: "Inventarizētie meži (VMD)", pane: "bottom" },
    { file: "geojson/DAP IADT ainavas_optimized_dissolved.geojson", color: "#f6d743", name: "Ainavu aizsardzības zonējumi (DAP)", pane: "bottom" },
    { file: "geojson/DAP Aizsargajamie koki_optimized_dissolved.geojson", color: "#f4e04d", name: "Aizsargājamie koki (DAP)", pane: "bottom" },
    { file: "geojson/DAP sugu atradnes_optimized_dissolved.geojson", color: "#ecff7d", name: "Sugu atradnes (DAP)", pane: "bottom" },
    { file: "geojson/DAP_Ipasi_aizsargajamie_biotopi_FAST.geojson", color: "#e65100", name: "Īpaši aizsargājamie biotopi (DAP)", pane: "middle-top" },
    { file: "geojson/DAP potencialas natura 2000 teritorijas_optimized_dissolved.geojson", color: "#ff8f00", name: "Natura 2000 teritorijas (DAP)", pane: "middle" },
    { file: "geojson/DAP Nacionalas ainavu telpas_optimized_dissolved.geojson", color: "#ffb74a", name: "Nacionālās ainavu telpas (DAP)", pane: "middle" },
    { file: "geojson/DAP mikroliegumi un buferzonas_optimized_dissolved.geojson", color: "#1565c0", name: "Mikroliegumi un buferzonas (DAP)", pane: "top" },
    { file: "geojson/DAP IADT dabas pieminekli_optimized_dissolved.geojson", color: "#2196f3", name: "Dabas pieminekļi (DAP)", pane: "top" },
    { file: "geojson/Īpaši aizsargājamas dabas teritorijas (zonējums nav vērts union)_optimized_dissolved.geojson", color: "#0d47a1", name: "ĪADT (zonējums, pilns) (DAP)", pane: "top" }
  ];

  const biomassLayerInfo = {
    file: "geojson/CSP_BAT_dati_pilsetas_optimized.geojson",
    color: "#ff8f00",
    name: "BAT dati pilsētās (CSP - Biomasa)",
    pane: "middle-top"
  };

  const blueCspLayerInfo = {
    file: "geojson/CSP_BAT_dati_pilsetas_optimized.geojson",
    color: "#1e88e5",
    name: "BAT dati pilsētās (CSP - Vējš līdz 2028.g.)",
    pane: "top-blue"
  };

  const loadedLayers = [];
  let currentActiveLayers = [...layers];

  // =====================================================
  //  SLĀŅU IELĀDE
  // =====================================================
  async function loadVectorLayer(layer) {
    if (layer.vLayer) return layer.vLayer;
    const res = await fetch(layer.file);
    let geojson;
    if (layer.file.endsWith(".gz")) {
      const buf = await res.arrayBuffer();
      const text = pako.inflate(buf, { to: "string" });
      geojson = JSON.parse(text);
    } else {
      geojson = await res.json();
    }
    const vLayer = L.vectorGrid.slicer(geojson, {
      pane: layer.pane,
      rendererFactory: L.canvas.tile,
      vectorTileLayerStyles: {
        sliced: {
          fill: true,
          fillColor: layer.color,
          fillOpacity: 0.7,
          stroke: false
        }
      },
      maxZoom: 18,
      interactive: false
    });
    layer.vLayer = vLayer;
    loadedLayers.push({ ...layer, data: geojson, vLayer });
    return vLayer;
  }

  // =====================================================
  //  POPUP
  // =====================================================
  map.on("click", e => {
    if (loadedLayers.length === 0) return;
    const { lat, lng } = e.latlng;
    const point = turf.point([lng, lat]);
    const found = [];
    loadedLayers.forEach(l => {
      if (!l.data?.features) return;
      l.data.features.forEach(f => {
        const geom = f.geometry;
        if (!geom) return;
        try {
          if (turf.booleanPointInPolygon(point, geom)) {
            found.push(`<span style="color:${l.color}">●</span> ${l.name}`);
          }
        } catch {}
      });
    });
    const html = found.length
      ? `<b>Šajā vietā pārklājas:</b><br>${found.join("<br>")}`
      : "Nav atrastu slāņu šajā punktā.";
    L.popup().setLatLng(e.latlng).setContent(html).openOn(map);
  });

  // =====================================================
  //  RADARI
  // =====================================================
  const lvgmcRadarGroup = [
    { file: "geojson/LVGMC Radars YELLOW LEVEL_optimized_dissolved.geojson", color: "#fdd835", name: "LVGMC Radars YELLOW", pane: "middle" },
    { file: "geojson/LVGMC Radars ORANGE level_optimized_dissolved.geojson", color: "#ff9800", name: "LVGMC Radars ORANGE", pane: "middle-top" },
    { file: "geojson/LVGMC Radars BLUE level_optimized_dissolved.geojson", color: "#1565c0", name: "LVGMC Radars BLUE", pane: "top-blue" }
  ];

  const amRadarGroup = [
    { file: "geojson/AM Radars YELLOW level spēkā līdz 2028. gadam;_optimized_dissolved.geojson", color: "#ffee58", name: "AM Radars YELLOW", pane: "middle" },
    { file: "geojson/AM Radars  BLUE level spēkā līdz 2028. gadam;_optimized_dissolved.geojson", color: "#1e88e5", name: "AM Radars BLUE", pane: "top-blue" }
  ];

  async function loadGroup(group) {
    const groupLayers = [];
    for (const l of group) {
      const vLayer = await loadVectorLayer(l);
      map.addLayer(vLayer);
      groupLayers.push(l);
    }
    return groupLayers;
  }

  function removeGroup(group) {
    group.forEach(l => {
      if (l.vLayer && map.hasLayer(l.vLayer)) map.removeLayer(l.vLayer);
    });
  }

  // =====================================================
  //  SLĀŅU SARAKSTS
  // =====================================================
  const layerControlsDiv = document.getElementById("layerControls");

  function updateLayerControlsGrouped(activeList) {
    layerControlsDiv.innerHTML = "";
    activeList.forEach((l, i) => {
      const div = document.createElement("div");
      div.className = "layer-item";
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.id = "layer-" + i;
      cb.checked = !!(l.vLayer && map.hasLayer(l.vLayer));
      const label = document.createElement("label");
      label.htmlFor = cb.id;
      label.innerHTML = `<span style="color:${l.color}">●</span> ${l.name}`;
      cb.addEventListener("change", async () => {
        if (l.group) {
          if (cb.checked) await loadGroup(l.group);
          else removeGroup(l.group);
        } else {
          const vLayer = await loadVectorLayer(l);
          if (cb.checked) map.addLayer(vLayer);
          else map.removeLayer(vLayer);
        }
      });
      div.appendChild(cb);
      div.appendChild(label);
      layerControlsDiv.appendChild(div);
    });
  }

  // =====================================================
  //  REŽĪMI
  // =====================================================
  async function applyEnergyMode(mode) {
    // vienmēr ielādē pamatslāņus
    for (const base of layers) {
      if (!base.vLayer) {
        const vLayer = await loadVectorLayer(base);
        map.addLayer(vLayer);
      }
    }

    let activeLayers = [...layers];

    removeGroup(lvgmcRadarGroup);
    removeGroup(amRadarGroup);
    if (biomassLayerInfo.vLayer && map.hasLayer(biomassLayerInfo.vLayer)) map.removeLayer(biomassLayerInfo.vLayer);
    if (blueCspLayerInfo.vLayer && map.hasLayer(blueCspLayerInfo.vLayer)) map.removeLayer(blueCspLayerInfo.vLayer);

    if (mode === "biomasa") {
      const bio = await loadVectorLayer(biomassLayerInfo);
      map.addLayer(bio);
      activeLayers.push(biomassLayerInfo);
    } else if (mode === "vejs2028") {
      await loadGroup(lvgmcRadarGroup);
      await loadGroup(amRadarGroup);
      const blue = await loadVectorLayer(blueCspLayerInfo);
      map.addLayer(blue);
      activeLayers.push(...lvgmcRadarGroup, ...amRadarGroup, blueCspLayerInfo);
    }

    currentActiveLayers = activeLayers;
    updateLayerControlsGrouped(activeLayers);
  }

  // =====================================================
  //  POGAS
  // =====================================================
  document.getElementById("toggleAll").addEventListener("click", async () => {
    for (const l of currentActiveLayers) {
      const v = await loadVectorLayer(l);
      map.addLayer(v);
    }
    document.querySelectorAll("#layerControls input").forEach(c => (c.checked = true));
  });

  document.getElementById("clearAll").addEventListener("click", () => {
    currentActiveLayers.forEach(l => {
      if (l.vLayer && map.hasLayer(l.vLayer)) map.removeLayer(l.vLayer);
    });
    document.querySelectorAll("#layerControls input").forEach(c => (c.checked = false));
  });

  // =====================================================
  //  RADIO
  // =====================================================
  document.querySelectorAll('.energy-switch input[name="energy"]').forEach(radio => {
    radio.addEventListener("change", e => applyEnergyMode(e.target.value));
  });

  const initialRadio = document.querySelector('.energy-switch input[name="energy"]:checked');
  if (initialRadio) applyEnergyMode(initialRadio.value);
});
