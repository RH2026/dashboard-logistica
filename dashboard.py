import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Control de Envíos – Enero 2026",
    layout="wide"
)
# TÍTULO Y SUBTÍTULO
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:32px; font-weight:700;">
            Panel de Seguimiento y Control de Embarques
        </div>
        <div style="color:#CCCCCC; font-size:22px; margin-top:8px;">
            Logística – Enero 2026
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# LÍNEA SUTIL SEGURA
st.divider()
# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Matriz_Excel_Dashboard.csv", encoding="utf-8")
    df.columns = df.columns.str.strip().str.upper()

    hoy = pd.Timestamp.today().normalize()

    # LIMPIEZA DE FECHAS
    for col in ["FECHA DE ENVÍO", "PROMESA DE ENTREGA", "FECHA DE ENTREGA REAL"]:
        if col in df.columns:
            df[col] = df[col].replace(["", "None", "NULL", "N/A", "n/a"], pd.NaT)
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # ESTATUS
    def calcular_estatus(row):
        hoy = pd.Timestamp.today().normalize()
        fecha_real = row["FECHA DE ENTREGA REAL"]
        promesa = row["PROMESA DE ENTREGA"]

        if pd.notna(fecha_real):
            return "ENTREGADO"
        if pd.notna(promesa) and promesa < hoy:
            return "RETRASADO"
        return "EN TRANSITO"

    df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)

    # DÍAS TRANSCURRIDOS
    df["DIAS TRANSCURRIDOS"] = (df["FECHA DE ENTREGA REAL"].fillna(hoy) - df["FECHA DE ENVÍO"]).dt.days

    # DÍAS DE RETRASO
    def calcular_dias_retraso(row):
        hoy = pd.Timestamp.today().normalize()
        fecha_real = row["FECHA DE ENTREGA REAL"]
        promesa = row["PROMESA DE ENTREGA"]

        if pd.notna(fecha_real) and pd.notna(promesa):
            return max((fecha_real - promesa).days, 0)
        if pd.isna(fecha_real) and pd.notna(promesa) and promesa < hoy:
            return (hoy - promesa).days
        return 0

    df["DIAS DE RETRASO"] = df.apply(calcular_dias_retraso, axis=1)

    return df

df = cargar_datos()

# --------------------------------------------------
# SIDEBAR – FILTROS
# --------------------------------------------------
st.sidebar.header("Filtros")
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
    fecha_min, fecha_max = (fechas_validas.min(), fechas_validas.max()) if not fechas_validas.empty else (pd.Timestamp.today(), pd.Timestamp.today())
    rango = st.sidebar.date_input(
        "Rango de Fecha de Envío",
        value=(fecha_min.date(), fecha_max.date())
    )
    if isinstance(rango, tuple) and len(rango) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado["FECHA DE ENVÍO"] >= pd.to_datetime(rango[0])) &
            (df_filtrado["FECHA DE ENVÍO"] <= pd.to_datetime(rango[1]))
        ]

# ==================================================
# 🎨 CAMBIA COLORES AQUÍ (AVANCE vs FALTANTE)
# ==================================================
COLOR_AVANCE_ENTREGADOS = "#4CAF50"   # Verde
COLOR_AVANCE_TRANSITO   = "#FFC107"   # Amarillo
COLOR_AVANCE_RETRASADOS = "#F44336"   # Rojo
COLOR_FALTANTE          = "#3A3A3A"   # Gris (lo que falta)
# ==================================================


# --------------------------------------------------
# FUNCIÓN DONITA CON NÚMERO DENTRO
# --------------------------------------------------
def donut_con_numero(avance, total, color_avance, color_faltante):
    data = pd.DataFrame({
        "segmento": ["avance", "faltante"],
        "valor": [avance, max(total - avance, 0)]
    })

    donut = alt.Chart(data).mark_arc(
        innerRadius=50
    ).encode(
        theta=alt.Theta("valor:Q"),
        color=alt.Color(
            "segmento:N",
            scale=alt.Scale(range=[color_avance, color_faltante]),
            legend=None
        )
    )

    texto = alt.Chart(
        pd.DataFrame({"texto": [f"{avance}"]})
    ).mark_text(
        align="center",
        baseline="middle",
        fontSize=26,
        fontWeight="bold",
        color="white"
    ).encode(
        text="texto:N"
    )

    return (donut + texto).properties(
        width=140,
        height=140
    )

# --------------------------------------------------
# DATAFRAME REAL
# --------------------------------------------------
df = cargar_datos()
df_filtrado = df.copy()

# --------------------------------------------------
# KPIs CON DONITAS
# --------------------------------------------------
st.markdown("<h2 style='color:white;'>Indicadores Clave</h2>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

total = len(df_filtrado)

entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
en_transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()

porc_entregados = (entregados / total * 100) if total > 0 else 0
porc_transito = (en_transito / total * 100) if total > 0 else 0
porc_retrasados = (retrasados / total * 100) if total > 0 else 0


# KPI TOTAL (CON DONA AL 100%)
c1.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Total de pedidos</div>",
    unsafe_allow_html=True
)

c1.altair_chart(
    donut_con_numero(total, total, "#FFD700", COLOR_FALTANTE),
    use_container_width=True
)

c2.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Entregados</div>",
    unsafe_allow_html=True
)

c2.altair_chart(
    donut_con_numero(entregados, total, COLOR_AVANCE_ENTREGADOS, COLOR_FALTANTE),
    use_container_width=True
)

c2.markdown(
    f"<div style='text-align:center; color:gray; margin-top:-18px;'>{porc_entregados:.1f}%</div>",
    unsafe_allow_html=True
)


# KPI EN TRÁNSITO
c3.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>En tránsito</div>",
    unsafe_allow_html=True
)

c3.altair_chart(
    donut_con_numero(en_transito, total, COLOR_AVANCE_TRANSITO, COLOR_FALTANTE),
    use_container_width=True
)

c3.markdown(
    f"<div style='text-align:center; color:gray; margin-top:-18px;'>{porc_transito:.1f}%</div>",
    unsafe_allow_html=True
)


# KPI RETRASADOS
c4.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Retrasados</div>",
    unsafe_allow_html=True
)

c4.altair_chart(
    donut_con_numero(retrasados, total, COLOR_AVANCE_RETRASADOS, COLOR_FALTANTE),
    use_container_width=True
)

c4.markdown(
    f"<div style='text-align:center; color:gray; margin-top:-18px;'>{porc_retrasados:.1f}%</div>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# TABLA FINAL – TITULO NARANJA
# --------------------------------------------------
st.markdown("<h2 style='color:white;'>Detalle de Envíos</h2>", unsafe_allow_html=True)
df_mostrar = df_filtrado.copy()
df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].dt.strftime('%d/%m/%Y')
df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].fillna('')

st.dataframe(df_mostrar, use_container_width=True, height=520)

# --------------------------------------------------
# GRÁFICO DE ESTATUS – TITULO NARANJA
# --------------------------------------------------
st.markdown("<h2 style='color:white;'>Estatus de Envíos</h2>", unsafe_allow_html=True)
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
# FOOTER
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Control de Envios</div>",
    unsafe_allow_html=True
)



































