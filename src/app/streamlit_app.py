import os
import pandas as pd
import pydeck as pdk
import streamlit as st
import yaml

SETTINGS_PATH = os.getenv("SH3_SETTINGS", "configs/settings.yaml")


@st.cache_data
def load_settings(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_columns(df: pd.DataFrame, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas: {missing}")
        st.stop()


def main():
    st.set_page_config(page_title="Spain Housing H3 – MVP", layout="wide")
    st.title("🏠 Spain Housing H3 – MVP (Histórico + Predicción)")
    st.caption("Mapa de calor H3 por trimestre. Cambia entre histórico y predicción con el toggle.")

    cfg = load_settings(SETTINGS_PATH)
    hex_parquet = cfg["data_paths"]["hex_prices_parquet"]
    demo_points_csv = cfg["data_paths"]["demo_points_csv"]

    # Sidebar
    st.sidebar.header("Controles")
    kind = st.sidebar.radio("Capa", options=["Histórico", "Predicción"], horizontal=True)
    view_cfg = cfg.get("app", {}).get("map_initial_view", {"lat": 40.4168, "lon": -3.7038, "zoom": 4.4})
    resolution = cfg.get("h3", {}).get("resolution", 8)

    # Intenta cargar datos H3
    use_fallback = False
    if os.path.exists(hex_parquet):
        df = pd.read_parquet(hex_parquet)
        ensure_columns(df, ["h3", "municipio_id", "municipio", "date", "price_eur_m2", "kind"])
        # Filtrado por capa
        if kind == "Histórico":
            layer_df = df[df["kind"] == "history"].copy()
        else:
            layer_df = df[df["kind"] == "forecast"].copy()

        # Slider temporal
        quarters = sorted(layer_df["date"].unique().tolist())
        q_sel = st.sidebar.select_slider("Trimestre", options=quarters, value=quarters[-1])
        layer_df = layer_df[layer_df["date"] == q_sel]
        st.sidebar.caption(f"Trimestre seleccionado: {q_sel}")

        # Rango de color automático por cuantiles
        qmin, qmax = layer_df["price_eur_m2"].quantile([0.02, 0.98]).tolist()
        tooltip = {"html": "<b>€/{m2}:</b> {price_eur_m2:.0f}<br/><b>Municipio:</b> {municipio}", "style": {"color": "white"}}
        layer = pdk.Layer(
            "H3HexagonLayer",
            data=layer_df,
            get_hexagon="h3",
            get_fill_color="[255 * (price_eur_m2 - qmin) / (qmax - qmin + 1e-9), 64, 200]",  # escala simple
            pickable=True,
            stroked=False,
            extruded=False,
            opacity=0.7,
            parameters={"depthTest": False},
        )
        initial_view_state = pdk.ViewState(latitude=view_cfg["lat"], longitude=view_cfg["lon"], zoom=view_cfg["zoom"])        
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=initial_view_state, tooltip=tooltip))
        st.success("Mostrando capa H3 desde Parquet")        
    else:
        use_fallback = True

    if use_fallback:
        st.warning("No se encontró `data/hex/hex_prices.parquet`. Mostrando **demo** con puntos y HexagonLayer (fallback). Ejecuta el pipeline para activar la capa H3.")
        demo = pd.read_csv(demo_points_csv)
        ensure_columns(demo, ["lat", "lon", "municipio", "municipio_id", "date", "price_eur_m2"])
        if kind == "Histórico":
            # Para la demo, tomamos últimos 8 años como "histórico"
            demo["quarter"] = pd.PeriodIndex(demo["date"], freq="Q")
            q_sel = demo["quarter"].max()
            demo = demo[demo["quarter"] == q_sel]
        else:
            # "Predicción" ficticia: +3% sobre el último valor por municipio
            demo = (demo.sort_values(["municipio_id", "date"]).groupby("municipio_id").tail(1).copy())
            demo["price_eur_m2"] *= 1.03

        qmin, qmax = demo["price_eur_m2"].quantile([0.02, 0.98]).tolist()
        layer = pdk.Layer(
            "HexagonLayer",
            data=demo,
            get_position="[lon, lat]",
            radius=1200,
            elevation_scale=0,
            extruded=False,
            get_fill_color="[255 * (price_eur_m2 - qmin) / (qmax - qmin + 1e-9), 64, 200]",
            pickable=True,
        )
        tooltip = {"html": "<b>€/{m2}:</b> {price_eur_m2:.0f}<br/><b>Municipio:</b> {municipio}", "style": {"color": "white"}}
        initial_view_state = pdk.ViewState(latitude=view_cfg["lat"], longitude=view_cfg["lon"], zoom=view_cfg["zoom"])        
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=initial_view_state, tooltip=tooltip))
        st.info("Demo mostrada. Ejecuta: `python -m src.pipeline.build_all --demo` para generar un Parquet H3 con datos sintéticos y activar la capa H3.")


if __name__ == "__main__":
    main()
