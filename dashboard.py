import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA – INICIA SIDEBAR COLAPSADA
# --------------------------------------------------
st.set_page_config(
    page_title="Control de Envíos – Enero 2026",
    layout="wide",
    initial_sidebar_state="collapsed"  # 🟢 inicia colapsada
)

# --------------------------------------------------
# TÍTULO Y SUBTÍTULO
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700;">
            Control de Embarques
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
    df["NO CLIENTE"] = df["NO CLIENTE"].astype(str).str.strip()
    df["FECHA DE ENVÍO"] = pd.to_datetime(df["FECHA DE ENVÍO"], errors="coerce", dayfirst=True)
    df["PROMESA DE ENTREGA"] = pd.to_datetime(df["PROMESA DE ENTREGA"], errors="coerce", dayfirst=True)
    df["FECHA DE ENTREGA REAL"] = pd.to_datetime(df["FECHA DE ENTREGA REAL"], errors="coerce", dayfirst=True)
    
    hoy = pd.Timestamp.today().normalize()
    
    def calcular_estatus(row):
        if pd.notna(row["FECHA DE ENTREGA REAL"]):
            return "ENTREGADO"
        if pd.notna(row["PROMESA DE ENTREGA"]) and row["PROMESA DE ENTREGA"] < hoy:
            return "RETRASADO"
        return "EN TRANSITO"
    
    df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)
    return df

df = cargar_datos()

# --------------------------------------------------
# SIDEBAR – FILTRO POR CLIENTE (auto-filtrado)
# --------------------------------------------------
st.sidebar.header("Filtro por Cliente")

# Inicializamos la variable de sesión si no existe
if "filtro_cliente_actual" not in st.session_state:
    st.session_state.filtro_cliente_actual = ""

# Función que actualiza la variable de sesión
def actualizar_filtro():
    st.session_state.filtro_cliente_actual = st.session_state.filtro_cliente_input

# Creamos un solo text_input
st.sidebar.text_input(
    "Ingresa el No Cliente",
    value=st.session_state.filtro_cliente_actual,
    key="filtro_cliente_input",
    on_change=actualizar_filtro
)

# Aplicamos el filtro a df_filtrado
if st.session_state.filtro_cliente_actual.strip() != "":
    df_filtrado = df[df["NO CLIENTE"].str.contains(st.session_state.filtro_cliente_actual.strip(), case=False, na=False)]
else:
    df_filtrado = df.copy()

# -----------------------------
# CAJA DE BÚSQUEDA POR PEDIDO – TARGETAS
# -----------------------------
pedido_buscar = st.text_input(
    "Buscar por Número de Pedido",
    value="",
    help="Ingresa un número de pedido para mostrar solo esos registros"
)

if pedido_buscar.strip() != "":
    # Filtrar solo por Número de Pedido
    df_busqueda = df_filtrado[
        df_filtrado["NÚMERO DE PEDIDO"].astype(str).str.contains(pedido_buscar.strip(), case=False, na=False)
    ].copy()

    hoy = pd.Timestamp.today().normalize()

    # Calcular días transcurridos y días de retraso
    df_busqueda["DIAS_TRANSCURRIDOS"] = (
        (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["FECHA DE ENVÍO"]).dt.days
    )

    df_busqueda["DIAS_RETRASO"] = (
        (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["PROMESA DE ENTREGA"]).dt.days
    )
    df_busqueda["DIAS_RETRASO"] = df_busqueda["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)

    # Formato de fechas DD/MM/YYYY
    for col in ["FECHA DE ENVÍO", "PROMESA DE ENTREGA", "FECHA DE ENTREGA REAL"]:
        df_busqueda[col] = df_busqueda[col].dt.strftime('%d/%m/%Y')

    # Mostrar las tarjetas usando df_busqueda
    for index, row in df_busqueda.iterrows():
        c1, c2, c3 = st.columns(3)

        # Tarjeta 1 – Información del Cliente
        c1.markdown(
            f"""
            <div style='background-color:#1A1E25; padding:15px; border-radius:10px;'>
                <div style='color:yellow; font-size:16px; font-weight:bold; margin-bottom:10px; text-align:center;'>Información del Cliente</div>
                <b>No Cliente:</b> {row['NO CLIENTE']}<br>
                <b>Nombre del Cliente:</b> {row['NOMBRE DEL CLIENTE']}<br>
                <b>Fletera:</b> {row['FLETERA']}<br>                
                <b>Número de Guía:</b> {row['NÚMERO DE GUÍA']}<br>
                <b>Costo de la Guía:</b> {row.get('COSTO DE LA GUÍA', '')}<br>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tarjeta 2 – Fechas y seguimiento
        dias_transcurridos = row["DIAS_TRANSCURRIDOS"]
        dias_retraso = row["DIAS_RETRASO"]
        color_retraso = "red" if dias_retraso > 0 else "white"

        c2.markdown(
            f"""
            <div style='background-color:#1A1E25; padding:15px; border-radius:10px;'>
                <div style='color:yellow; font-size:16px; font-weight:bold; margin-bottom:10px; text-align:center;'>Fechas y Seguimiento</div>
                <b>Fecha de Envío:</b> {row['FECHA DE ENVÍO']}<br>
                <b>Promesa de Entrega:</b> {row['PROMESA DE ENTREGA']}<br>
                <b>Fecha de Entrega Real:</b> {row['FECHA DE ENTREGA REAL']}<br>
                <b>Días Transcurridos:</b> {dias_transcurridos}<br>
                <b>Días de Retraso:</b> <span style='color:{color_retraso};'>{dias_retraso}</span><br>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tarjeta 3 – Estatus y observaciones
        c3.markdown(
            f"""
            <div style='background-color:#1A1E25; padding:15px; border-radius:10px;'>
                <div style='color:yellow; font-size:16px; font-weight:bold; margin-bottom:10px; text-align:center;'>Estatus y Observaciones</div>
                <b>Estatus:</b> {row['ESTATUS_CALCULADO']}<br>
                <b>Clase de Entrega:</b> {row['CLASES DE ENTREGA']}<br>                
                <b>Prioridad:</b> {row.get('PRIORIDAD', '')}<br>
                <b>Comentarios:</b> {row.get('COMENTARIOS', '')}<br>
                <b>Cantidad de Cajas:</b> {row['CANTIDAD DE CAJAS']}<br>                
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# KPIs
# --------------------------------------------------
total = len(df_filtrado)
entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
en_transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()

# st.write(f"Total de pedidos filtrados: {total}")
# st.write(f"Entregados: {entregados}, En tránsito: {en_transito}, Retrasados: {retrasados}")

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
    porcentaje = int((avance / total) * 100) if total > 0 else 0

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

    texto_numero = alt.Chart(
        pd.DataFrame({"texto": [f"{avance}"]})
    ).mark_text(
        align="center",
        baseline="middle",
        fontSize=26,
        fontWeight="bold",
        dy=-8,
        color="white"
    ).encode(
        text="texto:N"
    )

    texto_porcentaje = alt.Chart(
        pd.DataFrame({"texto": [f"{porcentaje}%"]})
    ).mark_text(
        align="center",
        baseline="middle",
        fontSize=14,
        dy=16,
        color="gray"
    ).encode(
        text="texto:N"
    )

    return (donut + texto_numero + texto_porcentaje).properties(
        width=140,
        height=140
    )

# --------------------------------------------------
# KPIs CON DONITAS
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">
            Indicadores Generales
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

total = len(df_filtrado)

entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
en_transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()

# KPI TOTAL
c1.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Total de pedidos</div>",
    unsafe_allow_html=True
)
c1.altair_chart(
    donut_con_numero(total, total, "#FFD700", COLOR_FALTANTE),
    use_container_width=True
)

# KPI ENTREGADOS
c2.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Entregados</div>",
    unsafe_allow_html=True
)
c2.altair_chart(
    donut_con_numero(entregados, total, COLOR_AVANCE_ENTREGADOS, COLOR_FALTANTE),
    use_container_width=True
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

# KPI RETRASADOS
c4.markdown(
    "<div style='text-align:center; color:yellow; margin-bottom:6px;'>Retrasados</div>",
    unsafe_allow_html=True
)
c4.altair_chart(
    donut_con_numero(retrasados, total, COLOR_AVANCE_RETRASADOS, COLOR_FALTANTE),
    use_container_width=True
)

# --------------------------------------------------
# TABLA FINAL – DISEÑO MEJORADO
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">
            Lista de envíos
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

hoy = pd.Timestamp.today().normalize()
df_mostrar = df_filtrado.copy()

# Días transcurridos y retraso
df_mostrar["DIAS_TRANSCURRIDOS"] = (
    (df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy) - df_mostrar["FECHA DE ENVÍO"]).dt.days
)
df_mostrar["DIAS_RETRASO"] = (
    (df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy) - df_mostrar["PROMESA DE ENTREGA"]).dt.days
)
df_mostrar["DIAS_RETRASO"] = df_mostrar["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)

# Formato de fecha
df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].dt.strftime('%d/%m/%Y')
df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].fillna('')

# Funciones de estilo
def colorear_retraso(val):
    color = '#ff4d4d' if val > 0 else 'white'  # rojo si hay retraso
    return f'background-color: {color}; color: black; font-weight: bold;' if val > 0 else ''

def zebra_filas(row):
    if row.name % 2 == 0:
        return ['background-color: #0E1117; color: white;' for _ in row]
    else:
        return ['background-color: #1A1E25; color: white;' for _ in row]

def estilo_encabezado(df):
    return [ 'background-color: orange; color: white; font-weight: bold; font-size:14px;' for _ in df.columns]

# Aplicamos estilos combinados
st.dataframe(
    df_mostrar.style.apply(zebra_filas, axis=1)
                    .applymap(colorear_retraso, subset=["DIAS_RETRASO"])
                    .set_table_styles([{'selector': 'th', 'props': [('background-color', 'orange'), ('color', 'white'), ('font-weight','bold')]}]),
    use_container_width=True,
    height=520
)

# --------------------------------------------------
# GRÁFICOS POR PAQUETERÍA – NUEVO BLOQUE
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">
            Pendientes por Paqueteria
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

g1, g2 = st.columns(2)

# En tránsito por paquetería
df_transito = (
    df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO"]
    .groupby("FLETERA")
    .size()
    .reset_index(name="PEDIDOS")
)

graf_transito = alt.Chart(df_transito).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X("FLETERA:N", title="Paquetería"),
    y=alt.Y("PEDIDOS:Q", title="Pedidos en tránsito"),
    tooltip=["FLETERA", "PEDIDOS"],
    color=alt.value("#FFC107")  # Amarillo
).properties(height=320)

g1.markdown("<h4 style='color:yellow; text-align:center;'>En tránsito</h4>", unsafe_allow_html=True)
g1.altair_chart(graf_transito, use_container_width=True)

# Retrasados por paquetería
df_retrasados = (
    df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO"]
    .groupby("FLETERA")
    .size()
    .reset_index(name="PEDIDOS")
)

graf_retrasados = alt.Chart(df_retrasados).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X("FLETERA:N", title="Paquetería"),
    y=alt.Y("PEDIDOS:Q", title="Pedidos retrasados"),
    tooltip=["FLETERA", "PEDIDOS"],
    color=alt.value("#F44336")  # Rojo
).properties(height=320)

g2.markdown("<h4 style='color:#F44336; text-align:center;'>Retrasados</h4>", unsafe_allow_html=True)
g2.altair_chart(graf_retrasados, use_container_width=True)

st.divider()  # línea separadora antes de la tabla

# --------------------------------------------------
# PEDIDOS ENTREGADOS CON RETRASO POR PAQUETERÍA (FECHA REAL)
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">
            Retrasos por Paqueteria
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Filtrar solo los pedidos que ya tienen fecha de entrega real
df_entregados = df_filtrado[pd.notna(df_filtrado["FECHA DE ENTREGA REAL"])]

# Filtrar los que llegaron con retraso (fecha real > fecha promesa)
df_entregados_retraso = df_entregados[
    (pd.notna(df_entregados["PROMESA DE ENTREGA"])) &
    (df_entregados["FECHA DE ENTREGA REAL"] > df_entregados["PROMESA DE ENTREGA"])
]

# Agrupar por paquetería
df_retraso_paquete = (
    df_entregados_retraso.groupby("FLETERA")
    .size()
    .reset_index(name="PEDIDOS_RETRASADOS")
)

if not df_retraso_paquete.empty:
    graf_retraso_paquete = alt.Chart(df_retraso_paquete).mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6
    ).encode(
        x=alt.X("FLETERA:N", title="Paquetería"),
        y=alt.Y("PEDIDOS_RETRASADOS:Q", title="Pedidos entregados con retraso"),
        tooltip=["FLETERA", "PEDIDOS_RETRASADOS"],
        color=alt.value("#F44336")  # Rojo
    ).properties(height=320)

    st.altair_chart(graf_retraso_paquete, use_container_width=True)
else:
    st.info("No hay entregas con retraso para mostrar con los filtros actuales.")

st.divider()  # línea separadora antes de la tabla

# --------------------------------------------------
# GRÁFICO DE ESTATUS – TITULO NARANJA
# --------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">
            Estatus de Envios
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Crear DataFrame base con las 3 categorías
estatus_base = pd.DataFrame({
    "Estatus": ["ENTREGADO", "EN TRANSITO", "RETRASADO"]
})

# Contar los estatus en los datos filtrados
df_est = df_filtrado["ESTATUS_CALCULADO"].value_counts().rename_axis("Estatus").reset_index(name="Cantidad")

# Combinar con base para asegurar que todas las categorías estén
df_est = estatus_base.merge(df_est, on="Estatus", how="left").fillna(0)

# Asignar colores igual que las donitas
df_est["Color"] = df_est["Estatus"].map({
    "ENTREGADO": COLOR_AVANCE_ENTREGADOS,
    "EN TRANSITO": COLOR_AVANCE_TRANSITO,
    "RETRASADO": COLOR_AVANCE_RETRASADOS
})

# Crear gráfico
chart = alt.Chart(df_est).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
    x=alt.X("Estatus:N", title="Estatus"),
    y=alt.Y("Cantidad:Q", title="Cantidad"),
    color=alt.Color("Color:N", scale=None, legend=None),
    tooltip=["Estatus:N", "Cantidad:Q"]
)

st.altair_chart(chart, use_container_width=True)
st.divider()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística – Control de Envios</div>",
    unsafe_allow_html=True
)




























































































