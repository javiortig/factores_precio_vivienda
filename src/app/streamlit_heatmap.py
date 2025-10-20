
import os
import pandas as pd
import pydeck as pdk
import streamlit as st
import yaml

def load_settings(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _cell_to_latlng(h):
    import h3
    if hasattr(h3, "h3_to_geo"):  # v3
        lat, lon = h3.h3_to_geo(h)
    elif hasattr(h3, "cell_to_latlng"):  # v4
        lat, lon = h3.cell_to_latlng(h)
    else:
        raise RuntimeError("Error de versiones v3/v4 de h3")
    return lat, lon

@st.cache_data(show_spinner=False)
def read_hex_parquet(path):
    df = pd.read_parquet(path)
    exp = {"h3","municipio_id","municipio","date","price_eur_m2","kind"}
    missing = exp - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en {path}: {missing}")
    return df

@st.cache_data(show_spinner=False)
def compute_centroids(unique_h3):
    lat, lon = [], []
    for h in unique_h3:
        la, lo = _cell_to_latlng(h)
        lat.append(la); lon.append(lo)
    return pd.DataFrame({"h3": list(unique_h3), "lat": lat, "lon": lon})

def color_palette(name: str):
    if name == "YlOrRd":
        return [[255,255,204],[255,237,160],[254,217,118],[254,178,76],[253,141,60],[227,26,28]]
    if name == "Viridis":
        return [[68,1,84],[59,82,139],[33,145,140],[94,201,98],[253,231,37],[253,253,191]]
    if name == "Turbo":
        return [[48,18,59],[65,68,135],[42,120,142],[34,168,132],[122,209,81],[245,233,25]]
    if name == "Magma":
        return [[0,0,4],[48,18,59],[100,3,79],[145,27,74],[191,52,61],[252,253,191]]
    return [[239,243,255],[198,219,239],[158,202,225],[107,174,214],[49,130,189],[8,81,156]]

def render_legend(min_val, max_val, palette_name):
    cols = color_palette(palette_name)
    stops = " ".join([f"rgb({r},{g},{b})" for r,g,b in cols])
    st.markdown(f"""
    <div style="position:relative; margin-top:10px;">
      <div style="font-size:0.9rem; margin-bottom:4px;">€ / m²</div>
      <div style="height:14px; background:linear-gradient(90deg, {stops}); border-radius:6px;"></div>
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:2px;">
        <span>{min_val:.0f}</span><span>{max_val:.0f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Spain Housing — Heatmap", layout="wide")
    st.markdown("<h2 style='margin-bottom:0'>🏠 Spain Housing — Heatmap</h2><div style='color:#6b7280'>Mapa de calor suave, bonito y rápido (histórico/predicción)</div>", unsafe_allow_html=True)

    settings_path = os.getenv("SH3_SETTINGS", "configs/settings.yaml")
    if not os.path.exists(settings_path):
        st.error("No encuentro configs/settings.yaml. Asegúrate de ejecutar desde la raíz del proyecto.")
        st.stop()

    cfg = load_settings(settings_path)
    hex_parquet = cfg["data_paths"]["hex_prices_parquet"]

    st.sidebar.header("Controles")
    layer_kind = st.sidebar.radio("Capa", options=["Histórico", "Predicción"], horizontal=True)
    palette_name = st.sidebar.selectbox("Paleta", ["YlOrRd", "Viridis", "Turbo", "Magma", "Blues"], index=0)
    norm = st.sidebar.selectbox("Normalización", ["cuantiles", "min-max"], index=0)
    radius = st.sidebar.slider("Radio (px)", 10, 70, 35, 1)
    intensity = st.sidebar.slider("Intensidad", 0.1, 5.0, 1.0, 0.1)
    threshold = st.sidebar.slider("Umbral", 0.0, 1.0, 0.05, 0.01)

    if not os.path.exists(hex_parquet):
        st.warning("No existe data/hex/hex_prices.parquet. Genera datos primero: `python -m src.pipeline.build_all --demo`")
        st.stop()

    df = read_hex_parquet(hex_parquet)
    df = df[df["kind"].eq("history" if layer_kind=="Histórico" else "forecast")].copy()

    quarters = sorted(df["date"].astype(str).unique().tolist())
    q_sel = st.sidebar.select_slider("Trimestre", options=quarters, value=quarters[-1])
    df = df[df["date"].astype(str).eq(q_sel)].copy()

    uniq = df["h3"].unique().tolist()
    centroids = compute_centroids(tuple(uniq))
    df = df.merge(centroids, on="h3", how="left")

    if norm == "cuantiles":
        qmin, qmax = df["price_eur_m2"].quantile([0.02, 0.98]).tolist()
    else:
        qmin, qmax = float(df["price_eur_m2"].min()), float(df["price_eur_m2"].max())
    denom = (qmax - qmin) if (qmax - qmin) > 0 else 1.0
    df["weight"] = (df["price_eur_m2"] - qmin) / denom
    df["weight"] = df["weight"].clip(0, 1)

    map_style = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
    view_cfg = cfg.get("app", {}).get("map_initial_view", {"lat": 40.4168, "lon": -3.7038, "zoom": 4.4})
    initial_view = pdk.ViewState(latitude=view_cfg["lat"], longitude=view_cfg["lon"], zoom=view_cfg["zoom"])

    layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position="[lon, lat]",
        get_weight="weight",
        radiusPixels=radius,
        intensity=intensity,
        threshold=threshold,
        colorRange=color_palette(palette_name),
        aggregation="MEAN",
        pickable=False,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=initial_view,
        map_style=map_style,
        tooltip=None,
        parameters={"depthTest": False},
    )

    st.pydeck_chart(deck, use_container_width=True)
    render_legend(qmin, qmax, palette_name)
    st.caption("Fuente: datos de demo o MITMA proyectados a H3. Capa HeatmapLayer (mean €/m² normalizado).")

if __name__ == "__main__":
    main()
