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
  // 🌍 Kartes inicializācija
  const map = L.map("map").setView([56.95, 24.1], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // ===============================
  // 🧱 Pane kārtas
  // ===============================
  map.createPane("bottom"); map.getPane("bottom").style.zIndex = 400;
  map.createPane("middle"); map.getPane("middle").style.zIndex = 450;
  map.createPane("top"); map.getPane("top").style.zIndex = 500;

  // ===============================
  // 📦 Slāņi pēc tabulas
  // ===============================
  const layers = [
    // 🌳 VVD + CSP (zaļie)
    { file: "geojson/VVD Atkritumu poligoni_optimized_dissolved.geojson", color: "#4caf50", name: "Atkritumu poligoni (VVD)", pane: "bottom" },
    { file: "geojson/CSP_BAT_dati_pilsetas_optimized.geojson", color: "#00c853", name: "BAT dati pilsētās (CSP)", pane: "bottom" },

    // 💛 Dzeltenie
    { file: "geojson/VVD Piesarnotas vietas_optimized_dissolved.geojson", color: "#ffeb3b", name: "Piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/VVD Potenciali piesarnotas vietas_optimized_dissolved.geojson", color: "#fff176", name: "Potenciāli piesārņotās vietas (VVD)", pane: "bottom" },
    { file: "geojson/DAP Aizsargajamie koki_optimized_dissolved.geojson", color: "#fff176", name: "Aizsargājamie koki (DAP)", pane: "bottom" },
    { file: "geojson/DAP sugu atradnes_optimized_dissolved.geojson", color: "#fff176", name: "Sugu atradnes (DAP)", pane: "bottom" },
    { file: "geojson/DAP IADT ainavas_optimized_dissolved.geojson", color: "#ffeb3b", name: "Ainavu aizsardzības zonējumi (DAP)", pane: "bottom" },
    { file: "geojson/VMD_mezi_optimizeti_FAST.geojson.gz", color: "#f9f622", name: "Inventarizētie meži (VMD)", pane: "bottom" },

    // 🟧 Oranžie
    { file: "geojson/DAP_Ipasi_aizsargajamie_biotopi_FAST.geojson", color: "#ff9800", name: "Īpaši aizsargājamie biotopi (DAP)", pane: "middle" },
    { file: "geojson/DAP potencialas natura 2000 teritorijas_optimized_dissolved.geojson", color: "#ffb74d", name: "Natura 2000 teritorijas (DAP)", pane: "middle" },
    { file: "geojson/DAP Nacionalas ainavu telpas_optimized_dissolved.geojson", color: "#ffa726", name: "Nacionālās ainavu telpas (DAP)", pane: "middle" },

    // 🔴 Sarkanie
    { file: "geojson/DAP mikroliegumi un buferzonas_optimized_dissolved.geojson", color: "#1e00ffff", name: "Mikroliegumi un buferzonas (DAP)", pane: "top" },
    { file: "geojson/DAP IADT dabas pieminekli_optimized_dissolved.geojson", color: "#1e00ffff", name: "Dabas pieminekļi (DAP)", pane: "top" },
    { file: "geojson/Īpaši aizsargājamas dabas teritorijas (zonējums nav vērts union)_optimized_dissolved.geojson", color: "#1e00ffff", name: "ĪADT (zonējums, pilns) (DAP)", pane: "top" }
  ];

  // ===============================
  // 💾 Saglabā slāņus popup analīzei
  // ===============================
  const loadedLayers = [];

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

      // 🌈 Zīmēšanai (VectorGrid)
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
      vLayer.addTo(map);

      // Saglabā arī ģeometriju pārklājumu meklēšanai
      loadedLayers.push({ name: layer.name, color: layer.color, data: geojson });
      console.log(`✅ Ielādēts: ${layer.name}`);
    } catch (err) {
      console.error(`❌ Kļūda ielādējot ${layer.file}:`, err);
    }
  }

  (async () => {
    for (const layer of layers) await loadVectorLayer(layer);
  })();

  // ===============================
  // 📍 Popup ar pārklājumiem (Turf.js)
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

        if (geom.type === "Polygon" || geom.type === "MultiPolygon") {
          try {
            const inside = turf.booleanPointInPolygon(point, geom);
            if (inside) found.push(`<span style="color:${l.color};">●</span> ${l.name}`);
          } catch (err) {}
        }
      });
    });

    if (found.length > 0) {
      L.popup()
        .setLatLng(e.latlng)
        .setContent(`<b>Šajā vietā pārklājas:</b><br>${found.join("<br>")}`)
        .openOn(map);
    } else {
      L.popup()
        .setLatLng(e.latlng)
        .setContent("Nav atrastu slāņu šajā punktā.")
        .openOn(map);
    }
  });
});
