import streamlit as st
import pandas as pd
import altair as alt
import time
import base64   # 👈 aquí
import textwrap

# 1. CONFIGURACIÓN (Línea 1)
st.set_page_config(
    page_title="Control de Envíos – Enero 2026",
    layout="wide",
    initial_sidebar_state="collapsed" # Le decimos que empiece cerrada
)

# 2. EL "BLOQUEADOR TOTAL" (Ponlo así, sin 'if' primero para probar)
# Este CSS mata la barra lateral desde que el navegador recibe el primer bit de datos
st.markdown("""
    <style>
        /* Oculta el contenedor de la barra lateral */
        [data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
        }
        
        /* Oculta el botón de la flecha de arriba a la izquierda */
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        /* Quita el espacio en blanco que deja la barra al intentar aparecer */
        .stAppDeployButton {
            display: none;
        }
        
        /* Desactiva TODAS las animaciones para que no haya parpadeo */
        * {
            transition: none !important;
            animation: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE LOGIN
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# --------------------------------------------------
# 2. ESTADOS INICIALES DE SESIÓN
# --------------------------------------------------
if "splash_visto" not in st.session_state:
    st.session_state.splash_visto = False

if "motivo_splash" not in st.session_state:
    st.session_state.motivo_splash = "inicio"

if "logueado" not in st.session_state:
    st.session_state.logueado = False

if "ultimo_movimiento" not in st.session_state:
    st.session_state.ultimo_movimiento = time.time()

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# --------------------------------------------------
# 3. CSS DE EMERGENCIA ANTIPARPADEO
# --------------------------------------------------
if not st.session_state.logueado:
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
                width: 0px !important;
            }
            [data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }
            .stMain {
                margin-left: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 4. FUNCIONES AUXILIARES
# --------------------------------------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# --------------------------------------------------
# 5. SPLASH SCREEN (INICIO Y SALIDA)
# --------------------------------------------------
if not st.session_state.splash_visto:
    texto_splash = (
        "Bye, cerrando sistema…"
        if st.session_state.motivo_splash == "logout"
        else "Inicializando módulos logísticos…"
    )

    st.markdown("""
    <style>
    .splash-container {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        height: 70vh;
        padding-top: 160px;
        background-color: #0e1117;
    }
    .loader {
        border: 6px solid #2a2a2a;
        border-top: 6px solid #00FFAA;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="splash-container">
        <div class="loader"></div>
        <div style="color:#aaa; font-size:14px; font-family: sans-serif;">
            {texto_splash}
        </div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(2)
    st.session_state.splash_visto = True
    st.session_state.motivo_splash = "inicio"
    st.rerun()

# --------------------------------------------------
# 6. LÓGICA DE AUTO LOGOUT
# --------------------------------------------------
TIEMPO_MAX_INACTIVIDAD = 10 * 60  # 10 minutos

if st.session_state.logueado:
    ahora = time.time()
    if ahora - st.session_state.ultimo_movimiento > TIEMPO_MAX_INACTIVIDAD:
        st.session_state.logueado = False
        st.session_state.splash_visto = False
        st.session_state.motivo_splash = "logout"
        st.session_state.usuario_actual = None
        st.rerun()

# --------------------------------------------------
# 7. INTERFAZ DE LOGIN (SI NO ESTÁ LOGUEADO)
# --------------------------------------------------
if not st.session_state.logueado:
    # Imagen de fondo
    img_base64 = get_base64_image("1.jpg")
    if img_base64:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            """, unsafe_allow_html=True)

    # Estilos de la Caja de Login
    st.markdown("""
        <style>
        .stForm {
            background-color: #1e293b;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #334151;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        div[data-testid="stTextInputRootElement"], 
        div[data-testid="stTextInputRootElement"] *, 
        .stForm input {
            background-color: #475569 !important;
            color: white !important;
            border: none !important;
        }
        div[data-testid="stTextInputRootElement"] {
            border: 1px solid #64748b !important;
            border-radius: 8px !important;
        }
        button[aria-label="Show password"], 
        button[aria-label="Hide password"] {
            background-color: transparent !important;
        }
        .login-header {
            text-align: center; color: white; font-size: 24px; font-weight: bold; margin-bottom: 20px;
        }
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
                usuarios = st.secrets["usuarios"]
                if u_input in usuarios and usuarios[u_input] == c_input:
                    st.session_state.logueado = True
                    st.session_state.usuario_actual = u_input
                    st.session_state.ultimo_movimiento = time.time()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    st.stop()

# --------------------------------------------------
# 8. DASHBOARD PRINCIPAL (DESPUÉS DEL LOGIN)
# --------------------------------------------------
else:
    # Actualizar último movimiento al cargar cualquier parte del dashboard
    st.session_state.ultimo_movimiento = time.time()

    # Barra Lateral
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    st.sidebar.markdown("---")
    
    # Estilo del botón Logout
    st.markdown("""
        <style>
        div[data-testid="stSidebar"] .stButton button {
            background-color: transparent !important;
            color: #ff4b4b !important;
            border: 1px solid rgba(255, 75, 75, 0.5) !important;
        }
        div[data-testid="stSidebar"] .stButton button:hover {
            background-color: rgba(255, 75, 75, 0.1) !important;
            border-color: #ff4b4b !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar sesión", use_container_width=True, key="btn_logout"):
        st.session_state.motivo_splash = "logout"
        st.session_state.splash_visto = False
        st.session_state.logueado = False
        st.rerun()

    # --- AQUÍ EMPIEZA TU CONTENIDO DE DASHBOARD ---
    st.title("🚚 Jypesa OpsDash 2026")
    st.info("Bienvenido al sistema. Selecciona una página en el menú superior para ver los KPIs.")
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

    # --------------------------------------------------
    # SIDEBAR – FILTROS (BLOQUE UNIFICADO Y CORREGIDO)
    # --------------------------------------------------
    st.sidebar.header("Filtros")
    
    # 1. FUNCIÓN DE LIMPIEZA
    def limpiar_filtros():
        st.session_state.filtro_cliente_actual = ""
        st.session_state.filtro_cliente_input = ""
        # Resetear Fechas al rango original
        f_min_res = df["FECHA DE ENVÍO"].min()
        f_max_res = df["FECHA DE ENVÍO"].max()
        st.session_state["fecha_filtro"] = (f_min_res, f_max_res)
        st.session_state["fletera_filtro"] = ""
        st.rerun()
    
    if st.sidebar.button("Limpiar Filtros 🧹", use_container_width=True):
        limpiar_filtros()
    
    st.sidebar.markdown("---")
    
    # --- BUSCADOR (CLIENTE O GUÍA) ---
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
    
    # --- CALENDARIO ---
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
    
    # --- SELECTOR DE FLETERA ---
    fletera_sel = st.sidebar.selectbox(
        "Selecciona Fletera",
        options=[""] + sorted(df["FLETERA"].dropna().unique()),
        index=0,
        key="fletera_filtro"
    )
    
    # --------------------------------------------------
    # APLICACIÓN DE FILTROS (LÓGICA FINAL SIN REPETICIONES)
    # --------------------------------------------------
    # Creamos la copia una sola vez
    df_filtrado = df.copy()
    
    valor_buscado = str(st.session_state.filtro_cliente_actual).strip().lower()
    
    # PRIORIDAD 1: Si el usuario escribió algo en el buscador
    if valor_buscado != "":
        col_cliente = "NO CLIENTE"
        col_guia = "NÚMERO DE GUÍA"
        
        # Función para limpiar datos (quitar .0 de Excel y espacios)
        def limpiar_col(s):
            return s.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lower()

        mask_cliente = limpiar_col(df_filtrado[col_cliente]).str.contains(valor_buscado, na=False)
        mask_guia = limpiar_col(df_filtrado[col_guia]).str.contains(valor_buscado, na=False)
        
        # Filtramos por texto (esto ignora fechas para que el dato aparezca sí o sí)
        df_filtrado = df_filtrado[mask_cliente | mask_guia]
        
    # PRIORIDAD 2: Si el buscador está vacío, aplicamos filtros normales
    else:
        # Validación de fechas para evitar el TypeError: len()
        if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
            f_inicio, f_fin = rango_fechas
            
            # Conversión segura a Datetime para comparar sin errores
            col_fechas_dt = pd.to_datetime(df_filtrado["FECHA DE ENVÍO"], errors='coerce')
            f_ini_dt = pd.to_datetime(f_inicio)
            f_fin_dt = pd.to_datetime(f_fin)
            
            df_filtrado = df_filtrado[(col_fechas_dt >= f_ini_dt) & (col_fechas_dt <= f_fin_dt)]
            
        # Filtro de fletera
        if fletera_sel != "":
            df_filtrado = df_filtrado[df_filtrado["FLETERA"].astype(str).str.strip() == fletera_sel]
    
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
        
        st.markdown(
            f"<h4 style='font-size:24px; text-align:center;'>Estatus de pedidos - {fletera_sel}</h4>",
            unsafe_allow_html=True
        )
        
        # Graficar con colores (st.bar_chart mantiene compatibilidad)
        st.bar_chart(graf_estatus["Total"])
    
    # -----------------------------
    # CAJA DE BÚSQUEDA POR PEDIDO – TARJETAS + TIMELINE
    # -----------------------------
    pedido_buscar = st.text_input(
        "Buscar por Número de Factura",
        value="",
        help="Ingresa un número de pedido para mostrar solo esos registros"
    )
    
    df_busqueda = pd.DataFrame()  # 👈 blindaje
    
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
    
            # Calcular días transcurridos y días de retraso
            df_busqueda["DIAS_TRANSCURRIDOS"] = (
                (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["FECHA DE ENVÍO"]).dt.days
            )
    
            df_busqueda["DIAS_RETRASO"] = (
                (df_busqueda["FECHA DE ENTREGA REAL"].fillna(hoy) - df_busqueda["PROMESA DE ENTREGA"]).dt.days
            )
            df_busqueda["DIAS_RETRASO"] = df_busqueda["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)
    
    # -----------------------------
    # -----------------------------
    # RENDERIZADO (TODO ESTO VA DENTRO DEL BUCLE)
    # -----------------------------
    if not df_busqueda.empty:
        for index, row in df_busqueda.iterrows():
            st.markdown(f'<p style="font-size:14px; font-weight:bold; color:Yellow; margin-bottom:-10px;">Estatus de Factura: {row["NÚMERO DE PEDIDO"]}</p>', unsafe_allow_html=True)
            
             # --- 1. EXTRACCIÓN CON LOS NOMBRES EXACTOS DE TU TABLA ---
            f_envio_val = row.get("FECHA DE ENVÍO") or row.get("FECHA DE ENVIO")
            f_promesa_val = row.get("PROMESA DE ENTREGA")  # Nombre exacto de tu última imagen
            f_real_val = row.get("FECHA DE ENTREGA REAL") # Nombre exacto de tu última imagen
            
            # Conversión segura a datetime
            f_envio_dt = pd.to_datetime(f_envio_val, errors='coerce')
            f_promesa_dt = pd.to_datetime(f_promesa_val, errors='coerce')
            f_real_dt = pd.to_datetime(f_real_val, errors='coerce')
            hoy_dt = pd.Timestamp.now().normalize()
            
            # Formateo de fechas para el HTML
            txt_f_envio = f_envio_dt.strftime('%d/%m/%Y') if pd.notna(f_envio_dt) else "S/D"
            txt_f_actual = hoy_dt.strftime('%d/%m/%Y')
            txt_f_promesa = f_promesa_dt.strftime('%d/%m/%Y') if pd.notna(f_promesa_dt) else "S/D"
            txt_f_real = f_real_dt.strftime('%d/%m/%Y') if pd.notna(f_real_dt) else ""
            
            # --- 2. LÓGICA DE ESTADOS CORREGIDA (11/12 <= 11/12 es Verde) ---
            entregado = pd.notna(f_real_dt)
            
            if entregado:
                t_fin, c_fin = "ENTREGADO", "#22c55e"
                # Si la fecha real es menor o igual a la promesa, es VERDE (En Tiempo)
                if pd.notna(f_promesa_dt) and f_real_dt <= f_promesa_dt:
                    t_medio, c_medio = "ENTREGADA EN TIEMPO", "#22c55e"
                else:
                    t_medio, c_medio = "ENTREGADA CON RETRASO", "#ef4444"
            else:
                t_fin, c_fin = "EN ESPERA", "#374151"
                if pd.notna(f_promesa_dt) and f_promesa_dt < hoy_dt:
                    t_medio, c_medio = "RETRASO", "#f97316"
                else:
                    t_medio, c_medio = "EN TRÁNSITO", "#3b82f6"
            
            # --- 3. HTML EN UNA SOLA LÍNEA (PUNTO 2 EN VERDE) ---
            html_timeline = f'<div style="background:#111827;padding:25px;border-radius:12px;border:1px solid #374151;margin-top:15px;"><div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;width:100%;"><div style="position:absolute;top:20px;left:10%;right:10%;height:6px;background:#374151;z-index:0;"></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">ENVIADO</div><div style="color:gray;font-size:10px;">{txt_f_envio}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">FECHA ACTUAL</div><div style="color:gray;font-size:10px;">{txt_f_actual}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:{c_medio};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_medio}</div><div style="color:gray;font-size:10px;"><span style="color:#22c55e;">PROMESA DE ENTREGA</span> {txt_f_promesa}</div></div><div style="text-align:center;z-index:1;width:25%;"><div style="width:40px;height:40px;border-radius:50%;background:{c_fin};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_fin}</div><div style="color:gray;font-size:10px;">FECHA REAL: {txt_f_real}</div></div></div></div>'
            
            st.markdown(html_timeline, unsafe_allow_html=True)
            st.divider()
            
            
            
            # --- 1. DISEÑO DE LAS 3 TARJETAS (DENTRO DEL BUCLE FOR) ---
            c1, c2, c3 = st.columns(3)
            estilo_card = "background-color:#1A1E25; padding:15px; border-radius:10px; border: 1px solid #374151; min-height: 270px;"
    
            with c1:
                # Formateo de Costo en Pesos
                costo_raw = row.get('COSTO DE LA GUÍA', 0)
                try:
                    costo_mxn = f"${float(costo_raw):,.2f}"
                except:
                    costo_mxn = f"${costo_raw}"
    
                st.markdown(f"""
                    <div style='{estilo_card}'>
                        <div style='color:yellow; font-weight:bold; text-align:center; margin-bottom:10px;'>Información Cliente</div>
                        <b>NO CLIENTE:</b> {row.get('NO CLIENTE', 'N/A')}<br>
                        <b>NOMBRE DEL CLIENTE:</b> {row.get('NOMBRE DEL CLIENTE', 'N/A')}<br>
                        <b>DESTINO:</b> {row.get('DESTINO', 'N/A')}<br>
                        <b>FLETERA:</b> {row.get('FLETERA', 'N/A')}<br>
                        <b>GUÍA:</b> {row.get('NÚMERO DE GUÍA', 'N/A')}<br>
                        <b>COSTO GUÍA:</b> <span style='color:#22c55e;'>{costo_mxn}</span>
                    </div>
                """, unsafe_allow_html=True)
    
            with c2:
                # Tarjeta 2: Fechas y Tiempos (Aquí agregamos DÍAS TRANSCURRIDOS)
                f_envio = row['FECHA DE ENVÍO'].strftime('%d/%m/%Y') if pd.notna(row['FECHA DE ENVÍO']) else "---"
                f_prom = row['PROMESA DE ENTREGA'].strftime('%d/%m/%Y') if pd.notna(row['PROMESA DE ENTREGA']) else "---"
                f_real = row['FECHA DE ENTREGA REAL'].strftime('%d/%m/%Y') if pd.notna(row['FECHA DE ENTREGA REAL']) else "PENDIENTE"                
                dias_trans = row.get('DIAS_TRANSCURRIDOS', 0)
                retraso = row.get('DIAS_RETRASO', 0)
                color_retraso = "red" if retraso > 0 else "white"
    
                st.markdown(f"""
                    <div style='{estilo_card}'>
                        <div style='color:yellow; font-weight:bold; text-align:center; margin-bottom:10px;'>Fechas y Seguimiento</div>
                        <b>FECHA DE ENVÍO:</b> {f_envio}<br>
                        <b>PROMESA ENTREGA:</b> {f_prom}<br>
                        <b>ENTREGA REAL:</b> {f_real}<br>
                        <b>DÍAS TRANSCURRIDOS:</b> {dias_trans}<br>
                        <b>DÍAS RETRASO:</b> <span style='color:{color_retraso}; font-weight:bold;'>{retraso}</span>
                    </div>
                """, unsafe_allow_html=True)
    
            with c3:
                st.markdown(f"""
                    <div style='{estilo_card}'>
                        <div style='color:yellow; font-weight:bold; text-align:center; margin-bottom:10px;'>Observaciones</div>
                        <b>ESTATUS:</b> {row.get('ESTATUS_CALCULADO', 'N/A')}<br>
                        <b>PRIORIDAD:</b> {row.get('PRIORIDAD', 'N/A')}<br>
                        <b>COMENTARIOS:</b>
                        <small>{row.get('COMENTARIOS', 'Sin comentarios') if pd.notna(row.get('COMENTARIOS')) else 'Sin comentarios'}</small>
                    </div>
                """, unsafe_allow_html=True)
    
            # --- 2. EL TIMELINE (Renderizado como HTML real, no texto) ---
           
    
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
    # GRÁFICOS POR PAQUETERÍA – CONTROL TOTAL DE TAMAÑO
    # --------------------------------------------------
    
    # ==========================================
    # 👇 AJUSTA ESTOS VALORES A TU GUSTO 👇
    # ==========================================
    TAMANO_TEXTO = 14   # Cambia este número para el tamaño de la fuente
    ESPACIADO_DY = -15   # Si haces el texto más grande, pon un número más negativo (ej. -20)
    # ==========================================
    
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
    
    # --- 1. EN TRÁNSITO ---
    df_transito = (
        df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO"]
        .groupby("FLETERA").size().reset_index(name="PEDIDOS")
    )
    
    # El factor 1.5 asegura que siempre haya espacio arriba para el número
    max_t = max(df_transito["PEDIDOS"].max() * 1.5, 5) if not df_transito.empty else 10
    
    chart_t = alt.Chart(df_transito).encode(x=alt.X("FLETERA:N", title="Paquetería"))
    
    bars_t = chart_t.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        y=alt.Y("PEDIDOS:Q", title="Pedidos", scale=alt.Scale(domain=[0, max_t])),
        color=alt.value("#FFC107")
    )
    
    text_t = chart_t.mark_text(
        align='center', baseline='bottom', dy=ESPACIADO_DY,
        fontSize=TAMANO_TEXTO, fontWeight='bold', color='white'
    ).encode(
        y=alt.Y("PEDIDOS:Q"),
        text=alt.Text("PEDIDOS:Q")
    )
    
    g1.markdown("<h4 style='color:yellow; text-align:center;'>En tránsito</h4>", unsafe_allow_html=True)
    g1.altair_chart((bars_t + text_t).properties(height=320), use_container_width=True)
    
    
    # --- 2. RETRASADOS ---
    df_retrasados = (
        df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO"]
        .groupby("FLETERA").size().reset_index(name="PEDIDOS")
    )
    
    max_r = max(df_retrasados["PEDIDOS"].max() * 1.5, 5) if not df_retrasados.empty else 10
    
    chart_r = alt.Chart(df_retrasados).encode(x=alt.X("FLETERA:N", title="Paquetería"))
    
    bars_r = chart_r.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        y=alt.Y("PEDIDOS:Q", title="Pedidos", scale=alt.Scale(domain=[0, max_r])),
        color=alt.value("#F44336")
    )
    
    text_r = chart_r.mark_text(
        align='center', baseline='bottom', dy=ESPACIADO_DY,
        fontSize=TAMANO_TEXTO, fontWeight='bold', color='white'
    ).encode(
        y=alt.Y("PEDIDOS:Q"),
        text=alt.Text("PEDIDOS:Q")
    )
    
    g2.markdown("<h4 style='color:#F44336; text-align:center;'>Retrasados</h4>", unsafe_allow_html=True)
    g2.altair_chart((bars_r + text_r).properties(height=320), use_container_width=True)
    
    st.divider()
    
    # -----------------------------------------------------
    # PEDIDOS ENTREGADOS CON RETRASO POR PAQUETERÍA (FECHA REAL)
    # --------------------------------------------------
    
    # === AJUSTES DE DISEÑO ===
    TAMANO_TEXTO_RETRASO = 14  # Ajusta este número a tu gusto
    ESPACIADO_RETRASO = -15    # Ajusta si el texto queda muy pegado a la barra
    # =========================
    
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
        # Calculamos el techo dinámico (30% extra) para que no se corte el número
        max_val = df_retraso_paquete["PEDIDOS_RETRASADOS"].max() * 1.3
        
        # Creamos la base del gráfico
        base_retraso = alt.Chart(df_retraso_paquete).encode(
            x=alt.X("FLETERA:N", title="Paquetería")
        )
        
        # Capa de barras
        bars_retraso = base_retraso.mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        ).encode(
            y=alt.Y("PEDIDOS_RETRASADOS:Q", 
                    title="Pedidos entregados con retraso", 
                    scale=alt.Scale(domain=[0, max_val])),
            tooltip=["FLETERA", "PEDIDOS_RETRASADOS"],
            color=alt.value("#F44336")  # Rojo
        )
        
        # Capa de texto (Los números grandes)
        text_retraso = base_retraso.mark_text(
            align='center',
            baseline='bottom',
            dy=ESPACIADO_RETRASO,
            fontSize=TAMANO_TEXTO_RETRASO,
            fontWeight='bold',
            color='white'
        ).encode(
            y=alt.Y("PEDIDOS_RETRASADOS:Q"),
            text=alt.Text("PEDIDOS_RETRASADOS:Q")
        )
        
        # Combinamos ambas capas
        graf_final = (bars_retraso + text_retraso).properties(height=320)
    
        st.altair_chart(graf_final, use_container_width=True)
    else:
        st.info("No hay entregas con retraso para mostrar con los filtros actuales.")
    
    st.divider()
    
    # --------------------------------------------------
    # GRÁFICO DE ESTATUS – CON NÚMEROS GRANDES
    # --------------------------------------------------
    
    # === AJUSTES DE DISEÑO (Cámbialos a tu gusto) ===
    TAMANO_TEXTO_EST = 14  # Tamaño de los números
    ESPACIADO_EST = -15    # Espacio hacia arriba
    # ===============================================
    
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
    
    # Cálculo dinámico del techo del gráfico (30% extra para que quepa el número)
    max_est = max(df_est["Cantidad"].max() * 1.3, 5)
    
    # Crear gráfico con capas
    base_est = alt.Chart(df_est).encode(
        x=alt.X("Estatus:N", title="Estatus", sort=["ENTREGADO", "EN TRANSITO", "RETRASADO"])
    )
    
    # Capa de barras
    bars_est = base_est.mark_bar(
        cornerRadiusTopLeft=6, 
        cornerRadiusTopRight=6
    ).encode(
        y=alt.Y("Cantidad:Q", title="Cantidad", scale=alt.Scale(domain=[0, max_est])),
        color=alt.Color("Color:N", scale=None), # Mantiene tus colores originales
        tooltip=["Estatus:N", "Cantidad:Q"]
    )
    
    # Capa de texto (Números grandes)
    text_est = base_est.mark_text(
        align='center',
        baseline='bottom',
        dy=ESPACIADO_EST,
        fontSize=TAMANO_TEXTO_EST,
        fontWeight='bold',
        color='white'
    ).encode(
        y=alt.Y("Cantidad:Q"),
        text=alt.Text("Cantidad:Q")
    )
    
    # Combinar capas y mostrar
    st.altair_chart((bars_est + text_est).properties(height=350), use_container_width=True)
    
    st.divider()
    
    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    st.markdown(
        """
        <div style="text-align:center; color: #888888; font-size: 12px; padding: 10px;">
            📦 0% de paquetes dañados emocionalmente durante la creación de este reporte.<br>
            © 2026 - Tu Dashboard de Operaciones | Design by Rigobertto Hernandez
        </div>
        """, 
        unsafe_allow_html=True
        )
    





























































































































































































































































