from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import folium
import branca.colormap as cm

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

file_path = DATA_DIR / "VARO_2016.shp"
gdf = gpd.read_file(file_path)


gdf["area_km2"] = gdf["AREAL"] / 1_000_000


print("\nHEAD:")
print(gdf.head())

print("\nCOLUMNS:")
print(gdf.columns)

print("\nINFO:")
print(gdf.info())

print("\nCATEGORY DISTRIBUTION:")
print(gdf["CATEGORY"].value_counts())


print("\nTOP 10 LARGEST WATER BODIES:")
print(
    gdf[["VATTENID", "CATEGORY", "AREAL", "area_km2"]]
    .sort_values(by="AREAL", ascending=False)
    .head(10)
)


area_by_category = gdf.groupby("CATEGORY")["AREAL"].sum().sort_values(ascending=False)
area_by_category_km2 = area_by_category / 1_000_000

print("\nTOTAL AREA PER CATEGORY:")
print(area_by_category)

print("\nTOTAL AREA PER CATEGORY (km²):")
print(area_by_category_km2)


fig, ax = plt.subplots(figsize=(12, 12))

gdf.plot(
    ax=ax,
    column="CATEGORY",
    legend=True,
    linewidth=0.05,
    edgecolor="black"
)

plt.title("Water Bodies in Sweden by Category", fontsize=16)
plt.axis("off")
plt.savefig(OUTPUT_DIR / "water_bodies_by_category.png", dpi=300, bbox_inches="tight")
plt.show()

gdf["log_area"] = np.log1p(gdf["area_km2"])

fig, ax = plt.subplots(figsize=(12, 12))

gdf.plot(
    ax=ax,
    column="log_area",
    legend=True,
    linewidth=0.05
)

plt.title("Water Bodies in Sweden Colored by Area", fontsize=16)
plt.axis("off")
plt.savefig(OUTPUT_DIR / "water_bodies_by_area.png", dpi=300, bbox_inches="tight")
plt.show()


gdf_web = gdf.to_crs(epsg=4326)


gdf_small = gdf_web.nlargest(200, "area_km2").copy()


gdf_small["geometry"] = gdf_small["geometry"].simplify(0.01)


m = folium.Map(
    location=[62.0, 15.0],
    zoom_start=5,
    tiles="CartoDB positron"
)


colormap = cm.linear.YlGnBu_09.scale(
    gdf_small["area_km2"].min(),
    gdf_small["area_km2"].max()
)
colormap.caption = "Area (km²)"


def style_function(feature):
    area = feature["properties"]["area_km2"]
    return {
        "fillColor": colormap(area),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    }



folium.GeoJson(
    gdf_small,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["VATTENID", "CATEGORY", "area_km2"],
        aliases=["Water ID:", "Category:", "Area (km²):"],
        localize=True
    )
).add_to(m)


colormap.add_to(m)


m.save(OUTPUT_DIR / "interactive_water_map.html")

print("\nInteractive map saved as 'interactive_water_map.html'")
print("Static maps saved as 'water_bodies_by_category.png' and 'water_bodies_by_area.png'")