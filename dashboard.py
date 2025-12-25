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

    # Normalizar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    # Convertir fechas
    for col in [
        "FECHA DE ENVÍO",
        "PROMESA DE ENTREGA",
        "FECHA DE ENTREGA REAL"
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

# --------------------------------------------------
# CALCULO DE DIAS TRANSCURRIDOS
# --------------------------------------------------
df["DIAS TRANSCURRIDOS"] = None

# Entregados
df.loc[
    df["FECHA DE ENTREGA REAL"].notna() & df["FECHA DE ENVÍO"].notna(),
    "DIAS TRANSCURRIDOS"
] = (
    df["FECHA DE ENTREGA REAL"] - df["FECHA DE ENVÍO"]
).dt.days

# En tránsito
df.loc[
    df["FECHA DE ENTREGA REAL"].isna() & df["FECHA DE ENVÍO"].notna(),
    "DIAS TRANSCURRIDOS"
] = (
    hoy - df["FECHA DE ENVÍO"]
).dt.days


# --------------------------------------------------
# CALCULO DE DIAS DE RETRASO
# --------------------------------------------------
df["DIAS DE RETRASO"] = 0

# Entregado con retraso
df.loc[
    df["FECHA DE ENTREGA REAL"].notna() &
    df["PROMESA DE ENTREGA"].notna() &
    (df["FECHA DE ENTREGA REAL"] > df["PROMESA DE ENTREGA"]),
    "DIAS DE RETRASO"
] = (
    df["FECHA DE ENTREGA REAL"] - df["PROMESA DE ENTREGA"]
).dt.days

# No entregado y vencido
df.loc[
    df["FECHA DE ENTREGA REAL"].isna() &
    df["PROMESA DE ENTREGA"].notna() &
    (hoy > df["PROMESA DE ENTREGA"]),
    "DIAS DE RETRASO"
] = (
    hoy - df["PROMESA DE ENTREGA"]
).dt.days

    # --------------------------------------------------
    # CALCULO AUTOMATICO DE ESTATUS
    # --------------------------------------------------
    hoy = pd.Timestamp.today().normalize()

    df["ESTATUS_CALCULADO"] = "EN TRANSITO"

    # ENTREGADO
    df.loc[
        df["FECHA DE ENTREGA REAL"].notna(),
        "ESTATUS_CALCULADO"
    ] = "ENTREGADO"

    # RETRASADO
    df.loc[
        (df["FECHA DE ENTREGA REAL"].isna()) &
        (df["PROMESA DE ENTREGA"].notna()) &
        (df["PROMESA DE ENTREGA"] < hoy),
        "ESTATUS_CALCULADO"
    ] = "RETRASADO"

    return df


df = cargar_datos()

# --------------------------------------------------
# SIDEBAR – FILTROS
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

# ---- Filtro No Cliente
if "NO CLIENTE" in df.columns:
    no_cliente = st.sidebar.text_input("Buscar No Cliente")
    if no_cliente:
        df_filtrado = df_filtrado[
            df_filtrado["NO CLIENTE"]
            .astype(str)
            .str.contains(no_cliente, case=False, na=False)
        ]

# ---- Filtro Estatus
estatus_sel = st.sidebar.multiselect(
    "Estatus de Envío",
    options=sorted(df["ESTATUS_CALCULADO"].unique())
)

if estatus_sel:
    df_filtrado = df_filtrado[
        df_filtrado["ESTATUS_CALCULADO"].isin(estatus_sel)
    ]

# ---- Filtro Fecha de Envío
if "FECHA DE ENVÍO" in df.columns:
    fecha_min = df["FECHA DE ENVÍO"].min()
    fecha_max = df["FECHA DE ENVÍO"].max()

    rango = st.sidebar.date_input(
        "Rango de Fecha de Envío",
        value=(fecha_min, fecha_max)
    )

    if isinstance(rango, tuple):
        df_filtrado = df_filtrado[
            (df_filtrado["FECHA DE ENVÍO"] >= pd.to_datetime(rango[0])) &
            (df_filtrado["FECHA DE ENVÍO"] <= pd.to_datetime(rango[1]))
        ]

# --------------------------------------------------
# KPIs
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total = len(df_filtrado)
entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()

c1.metric("📦 Total", total)
c2.metric("✅ Entregados", entregados)
c3.metric("🚚 En tránsito", transito)
c4.metric("⏰ Retrasados", retrasados)

st.divider()

# --------------------------------------------------
# GRÁFICO DE ESTATUS
# --------------------------------------------------
st.subheader("📊 Estatus de Envíos")

df_est = (
    df_filtrado["ESTATUS_CALCULADO"]
    .value_counts()
    .rename_axis("Estatus")
    .reset_index(name="Cantidad")
)

if not df_est.empty:
    chart = alt.Chart(df_est).mark_bar().encode(
        x=alt.X("Estatus:N", title="Estatus"),
        y=alt.Y("Cantidad:Q", title="Cantidad"),
        tooltip=["Estatus:N", "Cantidad:Q"]
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar con los filtros actuales.")

# --------------------------------------------------
# TABLA FINAL
# --------------------------------------------------
st.subheader("📋 Detalle de Envíos")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=520
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Dashboard de Atención al Cliente</div>",
    unsafe_allow_html=True
)
