import streamlit as st, geopandas as gpd, pandas as pd
import json
import pydeck as pdk, json

st.set_page_config(layout="wide", page_title="Vivienda España — Mapa municipal")

geo = gpd.read_file("data/curated/municipios_geo.geojson")
df  = pd.read_parquet("data/curated/municipios_master.parquet")

# Selector temporal (trimestres disponibles)
quarters = sorted(df["date"].astype(str).unique())
q_sel = st.select_slider("Trimestre", options=quarters, value=quarters[-1])

# Capa: Histórico / Predicción (por ahora histórico; “Predicción” cuando entrenes el modelo y guardes df_pred con mismo esquema)
layer = st.radio("Capa", ["Histórico", "Predicción"], horizontal=True)
use_df = df[df["date"].astype(str).eq(q_sel)].copy()
metric = "price_eur_m2"  # o "pred_price_eur_m2" cuando tengas predicción

# Merge para el mapa
m = geo.merge(use_df[["municipio_id", metric]], on="municipio_id", how="left")

# Choropleth básico con tooltip
st.markdown(f"### {layer} — {q_sel}")
st.map  # placeholder para evitar warning en algunos entornos

mjson = json.loads(m.to_json())
# valores para breaks
vals = use_df[metric].dropna()
vmin, vmax = (float(vals.quantile(0.05)), float(vals.quantile(0.95))) if len(vals) else (0,1)

layer_geo = pdk.Layer(
    "GeoJsonLayer",
    data=mjson,
    pickable=True,
    stroked=False,
    filled=True,
    get_fill_color=f"""
      [255*(1-((properties.{metric}-{vmin})/({vmax}-{vmin}))), 
       80, 
       255*((properties.{metric}-{vmin})/({vmax}-{vmin})),
       180]
    """,
)

view = pdk.ViewState(latitude=40.4, longitude=-3.7, zoom=4.5)
tooltip = {"html": "<b>{municipio}</b><br/>€ / m²: {"+metric+"}"}
st.pydeck_chart(pdk.Deck(layers=[layer_geo], initial_view_state=view, map_style=None, tooltip=tooltip), use_container_width=True)

st.caption("Pasar el ratón por encima muestra el valor del municipio. Cuando añadas predicción, guarda el mismo esquema con una columna `pred_price_eur_m2` y cambia `metric` según la capa.")
