import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
# Configuración de página
# ---------------------------
st.set_page_config(
    page_title="Dashboard de Envíos – Atención al Cliente",
    layout="wide"
)

st.title("📦 Dashboard de Envíos – Enero 2026")

# ---------------------------
# Cargar Excel (Cloud)
# ---------------------------
EXCEL_PATH = "Matriz_Excel_Dashboard.xlsx"
df = pd.read_excel(EXCEL_PATH)

# ---------------------------
# Conversión de fechas
# ---------------------------
df["Fecha de Envío"] = pd.to_datetime(df["Fecha de Envío"])
df["Promesa de Entrega"] = pd.to_datetime(df["Promesa de Entrega"])
df["Fecha de Entrega Real"] = pd.to_datetime(
    df["Fecha de Entrega Real"], errors="coerce"
)

# ---------------------------
# Calcular Estatus automático
# ---------------------------
def calcular_estatus(row):
    if pd.notnull(row["Fecha de Entrega Real"]):
        if row["Fecha de Entrega Real"] <= row["Promesa de Entrega"]:
            return "Entregado"
        else:
            return "Retrasado"
    return "En Tránsito"

df["Estatus_auto"] = df.apply(calcular_estatus, axis=1)

# ---------------------------
# Cálculos de días
# ---------------------------
df["Días Transcurridos"] = (
    pd.Timestamp.today().normalize() - df["Fecha de Envío"]
).dt.days

df["Días de Retraso"] = (
    df["Fecha de Entrega Real"] - df["Promesa de Entrega"]
).dt.days

df["Días de Retraso"] = df["Días de Retraso"].apply(
    lambda x: x if pd.notnull(x) and x > 0 else 0
)

# ---------------------------
# Formato visual
# ---------------------------
df["Fecha de Envío_str"] = df["Fecha de Envío"].dt.strftime("%Y-%m-%d")
df["Promesa de Entrega_str"] = df["Promesa de Entrega"].dt.strftime("%Y-%m-%d")
df["Fecha de Entrega Real_str"] = (
    df["Fecha de Entrega Real"].dt.strftime("%Y-%m-%d").fillna("")
)

df["Costo de la Guía_num"] = df["Costo de la Guía"]
df["Costo de la Guía"] = df["Costo de la Guía"].apply(
    lambda x: f"${x:,.2f}"
)

# ---------------------------
# SIDEBAR – FILTROS
# ---------------------------
st.sidebar.markdown(
    "<h2 style='color:#FF9800;'>Filtros</h2>",
    unsafe_allow_html=True
)

# Inicializar session_state
if "no_cliente_input" not in st.session_state:
    st.session_state.no_cliente_input = ""

if "fecha_inicio" not in st.session_state:
    st.session_state.fecha_inicio = df["Fecha de Envío"].min().date()

if "fecha_fin" not in st.session_state:
    st.session_state.fecha_fin = df["Fecha de Envío"].max().date()

if "estatus_seleccionados" not in st.session_state:
    st.session_state.estatus_seleccionados = list(df["Estatus_auto"].unique())

if "fleteras_seleccionadas" not in st.session_state:
    st.session_state.fleteras_seleccionadas = list(df["Fletera"].unique())

# Widgets
no_cliente_input = st.sidebar.text_input(
    "Buscar No Cliente",
    key="no_cliente_input"
)

fecha_inicio = st.sidebar.date_input(
    "Desde",
    key="fecha_inicio"
)

fecha_fin = st.sidebar.date_input(
    "Hasta",
    key="fecha_fin"
)

estatus_seleccionados = st.sidebar.multiselect(
    "Estatus",
    df["Estatus_auto"].unique(),
    key="estatus_seleccionados"
)

fleteras_seleccionadas = st.sidebar.multiselect(
    "Fletera",
    df["Fletera"].unique(),
    key="fleteras_seleccionadas"
)

# ---------------------------
# BOTÓN RESTABLECER (CORRECTO)
# ---------------------------
if st.sidebar.button("Restablecer filtros"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ---------------------------
# FILTRADO DE DATOS
# ---------------------------
df_filtrado = df.copy()

if no_cliente_input:
    df_filtrado = df_filtrado[
        df_filtrado["No Cliente"]
        .astype(str)
        .str.contains(no_cliente_input, case=False)
    ]

df_filtrado = df_filtrado[
    (df_filtrado["Fecha de Envío"] >= pd.to_datetime(fecha_inicio)) &
    (df_filtrado["Fecha de Envío"] <= pd.to_datetime(fecha_fin))
]

if estatus_seleccionados:
    df_filtrado = df_filtrado[
        df_filtrado["Estatus_auto"].isin(estatus_seleccionados)
    ]

if fleteras_seleccionadas:
    df_filtrado = df_filtrado[
        df_filtrado["Fletera"].isin(fleteras_seleccionadas)
    ]

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Envíos", len(df_filtrado))
col2.metric(
    "Entregados",
    len(df_filtrado[df_filtrado["Estatus_auto"] == "Entregado"])
)
col3.metric(
    "En Tránsito",
    len(df_filtrado[df_filtrado["Estatus_auto"] == "En Tránsito"])
)
col4.metric(
    "Retrasados",
    len(df_filtrado[df_filtrado["Estatus_auto"] == "Retrasado"])
)

st.divider()

# ---------------------------
# GRÁFICO POR ESTATUS
# ---------------------------
grafico_estatus = (
    alt.Chart(df_filtrado)
    .mark_bar()
    .encode(
        x=alt.X("Estatus_auto:N", title="Estatus"),
        y=alt.Y("count()", title="Total"),
        color="Estatus_auto:N"
    )
)

st.altair_chart(grafico_estatus, use_container_width=True)

st.divider()

# ---------------------------
# TABLA FINAL
# ---------------------------
st.subheader("📋 Detalle de Envíos")

columnas_tabla = [
    "No Cliente",
    "Número de Pedido",
    "Nombre del Cliente",
    "Fletera",
    "Destino",
    "Estatus_auto",
    "Fecha de Envío_str",
    "Promesa de Entrega_str",
    "Fecha de Entrega Real_str",
    "Días Transcurridos",
    "Días de Retraso",
    "Costo de la Guía"
]

st.dataframe(
    df_filtrado[columnas_tabla],
    use_container_width=True,
    hide_index=True
)

# ---------------------------
# PIE DE PÁGINA
# ---------------------------
st.markdown(
    "<div style='text-align:center;color:gray;margin-top:20px;'>"
    "© 2025 Logística – Dashboard de Atención al Cliente"
    "</div>",
    unsafe_allow_html=True
)
