import streamlit as st
import pandas as pd
import altair as alt
import time
import base64   # 👈 aquí


def get_base64_image(image_path):  # 👈 aquí
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Control de Envíos – Enero 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# FONDO DE PANTALLA SOLO PARA LOGIN (COMPATIBLE CLOUD)
# --------------------------------------------------
if not st.session_state.get("logueado", False):

    img_base64 = get_base64_image("1.jpg")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
# --------------------------------------------------
# CONFIGURACIÓN AUTO LOGOUT
# --------------------------------------------------
TIEMPO_MAX_INACTIVIDAD = 10 * 60  # 10 minutos

# --------------------------------------------------
# INICIALIZAR SESIÓN (NO BORRAR)
# --------------------------------------------------
if "logueado" not in st.session_state:
    st.session_state.logueado = False

if "ultimo_movimiento" not in st.session_state:
    st.session_state.ultimo_movimiento = time.time()

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# --------------------------------------------------
# SECRETOS – MULTIUSUARIOS
# --------------------------------------------------
usuarios = st.secrets["usuarios"]  # diccionario desde Secrets

# --------------------------------------------------
# AUTO LOGOUT POR INACTIVIDAD (SEGURO)
# --------------------------------------------------
if st.session_state.logueado:
    ahora = time.time()
    if ahora - st.session_state.ultimo_movimiento > TIEMPO_MAX_INACTIVIDAD:
        st.session_state.clear()
        st.warning("Sesión cerrada por inactividad ⏱️")
        st.rerun()


# --------------------------------------------------
# SIDEBAR – LOGIN / LOGOUT
# --------------------------------------------------
st.sidebar.title("🔐 Acceso")

if not st.session_state.logueado:

    st.sidebar.text_input("Usuario", key="usuario_input")
    st.sidebar.text_input("Contraseña", type="password", key="clave_input")

    if st.sidebar.button("Ingresar"):
        usuario = st.session_state.usuario_input
        clave = st.session_state.clave_input

        if usuario in usuarios and usuarios[usuario] == clave:
            # ⚠️ NO limpiar antes de usar variables
            st.session_state.logueado = True
            st.session_state.usuario_actual = usuario
            st.session_state.ultimo_movimiento = time.time()
            st.rerun()
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

else:
    st.sidebar.success(f"Sesión activa: {st.session_state.usuario_actual}")

    if st.sidebar.button("Cerrar sesión 🚪"):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------
# 👋 SALUDO PERSONALIZADO (SOLO ESTO SE AGREGÓ)
# --------------------------------------------------
if st.session_state.logueado:

    saludos = {
        "Rigoberto": "Bienvenido",
        "Cynthia": "Bienvenida",
        "Brenda": "Bienvenida"
    }

    saludo = saludos.get(st.session_state.usuario_actual, "Bienvenid@")

    st.markdown(
        f"""
        <div style="text-align:center; margin-top:10px;">
            <div style="font-size:16px; color:#00FFAA;">
                {saludo}, {st.session_state.usuario_actual} 💚
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# CONTENIDO PROTEGIDO
# --------------------------------------------------
if st.session_state.logueado:

    # -----------------------------
    # TÍTULO
    # -----------------------------
    st.markdown(
        f"""
        <div style="text-align:center;">
            <div style="font-size:26px; font-weight:700; color:white;">
                Control de Embarques
            </div>
            <div style="font-size:20px; color:#CCCCCC; margin-top:6px;">
                Logística – Enero 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------
    # CARGA DE DATOS
    # -----------------------------
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

    # -----------------------------
    # SIDEBAR – FILTROS
    # -----------------------------
    st.sidebar.header("Filtros")
    
    # --- FILTRO POR CLIENTE (ya existente) ---
    if "filtro_cliente_actual" not in st.session_state:
        st.session_state.filtro_cliente_actual = ""
    
    def actualizar_filtro():
        st.session_state.filtro_cliente_actual = st.session_state.filtro_cliente_input
    
    st.sidebar.text_input(
        "Ingresa el No Cliente",
        value=st.session_state.filtro_cliente_actual,
        key="filtro_cliente_input",
        on_change=actualizar_filtro
    )
    
    # --- FILTRO FECHA DE ENVÍO ---
    fecha_min = df["FECHA DE ENVÍO"].min()
    fecha_max = df["FECHA DE ENVÍO"].max()
    rango_fechas = st.sidebar.date_input(
        "Fecha de envío",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    # --- FILTRO FLETERA (solo una para gráficos) ---
    fletera_sel = st.sidebar.selectbox(
        "Fletera",
        options=[""] + sorted(df["FLETERA"].dropna().unique()),  # "" permite no seleccionar nada
        index=0
    )
    
    # -----------------------------
    # APLICAR FILTROS A DF
    # -----------------------------
    df_filtrado = df.copy()
    
    # Cliente
    if st.session_state.filtro_cliente_actual.strip() != "":
        df_filtrado = df_filtrado[
            df_filtrado["NO CLIENTE"].str.contains(
                st.session_state.filtro_cliente_actual.strip(), case=False, na=False
            )
        ]
    
    # Fecha de envío
    if len(rango_fechas) == 2:
        fecha_inicio, fecha_fin = rango_fechas
        df_filtrado = df_filtrado[
            (df_filtrado["FECHA DE ENVÍO"] >= pd.to_datetime(fecha_inicio)) &
            (df_filtrado["FECHA DE ENVÍO"] <= pd.to_datetime(fecha_fin))
        ]
    
    # -----------------------------
    # Tabla existente
    # -----------------------------
    df_mostrar = df_filtrado.copy()
    # st.dataframe(df_mostrar.style ...)  <- tu bloque de tabla existente sigue igual
    
    # -----------------------------
    # GRÁFICO DE ESTATUS POR FLETERA
    # -----------------------------
    # Diccionario de colores por estatus
    colores_estatus = {
        "EN TRANSITO": "#FF9800",  # naranja
        "ENTREGADO": "#4CAF50",    # verde
        "RETRASADO": "#F44336"      # rojo
    }
    
    # Mapeo de posibles valores a estatus normalizados
    mapa_estatus = {
        "En Tiempo": "ENTREGADO",
        "Entregado": "ENTREGADO",
        "ENTREGADO": "ENTREGADO",
        "En Tránsito": "EN TRANSITO",
        "En tránsito": "EN TRANSITO",
        "EN TRANSITO": "EN TRANSITO",
        "Retraso": "RETRASADO",
        "Retrasado": "RETRASADO",
        "RETRASO": "RETRASADO"
    }
    
    if fletera_sel:  # Solo si selecciona una fletera
        df_graf = df_filtrado[df_filtrado["FLETERA"] == fletera_sel].copy()
        
        # Normalizar los estatus
        df_graf["ESTATUS_NORMAL"] = df_graf["ESTATUS_CALCULADO"].map(mapa_estatus)
        
        graf_estatus = (
            df_graf.groupby("ESTATUS_NORMAL")
            .size()
            .reindex(colores_estatus.keys(), fill_value=0)  # asegura que siempre estén los 3 estatus
            .reset_index(name="Total")
            .set_index("ESTATUS_NORMAL")
        )
        
        st.subheader(f"📊 Estatus de pedidos - {fletera_sel}")
        
        # Graficar con colores (st.bar_chart mantiene compatibilidad)
        st.bar_chart(graf_estatus["Total"])
    
    # -----------------------------
    # CAJA DE BÚSQUEDA POR PEDIDO – TARGETAS
    # -----------------------------
    pedido_buscar = st.text_input(
        "Buscar por Número de Factura",
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
                        .set_table_styles([
            {
                'selector': 'td',
                'props': [
                    ('padding-top', '16px'),
                    ('padding-bottom', '16px')
                ]
            },
            {
                'selector': 'th',
                'props': [
                    ('background-color', 'orange'),
                    ('color', 'white'),
                    ('font-weight','bold'),
                    ('font-size','14px'),
                    ('padding-top', '12px'),
                    ('padding-bottom', '12px')
                ]
            }
        ]),
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
























































































































