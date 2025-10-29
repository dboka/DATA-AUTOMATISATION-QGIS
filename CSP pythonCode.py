import geopandas as gpd
import pandas as pd
import unicodedata
import os

# --- 1. Ceļš uz ievades failu (pielāgo pēc vajadzības) ---
input_path = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\BAT CSP\CSP BAT dati.shp"

# --- 2. Izvades fails ---
output_path = r"C:\Users\deniss.boka\Desktop\Boka_datuparbaude\BAT CSP\CSP_BAT_dati_pilsetas.gpkg"

# --- 3. Oficiālais Latvijas pilsētu saraksts (81 pilsēta) ---
city_names = pd.Series([
    "Ainaži", "Aizkraukle", "Aizpute", "Aknīste", "Aloja", "Alūksne", "Ape", "Auce",
    "Baldone", "Baloži", "Balvi", "Bauska", "Brocēni", "Cēsis", "Cesvaine", "Dagda",
    "Daugavpils", "Dobele", "Durbe", "Grobiņa", "Gulbene", "Ilūkste", "Ikšķile",
    "Jaunjelgava", "Jēkabpils", "Jelgava", "Jūrmala", "Kalnciems", "Kandava",
    "Karosta", "Kārsava", "Koknese", "Krāslava", "Kuldīga", "Lielvārde", "Liepāja",
    "Līgatne", "Limbaži", "Līvāni", "Lubāna", "Ludza", "Madona", "Mazsalaca",
    "Ogre", "Olaine", "Pāvilosta", "Piltene", "Pļaviņas", "Preiļi", "Rēzekne",
    "Rīga", "Rūjiena", "Sabile", "Salacgrīva", "Salaspils", "Saldus", "Saulkrasti",
    "Sigulda", "Skrunda", "Smiltene", "Staicele", "Stende", "Strenči", "Subate",
    "Talsi", "Tukums", "Valka", "Valmiera", "Varakļāni", "Vangaži", "Ventspils",
    "Viesīte", "Viļaka", "Viļāni", "Zilupe", "Ērgļi (Ērgļu pagasts)", "Ķegums", "Ķemeri",
    "Iecava", "Ķekava", "Mārupe", "Salaspils"
])

# --- 4. Palīgfunkcija diakritiku noņemšanai ---
def normalize_name(s):
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    # Noņem garumzīmes un mīkstinājumus (ā→a, ē→e utt.)
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

# --- 5. Ielādē shapefile ---
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Ievades fails nav atrasts: {input_path}")

gdf = gpd.read_file(input_path)
print(f"Ielādēti {len(gdf)} ieraksti no {os.path.basename(input_path)}")

# --- 6. Normalizē nosaukumus gan shapefile, gan pilsētu sarakstā ---
gdf['Name'] = gdf['Name'].astype(str).apply(normalize_name)
city_names = city_names.apply(normalize_name)

# --- 7. Filtrē tikai pilsētas ---
gdf_filtered = gdf[gdf['Name'].isin(city_names)]

print(f"\n✅ Atrastas {len(gdf_filtered)} pilsētas no {len(gdf)} kopā.")

# --- 8. Parāda, kuras pilsētas nav atrastas shapefile ---
found_cities = set(gdf_filtered['Name'].unique())
missing_cities = set(city_names) - found_cities

if missing_cities:
    print("\n⚠️ Pilsētas, kuras nav atrastas shapefile:")
    for city in sorted(missing_cities):
        print(" -", city.capitalize())
else:
    print("\n🎉 Atrastas visas 81 pilsētas!")

# --- 9. Saglabā jauno failu ---
if len(gdf_filtered) > 0:
    gdf_filtered.to_file(output_path, driver="GPKG")
    print(f"\n💾 Saglabāts fails: {output_path}")
else:
    print("\n⚠️ Netika atrasta neviena pilsēta no saraksta.")
