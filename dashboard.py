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
    df = pd.read_csv("Matriz_Excel_Dashboard.csv")

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
# DEBUG VISIBLE (CLAVE PARA QUE YA NO ADIVINEMOS)
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

COL_CLIENTE = encontrar_columna(["CLIENTE", "NOMBRE CLIENTE", "CLIENTES"])
COL_ESTATUS_ENTREGA = encontrar_columna(["ESTATUS DE ENTREGA", "ESTATUS ENTREGA"])
COL_ESTATUS_TIEMPO = encontrar_columna(["ESTATUS DE TIEMPO", "ESTATUS TIEMPO"])
COL_FECHA_SALIDA = encontrar_columna(["FECHA DE SALIDA", "FECHA SALIDA"])

# --------------------------------------------------
# SIDEBAR – FILTROS (SOLO SI EXISTEN)
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

if COL_CLIENTE:
    clientes = sorted(df[COL_CLIENTE].dropna().unique())
    cliente_sel = st.sidebar.multiselect("Cliente", clientes)
    if cliente_sel:
        df_filtrado = df_filtrado[df_filtrado[COL_CLIENTE].isin(cliente_sel)]
else:
    st.sidebar.info("Columna de cliente no detectada")

if COL_ESTATUS_ENTREGA:
    estatus = sorted(df[COL_ESTATUS_ENTREGA].dropna().unique())
    estatus_sel = st.sidebar.multiselect("Estatus de Entrega", estatus)
    if estatus_sel:
        df_filtrado = df_filtrado[df_filtrado[COL_ESTATUS_ENTREGA].isin(estatus_sel)]

if COL_FECHA_SALIDA:
    fecha_min = df[COL_FECHA_SALIDA].min()
    fecha_max = df[COL_FECHA_SALIDA].max()

    rango = st.sidebar.date_input(
        "Rango de Fecha de Salida",
        value=(fecha_min, fecha_max)
    )

    if len(rango) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado[COL_FECHA_SALIDA] >= pd.to_datetime(rango[0])) &
            (df_filtrado[COL_FECHA_SALIDA] <= pd.to_datetime(rango[1]))
        ]

# --------------------------------------------------
# KPIs (SEGUROS)
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total = len(df_filtrado)

entregados = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_ENTREGA] == "ENTREGADO"])
    if COL_ESTATUS_ENTREGA else 0
)

transito = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_ENTREGA] == "EN TRÁNSITO"])
    if COL_ESTATUS_ENTREGA else 0
)

retrasados = (
    len(df_filtrado[df_filtrado[COL_ESTATUS_TIEMPO] == "RETRASADO"])
    if COL_ESTATUS_TIEMPO else 0
)

c1.metric("📦 Total", total)
c2.metric("✅ Entregados", entregados)
c3.metric("🚚 En tránsito", transito)
c4.metric("⏰ Retrasados", retrasados)

st.divider()

# --------------------------------------------------
# GRÁFICO (SI EXISTE ESTATUS)
# --------------------------------------------------
if COL_ESTATUS_ENTREGA:
    st.subheader("📊 Estatus de Entrega")

    df_est = (
        df_filtrado[COL_ESTATUS_ENTREGA]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Estatus", COL_ESTATUS_ENTREGA: "Cantidad"})
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
