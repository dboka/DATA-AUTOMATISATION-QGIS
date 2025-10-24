document.addEventListener("DOMContentLoaded", () => {

  // ================================
  // 🌍 KARTES INICIALIZĀCIJA
  // ================================
  const map = L.map('map').setView([56.95, 24.1], 7);

  // OSM pamatslānis
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // ================================
  // 🧱 SLĀŅU KONTEINERS
  // ================================
  const layers = {}; // ← šis tagad noteikti eksistē

  // ================================
  // 🌞 SAULES FLĪZES
  // ================================
  layers.saule = L.tileLayer('SauleTiles/{z}/{x}/{y}.png', {
    minZoom: 5,
    maxZoom: 12,
    opacity: 0.8,
    tms: true // ja karte izskatās "apgriezta", maini uz false
  });

  // ================================
  // 🧩 POGU FUNKCIONALITĀTE
  // ================================
  const buttons = {
    biomasaBtn: "biomasa",
    biogazeBtn: "biogaze",
    vejs1Btn: "vejs1",
    vejs2Btn: "vejs2",
    sauleBtn: "saule"
  };

  // Pogas notikumi
  for (const btnId in buttons) {
    const btn = document.getElementById(btnId);
    const key = buttons[btnId];

    btn.addEventListener("click", () => {
      const layer = layers[key];

      if (!layer) {
        alert("Šis slānis vēl nav ielādēts vai pieejams tikai Saule testam.");
        return;
      }

      if (map.hasLayer(layer)) {
        map.removeLayer(layer);
        btn.classList.remove("active");
      } else {
        layer.addTo(map);
        btn.classList.add("active");
      }
    });
  }

});
