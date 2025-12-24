import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Envíos – Atención al Cliente",
    layout="wide"
)

st.title("📦 Dashboard de Envíos – Atención al Cliente")

# --------------------------------------------------
# CARGA DE DATOS DESDE CSV
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Matriz_Excel_Dashboard.csv")

    # NORMALIZAR NOMBRES DE COLUMNAS
    df.columns = (
        df.columns
        .str.strip()     # quita espacios invisibles
        .str.upper()     # todo en mayúsculas
    )

    # Convertir columnas de fecha si existen
    columnas_fecha = [
        "FECHA DE SALIDA",
        "FECHA PROMESA",
        "FECHA DE ENTREGA"
    ]

    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = cargar_datos()

# --------------------------------------------------
# SIDEBAR – FILTROS
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")

cliente_sel = st.sidebar.multiselect(
    "Cliente",
    options=sorted(df["CLIENTE"].dropna().unique())
)

estatus_entrega_sel = st.sidebar.multiselect(
    "Estatus de Entrega",
    options=sorted(df["ESTATUS DE ENTREGA"].dropna().unique())
)

fecha_min = df["FECHA DE SALIDA"].min()
fecha_max = df["FECHA DE SALIDA"].max()

rango_fechas = st.sidebar.date_input(
    "Rango de Fecha de Salida",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# --------------------------------------------------
# APLICAR FILTROS
# --------------------------------------------------
df_filtrado = df.copy()

if cliente_sel:
    df_filtrado = df_filtrado[df_filtrado["CLIENTE"].isin(cliente_sel)]

if estatus_entrega_sel:
    df_filtrado = df_filtrado[
        df_filtrado["ESTATUS DE ENTREGA"].isin(estatus_entrega_sel)
    ]

if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado["FECHA DE SALIDA"] >= pd.to_datetime(rango_fechas[0])) &
        (df_filtrado["FECHA DE SALIDA"] <= pd.to_datetime(rango_fechas[1]))
    ]

# --------------------------------------------------
# KPIs
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_envios = len(df_filtrado)
entregados = len(df_filtrado[df_filtrado["ESTATUS DE ENTREGA"] == "ENTREGADO"])
en_transito = len(df_filtrado[df_filtrado["ESTATUS DE ENTREGA"] == "EN TRÁNSITO"])
retrasados = len(df_filtrado[df_filtrado["ESTATUS DE TIEMPO"] == "RETRASADO"])

col1.metric("📦 Total de Envíos", total_envios)
col2.metric("✅ Entregados", entregados)
col3.metric("🚚 En Tránsito", en_transito)
col4.metric("⏰ Retrasados", retrasados)

st.divider()

# --------------------------------------------------
# GRÁFICO – ESTATUS DE ENTREGA
# --------------------------------------------------
st.subheader("📊 Estatus de Entrega")

df_estatus = (
    df_filtrado["ESTATUS DE ENTREGA"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Estatus", "ESTATUS DE ENTREGA": "Cantidad"})
)

grafico_estatus = alt.Chart(df_estatus).mark_bar().encode(
    x=alt.X("Estatus:N", title="Estatus"),
    y=alt.Y("Cantidad:Q", title="Cantidad"),
    tooltip=["Estatus", "Cantidad"]
)

st.altair_chart(grafico_estatus, use_container_width=True)

st.divider()

# --------------------------------------------------
# TABLA DE DETALLE
# --------------------------------------------------
st.subheader("📋 Detalle de Pedidos")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=500
)

# --------------------------------------------------
# PIE DE PÁGINA
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Dashboard de Atención al Cliente</div>",
    unsafe_allow_html=True
)
