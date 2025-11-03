// PATCH Leaflet.VectorGrid "fakeStop" kļūdai
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
  // ===============================
  //  KARTES INICIALIZĀCIJA
  // ===============================
  const map = L.map("map", {
    preferCanvas: true,
    zoomSnap: 0.5,
    zoomDelta: 0.5,
    zoomAnimation: true,
    fadeAnimation: true,
    markerZoomAnimation: false
  }).setView([56.95, 24.1], 7);

  // Pane kārtība
  map.createPane("background"); map.getPane("background").style.zIndex = 300;
  map.createPane("bottom");     map.getPane("bottom").style.zIndex = 400;
  map.createPane("middle");     map.getPane("middle").style.zIndex = 450;
  map.createPane("top");        map.getPane("top").style.zIndex = 500;

  // Pamatkarte
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 16,
    minZoom: 6,
    updateWhenIdle: true,
    updateWhenZooming: false,
    keepBuffer: 3,
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);

  // Latvijas robežas fons
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

  // ===============================
  //  SLĀŅI: sadalīti četrās krāsu grupās
  // ===============================
 const layers = [
  // 🌿 ZAĻIE SLĀŅI
  { file: "geojson/VVD Atkritumu poligoni_optimized_dissolved.geojson", color: "#2e7d32", name: "Atkritumu poligoni (VVD)", pane: "bottom" },

 // 💛 DZELTENIE SLĀŅI — siltā saimes pāreja no olīvdzeltena uz neona
  { file: "geojson/VVD Piesarnotas vietas_optimized_dissolved.geojson", color: "#e0b200", name: "Piesārņotās vietas (VVD)", pane: "bottom" },      // dziļš zeltains dzeltens
  { file: "geojson/VVD Potenciali piesarnotas vietas_optimized_dissolved.geojson", color: "#fff263", name: "Potenciāli piesārņotās vietas (VVD)", pane: "bottom" },  // gaišs, maigs dzeltens
  { file: "geojson/VMD_mezi_optimizeti_FAST.geojson.gz", color: "#d6cb3f", name: "Inventarizētie meži (VMD)", pane: "bottom" },                 // olīvzaļgandzelts
  { file: "geojson/DAP IADT ainavas_optimized_dissolved.geojson", color: "#f6d743", name: "Ainavu aizsardzības zonējumi (DAP)", pane: "bottom" }, // tīrs zeltains
  { file: "geojson/DAP Aizsargajamie koki_optimized_dissolved.geojson", color: "#f4e04d", name: "Aizsargājamie koki (DAP)", pane: "bottom" },    // bāls, maigs tonis, labs pārklājumos
  { file: "geojson/DAP sugu atradnes_optimized_dissolved.geojson", color: "#ecff7d", name: "Sugu atradnes (DAP)", pane: "bottom" },             // gaiši dzeltenzaļš (dabisks kontrasts pret mežiem)
  
  // 🟠 ORANŽIE SLĀŅI — siltā pāreja no dziļa oranža uz vieglu persiku
  { file: "geojson/DAP_Ipasi_aizsargajamie_biotopi_FAST.geojson", color: "#e65100", name: "Īpaši aizsargājamie biotopi (DAP)", pane: "middle" }, // tumšs, spēcīgs oranžs
  { file: "geojson/DAP potencialas natura 2000 teritorijas_optimized_dissolved.geojson", color: "#ff8f00", name: "Natura 2000 teritorijas (DAP)", pane: "middle" }, // tīrs oranžs
  { file: "geojson/DAP Nacionalas ainavu telpas_optimized_dissolved.geojson", color: "#ffb74a", name: "Nacionālās ainavu telpas (DAP)", pane: "middle" }, // gaišs, persikains tonis

  // 🔵 ZILIE SLĀŅI — vēsā saime ar dziļuma gradāciju
  { file: "geojson/DAP mikroliegumi un buferzonas_optimized_dissolved.geojson", color: "#1565c0", name: "Mikroliegumi un buferzonas (DAP)", pane: "top" }, // dziļš kobaltzils
  { file: "geojson/DAP IADT dabas pieminekli_optimized_dissolved.geojson", color: "#2196f3", name: "Dabas pieminekļi (DAP)", pane: "top" }, // tīrs debeszils
  { file: "geojson/Īpaši aizsargājamas dabas teritorijas (zonējums nav vērts union)_optimized_dissolved.geojson", color: "#0d47a1", name: "ĪADT (zonējums, pilns) (DAP)", pane: "top" } // tumši jūras zils
];

  const loadedLayers = [];
  const layerControlsDiv = document.getElementById("layerControls");

  // ===============================
  //  SLĀŅU IELĀDE
  // ===============================
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
          fillOpacity: 0.70,   // caurspīdīgums
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

  // ===============================
  //  POPUP LOĢIKA (pārklājumi klikšķa vietā)
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

    const html = found.length
      ? `<b>Šajā vietā pārklājas:</b><br>${found.join("<br>")}`
      : "Nav atrastu slāņu šajā punktā.";

    L.popup()
      .setLatLng(e.latlng)
      .setContent(html)
      .openOn(map);
  });

  // ===============================
  //  CHECKBOX KONTROLE
  // ===============================
  function createLayerCheckboxes() {
    layerControlsDiv.innerHTML = "";
    layers.forEach((l, i) => {
      const wrapper = document.createElement("div");
      wrapper.className = "layer-item";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = "layer-" + i;

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.innerHTML = `<span style="color:${l.color}">●</span> ${l.name}`;

      checkbox.addEventListener("change", async () => {
        if (checkbox.checked) {
          const vLayer = await loadVectorLayer(l);
          map.addLayer(vLayer);
        } else if (l.vLayer) {
          map.removeLayer(l.vLayer);
        }
      });

      wrapper.appendChild(checkbox);
      wrapper.appendChild(label);
      layerControlsDiv.appendChild(wrapper);
    });
  }

  createLayerCheckboxes();

  // ===============================
  //  POGAS
  // ===============================
  document.getElementById("toggleAll").addEventListener("click", async () => {
    const checkboxes = document.querySelectorAll("#layerControls input");
    for (let i = 0; i < layers.length; i++) {
      const vLayer = await loadVectorLayer(layers[i]);
      map.addLayer(vLayer);
      checkboxes[i].checked = true;
    }
  });

  document.getElementById("clearAll").addEventListener("click", () => {
    layers.forEach(l => { if (l.vLayer) map.removeLayer(l.vLayer); });
    document.querySelectorAll("#layerControls input").forEach(cb => cb.checked = false);
  });
});
// === Enerģijas pārslēgšana ===
document.querySelectorAll('.energy-switch input[name="energy"]').forEach(radio => {
  radio.addEventListener('change', e => {
    const value = e.target.value;
    const mapContainer = document.getElementById('map');

    if (value === 'saule' || value === 'biomasa') {
      mapContainer.style.display = 'block'; // rāda karti
    } else {
      mapContainer.style.display = 'none';  // slēpj karti (kamēr citi resursi nav gatavi)
    }
  });
});