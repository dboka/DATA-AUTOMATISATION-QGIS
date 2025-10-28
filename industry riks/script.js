document.addEventListener("DOMContentLoaded", () => {

  // ================================
  // 🌍 MAP INITIALIZATION
  // ================================
  const map = L.map('map').setView([56.95, 24.1], 7);

  // OSM base layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // ================================
  // 🧱 LAYER CONTAINER
  // ================================
  const layers = {};

  // ================================
  // 🌞 LOAD GEOTIFF (SAULE)
  // ================================
  // 👇 IMPORTANT: include folder name since Live Server runs from parent directory
  fetch("industry riks/Saule_raster_overlay_colored.tif")
    .then(response => {
      if (!response.ok) {
        throw new Error("File not found at: " + response.url);
      }
      return response.arrayBuffer();
    })
    .then(arrayBuffer => {
      parseGeoraster(arrayBuffer).then(georaster => {
        const sauleLayer = new GeoRasterLayer({
          georaster: georaster,
          opacity: 0.8,
          resolution: 256
        });

        layers.saule = sauleLayer;
        console.log("✅ Saule GeoTIFF fully loaded and ready!");
      });
    })
    .catch(err => console.error("❌ Error loading Saule GeoTIFF:", err));

  // ================================
  // 🧩 BUTTON FUNCTIONALITY
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
      const
