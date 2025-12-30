import streamlit as st
import pandas as pd
import altair as alt
import time
import base64
import textwrap

# 1. FUNCIÓN PARA IMAGEN DE FONDO
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# 2. ESTADOS DE SESIÓN (Control de navegación y login)
if "splash_visto" not in st.session_state:
    st.session_state.splash_visto = False
if "motivo_splash" not in st.session_state:
    st.session_state.motivo_splash = "inicio"
if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "principal"
if "ultimo_movimiento" not in st.session_state:
    st.session_state.ultimo_movimiento = time.time()

# 3. SPLASH SCREEN
if not st.session_state.splash_visto:
    texto_splash = "Bye, cerrando sistema…" if st.session_state.motivo_splash == "logout" else "Inicializando módulos logísticos…"
    st.markdown("""
    <style>
    .splash-container { display: flex; flex-direction: column; justify-content: flex-start; align-items: center; height: 100vh; padding-top: 160px; background-color: #0e1117; }
    .loader { border: 6px solid #2a2a2a; border-top: 6px solid #00FFAA; border-radius: 50%; width: 120px; height: 120px; animation: spin 1s linear infinite; margin-bottom: 20px; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="splash-container"><div class="loader"></div><div style="color:#aaa; font-size:14px;">{texto_splash}</div></div>', unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.splash_visto = True
    st.session_state.motivo_splash = "inicio"
    st.rerun()

# 4. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Control de Envíos – Enero 2026", layout="wide", initial_sidebar_state="collapsed")

# --------------------------------------------------
# FONDO DE PANTALLA SOLO PARA LOGIN
# --------------------------------------------------
if not st.session_state.logueado:
    img_base64 = get_base64_image("1.jpg")
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        /* CAJA DE LOGIN */
        .stForm {{
            background-color: #1e293b;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #334151;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}
        /* UNIFICACIÓN DE COLOR INPUTS */
        div[data-testid="stTextInputRootElement"], 
        div[data-testid="stTextInputRootElement"] *, 
        .stForm input {{
            background-color: #475569 !important;
            color: white !important;
            border: none !important;
        }}
        .login-header {{
            text-align: center; color: white; font-size: 24px; font-weight: bold; margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown('<div class="login-header">🔐 Acceso</div>', unsafe_allow_html=True)
            u_input = st.text_input("Usuario")
            c_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)

            if submit:
                # Usamos los secretos guardados en Streamlit Cloud
                usuarios = st.secrets["usuarios"]
                if u_input in usuarios and usuarios[u_input] == c_input:
                    st.session_state.logueado = True
                    st.session_state.usuario_actual = u_input
                    st.session_state.ultimo_movimiento = time.time()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    
    # Detenemos la ejecución aquí si no está logueado
    st.stop()

# --------------------------------------------------
# INICIO DEL CONTENIDO PRIVADO (SI ESTÁ LOGUEADO)
# --------------------------------------------------
else:
    # A partir de aquí, todo el código futuro irá dentro de este 'else'
    st.sidebar.title("🔐 Sesión Activa")
    
    # Estilo para el botón de cerrar sesión
    st.markdown("""
        <style>
        div[data-testid="stSidebar"] .stButton:first-of-type button {
            background-color: transparent !important;
            color: #ff4b4b !important;
            border: 1px solid rgba(255, 75, 75, 0.5) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.motivo_splash = "logout"
        st.session_state.splash_visto = False
        st.session_state.logueado = False
        st.rerun()

# --------------------------------------------------
# 👋 SALUDO PERSONALIZADO
# --------------------------------------------------
saludos = {"Rigoberto": "Bienvenido", "Cynthia": "Bienvenida", "Brenda": "Bienvenida"}
saludo = saludos.get(st.session_state.usuario_actual, "Bienvenid@")

st.markdown(f"""
    <div style="text-align:center; margin-top:10px;">
        <div style="font-size:16px; color:#00FFAA;">
            {saludo}, {st.session_state.usuario_actual} 💚
        </div>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 📊 MOTOR DE CARGA DE DATOS (Optimizado con Cache)
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    # Carga del CSV
    df = pd.read_csv("Matriz_Excel_Dashboard.csv", encoding="utf-8")
    
    # Limpieza de nombres de columnas
    df.columns = df.columns.str.strip().str.upper()

    # Formateo de columnas críticas
    df["NO CLIENTE"] = df["NO CLIENTE"].astype(str).str.strip()
    df["FECHA DE ENVÍO"] = pd.to_datetime(df["FECHA DE ENVÍO"], errors="coerce", dayfirst=True)
    df["PROMESA DE ENTREGA"] = pd.to_datetime(df["PROMESA DE ENTREGA"], errors="coerce", dayfirst=True)
    df["FECHA DE ENTREGA REAL"] = pd.to_datetime(df["FECHA DE ENTREGA REAL"], errors="coerce", dayfirst=True)

    hoy = pd.Timestamp.today().normalize()

    # Lógica de Estatus Calculado
    def calcular_estatus(row):
        if pd.notna(row["FECHA DE ENTREGA REAL"]):
            return "ENTREGADO"
        if pd.notna(row["PROMESA DE ENTREGA"]) and row["PROMESA DE ENTREGA"] < hoy:
            return "RETRASADO"
        return "EN TRANSITO"

    df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)
    return df

# Ejecutamos la carga (Disponible para todas las páginas)
df = cargar_datos()

# --------------------------------------------------
# 🛣️ INICIO DE LA LÓGICA DE NAVEGACIÓN
# --------------------------------------------------
if st.session_state.pagina == "principal":
    # A partir de aquí pondremos todo lo del Dashboard Principal
    # --------------------------------------------------
    # TÍTULO Y ENCABEZADO
    # --------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Control de Embarques</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Logística – Enero 2026</p>", unsafe_allow_html=True)
    st.divider()

    # --------------------------------------------------
    # SIDEBAR – FILTROS
    # --------------------------------------------------
    st.sidebar.header("Filtros")

    # 1. FUNCIÓN DE LIMPIEZA
    def limpiar_filtros():
        st.session_state.filtro_cliente_actual = ""
        st.session_state.filtro_cliente_input = ""
        f_min_res = df["FECHA DE ENVÍO"].min()
        f_max_res = df["FECHA DE ENVÍO"].max()
        st.session_state["fecha_filtro"] = (f_min_res, f_max_res)
        st.session_state["fletera_filtro"] = ""
        st.rerun()

    if st.sidebar.button("Limpiar Filtros 🧹", use_container_width=True):
        limpiar_filtros()

    st.sidebar.markdown("---")

    # 2. BUSCADOR (CLIENTE O GUÍA)
    if "filtro_cliente_actual" not in st.session_state:
        st.session_state.filtro_cliente_actual = ""

    def actualizar_filtro():
        st.session_state.filtro_cliente_actual = st.session_state.filtro_cliente_input

    st.sidebar.text_input(
        "No. Cliente o Número de Guía",
        value=st.session_state.filtro_cliente_actual,
        key="filtro_cliente_input",
        on_change=actualizar_filtro
    )

    # 3. CALENDARIO
    f_min_data = df["FECHA DE ENVÍO"].min()
    f_max_data = df["FECHA DE ENVÍO"].max()

    if "fecha_filtro" not in st.session_state:
        st.session_state["fecha_filtro"] = (f_min_data, f_max_data)

    rango_fechas = st.sidebar.date_input(
        "Fecha de envío",
        min_value=f_min_data,
        max_value=f_max_data,
        key="fecha_filtro"
    )

    # 4. SELECTOR DE FLETERA
    fletera_sel = st.sidebar.selectbox(
        "Selecciona Fletera",
        options=[""] + sorted(df["FLETERA"].dropna().unique()),
        index=0,
        key="fletera_filtro"
    )
    # --------------------------------------------------
    # APLICACIÓN DE FILTROS (LÓGICA PRIORIZADA)
    # --------------------------------------------------
    df_filtrado = df.copy()
    valor_buscado = str(st.session_state.filtro_cliente_actual).strip().lower()

    # PRIORIDAD 1: Búsqueda de Texto (Cliente o Guía)
    if valor_buscado != "":
        col_cliente = "NO CLIENTE"
        col_guia = "NÚMERO DE GUÍA"
        
        def limpiar_col(s):
            return s.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lower()

        mask_cliente = limpiar_col(df_filtrado[col_cliente]).str.contains(valor_buscado, na=False)
        mask_guia = limpiar_col(df_filtrado[col_guia]).str.contains(valor_buscado, na=False)
        
        df_filtrado = df_filtrado[mask_cliente | mask_guia]
        
    # PRIORIDAD 2: Filtros Normales (Fecha y Fletera)
    else:
        if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
            f_inicio, f_fin = rango_fechas
            col_fechas_dt = pd.to_datetime(df_filtrado["FECHA DE ENVÍO"], errors='coerce')
            df_filtrado = df_filtrado[(col_fechas_dt >= pd.to_datetime(f_inicio)) & 
                                      (col_fechas_dt <= pd.to_datetime(f_fin))]
            
        if fletera_sel != "":
            df_filtrado = df_filtrado[df_filtrado["FLETERA"].astype(str).str.strip() == fletera_sel]

    # --------------------------------------------------
    # GRÁFICO DE ESTATUS POR FLETERA (Visualización Interactiva)
    # --------------------------------------------------
    if fletera_sel:
        st.markdown(f"<h4 style='text-align:center;'>Estatus de pedidos - {fletera_sel}</h4>", unsafe_allow_html=True)
        
        df_graf = df_filtrado[df_filtrado["FLETERA"] == fletera_sel].copy()
        # Agrupamos y rellenamos ceros para que la gráfica no desaparezca si no hay datos de un tipo
        graf_estatus = df_graf.groupby("ESTATUS_CALCULADO").size().reset_index(name="Total")
        
        st.bar_chart(graf_estatus.set_index("ESTATUS_CALCULADO")["Total"])
        st.divider()

    # --------------------------------------------------
    # CAJA DE BÚSQUEDA POR PEDIDO – TARJETAS + TIMELINE
    # --------------------------------------------------
    pedido_buscar = st.text_input(
        "Buscar por Número de Factura",
        value="",
        help="Ingresa un número de pedido para mostrar solo esos registros"
    )

    df_busqueda = pd.DataFrame() # Blindaje inicial

    if pedido_buscar.strip() != "":
        # Filtrar solo por Número de Pedido
        df_busqueda = df_filtrado[
            df_filtrado["NÚMERO DE PEDIDO"]
            .astype(str)
            .str.contains(pedido_buscar.strip(), case=False, na=False)
        ].copy()

        if df_busqueda.empty:
            st.warning("No se encontró ningún pedido con ese número.")
        else:
            hoy = pd.Timestamp.today().normalize()
            
            # Cálculos de tiempo para las tarjetas
            df_busqueda["DIAS_TRANSCURRIDOS"] = (
                (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["FECHA DE ENVÍO"]).dt.days
            )
            df_busqueda["DIAS_RETRASO"] = (
                (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["PROMESA DE ENTREGA"]).dt.days
            )
            df_busqueda["DIAS_RETRASO"] = df_busqueda["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)

            # Renderizado de Tarjetas y Timeline por cada registro encontrado
            for index, row in df_busqueda.iterrows():
                st.markdown(f'<p style="font-size:14px; font-weight:bold; color:Yellow; margin-bottom:-10px;">Estatus de Factura: {row["NÚMERO DE PEDIDO"]}</p>', unsafe_allow_html=True)
                
                # Preparación de Fechas para el Timeline
                f_envio_dt = pd.to_datetime(row.get("FECHA DE ENVÍO"), errors='coerce')
                f_promesa_dt = pd.to_datetime(row.get("PROMESA DE ENTREGA"), errors='coerce')
                f_real_dt = pd.to_datetime(row.get("FECHA DE ENTREGA REAL"), errors='coerce')
                hoy_dt = pd.Timestamp.now().normalize()
                
                txt_f_envio = f_envio_dt.strftime('%d/%m/%Y') if pd.notna(f_envio_dt) else "S/D"
                txt_f_actual = hoy_dt.strftime('%d/%m/%Y')
                txt_f_promesa = f_promesa_dt.strftime('%d/%m/%Y') if pd.notna(f_promesa_dt) else "S/D"
                txt_f_real = f_real_dt.strftime('%d/%m/%Y') if pd.notna(f_real_dt) else ""
                
                # Lógica de colores del Timeline
                entregado = pd.notna(f_real_dt)
                if entregado:
                    t_fin, c_fin = "ENTREGADO", "#22c55e"
                    t_medio, c_medio = ("ENTREGADA EN TIEMPO", "#22c55e") if f_real_dt <= f_promesa_dt else ("ENTREGADA CON RETRASO", "#ef4444")
                else:
                    t_fin, c_fin = "EN ESPERA", "#374151"
                    t_medio, c_medio = ("RETRASO", "#f97316") if pd.notna(f_promesa_dt) and f_promesa_dt < hoy_dt else ("EN TRÁNSITO", "#3b82f6")

                # HTML del Timeline
                html_timeline = f'<div style="background:#111827;padding:25px;border-radius:12px;border:1px solid #374151;margin-top:15px;"><div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;width:100%;"><div style="position:absolute;top:20px;left:10%;right:10%;height:6px;background:#374151;z-index:0;"></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">ENVIADO</div><div style="color:gray;font-size:10px;">{txt_f_envio}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">FECHA ACTUAL</div><div style="color:gray;font-size:10px;">{txt_f_actual}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:{c_medio};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_medio}</div><div style="color:gray;font-size:10px;"><span style="color:#22c55e;">PROMESA</span> {txt_f_promesa}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:{c_fin};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_fin}</div><div style="color:gray;font-size:10px;">FECHA REAL: {txt_f_real}</div></div></div></div>'
                st.markdown(html_timeline, unsafe_allow_html=True)
                
                # Tarjetas Informativas
                c1, c2, c3 = st.columns(3)
                estilo_card = "background-color:#1A1E25; padding:15px; border-radius:10px; border: 1px solid #374151; min-height: 270px;"
                
                with c1:
                    costo_mxn = f"${float(row.get('COSTO DE LA GUÍA', 0)):,.2f}"
                    st.markdown(f"<div style='{estilo_card}'><div style='color:yellow; font-weight:bold; text-align:center;'>Información Cliente</div><b>NO CLIENTE:</b> {row.get('NO CLIENTE')}<br><b>NOMBRE:</b> {row.get('NOMBRE DEL CLIENTE')}<br><b>DESTINO:</b> {row.get('DESTINO')}<br><b>FLETERA:</b> {row.get('FLETERA')}<br><b>COSTO:</b> <span style='color:#22c55e;'>{costo_mxn}</span></div>", unsafe_allow_html=True)
                with c2:
                    retraso = row.get('DIAS_RETRASO', 0)
                    st.markdown(f"<div style='{estilo_card}'><div style='color:yellow; font-weight:bold; text-align:center;'>Seguimiento</div><b>ENVÍO:</b> {txt_f_envio}<br><b>PROMESA:</b> {txt_f_promesa}<br><b>REAL:</b> {txt_f_real if txt_f_real else 'PENDIENTE'}<br><b>DÍAS TRANS:</b> {row.get('DIAS_TRANSCURRIDOS')}<br><b>RETRASO:</b> <span style='color:{'red' if retraso > 0 else 'white'};'>{retraso}</span></div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div style='{estilo_card}'><div style='color:yellow; font-weight:bold; text-align:center;'>Observaciones</div><b>ESTATUS:</b> {row.get('ESTATUS_CALCULADO')}<br><b>PRIORIDAD:</b> {row.get('PRIORIDAD')}<br><b>COMENTARIOS:</b><br><small>{row.get('COMENTARIOS', 'Sin comentarios')}</small></div>", unsafe_allow_html=True)
                st.divider()
    
    # --------------------------------------------------
    # KPIs CON DONITAS (Función y Renderizado)
    # --------------------------------------------------
    COLOR_AVANCE_ENTREGADOS = "#4CAF50"   # Verde
    COLOR_AVANCE_TRANSITO   = "#FFC107"   # Amarillo
    COLOR_AVANCE_RETRASADOS = "#F44336"   # Rojo
    COLOR_FALTANTE          = "#3A3A3A"   # Gris

    def donut_con_numero(avance, total, color_avance, color_faltante):
        porcentaje = int((avance / total) * 100) if total > 0 else 0
        data = pd.DataFrame({
            "segmento": ["avance", "faltante"],
            "valor": [avance, max(total - avance, 0)]
        })
        donut = alt.Chart(data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("valor:Q"),
            color=alt.Color("segmento:N", scale=alt.Scale(range=[color_avance, color_faltante]), legend=None)
        )
        texto_numero = alt.Chart(pd.DataFrame({"texto": [f"{avance}"]})).mark_text(
            align="center", baseline="middle", fontSize=26, fontWeight="bold", dy=-8, color="white"
        ).encode(text="texto:N")
        texto_porcentaje = alt.Chart(pd.DataFrame({"texto": [f"{porcentaje}%"]})).mark_text(
            align="center", baseline="middle", fontSize=14, dy=16, color="gray"
        ).encode(text="texto:N")
        return (donut + texto_numero + texto_porcentaje).properties(width=140, height=140)

    st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">Indicadores Generales</div></div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    # Conteos para las donitas
    t_val = len(df_filtrado)
    e_val = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
    tr_val = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
    r_val = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()

    with c1:
        st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Total de pedidos</div>", unsafe_allow_html=True)
        st.altair_chart(donut_con_numero(t_val, t_val, "#FFD700", COLOR_FALTANTE), use_container_width=True)
    with c2:
        st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Entregados</div>", unsafe_allow_html=True)
        st.altair_chart(donut_con_numero(e_val, t_val, COLOR_AVANCE_ENTREGADOS, COLOR_FALTANTE), use_container_width=True)
    with c3:
        st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>En tránsito</div>", unsafe_allow_html=True)
        st.altair_chart(donut_con_numero(tr_val, t_val, COLOR_AVANCE_TRANSITO, COLOR_FALTANTE), use_container_width=True)
    with c4:
        st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Retrasados</div>", unsafe_allow_html=True)
        st.altair_chart(donut_con_numero(r_val, t_val, COLOR_AVANCE_RETRASADOS, COLOR_FALTANTE), use_container_width=True)
    
    # --------------------------------------------------
    # TABLA FINAL – LISTA DE ENVÍOS CON ESTILOS
    # --------------------------------------------------
    st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">Lista de envíos</div></div>""", unsafe_allow_html=True)

    hoy_tabla = pd.Timestamp.today().normalize()
    df_mostrar = df_filtrado.copy()

    # Cálculos para la tabla
    df_mostrar["DIAS_TRANSCURRIDOS"] = ((df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy_tabla) - df_mostrar["FECHA DE ENVÍO"]).dt.days)
    df_mostrar["DIAS_RETRASO"] = ((df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy_tabla) - df_mostrar["PROMESA DE ENTREGA"]).dt.days)
    df_mostrar["DIAS_RETRASO"] = df_mostrar["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)

    # Formateo de fechas para visualización
    df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].dt.strftime('%d/%m/%Y').fillna('')
    df_mostrar["FECHA DE ENVÍO"] = df_mostrar["FECHA DE ENVÍO"].dt.strftime('%d/%m/%Y').fillna('')
    df_mostrar["PROMESA DE ENTREGA"] = df_mostrar["PROMESA DE ENTREGA"].dt.strftime('%d/%m/%Y').fillna('')

    # Funciones de Estilo para la Tabla
    def colorear_retraso(val):
        return 'background-color: #ff4d4d; color: black; font-weight: bold;' if val > 0 else ''

    def zebra_filas(row):
        color = '#0E1117' if row.name % 2 == 0 else '#1A1E25'
        return [f'background-color: {color}; color: white;' for _ in row]

    # Renderizado de la Tabla con CSS inyectado
    st.dataframe(
        df_mostrar.style.apply(zebra_filas, axis=1)
                        .applymap(colorear_retraso, subset=["DIAS_RETRASO"])
                        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', 'orange'), ('color', 'white'), ('font-weight','bold')]},
            {'selector': 'td', 'props': [('padding', '10px')]}
        ]),
        use_container_width=True,
        height=520
    )

    # --------------------------------------------------
    # GRÁFICOS POR PAQUETERÍA – (TRÁNSITO Y RETRASOS)
    # --------------------------------------------------
    TAMANO_FUENTE = 14
    ESPACIADO_DY = -12
    MARGEN_SUPERIOR = 1.3

    st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">Pendientes por Paquetería</div></div>""", unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    # --- 1. GRÁFICO: EN TRÁNSITO ---
    df_transito = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO"].groupby("FLETERA").size().reset_index(name="PEDIDOS")
    
    if not df_transito.empty:
        max_t = df_transito["PEDIDOS"].max() * MARGEN_SUPERIOR
        base_t = alt.Chart(df_transito).encode(x=alt.X("FLETERA:N", title="Paquetería"))
        bars_t = base_t.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            y=alt.Y("PEDIDOS:Q", title="Pedidos en tránsito", scale=alt.Scale(domain=[0, max_t])),
            color=alt.value("#FFC107")
        )
        text_t = base_t.mark_text(align='center', baseline='bottom', dy=ESPACIADO_DY, fontSize=TAMANO_FUENTE, fontWeight='bold', color='white').encode(
            y=alt.Y("PEDIDOS:Q"), text=alt.Text("PEDIDOS:Q")
        )
        g1.markdown("<h4 style='color:yellow; text-align:center;'>En tránsito</h4>", unsafe_allow_html=True)
        g1.altair_chart((bars_t + text_t).properties(height=320), use_container_width=True)

    # --- 2. GRÁFICO: RETRASADOS ---
    df_retrasados = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO"].groupby("FLETERA").size().reset_index(name="PEDIDOS")
    
    if not df_retrasados.empty:
        max_r = df_retrasados["PEDIDOS"].max() * MARGEN_SUPERIOR
        base_r = alt.Chart(df_retrasados).encode(x=alt.X("FLETERA:N", title="Paquetería"))
        bars_r = base_r.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            y=alt.Y("PEDIDOS:Q", title="Pedidos retrasados", scale=alt.Scale(domain=[0, max_r])),
            color=alt.value("#F44336")
        )
        text_r = base_r.mark_text(align='center', baseline='bottom', dy=ESPACIADO_DY, fontSize=TAMANO_FUENTE, fontWeight='bold', color='white').encode(
            y=alt.Y("PEDIDOS:Q"), text=alt.Text("PEDIDOS:Q")
        )
        g2.markdown("<h4 style='color:#F44336; text-align:center;'>Retrasados</h4>", unsafe_allow_html=True)
        g2.altair_chart((bars_r + text_r).properties(height=320), use_container_width=True)

    # --- 1. FINAL DE LA PÁGINA PRINCIPAL ---
        st.divider()
        
        # Botón para ir a los KPIs (Cerca del final)
        col_esp, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("📊 Ver KPIs Detallados", use_container_width=True):
                st.session_state.pagina = "KPIs"
                st.rerun()

        st.markdown("<div style='text-align:center; color:gray;'>© 2026 Logística - Vista Operativa</div>", unsafe_allow_html=True) 

    # ------------------------------------------------------------------
    # --- 2. VISTA DE KPIs (Esta es la nueva habitación de tu casa) ---
    # ------------------------------------------------------------------
    elif st.session_state.pagina == "KPIs":
        st.markdown("<h1 style='text-align:center; color:#00FFAA;'>📈 Análisis Detallado de KPIs</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Logística – Indicadores de Rendimiento</p>", unsafe_allow_html=True)
        st.divider()

        # MÉTRICAS GERENCIALES
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Calculamos algunos datos globales para esta vista
        total_p = len(df)
        eficiencia = (len(df[df['ESTATUS_CALCULADO'] == 'ENTREGADO']) / total_p * 100) if total_p > 0 else 0
        
        with kpi1:
            st.metric("Total de Pedidos Mes", f"{total_p}")
        with kpi2:
            st.metric("Eficiencia de Entrega", f"{eficiencia:.1f}%", "+2.5%")
        with kpi3:
            st.metric("Costo Promedio Envío", "$425 MXN", "-1.2%")

        st.write("##")
        
        # Espacio para tus futuras gráficas de KPIs
        st.info("💡 En esta sección puedes agregar comparativas anuales o gráficas de rendimiento por fletera sin que se mezclen con el tablero de búsqueda.")

        # --- BOTÓN PARA VOLVER ---
        st.divider()
        if st.button("⬅ Volver al Tablero de Control", use_container_width=True):
            st.session_state.pagina = "principal"
            st.rerun()

        st.markdown("<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Logística - Vista Gerencial</div>", unsafe_allow_html=True)








































































































































































































































