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
    df = pd.read_csv("Matriz_Excel_Dashboard.csv", encoding="utf-8")
    df.columns = df.columns.str.strip().str.upper()

    hoy = pd.Timestamp.today().normalize()

    # --------------------------------------------------
    # LIMPIEZA BÁSICA DE FECHAS
    # --------------------------------------------------
    for col in ["FECHA DE ENVÍO", "PROMESA DE ENTREGA", "FECHA DE ENTREGA REAL"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # --------------------------------------------------
    # CALCULO DE ESTATUS DEFINITIVO
    # --------------------------------------------------
    def calcular_estatus(row):
        # Si la fecha de entrega real dice "Transito" (o variantes), marcar en tránsito
        if str(row["FECHA DE ENTREGA REAL"]).strip().lower() in ["transito", "tránsito"]:
            return "EN TRANSITO"
        # Si hay fecha real válida, marcar entregado
        elif pd.notna(row["FECHA DE ENTREGA REAL"]) and row["FECHA DE ENTREGA REAL"] not in ["", "None", "N/A", "NULL", "null"]:
            # Intentar convertir a fecha
            try:
                fecha_real = pd.to_datetime(row["FECHA DE ENTREGA REAL"], dayfirst=True, errors='coerce')
                if pd.notna(fecha_real):
                    return "ENTREGADO"
            except:
                pass
        # Si hay promesa pero ya pasó la fecha, retrasado; sino en tránsito
        elif pd.notna(row["PROMESA DE ENTREGA"]):
            try:
                promesa = pd.to_datetime(row["PROMESA DE ENTREGA"], dayfirst=True, errors='coerce')
                return "RETRASADO" if promesa < hoy else "EN TRANSITO"
            except:
                return "EN TRANSITO"
        else:
            return "EN TRANSITO"

    df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)

    # --------------------------------------------------
    # DÍAS TRANSCURRIDOS
    # --------------------------------------------------
    df["DIAS TRANSCURRIDOS"] = df.apply(
        lambda row: (pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors='coerce') - pd.to_datetime(row["FECHA DE ENVÍO"], errors='coerce')).days
        if str(row["FECHA DE ENTREGA REAL"]).lower() not in ["transito", "tránsito"] and pd.notna(pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors='coerce')) else
        (hoy - pd.to_datetime(row["FECHA DE ENVÍO"], errors='coerce')).days
        if pd.notna(pd.to_datetime(row["FECHA DE ENVÍO"], errors='coerce')) else None,
        axis=1
    )

    # --------------------------------------------------
    # DÍAS DE RETRASO
    # --------------------------------------------------
    df["DIAS DE RETRASO"] = df.apply(
        lambda row: max(
            (pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors='coerce') - pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce')).days,
            0
        ) if pd.notna(pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors='coerce')) and pd.notna(pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce')) and pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors='coerce') > pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce') else
        max((hoy - pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce')).days, 0)
        if str(row["FECHA DE ENTREGA REAL"]).strip().lower() in ["transito", "tránsito"] and pd.notna(pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce')) and hoy > pd.to_datetime(row["PROMESA DE ENTREGA"], errors='coerce') else 0,
        axis=1
    )

    return df

df = cargar_datos()

# --------------------------------------------------
# SIDEBAR – FILTROS
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")
df_filtrado = df.copy()

# Filtro No Cliente
if "NO CLIENTE" in df.columns:
    no_cliente = st.sidebar.text_input("Buscar No Cliente")
    if no_cliente:
        df_filtrado = df_filtrado[df_filtrado["NO CLIENTE"].astype(str).str.contains(no_cliente, case=False, na=False)]

# Filtro Estatus
estatus_sel = st.sidebar.multiselect(
    "Estatus de Envío",
    options=sorted(df["ESTATUS_CALCULADO"].unique())
)
if estatus_sel:
    df_filtrado = df_filtrado[df_filtrado["ESTATUS_CALCULADO"].isin(estatus_sel)]

# Filtro Fecha de Envío
if "FECHA DE ENVÍO" in df.columns:
    fecha_min, fecha_max = df["FECHA DE ENVÍO"].min(), df["FECHA DE ENVÍO"].max()
    rango = st.sidebar.date_input("Rango de Fecha de Envío", value=(fecha_min, fecha_max))
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
c1.metric("📦 Total", total)
c2.metric("✅ Entregados", (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum())
c3.metric("🚚 En tránsito", (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum())
c4.metric("⏰ Retrasados", (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum())

st.divider()

# --------------------------------------------------
# GRÁFICO DE ESTATUS
# --------------------------------------------------
st.subheader("📊 Estatus de Envíos")
df_est = df_filtrado["ESTATUS_CALCULADO"].value_counts().rename_axis("Estatus").reset_index(name="Cantidad")
if not df_est.empty:
    chart = alt.Chart(df_est).mark_bar().encode(
        x=alt.X("Estatus:N", title="Estatus"),
        y=alt.Y("Cantidad:Q", title="Cantidad"),
        tooltip=["Estatus:N", "Cantidad:Q"]
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar con los filtros actuales.")

st.divider()

# --------------------------------------------------
# TABLA FINAL
# --------------------------------------------------
st.subheader("📋 Detalle de Envíos")
st.dataframe(df_filtrado, use_container_width=True, height=520)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Dashboard de Atención al Cliente</div>",
    unsafe_allow_html=True
)
