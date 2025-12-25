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
# CARGA DE DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "Matriz_Excel_Dashboard.csv",
        encoding="utf-8"
    )

    # Normalizar columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    # Convertir fechas si existen
    for col in ["FECHA DE SALIDA", "FECHA PROMESA", "FECHA DE ENTREGA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = cargar_datos()

# --------------------------------------------------
# DEBUG VISIBLE
# --------------------------------------------------
with st.expander("🧪 Columnas detectadas en el CSV"):
    st.write(list(df.columns))

# --------------------------------------------------
# DETECCIÓN FLEXIBLE DE COLUMNAS
# --------------------------------------------------
def encontrar_columna(posibles):
    for c in posibles:
        if c in df.columns:
            return c
    return None

COL_NO_CLIENTE = encontrar_columna(["NO CLIENTE"])
COL_ESTATUS_ENTREGA = encontrar_columna(["ESTATUS DE ENTREGA", "ESTATUS ENTREGA"])
COL_ESTATUS_TIEMPO = encontrar_columna(["ESTATUS DE TIEMPO", "ESTATUS TIEMPO"])
COL_FECHA_SALIDA = encontrar_columna(["FECHA DE SALIDA", "FECHA SALIDA"])

# --------------------------------------------------
# SIDEBAR – FILTROS
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

# ---- Filtro NO CLIENTE (caja de búsqueda)
if COL_NO_CLIENTE:
    no_cliente_input = st.sidebar.text_input("Buscar No Cliente")
    if no_cliente_input:
        df_filtrado = df_filtrado[
            df_filtrado[COL_NO_CLIENTE]
            .astype(str)
            .str.contains(no_cliente_input, case=False, na=False)
        ]
else:
    st.sidebar.info("Columna 'NO CLIENTE' no detectada")

# ---- Filtro Estatus de Entrega
if COL_ESTATUS_ENTREGA:
    estatus = sorted(df[COL_ESTATUS_ENTREGA].dropna().unique())
    estatus_sel = st.sidebar.multiselect("Estatus de Entrega", estatus)
    if estatus_sel:
        df_filtrado = df_filtrado[
            df_filtrado[COL_ESTATUS_ENTREGA].isin(estatus_sel)
        ]

# ---- Filtro Fecha de Salida
if COL_FECHA_SALIDA:
    fecha_min = df[COL_FECHA_SALIDA].min()
    fecha_max = df[COL_FECHA_SALIDA].max()

    rango = st.sidebar.date_input(
        "Rango de Fecha de Salida",
        value=(fecha_min, fecha_max)
    )

    if isinstance(rango, tuple) and len(rango) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado[COL_FECHA_SALIDA] >= pd.to_datetime(rango[0])) &
            (df_filtrado[COL_FECHA_SALIDA] <= pd.to_datetime(rango[1]))
        ]

# --------------------------------------------------
# KPIs
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total = len(df_filtrado)

entregados = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_ENTREGA] == "ENTREGADO"])
    if COL_ESTATUS_ENTREGA and COL_ESTATUS_ENTREGA in df_filtrado.columns else 0
)

transito = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_ENTREGA] == "EN TRÁNSITO"])
    if COL_ESTATUS_ENTREGA and COL_ESTATUS_ENTREGA in df_filtrado.columns else 0
)

retrasados = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_TIEMPO] == "RETRASADO"])
    if COL_ESTATUS_TIEMPO and COL_ESTATUS_TIEMPO in df_filtrado.columns else 0
)

c1.metric("📦 Total", total)
c2.metric("✅ Entregados", entregados)
c3.metric("🚚 En tránsito", transito)
c4.metric("⏰ Retrasados", retrasados)

st.divider()

# --------------------------------------------------
# GRÁFICO
# --------------------------------------------------
if COL_ESTATUS_ENTREGA and not df_filtrado.empty:
    st.subheader("📊 Estatus de Entrega")

    df_est = (
        df_filtrado[COL_ESTATUS_ENTREGA]
        .value_counts()
        .reset_index()
        .rename(columns={
            "index": "Estatus",
            COL_ESTATUS_ENTREGA: "Cantidad"
        })
    )

    chart = alt.Chart(df_est).mark_bar().encode(
        x="Estatus:N",
        y="Cantidad:Q",
        tooltip=["Estatus", "Cantidad"]
    )

    st.altair_chart(chart, use_container_width=True)

st.divider()

# --------------------------------------------------
# TABLA FINAL
# --------------------------------------------------
st.subheader("📋 Detalle de Registros")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=500
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Dashboard de Atención al Cliente</div>",
    unsafe_allow_html=True
)
