// ====== PATCH Leaflet.VectorGrid "fakeStop" kļūdai ======
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
  //  Kartes inicializācija
  const map = L.map("map").setView([56.95, 24.1], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // ===============================
  //  Pane kārtas 
  // ===============================
  map.createPane("bottom"); map.getPane("bottom").style.zIndex = 400;
  map.createPane("middle"); map.getPane("middle").style.zIndex = 450;
  map.createPane("top"); map.getPane("top").style.zIndex = 500;

  // ===============================
  //  Slāņu definīcija
  // ===============================
  const layers = [
    { file: "geojson/VVD Atkritumu poligoni_optimized_dissolved.geojson", color: "#4caf50", name: "Atkritumu poligoni (VVD)", pane: "bottom" },
    { file: "geojson/CSP_BAT_dati_pilsetas_optimized.geojson", color: "#00c853", name: "BAT dati pilsētās (CSP)", pane: "bottom" },
    { file: "geojson/VVD Piesarnotas vietas_optimized_dissolved.geojson", color: "#ffeb3b", name: "Piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/VVD Potenciali piesarnotas vietas_optimized_dissolved.geojson", color: "#fff176", name: "Potenciāli piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/DAP Aizsargajamie koki_optimized_dissolved.geojson", color: "#fff176", name: "Aizsargājamie koki (DAP)", pane: "bottom" },
    { file: "geojson/DAP sugu atradnes_optimized_dissolved.geojson", color: "#fff176", name: "Sugu atradnes (DAP)", pane: "bottom" },
    { file: "geojson/DAP IADT ainavas_optimized_dissolved.geojson", color: "#ffeb3b", name: "Ainavu aizsardzības zonējumi (DAP)", pane: "bottom" },
    { file: "geojson/VMD_mezi_optimizeti_FAST.geojson.gz", color: "#f9f622", name: "Inventarizētie meži (VMD)", pane: "bottom" },
    { file: "geojson/DAP_Ipasi_aizsargajamie_biotopi_FAST.geojson", color: "#ff9800", name: "Īpaši aizsargājamie biotopi (DAP)", pane: "middle" },
    { file: "geojson/DAP potencialas natura 2000 teritorijas_optimized_dissolved.geojson", color: "#ffb74d", name: "Natura 2000 teritorijas (DAP)", pane: "middle" },
    { file: "geojson/DAP Nacionalas ainavu telpas_optimized_dissolved.geojson", color: "#ffa726", name: "Nacionālās ainavu telpas (DAP)", pane: "middle" },
    { file: "geojson/DAP mikroliegumi un buferzonas_optimized_dissolved.geojson", color: "#1e00ff", name: "Mikroliegumi un buferzonas (DAP)", pane: "top" },
    { file: "geojson/DAP IADT dabas pieminekli_optimized_dissolved.geojson", color: "#1e00ff", name: "Dabas pieminekļi (DAP)", pane: "top" },
    { file: "geojson/Īpaši aizsargājamas dabas teritorijas (zonējums nav vērts union)_optimized_dissolved.geojson", color: "#1e00ff", name: "ĪADT (zonējums, pilns) (DAP)", pane: "top" }
  ];

  const loadedLayers = [];

  // ===============================
  //  Slāņu ielāde
  // ===============================
  async function loadVectorLayer(layer) {
    try {
      const res = await fetch(layer.file);
      if (!res.ok) throw new Error("Nevar ielādēt failu: " + layer.file);

      let geojson;
      if (layer.file.endsWith(".gz")) {
        const buf = await res.arrayBuffer();
        const text = pako.inflate(buf, { to: "string" });
        geojson = JSON.parse(text);
      } else {
        geojson = await res.json();
      }

      const vLayer = L.vectorGrid.slicer(geojson, {
        rendererFactory: L.canvas.tile,
        pane: layer.pane,
        vectorTileLayerStyles: {
          sliced: {
            fill: true,
            fillColor: layer.color,
            fillOpacity: 0.8,
            color: "#222",
            weight: 0.4,
            stroke: true
          }
        },
        maxZoom: 16
      });

      loadedLayers.push({ ...layer, data: geojson, vLayer });
      vLayer.addTo(map);
      console.log(`✅ Ielādēts: ${layer.name}`);
    } catch (err) {
      console.error(`❌ Kļūda ielādējot ${layer.file}:`, err);
    }
  }

  // ===============================
  //  Ielādē visus slāņus UN tad izveido checkbox sarakstu
  // ===============================
  (async () => {
    for (const layer of layers) await loadVectorLayer(layer);
    createLayerCheckboxes();
  })();

  // ===============================
  //  Checkbox kontrole katram slānim
  // ===============================
  const layerControlsDiv = document.getElementById("layerControls");

  function createLayerCheckboxes() {
    layerControlsDiv.innerHTML = "";
    loadedLayers.forEach((l, i) => {
      const wrapper = document.createElement("div");
      wrapper.className = "layer-item";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = "layer-" + i;
      checkbox.checked = true;

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.innerHTML = `<span style="color:${l.color}">●</span> ${l.name}`;

      checkbox.addEventListener("change", () => {
        if (checkbox.checked) map.addLayer(l.vLayer);
        else map.removeLayer(l.vLayer);
      });

      wrapper.appendChild(checkbox);
      wrapper.appendChild(label);
      layerControlsDiv.appendChild(wrapper);
    });
  }

  // ===============================
  //  Popup ar pārklājumiem
  // ===============================
  map.on("click", e => {
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

    const html = found.length > 0
      ? `<b>Šajā vietā pārklājas:</b><br>${found.join("<br>")}`
      : "Nav atrastu slāņu šajā punktā.";

    L.popup().setLatLng(e.latlng).setContent(html).openOn(map);
  });

  // ===============================
  //  Pogu funkcijas
  // ===============================
  const btnOn = document.getElementById("toggleAll");
  const btnOff = document.getElementById("clearAll");

  btnOn.addEventListener("click", () => {
    loadedLayers.forEach(l => map.addLayer(l.vLayer));
    document.querySelectorAll("#layerControls input").forEach(cb => cb.checked = true);
  });

  btnOff.addEventListener("click", () => {
    loadedLayers.forEach(l => map.removeLayer(l.vLayer));
    document.querySelectorAll("#layerControls input").forEach(cb => cb.checked = false);
  });
});
