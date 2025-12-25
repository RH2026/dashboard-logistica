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
            df[col] = df[col].replace(["", "None", "N/A", "n/a", "NULL", "null", "nan"], pd.NaT)

    # --------------------------------------------------
    # CALCULO DE ESTATUS DEFINITIVO
    # --------------------------------------------------
    def calcular_estatus(row):
        hoy = pd.Timestamp.today().normalize()
        fecha_real_str = str(row["FECHA DE ENTREGA REAL"]).strip().lower()
        promesa = pd.to_datetime(row["PROMESA DE ENTREGA"], errors="coerce", dayfirst=True)
        
        # Si fecha real es válida → ENTREGADO
        fecha_real = pd.to_datetime(row["FECHA DE ENTREGA REAL"], errors="coerce", dayfirst=True)
        if pd.notna(fecha_real):
            return "ENTREGADO"
        
        # Si dice transito
        if fecha_real_str in ["transito", "tránsito"]:
            if pd.notna(promesa) and promesa < hoy:
                return "RETRASADO"
            return "EN TRANSITO"
        
        # Si no hay fecha real
        if pd.notna(promesa):
            if promesa < hoy:
                return "RETRASADO"
            else:
                return "EN TIEMPO"
        
        # Caso por defecto
        return "EN TRANSITO"

    df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)

    # --------------------------------------------------
    # CONVERTIR FECHAS A DATETIME PARA CÁLCULOS
    # --------------------------------------------------
    for col in ["FECHA DE ENVÍO", "PROMESA DE ENTREGA", "FECHA DE ENTREGA REAL"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # --------------------------------------------------
    # DÍAS TRANSCURRIDOS
    # --------------------------------------------------
    df["DIAS TRANSCURRIDOS"] = (df["FECHA DE ENTREGA REAL"].fillna(hoy) - df["FECHA DE ENVÍO"]).dt.days

    # --------------------------------------------------
    # DÍAS DE RETRASO
    # --------------------------------------------------
    def calcular_dias_retraso(row):
        hoy = pd.Timestamp.today().normalize()
        promesa = row["PROMESA DE ENTREGA"]
        fecha_real = row["FECHA DE ENTREGA REAL"]

        if pd.notna(fecha_real) and pd.notna(promesa):
            return max((fecha_real - promesa).days, 0)
        elif (pd.isna(fecha_real) or str(fecha_real).strip().lower() in ["transito", "tránsito"]) and pd.notna(promesa):
            return max((hoy - promesa).days, 0) if hoy > promesa else 0
        else:
            return 0

    df["DIAS DE RETRASO"] = df.apply(calcular_dias_retraso, axis=1)

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
    fechas_validas = df["FECHA DE ENVÍO"].dropna()
    if not fechas_validas.empty:
        fecha_min, fecha_max = fechas_validas.min(), fechas_validas.max()
    else:
        fecha_min = fecha_max = pd.Timestamp.today()
    rango = st.sidebar.date_input(
        "Rango de Fecha de Envío",
        value=(fecha_min.date(), fecha_max.date())
    )
    if isinstance(rango, tuple) and len(rango) == 2:
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
c5 = st.columns(1)
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
