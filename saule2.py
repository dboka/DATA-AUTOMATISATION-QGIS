import geopandas as gpd
import pandas as pd
import glob
import os

# ==========================
# 1. KONFIGURĀCIJA
# ==========================
input_folder = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\OVERLAY\Saule\Saule Union"
latvia_border_path = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\Shapefaili CSP\Robeza.shp"

output_gpkg = os.path.join(input_folder, "solar_overlay_RISKSTEP.gpkg")
output_qml = os.path.join(input_folder, "solar_overlay_RISKSTEP.qml")

# ==========================
# 2. NOLASA ROBEŽU
# ==========================
border = gpd.read_file(latvia_border_path)
if border.crs and border.crs.to_epsg() != 3059:
    border = border.to_crs(epsg=3059)
border["final_color"] = "zals"
border["source_file"] = "robeza"
print("🟢 Latvijas robeža nolasīta.")

# ==========================
# 3. NOLASA VISUS GPKG FAILUS
# ==========================
files = glob.glob(os.path.join(input_folder, "*.gpkg"))
layers = [border]

for file in files:
    if "solar_overlay" in file.lower():
        continue
    try:
        gdf = gpd.read_file(file)
        gdf["source_file"] = os.path.basename(file)

        # CRS normalizācija
        if gdf.crs and gdf.crs.to_epsg() != 3059:
            gdf = gdf.to_crs(epsg=3059)

        name = os.path.basename(file).lower()
        if "sark" in name or "red" in name:
            gdf["final_color"] = "sarkans"
        elif "oran" in name or "orange" in name:
            gdf["final_color"] = "oranzs"
        elif "dzelt" in name or "yellow" in name:
            gdf["final_color"] = "dzeltens"
        else:
            continue

        keep_cols = ["geometry", "final_color", "source_file"]
        gdf = gdf[[c for c in gdf.columns if c in keep_cols]]
        layers.append(gdf)
    except Exception as e:
        print(f"⚠️ Nevarēja nolasīt {file}: {e}")

print(f"✅ Nolasīti {len(layers)-1} krāsotie slāņi + robeža.")

# ==========================
# 4. PĀRKLĀJUMA LOĢIKA
# ==========================
print("🧠 Izveido pārklājumus: dzeltens+dzeltens→oranzs, oranzs+oranžs→sarkans...")

# Izgūst oranžos un dzeltenos
orange_layers = [l for l in layers if "oranzs" in l["final_color"].values]
yellow_layers = [l for l in layers if "dzeltens" in l["final_color"].values]

if len(orange_layers) > 0:
    orange_merged = gpd.GeoDataFrame(pd.concat(orange_layers, ignore_index=True), crs="EPSG:3059")
else:
    orange_merged = gpd.GeoDataFrame(columns=["geometry", "final_color", "source_file"], geometry="geometry", crs="EPSG:3059")

if len(yellow_layers) > 0:
    yellow_merged = gpd.GeoDataFrame(pd.concat(yellow_layers, ignore_index=True), crs="EPSG:3059")
else:
    yellow_merged = gpd.GeoDataFrame(columns=["geometry", "final_color", "source_file"], geometry="geometry", crs="EPSG:3059")

# 4.1. Dzeltenais + Dzeltenais = Oranžs
if not yellow_merged.empty:
    yellow_overlap = gpd.overlay(yellow_merged, yellow_merged, how='intersection')
    yellow_overlap["final_color"] = "oranzs"
    yellow_overlap["source_file"] = "auto_yellow_yellow_to_orange"
    layers.append(yellow_overlap)

# 4.2. Oranžs + Oranžs = Sarkans
if not orange_merged.empty:
    orange_overlap = gpd.overlay(orange_merged, orange_merged, how='intersection')
    orange_overlap["final_color"] = "sarkans"
    orange_overlap["source_file"] = "auto_orange_orange_to_red"
    layers.append(orange_overlap)

# ==========================
# 5. APVIENO VISUS SLĀŅUS
# ==========================
print("🔄 Apvieno visus slāņus un piešķir prioritāti...")

for i in range(len(layers)):
    l = layers[i]
    for col in ["final_color", "source_file"]:
        if col not in l.columns:
            l[col] = ""
    layers[i] = l[["geometry", "final_color", "source_file"]]

merged = gpd.GeoDataFrame(pd.concat(layers, ignore_index=True), crs="EPSG:3059")

# Prioritātes kārtošana (kas virs kā)
priority = {"sarkans": 1, "oranzs": 2, "dzeltens": 3, "zals": 4}
merged["priority"] = merged["final_color"].map(priority)
merged = merged.sort_values("priority").reset_index(drop=True)

# ==========================
# 6. SAGLABĀ
# ==========================
if os.path.exists(output_gpkg):
    os.remove(output_gpkg)
merged.to_file(output_gpkg, driver="GPKG")

print(f"✅ Saglabāts: {output_gpkg}")

# ==========================
# 7. QGIS STILA FAILS
# ==========================
qml_style = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="final_color" symbollevels="0">
    <categories>
      <category render="true" symbol="0" value="sarkans" label="Sarkans"/>
      <category render="true" symbol="1" value="oranzs" label="Oranžs"/>
      <category render="true" symbol="2" value="dzeltens" label="Dzeltens"/>
      <category render="true" symbol="3" value="zals" label="Zaļš"/>
    </categories>
    <symbols>
      <symbol name="0" alpha="1" type="fill">
        <layer pass="0" class="SimpleFill">
          <prop k="color" v="255,0,0,160"/>
          <prop k="outline_color" v="0,0,0,0"/>
        </layer>
      </symbol>
      <symbol name="1" alpha="1" type="fill">
        <layer pass="0" class="SimpleFill">
          <prop k="color" v="255,140,0,140"/>
          <prop k="outline_color" v="0,0,0,0"/>
        </layer>
      </symbol>
      <symbol name="2" alpha="1" type="fill">
        <layer pass="0" class="SimpleFill">
          <prop k="color" v="255,255,0,120"/>
          <prop k="outline_color" v="0,0,0,0"/>
        </layer>
      </symbol>
      <symbol name="3" alpha="1" type="fill">
        <layer pass="0" class="SimpleFill">
          <prop k="color" v="0,200,0,80"/>
          <prop k="outline_color" v="0,0,0,0"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>
"""
with open(output_qml, "w", encoding="utf-8") as f:
    f.write(qml_style)

print(f"🎨 Izveidots QGIS stila fails: {output_qml}")
print("🚀 Gatavs! Ielādē QGIS → 'solar_overlay_RISKSTEP.gpkg' → 'Load Style' → 'solar_overlay_RISKSTEP.qml'")
