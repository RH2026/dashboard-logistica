import streamlit as st
import pandas as pd
import altair as alt
import time
import base64
import textwrap
import streamlit.components.v1 as components
import numpy as np
import datetime
import io
import os

# --- FUNCIÓN PARA CARGAR EL LOGO ---
def get_base64_bin(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

# CARGAMOS LA VARIABLE ANTES DE USARLA
logo_b64 = get_base64_bin("n1.png")# --- NUEVO PROTOCOLO DE IMPORTACIÓN PARA FPDF2 (BLOQUE ELITE) ---
# --- PROTOCOLO DE CONEXIÓN FINAL ---
try:
    from fpdf import FPDF
    PDF_READY = True
except (ImportError, ModuleNotFoundError):
    PDF_READY = False

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Distribucion y Logística Inteligente", layout="wide", initial_sidebar_state="collapsed")


# 2. ESTADOS DE SESIÓN
if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "splash_completado" not in st.session_state:
    st.session_state.splash_completado = False
if "motivo_splash" not in st.session_state:
    st.session_state.motivo_splash = "inicio"
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "principal"  # Controla qué sección del dashboard se ve
if "ultimo_movimiento" not in st.session_state:
    st.session_state.ultimo_movimiento = time.time() # Para control de inactividad
if "tabla_expandida" not in st.session_state:
    st.session_state.tabla_expandida = False


# --- 2. LÓGICA DE MÁRGENES Y ALTURA (Flecha visible y espacios respetados) ---
st.markdown("""
    <style>
        /* Margen general del dashboard */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        /* Ocultamos solo el footer (la marca de Streamlit) */
        footer {visibility: hidden;}
        
        /* ESPACIO DE BOTONES: Mantiene la cercanía profesional a la tabla */
        div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
            margin-bottom: -0.5rem !important;
        }
        
        /* ESPACIO DE DONITAS: Mantiene el despegue de los indicadores */
        div[data-testid="stHorizontalBlock"]:has(div[style*="text-align:center"]) {
            margin-bottom: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Altura dinámica según el botón presionado (Esto no cambia)
if st.session_state.tabla_expandida:
    h_dinamica = 850
else:
    h_dinamica = 200

#---------------------------------------------------

# Colores
color_fondo_nativo = "#0e1117" 
color_blanco = "#FFFFFF"
color_verde = "#00FF00" 
color_borde_gris = "#00ffa2"
# --------------------------------------------------
# 3. ESTILOS CSS (Corregido para NO ocultar la flecha)
# --------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap');
    
    .stApp {{ background-color: {color_fondo_nativo} !important; }}
    
    /* Mostrar flecha de sidebar pero ocultar decoradores innecesarios */
    header[data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
    footer {{ visibility: hidden !important; }}
    div[data-testid="stDecoration"] {{ display: none !important; }}

    /* Caja 3D Logística Sellada */
    .scene {{ width: 100%; height: 120px; perspective: 600px; display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }}
    .cube {{ width: 60px; height: 60px; position: relative; transform-style: preserve-3d; transform: rotateX(-20deg) rotateY(45deg); animation: move-pkg 6s infinite ease-in-out; }}
    .cube-face {{ position: absolute; width: 60px; height: 60px; background: #d2a679; border: 1.5px solid #b08d5c; box-shadow: inset 0 0 15px rgba(0,0,0,0.1); }}
    .cube-face::after {{ content: ''; position: absolute; top: 45%; width: 100%; height: 6px; background: rgba(0,0,0,0.15); }}
    
    .front  {{ transform: rotateY(0deg) translateZ(30px); }}
    .back   {{ transform: rotateY(180deg) translateZ(30px); }}
    .right  {{ transform: rotateY(90deg) translateZ(30px); }}
    .left   {{ transform: rotateY(-90deg) translateZ(30px); }}
    .top    {{ transform: rotateX(90deg) translateZ(30px); background: #e3bc94; }}
    .bottom {{ transform: rotateX(-90deg) translateZ(30px); background: #b08d5c; }}
    
    @keyframes move-pkg {{ 0%, 100% {{ transform: translateY(0px) rotateX(-20deg) rotateY(45deg); }} 50% {{ transform: translateY(-15px) rotateX(-20deg) rotateY(225deg); }} }}
    
    /* Login Form */
    .stForm {{ background-color: {color_fondo_nativo} !important; border: 1.5px solid {color_borde_gris} !important; border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .login-header {{ text-align: center; color: white; font-family: Arial; font-size: 24px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; }}
    input {{ font-family: 'Arial', monospace !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

# --------------------------------------------------
# 4. FLUJO DE PANTALLAS
# --------------------------------------------------

# --- 1. PREPARACIÓN DE RECURSOS (Asegúrate de tener esto al inicio) ---
import base64
import streamlit as st

def get_base64_file(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_b64 = get_base64_file("n1.png")

# --- 2. CASO A: LOGIN (ENSAMBLADO FINAL) ---
if not st.session_state.logueado:
    with placeholder.container():
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.markdown('<div style="height:10vh"></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                
                # --- SECCIÓN VISUAL: LOGO + ANIMACIÓN ---
                if logo_b64:
                    st.markdown(f'<div style="text-align:center;margin-bottom:20px;"><img src="data:image/png;base64,{logo_b64}" style="width:250px;mix-blend-mode:screen;display:block;margin:0 auto;"><div style="width:160px;height:2px;background:#00FFAA;margin:15px auto 5px auto;box-shadow:0 0 12px #00FFAA;animation:s 2.5s infinite ease-in-out;"></div><div style="font-family:monospace;color:#00FFAA;font-size:11px;letter-spacing:4px;animation:b 1.5s infinite;">Distribucion y Logística: Inteligente</div></div><style>@keyframes s{{0%,100%{{width:0%;opacity:0;}}50%{{width:80%;opacity:1;}}}}@keyframes b{{0%,100%{{opacity:1;}}50%{{opacity:0.3;}}}}</style>', unsafe_allow_html=True)
                
                # --- EL RESTO DEL FORMULARIO SE QUEDA IGUAL ---
                u_input = st.text_input("Usuario")
                c_input = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("INGRESAR", use_container_width=True):
                    usuarios = st.secrets["usuarios"]
                    if u_input in usuarios and str(usuarios[u_input]) == str(c_input):
                        st.session_state.logueado = True
                        st.session_state.usuario_actual = u_input
                        st.session_state.splash_completado = False
                        st.session_state.motivo_splash = "inicio"
                        st.rerun()
                    else:
                        st.error("Acceso Denegado")
    st.stop()

# CASO B: SPLASH SCREEN
elif not st.session_state.splash_completado:
    with placeholder.container():
        
        # --- DEFINICIÓN GLOBAL (Para que no de NameError) ---
        usuario = st.session_state.usuario_actual.capitalize() if st.session_state.usuario_actual else "Usuario"
        color_cyan = "#FFFFFF" # Usamos el Cyan que nos gustó
        
        # Definición de mensajes según el motivo
        if st.session_state.motivo_splash == "logout":
            mensajes = [
                f"Cerrando sesión, <span style='color:{color_cyan};'>{usuario}</span>...", 
                "Guardando cambios...", 
                "Conexión con Nexion terminada!"
            ]
            c_caja = "#FF4B4B"
        else:
            # Mensajes dinámicos de bienvenida
            mensajes = [
                f"¡Hola de vuelta, <span style='color:{color_cyan};'>{usuario}</span>!",
                "Actualizando base de datos...",
                "Sincronizando estatus de envíos...",
                "Accediendo al sistema..."
            ]
            c_caja = "#d2a679"

        # Contenedor vacío para actualizar el texto sin refrescar toda la página
        splash_placeholder = st.empty()

        for i, msg in enumerate(mensajes):
            splash_placeholder.markdown(f"""
                <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0e1117; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div class="scene">
                        <div class="cube" style="width:80px; height:80px; animation: move-pkg 3s infinite linear;">
                            <div class="cube-face front"  style="width:80px; height:80px; background:{c_caja}; transform: rotateY(0deg) translateZ(40px);"></div>
                            <div class="cube-face back"   style="width:80px; height:80px; background:{c_caja}; transform: rotateY(180deg) translateZ(40px);"></div>
                            <div class="cube-face right"  style="width:80px; height:80px; background:{c_caja}; transform: rotateY(90deg) translateZ(40px);"></div>
                            <div class="cube-face left"   style="width:80px; height:80px; background:{c_caja}; transform: rotateY(-90deg) translateZ(40px);"></div>
                            <div class="cube-face top"    style="width:80px; height:80px; background:#e3bc94; transform: rotateX(90deg) translateZ(40px);"></div>
                            <div class="cube-face bottom" style="width:80px; height:80px; background:#b08d5c; transform: rotateX(-90deg) translateZ(40px);"></div>
                        </div>
                    </div>
                    <div style="color:#00FFAA; font-family:'monospace'; margin-top:25px; letter-spacing:2px; text-transform:none; font-size: 14px; font-weight: normal;">{msg}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Tiempo entre cada mensaje (ajustable)
            time.sleep(0.8 if i < len(mensajes)-1 else 1.0)
        
        # Lógica de cierre de sesión
        if st.session_state.motivo_splash == "logout":
            st.session_state.logueado = False
            st.session_state.usuario_actual = None
            st.session_state.pagina = "principal"
            st.session_state.motivo_splash = "inicio"
            st.cache_data.clear()
        
        st.session_state.splash_completado = True
        st.rerun()
    st.stop()

# 3. CONTENIDO PRIVADO (DASHBOARD)
else:      
    # --- MOTOR DE DATOS ---
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
            if pd.notna(row["FECHA DE ENTREGA REAL"]): return "ENTREGADO"
            if pd.notna(row["PROMESA DE ENTREGA"]) and row["PROMESA DE ENTREGA"] < hoy: return "RETRASADO"
            return "EN TRANSITO"
        
        df["ESTATUS_CALCULADO"] = df.apply(calcular_estatus, axis=1)
        return df

    df = cargar_datos()

    # BARRA LATERAL
    
    # --- RECONEXIÓN DE LOGO NEXION (FUERZA BRUTA) ---
    import base64
    def get_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    try:
        logo_base64 = get_base64("n1.png")
        # Inyectamos el logo como un bloque HTML real, no como fondo de CSS
        st.sidebar.markdown(
            f"""
            <div style="text-align: center; padding: 10px 0px;">
                <img src="data:image/png;base64,{logo_base64}" width="220">
            </div>
            <style>
                /* Esto elimina el espacio vacío que Streamlit deja arriba por defecto */
                [data-testid="stSidebarNav"] {{
                    padding-top: 20px !important;
                }}
            </style>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.sidebar.warning("Logo n1.png no detectado en el radar.")
    
    st.sidebar.markdown(f'<div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-top:12px;margin-left:-8px;"><svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="4" stroke="#00FFAA" stroke-width="1.8"/><path d="M4 20c0-3.5 3.6-6 8-6s8 2.5 8 6" stroke="#00FFAA" stroke-width="1.8" stroke-linecap="round"/></svg><span style="color:#999;font-size:16px;">Sesión: <span style="color:#00FFAA;font-weight:500;">{st.session_state.usuario_actual}</span></span></div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.splash_completado = False 
        st.session_state.motivo_splash = "logout"
        st.rerun()

        
    # --------------------------------------------------
    # 🛣️ INICIO DE LA LÓGICA DE NAVEGACIÓN
    # --------------------------------------------------
    if st.session_state.pagina == "principal":
        # A partir de aquí pondremos todo lo del Dashboard Principal
        # --------------------------------------------------
        # TÍTULO Y ENCABEZADO
        # --------------------------------------------------
        st.markdown("<style>@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}</style>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align:center; font-family:"Inter",sans-serif; padding:5px 0;'>
                <svg style='animation:float 3s infinite; margin-bottom:2px;' width='45' height='45' viewBox='0 0 24 24' fill='none' stroke='#00FFAA' stroke-width='1.5' xmlns='http://www.w3.org/2000/svg'><path d='M3 7L12 2L21 7L12 12L3 7ZM3 7V17L12 22L21 17V7M12 12V22M7.5 4.8L16.5 9.3' opacity='0.7'/></svg>
                <h1 style='color:white; font-weight:800; font-size:42px; margin:0; letter-spacing:-1.5px; line-height:1;'>TRACKING <span style='color:#FFFFFF;'>INDICATOR</span></h1>
                <p style='color:#94a3b8; font-size:16px; margin:10px 0 15px 0; font-weight:400;'>Logística & Rendimiento de Paqueterías</p>
                <div style='height:3px; width:60px; background:#00FFAA; margin:0 auto; border-radius:10px;'></div>
            </div>
        """, unsafe_allow_html=True)
       
        st.divider()
           
        # 1. FUNCIÓN DE LIMPIEZA
        def limpiar_filtros():
            st.session_state.filtro_cliente_actual = ""
            st.session_state.filtro_cliente_input = ""
            f_min_res = df["FECHA DE ENVÍO"].min()
            f_max_res = df["FECHA DE ENVÍO"].max()
            st.session_state["fecha_filtro"] = (f_min_res, f_max_res)
            st.session_state["fletera_filtro"] = ""
            st.rerun()
    
        if st.sidebar.button("Limpiar Filtros", use_container_width=True):
            limpiar_filtros()
    
        st.sidebar.markdown("---")
                
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
                
        # 4. SELECTOR DE FLETERA
        fletera_sel = st.sidebar.selectbox(
            "Selecciona Fletera",
            options=[""] + sorted(df["FLETERA"].dropna().unique()),
            index=0,
            key="fletera_filtro"
        )
        # --------------------------------------------------
        # APLICACIÓN DE FILTROS (CORREGIDO Y REFORZADO)
        # --------------------------------------------------
        df_filtrado = df.copy()
        
        # 1. Limpiamos el valor buscado para evitar errores de espacios
        valor_buscado = str(st.session_state.filtro_cliente_actual).strip().lower()
    
        # PRIORIDAD 1: Si el usuario escribió algo en el buscador
        if valor_buscado != "":
            # Convertimos las columnas a texto y quitamos el .0 que pone Excel a veces
            col_cliente_txt = df_filtrado["NO CLIENTE"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lower()
            col_guia_txt = df_filtrado["NÚMERO DE GUÍA"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lower()
            
            # Creamos la máscara de búsqueda
            mask_cliente = col_cliente_txt.str.contains(valor_buscado, na=False)
            mask_guia = col_guia_txt.str.contains(valor_buscado, na=False)
            
            # Filtramos (Si coincide con cliente O con guía)
            df_filtrado = df_filtrado[mask_cliente | mask_guia]
            
        # PRIORIDAD 2: Si el buscador está vacío, aplicamos fechas y fletera
        else:
            # Validación de fechas
            if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
                f_inicio, f_fin = rango_fechas
                f_ini_dt = pd.to_datetime(f_inicio)
                f_fin_dt = pd.to_datetime(f_fin)
                
                df_filtrado = df_filtrado[
                    (df_filtrado["FECHA DE ENVÍO"] >= f_ini_dt) & 
                    (df_filtrado["FECHA DE ENVÍO"] <= f_fin_dt)
                ]
            
            # Filtro de fletera
            if fletera_sel != "":
                df_filtrado = df_filtrado[df_filtrado["FLETERA"].astype(str).str.strip() == fletera_sel]
    
            # --------------------------------------------------
            # ACTUALIZACIÓN DE MÉTRICAS (Para que los círculos cambien)
            # --------------------------------------------------
            total = len(df_filtrado)
            entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
            en_transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
            retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()
    
        # --------------------------------------------------
        # CAJA DE BÚSQUEDA POR PEDIDO – TARJETAS + TIMELINE
        # --------------------------------------------------

              
        st.markdown("""
        <style>
        /* Animaciones con radio de borde corregido para que siempre sean círculos */
        @keyframes p-green { 0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); } 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); } }
        @keyframes p-blue { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }
        @keyframes p-orange { 0% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(249, 115, 22, 0); } 100% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0); } }
        @keyframes p-red { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }
        
        .dot-green { border-radius: 50% !important; animation: p-green 2s infinite; }
        .dot-blue { border-radius: 50% !important; animation: p-blue 2s infinite; }
        .dot-orange { border-radius: 50% !important; animation: p-orange 2s infinite; }
        .dot-red { border-radius: 50% !important; animation: p-red 2s infinite; }
        </style>
        """, unsafe_allow_html=True)
        
        pedido_buscar = st.text_input(
            "Status de Factura",
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
                    
                    # 1. Asegúrate de tener este bloque de Estilos CSS corregido antes de la búsqueda
                    st.markdown("""<style>@keyframes p-green { 0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); } 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); } } @keyframes p-blue { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } } @keyframes p-orange { 0% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(249, 115, 22, 0); } 100% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0); } } @keyframes p-red { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } } .dot-green { border-radius: 50% !important; animation: p-green 2s infinite; } .dot-blue { border-radius: 50% !important; animation: p-blue 2s infinite; } .dot-orange { border-radius: 50% !important; animation: p-orange 2s infinite; } .dot-red { border-radius: 50% !important; animation: p-red 2s infinite; }</style>""", unsafe_allow_html=True)
                    
                    # 2. Bloque de Lógica y Timeline (Dentro de tu bucle for)
                    f_envio_dt = pd.to_datetime(row.get("FECHA DE ENVÍO"), errors='coerce')
                    f_promesa_dt = pd.to_datetime(row.get("PROMESA DE ENTREGA"), errors='coerce')
                    f_real_dt = pd.to_datetime(row.get("FECHA DE ENTREGA REAL"), errors='coerce')
                    hoy_dt = pd.Timestamp.now().normalize()
                    entregado = pd.notna(f_real_dt)
                    
                    # Definición de animaciones y estados
                    if entregado:
                        t_fin, c_fin, anim_fin = "ENTREGADO", "#22c55e", "dot-green"
                        if f_real_dt <= f_promesa_dt:
                            t_medio, c_medio, anim_medio = "ENTREGADA EN TIEMPO", "#22c55e", "dot-green"
                        else:
                            t_medio, c_medio, anim_medio = "ENTREGADA CON RETRASO", "#ef4444", "dot-red"
                    else:
                        t_fin, c_fin, anim_fin = "EN ESPERA", "#374151", ""
                        if pd.notna(f_promesa_dt) and f_promesa_dt < hoy_dt:
                            t_medio, c_medio, anim_medio = "RETRASO", "#f97316", "dot-orange"
                        else:
                            t_medio, c_medio, anim_medio = "EN TRÁNSITO", "#3b82f6", "dot-blue"
                    
                    # Formateo de fechas
                    txt_f_envio = f_envio_dt.strftime('%d/%m/%Y') if pd.notna(f_envio_dt) else "S/D"
                    txt_f_promesa = f_promesa_dt.strftime('%d/%m/%Y') if pd.notna(f_promesa_dt) else "S/D"
                    txt_f_real = f_real_dt.strftime('%d/%m/%Y') if entregado else "PENDIENTE"
                    txt_f_actual = hoy_dt.strftime('%d/%m/%Y')
                    
                    # HTML en UNA SOLA LÍNEA para renderizado óptimo
                    html_timeline = f'<div style="background:#111827;padding:25px;border-radius:12px;border:1px solid #374151;margin-top:15px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;width:100%;"><div style="position:absolute;top:20px;left:10%;right:10%;height:6px;background:#374151;z-index:0;"></div><div style="text-align:center;z-index:1;width:25%;"><div class="dot-green" style="width:40px;height:40px;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">ENVIADO</div><div style="color:gray;font-size:10px;">{txt_f_envio}</div></div><div style="text-align:center;z-index:1;width:25%;"><div class="dot-green" style="width:40px;height:40px;background:#22c55e;margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">FECHA ACTUAL</div><div style="color:gray;font-size:10px;">{txt_f_actual}</div></div><div style="text-align:center;z-index:1;width:25%;"><div class="{anim_medio}" style="width:40px;height:40px;background:{c_medio};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_medio}</div><div style="color:gray;font-size:10px;"><span style="color:#22c55e;">PROMESA</span> {txt_f_promesa}</div></div><div style="text-align:center;z-index:1;width:25%;"><div class="{anim_fin}" style="width:40px;height:40px;border-radius:50%;background:{c_fin};margin:0 auto 10px auto;border:4px solid #111827;"></div><div style="color:white;font-size:11px;font-weight:bold;">{t_fin}</div><div style="color:gray;font-size:10px;">FECHA REAL: {txt_f_real}</div></div></div></div>'
                    
                    st.markdown(html_timeline, unsafe_allow_html=True)
                    
                                       
                    
                    ## --- PASO 1: INYECTAR EL ADN (ESTILOS OCULTOS) ---
                    st.markdown("<style>.elite-card{transition:all 0.4s ease;display:flex;flex-direction:column;justify-content:space-between;}.elite-card:hover{transform:translateY(-8px);box-shadow:0 20px 40px rgba(0,0,0,0.7)!important;border:1px solid rgba(255,255,255,0.25)!important;background:rgba(255,255,255,0.04)!important;}</style>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)

                    # Altura común para simetría total
                    h_size = "360px"
                    
                    # --- TARJETA 1: EXPEDICIÓN (CON FLETERA) ---
                    with c1:
                        costo = f"${float(row.get('COSTO DE LA GUÍA', 0)):,.2f}"
                        html_c1 = f"<div class='elite-card' style='background:#11141C;padding:24px;border-radius:20px;border:1px solid rgba(255,255,255,0.08);border-top:4px solid #38bdf8;min-height:{h_size};'><div style='display:flex;align-items:center;margin-bottom:15px;'><div style='background:#38bdf822;padding:10px;border-radius:12px;margin-right:15px;'>📦</div><div style='color:white;font-weight:800;font-size:14px;'>DATOS DEL CLIENTE</div></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Tracking</span><span style='color:#38bdf8;font-size:13px;font-weight:800;'>{row.get('NÚMERO DE GUÍA','—')}</span></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Cliente</span><span style='color:#e2e8f0;font-size:13px;'>{row.get('NOMBRE DEL CLIENTE','—')}</span></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Destino</span><span style='color:#e2e8f0;font-size:13px;'>{row.get('DESTINO','—')}</span></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Fletera</span><span style='color:#fbbf24;font-size:13px;font-weight:700;'>{row.get('FLETERA','—')}</span></div><div style='margin-top:auto;text-align:right;'><div style='color:#64748b;font-size:12px;font-weight:800;'>Costo Guia</div><div style='color:#00FFAA;font-size:26px;font-weight:900;'>{costo}</div></div></div>"
                        st.markdown(html_c1, unsafe_allow_html=True)
                    
                    # --- TARJETA 2: TIEMPOS ---
                    with c2:
                        retraso = row.get('DIAS_RETRASO', 0)
                        color_t = "#fb7185" if retraso > 0 else "#00FFAA"
                        html_c2 = f"<div class='elite-card' style='background:#11141C;padding:24px;border-radius:20px;border:1px solid rgba(255,255,255,0.08);border-top:4px solid #fbbf24;min-height:{h_size};'><div style='display:flex;align-items:center;margin-bottom:15px;'><div style='background:#fbbf2422;padding:10px;border-radius:12px;margin-right:15px;'>⏱️</div><div style='color:white;font-weight:800;font-size:14px;'>TIEMPOS</div></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Fecha de Envio</span><span style='color:#e2e8f0;font-size:13px;'>{txt_f_envio}</span></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Promesa de entrega</span><span style='color:#e2e8f0;font-size:13px;'>{txt_f_promesa}</span></div><div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Fecha de entrega</span><span style='color:#00FFAA;font-size:13px;'>{txt_f_real}</span></div><div style='margin-top:auto;background:rgba(255,255,255,0.03);padding:15px;border-radius:12px;border-left:4px solid {color_t};'><div style='color:{color_t};font-size:10px;font-weight:800;'>DESVIACIÓN</div><div style='color:white;font-size:22px;font-weight:900;'>{retraso} DÍAS</div></div></div>"
                        st.markdown(html_c2, unsafe_allow_html=True)
                    
                    # --- TARJETA 3: ESTADO ---
                    with c3:
                        est = row.get('ESTATUS_CALCULADO', '—')
                        color_e = "#00FFAA" if est == "ENTREGADO" else "#fb7185" if est == "RETRASADO" else "#3b82f6"
                        html_c3 = f"<div class='elite-card' style='background:#11141C;padding:24px;border-radius:20px;border:1px solid rgba(255,255,255,0.08);border-top:4px solid #a855f7;min-height:{h_size};'><div style='display:flex;align-items:center;margin-bottom:15px;'><div style='background:#a855f722;padding:10px;border-radius:12px;margin-right:15px;'>📊</div><div style='color:white;font-weight:800;font-size:14px;'>ESTATUS</div></div><div style='display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Estatus</span><span style='color:{color_e};font-size:13px;font-weight:800;'>{est}</span></div><div style='display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.03);'><span style='color:#64748b;font-size:14px;font-weight:700;text-transform:uppercase;'>Prioridad</span><span style='color:#e2e8f0;font-size:13px;'>{row.get('PRIORIDAD','NORMAL')}</span></div><div style='margin-top:auto;'><div style='color:#64748b;font-size:14px;font-weight:700;margin-bottom:8px;'>NOTAS</div><div style='background:rgba(0,0,0,0.3);padding:12px;border-radius:10px;border:1px dashed rgba(255,255,255,0.1);color:#cbd5e1;font-size:12px;min-height:90px;'>{row.get('COMENTARIOS','Sin incidencias.')}</div></div></div>"
                        st.markdown(html_c3, unsafe_allow_html=True)
        
               

        # --- 1. CÁLCULO DE MÉTRICAS ---
        st.markdown("<style>.elite-card{transition:all 0.4s ease;padding:20px;border-radius:20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);text-align:center;margin-bottom:10px;}.elite-card:hover{transform:translateY(-8px);box-shadow:0 20px 40px rgba(0,0,0,0.7)!important;border:1px solid rgba(255,255,255,0.25)!important;}</style>", unsafe_allow_html=True)
        
        total = int(len(df_filtrado))
        entregados = int((df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum())
        en_transito = int((df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum())
        retrasados = int((df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum())

        # --- 2. COLORES ---
        COLOR_AVANCE_ENTREGADOS = "#00FFAA" 
        COLOR_AVANCE_TRANSITO   = "#38bdf8" 
        COLOR_AVANCE_RETRASADOS = "#fb7185" 
        COLOR_TOTAL             = "#fbbf24" 
        COLOR_FALTANTE          = "#262730" 

        # --- 3. FUNCIÓN CORREGIDA (Sintaxis simplificada para evitar el TypeError) ---
        def donut_con_numero(avance, total_val, color_avance, color_faltante):
            porcentaje = int((avance / total_val) * 100) if total_val > 0 else 0
            
            # DataFrame con tipos de datos limpios
            data_dona = pd.DataFrame({
                "segmento": ["A", "B"], 
                "valor": [float(avance), float(max(total_val - avance, 0))]
            })
            
            # 1. El arco (Dona) con sintaxis explícita
            donut = alt.Chart(data_dona).mark_arc(innerRadius=52, outerRadius=65, cornerRadius=10).encode(
                theta=alt.Theta(field="valor", type="quantitative"),
                color=alt.Color(field="segmento", type="nominal", 
                                scale=alt.Scale(domain=["A", "B"], range=[color_avance, color_faltante]), 
                                legend=None),
                tooltip=alt.value(None) # Forma segura de desactivar tooltip
            )
            
            # 2. Número central
            texto_n = alt.Chart(pd.DataFrame({"t": [str(avance)]})).mark_text(
                align="center", baseline="middle", fontSize=28, fontWeight=800, dy=-6, color="white"
            ).encode(text=alt.Text(field="t", type="nominal"))
            
            # 3. Porcentaje inferior
            texto_p = alt.Chart(pd.DataFrame({"t": [f"{porcentaje}%"]})).mark_text(
                align="center", baseline="middle", fontSize=12, fontWeight=400, dy=18, color="#94a3b8"
            ).encode(text=alt.Text(field="t", type="nominal"))
            
            return (donut + texto_n + texto_p).properties(width=180, height=180).configure_view(strokeOpacity=0)

        # --- 4. RENDERIZADO DE COLUMNAS ---
        st.markdown("<div style='background:rgba(255,255,255,0.02);padding:15px;border-radius:15px;border-left:5px solid #38bdf8;margin-bottom:25px;'><span style='color:white;font-size:20px;font-weight:800;letter-spacing:1.5px;'>CONSOLA GLOBAL DE RENDIMIENTO</span></div>", unsafe_allow_html=True)
    
        c1, c2, c3, c4 = st.columns(4)
        l_style = "color:#94a3b8;font-size:14px;font-weight:800;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;"

        with c1:
            st.markdown(f"<div class='elite-card'><p style='{l_style}'>Total Pedidos</p>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(total, total, COLOR_TOTAL, COLOR_FALTANTE), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
        with c2:
            st.markdown(f"<div class='elite-card'><p style='{l_style}'>Entregados</p>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(entregados, total, COLOR_AVANCE_ENTREGADOS, COLOR_FALTANTE), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
        with c3:
            st.markdown(f"<div class='elite-card'><p style='{l_style}'>En Tránsito</p>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(en_transito, total, COLOR_AVANCE_TRANSITO, COLOR_FALTANTE), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
        with c4:
            st.markdown(f"<div class='elite-card'><p style='{l_style}'>Retrasados</p>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(retrasados, total, COLOR_AVANCE_RETRASADOS, COLOR_FALTANTE), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # --------------------------------------------------
        # TABLA DE ENVÍOS – DISEÑO PREMIUM ELITE (SIN CAJA)
        # --------------------------------------------------
        # Espaciador para separar de las donas
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        
        # Estructura de 3 columnas para centrado perfecto
        col_izq, col_centro, col_der = st.columns([2, 3, 2])
        
        with col_izq:
            btn_c1, btn_c2 = st.columns(2)
            with btn_c1:
                if st.button("BD Completa", use_container_width=True, key="btn_full_v3"):
                    st.session_state.tabla_expandida = True
                    st.rerun()
            with btn_c2:
                if st.button("BD Vista Normal", use_container_width=True, key="btn_norm_v3"):
                    st.session_state.tabla_expandida = False
                    st.rerun()
        
        with col_centro:
            # Título con padding-bottom para empujar la tabla hacia abajo
            st.markdown("""
                <div style="text-align:center; padding-bottom: 25px;">
                    <span style="color:white; font-size:24px; font-weight:800; letter-spacing:3px; text-transform:uppercase;">
                        REGISTRO DE ENVIOS
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with col_der:
            # Columna de equilibrio
            st.write("")
        
        # Lógica de altura dinámica
        h_dinamica = 850 if st.session_state.get('tabla_expandida', False) else 400
        
        # Preparación de datos final
        df_visual = df_filtrado.copy()
        hoy_t = pd.Timestamp.today().normalize()
        
        # Cálculos de tiempo para las barras de progreso y métricas
        df_visual["DIAS_TRANSCURRIDOS"] = ((df_visual["FECHA DE ENTREGA REAL"].fillna(hoy_t) - df_visual["FECHA DE ENVÍO"]).dt.days)
        df_visual["DIAS_RETRASO_VAL"] = ((df_visual["FECHA DE ENTREGA REAL"].fillna(hoy_t) - df_visual["PROMESA DE ENTREGA"]).dt.days).clip(lower=0)
        
        # RENDERIZADO DE TABLA ULTRA MODERNA
        st.dataframe(
            df_visual,
            column_config={
                "ESTATUS_CALCULADO": st.column_config.SelectboxColumn(
                    "ESTATUS",
                    options=["ENTREGADO", "EN TRANSITO", "RETRASADO"],
                    required=True,
                ),
                "DIAS_TRANSCURRIDOS": st.column_config.NumberColumn(
                    "DÍAS TRANSCURRIDOS",
                    format="%d d"
                ),
                "DIAS_RETRASO_VAL": st.column_config.ProgressColumn(
                    "RETRASO",
                    format="%d d",
                    min_value=0,
                    max_value=15,
                    color="red",
                ),
                "COSTO DE LA GUÍA": st.column_config.NumberColumn(
                    "COSTO DE LA GUÍA",
                    format="$ %.2f",
                ),
                "FECHA DE ENVÍO": st.column_config.DateColumn("FECHA DE ENVÍO", format="DD/MM/YYYY"),
                "PROMESA DE ENTREGA": st.column_config.DateColumn("PROMESA DE ENTREGA", format="DD/MM/YYYY"),
                "FECHA DE ENTREGA REAL": st.column_config.DateColumn("FECHA DE ENTREGA REAL", format="DD/MM/YYYY"),
                "NÚMERO DE GUÍA": "NÚMERO DE GUÍA",
                "NOMBRE DEL CLIENTE": "NOMBRE DEL CLIENTE",
                "FLETERA": "FLETERA",
                "DESTINO": "DESTINO",
                "NO CLIENTE": "NO CLIENTE"
            },
            hide_index=True,
            use_container_width=True,
            height=h_dinamica
        )
        
        st.divider()
        # --------------------------------------------------
        # GRÁFICOS DE BARRAS POR PAQUETERÍA (CON ETIQUETAS)
        # --------------------------------------------------
        # --- 📦 PANEL DE CONTROL DE OPERACIONES (CON ETIQUETAS DE DATOS) ---
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.02); padding: 12px 20px; border-radius: 8px; border-left: 4px solid #38bdf8; margin-top: 30px; margin-bottom: 25px;'>
                <span style='color: #e2e8f0; font-weight: 700; font-size: 15px; letter-spacing: 1.5px;'>🚀 ESTADO DE CARGA EN TIEMPO REAL</span>
            </div>
        """, unsafe_allow_html=True)

        color_transito = "#fbbf24" 
        color_retraso = "#fb7185"  
        
        col1, col2 = st.columns(2)

        # --- COLUMNA 1: EN TRÁNSITO ---
        with col1:
            df_t = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO"].groupby("FLETERA").size().reset_index(name="CANTIDAD")
            total_t = df_t["CANTIDAD"].sum()
            
            st.markdown(f"""
                <div style='background: linear-gradient(90deg, rgba(251, 191, 36, 0.1) 0%, transparent 100%); padding: 15px; border-radius: 10px; border-bottom: 2px solid {color_transito}33;'>
                    <p style='margin:0; color:{color_transito}; font-size:12px; font-weight:800; text-transform:uppercase;'>🟡 En Movimiento</p>
                    <h2 style='margin:0; color:white; font-size:32px;'>{total_t} <span style='font-size:14px; color:#94a3b8;'>pedidos</span></h2>
                </div>
            """, unsafe_allow_html=True)

            if not df_t.empty:
                # Base del gráfico
                base_t = alt.Chart(df_t).encode(
                    x=alt.X("CANTIDAD:Q", title=None, axis=None),
                    y=alt.Y("FLETERA:N", title=None, sort='-x', axis=alt.Axis(labelColor='white', labelFontSize=12))
                )
                
                # Capa de barras
                bars_t = base_t.mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5, size=18, color=color_transito)
                
                # Capa de números (ETIQUETAS)
                text_t = base_t.mark_text(align='left', baseline='middle', dx=8, color='white', fontWeight=700, fontSize=13).encode(text="CANTIDAD:Q")
                
                st.altair_chart((bars_t + text_t).properties(height=200).configure_view(strokeOpacity=0), use_container_width=True)
            else:
                st.markdown(f"<div style='padding:40px; text-align:center; color:#475569;'>Sin carga activa</div>", unsafe_allow_html=True)

        # --- COLUMNA 2: RETRASADOS ---
        with col2:
            df_r = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO"].groupby("FLETERA").size().reset_index(name="CANTIDAD")
            total_r = df_r["CANTIDAD"].sum()
            
            st.markdown(f"""
                <div style='background: linear-gradient(90deg, rgba(251, 113, 133, 0.1) 0%, transparent 100%); padding: 15px; border-radius: 10px; border-bottom: 2px solid {color_retraso}33;'>
                    <p style='margin:0; color:{color_retraso}; font-size:12px; font-weight:800; text-transform:uppercase;'>🔴 Alerta de Retraso</p>
                    <h2 style='margin:0; color:white; font-size:32px;'>{total_r} <span style='font-size:14px; color:#94a3b8;'>pedidos</span></h2>
                </div>
            """, unsafe_allow_html=True)

            if not df_r.empty:
                # Base del gráfico
                base_r = alt.Chart(df_r).encode(
                    x=alt.X("CANTIDAD:Q", title=None, axis=None),
                    y=alt.Y("FLETERA:N", title=None, sort='-x', axis=alt.Axis(labelColor='white', labelFontSize=12))
                )
                
                # Capa de barras
                bars_r = base_r.mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5, size=18, color=color_retraso)
                
                # Capa de números (ETIQUETAS)
                text_r = base_r.mark_text(align='left', baseline='middle', dx=8, color='white', fontWeight=700, fontSize=13).encode(text="CANTIDAD:Q")
                
                st.altair_chart((bars_r + text_r).properties(height=200).configure_view(strokeOpacity=0), use_container_width=True)
            else:
                st.markdown(f"<div style='padding:40px; text-align:center; color:#059669; font-weight:bold;'>✓ Operación al día</div>", unsafe_allow_html=True)
               
        # --------------------------------------------------
        # GRÁFICO EXCLUSIVO: RETRASO PROMEDIO (DÍAS) + NOTA
        # --------------------------------------------------
        # --- ANÁLISIS DE DESVIACIÓN (DISEÑO SUPER ELITE) ---
        
        # Colores de la marca OPS MONITOR
        verde_esmeralda = "#059669"
        naranja_ambar = "#d97706"
        rojo_coral = "#fb7185"

        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.02); padding: 12px 20px; border-radius: 8px; border-left: 4px solid {naranja_ambar}; margin-bottom: 20px;'>
                <span style='color: #e2e8f0; font-weight: 700; font-size: 15px; letter-spacing: 1.5px;'>⏱️ RETRASO PROMEDIO POR PAQUETERÍA</span>
            </div>
        """, unsafe_allow_html=True)

        df_entregados_p = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        
        if not df_entregados_p.empty:
            # Cálculo de desviación en días
            df_entregados_p["DIAS_DESVIACION"] = (df_entregados_p["FECHA DE ENTREGA REAL"] - df_entregados_p["PROMESA DE ENTREGA"]).dt.days
            df_prom = df_entregados_p.groupby("FLETERA")["DIAS_DESVIACION"].mean().reset_index(name="PROMEDIO")
            
            # Asignación de colores segura para evitar TypeErrors
            df_prom["COLOR_HEX"] = df_prom["PROMEDIO"].apply(lambda x: verde_esmeralda if x <= 0 else naranja_ambar)

            # Gráfico Horizontal Premium
            bars = alt.Chart(df_prom).mark_bar(
                cornerRadiusTopRight=10, 
                cornerRadiusBottomRight=10,
                size=22
            ).encode(
                y=alt.Y("FLETERA:N", title=None, sort='-x', axis=alt.Axis(labelColor='white', labelFontSize=12)),
                x=alt.X("PROMEDIO:Q", title="Días Promedio", axis=alt.Axis(gridOpacity=0.05, labelColor='#94a3b8')),
                color=alt.Color("COLOR_HEX:N", scale=None)
            )
            
            # Etiquetas de datos con fuente bold
            text_labels = bars.mark_text(
                align='left', baseline='middle', dx=10, fontSize=14, fontWeight=700, color='white'
            ).encode(text=alt.Text("PROMEDIO:Q", format='.1f'))
            
            st.altair_chart((bars + text_labels).properties(height=400).configure_view(strokeOpacity=0), use_container_width=True)

            # --- DIAGNÓSTICO CON CORRECCIÓN DE DATETIME ---
            peor_fletera = df_prom.sort_values(by="PROMEDIO", ascending=False).iloc[0]
            # CORRECCIÓN AQUÍ: Usamos datetime.date.today()
            fecha_actual = datetime.date.today().strftime('%d/%m/%Y')
            
            if peor_fletera["PROMEDIO"] > 0:
                st.markdown(f"""
                    <div style='background: rgba(251, 113, 133, 0.1); border: 1px solid {rojo_coral}; padding: 20px; border-radius: 12px; margin-top: 20px;'>
                        <p style='margin:0; color:{rojo_coral}; font-weight:800; font-size:14px; text-transform:uppercase;'>🔍 Diagnóstico Crítico al {fecha_actual}</p>
                        <p style='margin:10px 0 0 0; color:white; font-size:16px;'>
                            El mayor impacto en la logística lo tiene <b>{peor_fletera['FLETERA']}</b> 
                            con un retraso de <span style='color:{rojo_coral}; font-weight:bold;'>{peor_fletera['PROMEDIO']:.1f} días</span>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='background: rgba(5, 150, 105, 0.1); border: 1px solid {verde_esmeralda}; padding: 20px; border-radius: 12px; margin-top: 20px;'>
                        <p style='margin:0; color:{verde_esmeralda}; font-weight:800; font-size:14px; text-transform:uppercase;'>✨ Reporte de Excelencia al {fecha_actual}</p>
                        <p style='margin:10px 0 0 0; color:white; font-size:16px;'>
                            Operación impecable: Todas las entregas están <b>a tiempo o adelantadas</b>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
        # --------------------------------------------------
        # RANKING DE CALIDAD: MEJOR A PEOR FLETERA (MENOS FALLOS A MÁS)
        # --------------------------------------------------
        # --- RANKING DE CALIDAD (DISEÑO ELITE) ---
        
        # Estética de colores de la central de monitoreo
        color_perfecto = "#059669"  # Esmeralda (Cero fallos)
        color_con_fallo = "#fb7185" # Coral/Rojo (Con retrasos)

        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.02); padding: 12px 20px; border-radius: 8px; border-left: 4px solid #00FFAA; margin-top: 30px; margin-bottom: 20px;'>
                <span style='color: #e2e8f0; font-weight: 700; font-size: 15px; letter-spacing: 1.5px;'>🏆 RANKING DE CALIDAD: INCIDENCIAS POR FLETERA</span>
            </div>
        """, unsafe_allow_html=True)

        # 1. Procesamiento de incidencias
        df_entregas_tarde = df_filtrado[
            (df_filtrado["FECHA DE ENTREGA REAL"].notna()) & 
            (df_filtrado["FECHA DE ENTREGA REAL"] > df_filtrado["PROMESA DE ENTREGA"])
        ].copy()

        df_ranking = df_entregas_tarde.groupby("FLETERA").size().reset_index(name="FALLOS")
        todas_f = pd.DataFrame(df_filtrado["FLETERA"].unique(), columns=["FLETERA"])
        df_rk = pd.merge(todas_f, df_ranking, on="FLETERA", how="left").fillna(0)

        if not df_rk.empty:
            # Asignación de colores segura (Elite Style)
            df_rk["COLOR_HEX"] = df_rk["FALLOS"].apply(lambda x: color_perfecto if x == 0 else color_con_fallo)

            # 2. Gráfico Vertical Premium
            chart_base = alt.Chart(df_rk).encode(
                x=alt.X("FLETERA:N", title=None, sort='y', axis=alt.Axis(labelAngle=-45, labelColor='white', labelFontSize=11)),
                y=alt.Y("FALLOS:Q", title=None, axis=alt.Axis(gridOpacity=0.05, labelColor='#94a3b8')),
                color=alt.Color("COLOR_HEX:N", scale=None)
            )

            bars = chart_base.mark_bar(
                cornerRadiusTopLeft=10, 
                cornerRadiusTopRight=10,
                size=40
            )

            # Etiquetas de datos (Los números arriba de las barras)
            labels = chart_base.mark_text(
                align='center', baseline='bottom', dy=-10, fontSize=15, fontWeight=700, color='white'
            ).encode(text=alt.Text("FALLOS:Q", format='d'))

            st.altair_chart((bars + labels).properties(height=400).configure_view(strokeOpacity=0), use_container_width=True)
            
            # Guía de lectura rápida
            st.markdown(f"""
                <p style='text-align:center; color:#94a3b8; font-size:12px; font-style:italic;'>
                    <span style='color:{color_perfecto};'>●</span> <b>Cero Incidencias</b> | 
                    <span style='color:{color_con_fallo};'>●</span> <b>Con Pedidos Tarde</b> <br>
                    Las fleteras a la izquierda son las de mayor confianza operativa.
                </p>
            """, unsafe_allow_html=True)
        else:
            st.info("No se detectaron entregas fuera de tiempo en el periodo actual.")
        
        # --------------------------------------------------
        # SECCIÓN UNIFICADA: ANÁLISIS DE EXPERIENCIA (LUPA)
        # --------------------------------------------------
        # --- ANÁLISIS POR PAQUETERÍA: LUPA DE EXPERIENCIA (NIVEL ELITE) ---
        
        # Estética de colores OPS MONITOR
        color_entrega_ok = "#059669" # Esmeralda (A tiempo o antes)
        color_entrega_late = "#fb7185" # Coral (Retraso)

        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.02); padding: 12px 20px; border-radius: 8px; border-left: 4px solid #38bdf8; margin-top: 30px; margin-bottom: 20px;'>
                <span style='color: #e2e8f0; font-weight: 700; font-size: 15px; letter-spacing: 1.5px;'>🔍 DISTRIBUCIÓN DE EXPERIENCIA: {fletera_seleccionada if 'fletera_seleccionada' in locals() else 'GENERAL'}</span>
            </div>
        """, unsafe_allow_html=True)

        # 1. Selector Elite con mejor espaciado
        lista_fleteras = ["TODAS"] + sorted(df_filtrado["FLETERA"].unique().tolist())
        fletera_seleccionada = st.selectbox("🎯 Filtrar por Paquetería:", lista_fleteras, help="Analiza la puntualidad específica de cada proveedor.")

        # 2. Procesamiento de datos de experiencia
        df_lupa = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        if fletera_seleccionada != "TODAS":
            df_lupa = df_lupa[df_lupa["FLETERA"] == fletera_seleccionada]
        
        df_lupa["DIAS_DIF"] = (df_lupa["FECHA DE ENTREGA REAL"] - df_lupa["PROMESA DE ENTREGA"]).dt.days

        if not df_lupa.empty:
            df_dist_lupa = df_lupa.groupby("DIAS_DIF").size().reset_index(name="PEDIDOS")
            
            # --- ASIGNACIÓN DE COLORES SEGURA ---
            df_dist_lupa["COLOR_HEX"] = df_dist_lupa["DIAS_DIF"].apply(lambda x: color_entrega_ok if x <= 0 else color_entrega_late)

            # 3. Gráfico de Histograma Técnico
            base_lupa = alt.Chart(df_dist_lupa).encode(
                x=alt.X("DIAS_DIF:Q", title="Días vs Promesa (← Antes | Retraso →)", axis=alt.Axis(gridOpacity=0.05, labelColor='#94a3b8')),
                y=alt.Y("PEDIDOS:Q", title=None, axis=alt.Axis(gridOpacity=0.05, labelColor='#94a3b8')),
                color=alt.Color("COLOR_HEX:N", scale=None)
            )

            bars_lupa = base_lupa.mark_bar(
                cornerRadiusTopLeft=6, 
                cornerRadiusTopRight=6,
                size=35 if len(df_dist_lupa) < 10 else 20 # Ajuste dinámico de ancho
            )

            # Etiquetas de datos para precisión absoluta
            text_lupa = base_lupa.mark_text(
                align='center', baseline='bottom', dy=-8, fontWeight=700, color='white', fontSize=12
            ).encode(text=alt.Text("PEDIDOS:Q"))

            st.altair_chart((bars_lupa + text_lupa).properties(height=350).configure_view(strokeOpacity=0), use_container_width=True)

            # 4. Tip Inteligente con Estilo de Tarjeta
            st.markdown(f"""
                <div style='background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); padding: 15px; border-radius: 10px;'>
                    <p style='margin:0; color:#38bdf8; font-size:13px; font-weight:600;'>💡 TIP DE OPERACIONES:</p>
                    <p style='margin:5px 0 0 0; color:#e2e8f0; font-size:14px;'>
                        Analizando a <b>{fletera_seleccionada}</b>: Las barras a la derecha del '0' representan promesas incumplidas. 
                        Busca reducir la dispersión hacia el lado rojo para mejorar la lealtad del cliente.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Sin registros de entrega para los filtros seleccionados.")
        
        # --------------------------------------------------
        # TABLA SCORECARD: CALIFICACIÓN DE FLETERAS
        # --------------------------------------------------
        # --- 🏆 SCORECARD DE DESEMPEÑO LOGÍSTICO (INTEGRADO & DESPLEGABLE) ---
        
        # 1. Preparación de datos (Cálculos Pro)
        resumen_score = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        resumen_score["ES_TARDE"] = (resumen_score["FECHA DE ENTREGA REAL"] > resumen_score["PROMESA DE ENTREGA"])
        resumen_score["DIAS_DIF"] = (resumen_score["FECHA DE ENTREGA REAL"] - resumen_score["PROMESA DE ENTREGA"]).dt.days

        df_score = resumen_score.groupby("FLETERA").agg(
            Total_Entregas=('FLETERA', 'count'),
            Pedidos_Tarde=('ES_TARDE', 'sum'),
            Promedio_Dias=('DIAS_DIF', 'mean')
        ).reset_index()

        df_score["Eficiencia"] = ((1 - (df_score["Pedidos_Tarde"] / df_score["Total_Entregas"])) * 100).round(1)
        df_score = df_score.sort_values(by="Eficiencia", ascending=False)

        # 2. CSS para el Botón Desplegable Ultra-Moderno
        st.markdown("""
            <style>
            .streamlit-expanderHeader {
                background: rgba(255, 255, 255, 0.03) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
                padding: 18px !important;
                color: #00FFAA !important;
                font-weight: 800 !important;
                transition: 0.3s all ease;
            }
            .streamlit-expanderHeader:hover {
                background: rgba(0, 255, 170, 0.05) !important;
                border: 1px solid #00FFAA !important;
            }
            .streamlit-expanderContent {
                border: none !important;
                background: transparent !important;
                padding-top: 20px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # 3. El Botón y el Contenido
        with st.expander("🏆 CLASIFICACIÓN DE SOCIOS LOGÍSTICOS (SCORECARD)"):
            st.markdown("<p style='color: #94a3b8; font-size: 13px; margin-bottom: 25px; margin-left: 5px;'>Análisis profundo de rendimiento y cumplimiento de promesas de entrega.</p>", unsafe_allow_html=True)
            
            for _, row in df_score.iterrows():
                # Colores Dinámicos
                if row["Eficiencia"] >= 95:
                    s_color, s_bg, label = "#059669", "rgba(5, 150, 105, 0.1)", "⭐ EXCELENTE"
                elif row["Eficiencia"] >= 80:
                    s_color, s_bg, label = "#3b82f6", "rgba(59, 130, 246, 0.1)", "✅ CONFIABLE"
                elif row["Eficiencia"] >= 60:
                    s_color, s_bg, label = "#f59e0b", "rgba(245, 158, 11, 0.1)", "⚠️ OBSERVACIÓN"
                else:
                    s_color, s_bg, label = "#fb7185", "rgba(251, 113, 133, 0.1)", "🚨 CRÍTICO"

                # Render de Tarjeta Amazon Style
                st.markdown(f"""
                    <div style='background: {s_bg}; border: 1px solid {s_color}33; padding: 20px; border-radius: 15px; margin-bottom: 15px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='flex-grow: 1;'>
                                <h3 style='margin:0; color:white; font-size:18px; font-family:"Inter", sans-serif;'>{row['FLETERA']}</h3>
                                <span style='background: {s_color}; color: white; padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: 800;'>{label}</span>
                            </div>
                            <div style='text-align: right; margin-right: 30px;'>
                                <p style='margin:0; color:#94a3b8; font-size:10px; text-transform:uppercase;'>Eficiencia</p>
                                <h2 style='margin:0; color:{s_color}; font-size:28px; font-weight:800;'>{row['Eficiencia']}%</h2>
                            </div>
                            <div style='text-align: right; min-width: 100px;'>
                                <p style='margin:0; color:#94a3b8; font-size:10px; text-transform:uppercase;'>Días Prom.</p>
                                <h2 style='margin:0; color:white; font-size:24px;'>{row['Promedio_Dias']:.1f}</h2>
                            </div>
                        </div>
                        <div style='width: 100%; height: 4px; background: rgba(255,255,255,0.05); margin-top: 15px; border-radius: 10px;'>
                            <div style='width: {row['Eficiencia']}%; height: 100%; background: {s_color}; border-radius: 10px; box-shadow: 0 0 10px {s_color}55;'></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # --------------------------------------------------
        # FINAL DE PÁGINA Y BOTÓN A KPIs
        # --------------------------------------------------
        st.divider()
        # --- FINAL DE PÁGINA PRINCIPAL (Añadir nuevo botón) ---
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("SEGUIMIENTO", use_container_width=True):
                st.session_state.pagina = "KPIs"
                st.rerun()
                
        with col_btn2:
            if st.button("REPORTE OPS", use_container_width=True):
                st.session_state.pagina = "Reporte"
                st.rerun()
        
        st.markdown("<div style='text-align:center; color:#475569; font-size:10px; margin-top:20px;'>LOGISTICS INTELLIGENCE UNIT - CONFIDENTIAL</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # BLOQUE 9: PÁGINA DE KPIs (VISTA GERENCIAL DEFINITIVA)
    # ------------------------------------------------------------------
    elif st.session_state.pagina == "KPIs":
        # 1. Fuerza el scroll hacia arriba
        st.components.v1.html("<script>parent.window.scrollTo(0,0);</script>", height=0)
        
        st.markdown("""
            <div style='text-align: center; padding: 10px 0px 30px 0px;'>
                <h1 style='color: white; font-family: "Inter", sans-serif; font-weight: 800; font-size: 42px; margin-bottom: 5px; letter-spacing: -1px;'>
                    PANEL DE SEGUIMIENTO<span style='color: #00FFAA;'></span>
                </h1>
                <p style='color: #94a3b8; font-size: 16px; font-weight: 400; letter-spacing: 1px;'>
                    Análisis de Eficiencia y Seguimiento
                </p>
                <div style='height: 2px; width: 60px; background: #00FFAA; margin: 10px auto;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        # --- 2. LÓGICA DE DATOS (ESTANDARIZADA) ---
        hoy = pd.Timestamp.today().normalize()
        df_kpi = df.copy()
        df_kpi.columns = [c.upper() for c in df_kpi.columns] # Blindaje contra KeyErrors
        
        df_kpi["COSTO DE LA GUÍA"] = pd.to_numeric(df_kpi["COSTO DE LA GUÍA"], errors='coerce').fillna(0)
        df_kpi["CANTIDAD DE CAJAS"] = pd.to_numeric(df_kpi["CANTIDAD DE CAJAS"], errors='coerce').fillna(1).replace(0, 1)
        df_kpi["COSTO_UNITARIO"] = df_kpi["COSTO DE LA GUÍA"] / df_kpi["CANTIDAD DE CAJAS"]
        
        df_sin_entregar = df_kpi[df_kpi["FECHA DE ENTREGA REAL"].isna()].copy()
        df_sin_entregar["DIAS_ATRASO_KPI"] = (hoy - df_sin_entregar["PROMESA DE ENTREGA"]).dt.days
        df_sin_entregar["DIAS_ATRASO_KPI"] = df_sin_entregar["DIAS_ATRASO_KPI"].apply(lambda x: x if x > 0 else 0)
        df_sin_entregar["DIAS_TRANS"] = (hoy - df_sin_entregar["FECHA DE ENVÍO"]).dt.days

        # --- 3. FILTRO DINÁMICO DE RETRASOS CRÍTICOS ---       
        df_criticos = df_sin_entregar[df_sin_entregar["DIAS_ATRASO_KPI"] > 0].copy()
        paqueterias_con_retraso = sorted(df_criticos["FLETERA"].unique())
        
        if len(paqueterias_con_retraso) > 0:
            seleccion = st.multiselect(
                "Selecciona paqueterías con pedidos vencidos:", 
                options=paqueterias_con_retraso
            )
            
            if seleccion:
                df_ver = df_criticos[df_criticos["FLETERA"].isin(seleccion)].copy()
                
                # Formatear fechas como texto antes de mostrar para asegurar alineación izquierda
                df_ver["FECHA DE ENVÍO"] = df_ver["FECHA DE ENVÍO"].dt.strftime('%d/%m/%Y')
                df_ver["PROMESA DE ENTREGA"] = df_ver["PROMESA DE ENTREGA"].dt.strftime('%d/%m/%Y')
                
                columnas_finales = [
                    "NÚMERO DE PEDIDO", "NOMBRE DEL CLIENTE", "FLETERA", 
                    "FECHA DE ENVÍO", "PROMESA DE ENTREGA", "NÚMERO DE GUÍA", 
                    "DIAS_TRANS", "DIAS_ATRASO_KPI"
                ]
                
                df_tabla_ver = df_ver[columnas_finales].rename(columns={
                    "DIAS_ATRASO_KPI": "DÍAS ATRASO",
                    "DIAS_TRANS": "DÍAS TRANS."
                })

                # CONFIGURACIÓN MAESTRA DE ALINEACIÓN
                st.dataframe(
                    df_tabla_ver.sort_values("DÍAS ATRASO", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "NÚMERO DE PEDIDO": st.column_config.TextColumn("NÚMERO DE PEDIDO"),
                        "NOMBRE DEL CLIENTE": st.column_config.TextColumn("NOMBRE DEL CLIENTE", width="large"),
                        "FLETERA": st.column_config.TextColumn("FLETERA"),
                        "FECHA DE ENVÍO": st.column_config.TextColumn("FECHA DE ENVÍO"),
                        "PROMESA DE ENTREGA": st.column_config.TextColumn("PROMESA DE ENTREGA"),
                        "NÚMERO DE GUÍA": st.column_config.TextColumn("NÚMERO DE GUÍA"),
                        "DÍAS TRANS.": st.column_config.TextColumn("DÍAS TRANS."),
                        "DÍAS ATRASO": st.column_config.TextColumn("DÍAS ATRASO ⚠️")
                    }
                )
                st.divider()

        # --- 4. CÁLCULO DE MÉTRICAS Y TARJETAS ---
        total_p = len(df_kpi)
        pend_p = len(df_sin_entregar)
        eficiencia_p = (len(df_kpi[df_kpi['ESTATUS_CALCULADO'] == 'ENTREGADO']) / total_p * 100) if total_p > 0 else 0

        # Valores para monitoreo de atrasos
        a1_val = len(df_sin_entregar[df_sin_entregar["DIAS_ATRASO_KPI"] == 1])
        a2_val = len(df_sin_entregar[df_sin_entregar["DIAS_ATRASO_KPI"] == 2])
        a5_val = len(df_sin_entregar[df_sin_entregar["DIAS_ATRASO_KPI"] >= 5])

        # --- ESTILO CSS PREMIUM (TARJETAS ALTAS Y NÚMEROS GRANDES) ---
        st.markdown("""
            <style>
            .main-card-kpi {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-left: 6px solid #38bdf8;
                border-radius: 15px;
                
                /* AJUSTE DE ALTURA Y ESPACIADO */
                padding: 45px 25px;       
                min-height: 140px;        
                
                display: flex;
                flex-direction: column;
                justify-content: center;   
                align-items: center;
                text-align: center;
                
                box-shadow: 0 15px 30px rgba(0,0,0,0.3);
                margin-bottom: 15px;
            }
            .kpi-label { 
                color: #94a3b8; 
                font-size: 14px; 
                font-weight: 700; 
                text-transform: uppercase; 
                letter-spacing: 2px; 
                margin-bottom: 15px; 
            }
            .kpi-value { 
                color: #f8fafc; 
                font-size: 32px; /* Número extra grande */
                font-weight: 800; 
                font-family: 'Inter', sans-serif;
                line-height: 1;
            }
            
            /* Tarjetas de Alerta Inferiores */
            .card-alerta {
                background-color:#161B22; 
                padding:25px; 
                border-radius:12px; 
                border-top:1px solid #2D333F; 
                border-right:1px solid #2D333F; 
                border-bottom:1px solid #2D333F; 
                text-align:center;
            }
            </style>
        """, unsafe_allow_html=True)

        # --- FILA 1: MÉTRICAS PRINCIPALES (ANCHAS Y ALTAS) ---
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown(f"""
                <div class='main-card-kpi' style='border-left-color: #f1f5f9;'>
                    <div class='kpi-label'>Pedidos Totales</div>
                    <div class='kpi-value'>{total_p}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
                <div class='main-card-kpi' style='border-left-color: #38bdf8;'>
                    <div class='kpi-label'>Sin Entregar</div>
                    <div class='kpi-value' style='color:#38bdf8;'>{pend_p}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with m3:
            # Color dinámico para eficiencia
            color_ef = "#00FFAA" if eficiencia_p >= 95 else "#f97316"
            st.markdown(f"""
                <div class='main-card-kpi' style='border-left-color: {color_ef};'>
                    <div class='kpi-label'>Eficiencia Real</div>
                    <div class='kpi-value' style='color:{color_ef};'>{eficiencia_p:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.write("##")
        
        # --- FILA 2: MONITOREO DE ATRASOS ---
        st.markdown("<p style='color:#9CA3AF; font-size:13px; font-weight:bold; letter-spacing:1px; margin-bottom:20px;'>⚠️ MONITOREO DE ATRASOS (SOLO PENDIENTES)</p>", unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        
        a1.markdown(f"<div class='card-alerta' style='border-left: 6px solid yellow;'><div style='color:#9CA3AF; font-size:11px; font-weight:bold; text-transform:uppercase;'>1 Día Retraso</div><div style='color:white; font-size:36px; font-weight:bold;'>{a1_val}</div></div>", unsafe_allow_html=True)
        a2.markdown(f"<div class='card-alerta' style='border-left: 6px solid #f97316;'><div style='color:#9CA3AF; font-size:11px; font-weight:bold; text-transform:uppercase;'>2 Días Retraso</div><div style='color:white; font-size:36px; font-weight:bold;'>{a2_val}</div></div>", unsafe_allow_html=True)
        a3.markdown(f"<div class='card-alerta' style='border-left: 6px solid #FF4B4B;'><div style='color:#9CA3AF; font-size:11px; font-weight:bold; text-transform:uppercase;'>+5 Días Retraso</div><div style='color:white; font-size:36px; font-weight:bold;'>{a5_val}</div></div>", unsafe_allow_html=True)

        st.write("##")
        st.divider()
               
                
        # --- 8. SECCIÓN DE GRÁFICOS ELITE (CONTROL & RENDIMIENTO) ---
                       
        # Paleta de colores ejecutiva (Semáforo de alto contraste)
        color_excelencia = "#059669" # Esmeralda (>= 95%)
        color_alerta = "#fbbf24"     # Ámbar (85% - 94%)
        color_critico = "#fb7185"    # Coral/Rojo (< 85%)

        # DEFINICIÓN DE LA FUNCIÓN (Debe ir antes de usarse)
        def titulo_grafico_elite(texto, emoji):
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.02); padding: 12px 20px; border-radius: 8px; border-left: 4px solid {color_excelencia}; margin-bottom: 20px;'>
                    <span style='color: #e2e8f0; font-weight: 700; font-size: 15px; letter-spacing: 1.5px;'>{emoji} {texto.upper()}</span>
                </div>
            """, unsafe_allow_html=True)

        # --- GRÁFICO 1: VOLUMEN DE OPERACIÓN (CON ETIQUETAS DE DATOS) ---
        titulo_grafico_elite("Volumen Diario de Envíos", "📈")
        df_vol = df_kpi.groupby(df_kpi["FECHA DE ENVÍO"].dt.date).size().reset_index(name="Pedidos")
        
        # Base del gráfico
        line_base = alt.Chart(df_vol).encode(
            x=alt.X('FECHA DE ENVÍO:T', title=None, axis=alt.Axis(grid=False, labelColor='#94a3b8')),
            y=alt.Y('Pedidos:Q', title=None, axis=alt.Axis(gridOpacity=0.05, labelColor='#94a3b8'))
        )

        # Capa 1: El área sombreada y la línea recta (Estilo Trading)
        area = line_base.mark_area(
            line={'color': color_excelencia, 'strokeWidth': 2.5},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color=color_excelencia, offset=0), alt.GradientStop(color='transparent', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            ),
            interpolate='linear'
        )

        # Capa 2: Puntos en cada vértice
        points = line_base.mark_point(color=color_excelencia, size=60, fill="#0f172a")

        # Capa 3: ETIQUETAS DE DATOS (Los números sobre los puntos)
        labels = line_base.mark_text(
            align='center',
            baseline='bottom',
            dy=-12, # Espacio para que no toque el punto
            color='#e2e8f0',
            fontWeight=600,
            fontSize=12
        ).encode(
            text='Pedidos:Q'
        )

        # Combinar todas las capas
        st.altair_chart((area + points + labels).properties(height=280).configure_view(strokeOpacity=0), use_container_width=True)

        st.write("##")

        # --- GRÁFICO 2: EFICIENCIA POR FLETERA (SEMÁFORO) ---
        titulo_grafico_elite("Ranking de Eficiencia por Fletera", "🏆")
        df_ent = df_kpi[df_kpi["FECHA DE ENTREGA REAL"].notna()].copy()
        
        if not df_ent.empty:
            df_ent["AT"] = df_ent["FECHA DE ENTREGA REAL"] <= df_ent["PROMESA DE ENTREGA"]
            df_p = (df_ent.groupby("FLETERA")["AT"].mean() * 100).reset_index()
            
            # Asignación de colores para el semáforo
            def asignar_color(valor):
                if valor >= 95: return color_excelencia
                if valor >= 85: return color_alerta
                return color_critico
            
            df_p["COLOR_HEX"] = df_p["AT"].apply(asignar_color)

            # Gráfico de barras con etiquetas
            bars = alt.Chart(df_p).mark_bar(
                cornerRadiusTopRight=8,
                cornerRadiusBottomRight=8,
                size=24
            ).encode(
                x=alt.X('AT:Q', title='Cumplimiento (%)', scale=alt.Scale(domain=[0, 118]), axis=alt.Axis(gridOpacity=0.05)),
                y=alt.Y('FLETERA:N', sort='-x', title=None, axis=alt.Axis(labelColor='white', labelFontSize=12)),
                color=alt.Color('COLOR_HEX:N', scale=None) 
            )

            chart_text = bars.mark_text(
                align='left',
                baseline='middle',
                dx=12,
                color='white',
                fontWeight=700,
                fontSize=13
            ).encode(text=alt.Text('AT:Q', format='.1f'))

            st.altair_chart((bars + chart_text).properties(height=400), use_container_width=True)
            
       
       
        # =========================================================
        #             SISTEMA DE ARMAMENTO: MÓDULO ZEUS
        # =========================================================
        import os
        import math
        
        # --- FASE 1: CARGA DE DATOS (HANGAR SEGURO) ---
        def hangar_zeus(nombre_base):
            # El radar busca variaciones de nombre y extensión
            variaciones = [
                f"{nombre_base}.csv", f"{nombre_base}.scv",
                f"{nombre_base.upper()}.csv", "Matriz_Excel_Dasgboard.csv", "Matriz_Excel_Dashboard.csv"
            ]
            for archivo in variaciones:
                if os.path.exists(archivo):
                    df = pd.read_csv(archivo, encoding='latin-1')
                    df.columns = [c.strip().upper() for c in df.columns]
                    return df
            return None
        
        # Activación de variables de flota
        df_mensual = hangar_zeus("matriz_mensual")
        df_dashboard = hangar_zeus("Matriz_Excel_Dashboard")
        
        # --- FASE 2: EJECUCIÓN DEL MÓDULO ---
        if df_mensual is not None and df_dashboard is not None:
            st.markdown(f"## <span style='color:#00ffa2'>⚙️ MÓDULO ZEUS: ANÁLISIS POR PAQUETERÍA</span>", unsafe_allow_html=True)
        
            # 1. FILTRO MAESTRO
            fleteras = sorted(df_mensual['FLETERA'].unique().tolist())
            paqueteria = st.selectbox("🎯 SELECCIONE UNIDAD A ANALIZAR:", fleteras)
        
            # 2. FILTRADO Y LIMPIEZA TÁCTICA
            f_mensual = df_mensual[df_mensual['FLETERA'] == paqueteria].copy()
            f_dash = df_dashboard[df_dashboard['FLETERA'] == paqueteria].copy()
        
            # Limpieza de moneda y números
            for col in ['COSTO DE GUIA', 'VALOR FACTURA']:
                if col in f_mensual.columns:
                    f_mensual[col] = pd.to_numeric(f_mensual[col].astype(str).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
            
            f_mensual['CAJAS'] = pd.to_numeric(f_mensual['CAJAS'], errors='coerce').fillna(0)
            f_mensual['FECHA_F'] = pd.to_datetime(f_mensual['FECHA DE FACTURA'], dayfirst=True, errors='coerce')
        
            # 3. CÁLCULOS KPI (CON BLINDAJE ANTI-NaN)
            t_costo = f_mensual['COSTO DE GUIA'].sum()
            t_cajas = f_mensual['CAJAS'].sum()
            
            # Ecuación Almirante: Costo / Cajas
            raw_costo_caja = t_costo / t_cajas if t_cajas > 0 else 0
            costo_display = "$0.00" if math.isnan(raw_costo_caja) or math.isinf(raw_costo_caja) else f"${raw_costo_caja:,.2f}"
        
            # Puntualidad
            total_envios = len(f_dash)
            if total_envios > 0:
                f_dash['ENTREGA_REAL'] = pd.to_datetime(f_dash['FECHA DE ENTREGA REAL'], dayfirst=True, errors='coerce')
                f_dash['PROMESA'] = pd.to_datetime(f_dash['PROMESA DE ENTREGA'], dayfirst=True, errors='coerce')
                retraso_pct = ((f_dash['ENTREGA_REAL'] > f_dash['PROMESA']).sum() / total_envios) * 100
                retraso_display = f"{retraso_pct:.1f}%"
            else:
                retraso_display = "0.0%"
        
            # 4. DESPLIEGUE DE TARJETAS KPI
            st.markdown("### 📊 INDICADORES DE EFICIENCIA")
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"<div class='kpi-container'><div class='kpi-title'>COSTO X CAJA</div><div class='kpi-value'>{costo_display}</div><div class='kpi-description'>Gasto Guía / Cajas</div></div>", unsafe_allow_html=True)
            with k2:
                st.markdown(f"<div class='kpi-container'><div class='kpi-title'>% RETRASO</div><div class='kpi-value'>{retraso_display}</div><div class='kpi-description'>Puntualidad de Entrega</div></div>", unsafe_allow_html=True)
            with k3:
                fact_t = f_mensual['VALOR FACTURA'].sum()
                st.markdown(f"<div class='kpi-container'><div class='kpi-title'>FACTURACIÓN</div><div class='kpi-value'>${fact_t:,.0f}</div><div class='kpi-description'>Venta por Paquetería</div></div>", unsafe_allow_html=True)
            with k4:
                st.markdown(f"<div class='kpi-container'><div class='kpi-title'>VOLUMEN CAJAS</div><div class='kpi-value'>{int(t_cajas):,}</div><div class='kpi-description'>Total Unidades Enviadas</div></div>", unsafe_allow_html=True)
        
            # 5. RADARES VISUALES
            st.write("---")
            c1, c2 = st.columns(2)
            
            with c1:
                trend = f_mensual.groupby(f_mensual['FECHA_F'].dt.strftime('%Y-%m')).agg({'COSTO DE GUIA':'sum', 'CAJAS':'sum'}).reset_index()
                trend['EFICIENCIA'] = (trend['COSTO DE GUIA'] / trend['CAJAS']).replace([math.inf, -math.inf], 0).fillna(0)
                chart_line = alt.Chart(trend).mark_line(point=True, color='#00ffa2').encode(
                    x=alt.X('FECHA_F:O', title="Mes"),
                    y=alt.Y('EFICIENCIA:Q', title="Costo por Caja ($)"),
                    tooltip=['FECHA_F', alt.Tooltip('EFICIENCIA:Q', format="$,.2f")]
                ).properties(title="TENDENCIA DE COSTO POR CAJA", height=300)
                st.altair_chart(chart_line, use_container_width=True)
        
            with c2:
                top_c = f_mensual.groupby('RAZON SOCIAL')['VALOR FACTURA'].sum().reset_index().sort_values('VALOR FACTURA', ascending=False).head(10)
                chart_bar = alt.Chart(top_c).mark_bar(color='#eab308', cornerRadiusTopRight=10).encode(
                    x=alt.X('VALOR FACTURA:Q', title="Venta Real ($)"),
                    y=alt.Y('RAZON SOCIAL:N', sort='-x', title=None)
                ).properties(title="TOP 10 CLIENTES ASIGNADOS", height=300)
                st.altair_chart(chart_bar, use_container_width=True)
        
        else:
            st.error("🚨 ERROR: Tablas Maestras no detectadas. Verifique archivos en el hangar.")
        # =========================================================
                
        
        # --- NAVEGACIÓN DESDE KPIs ---
        st.divider()
        col_nav1, col_nav2 = st.columns(2)
        
        with col_nav1:
            if st.button("ESTATUS AAC", use_container_width=True):
                st.session_state.pagina = "principal"
                st.components.v1.html("<script>parent.window.scrollTo(0,0);</script>", height=0)
                st.rerun()
                
        with col_nav2:
            if st.button("REPORTE OPS", use_container_width=True):
                st.session_state.pagina = "Reporte"
                st.components.v1.html("<script>parent.window.scrollTo(0,0);</script>", height=0)
                st.rerun()

        # Pie de página
        st.markdown("<div style='text-align:center; color:#475569; font-size:10px; margin-top:20px;'>LOGISTICS INTELLIGENCE UNIT - CONFIDENTIAL</div>", unsafe_allow_html=True)
    # ----------------------------------------------
    # ------------------------------------------------------------------
    # BLOQUE 10: REPORTE EJECUTIVO DE ALTO NIVEL
    # ------------------------------------------------------------------
    elif st.session_state.pagina == "Reporte":
        st.components.v1.html("<script>parent.window.scrollTo(0,0);</script>", height=0)
        
        # Título con estilo minimalista
        st.markdown("""
            <div style='text-align: center; padding: 10px 0px 30px 0px;'>
                <h1 style='color: white; font-family: "Inter", sans-serif; font-weight: 800; font-size: 42px; margin-bottom: 5px; letter-spacing: -1px;'>
                    REPORTE MENSUAL<span style='color: #00FFAA;'>OPS</span>
                </h1>
                <p style='color: #94a3b8; font-size: 16px; font-weight: 400; letter-spacing: 1px;'>
                    Análisis de Eficiencia Logística y Rentabilidad
                </p>
                <div style='height: 2px; width: 60px; background: #00FFAA; margin: 10px auto;'></div>
            </div>
        """, unsafe_allow_html=True)
             
               
        # --- 1. MOTOR DE DATOS NIVEL ELITE ---
        @st.cache_data
        def cargar_analisis_elite():
            try:
                df = pd.read_csv("analisis.csv", encoding="utf-8")
                df.columns = [str(c).strip().upper() for c in df.columns]
                df = df.dropna(subset=['MES'])
                df = df[df['MES'].str.contains('Unnamed|TOTAL', case=False) == False]
                
                def limpiar_a_numero(v):
                    if pd.isna(v): return 0.0
                    if isinstance(v, (int, float)): return float(v)
                    s = str(v).replace('$', '').replace(',', '').replace('%', '').replace('(', '-').replace(')', '').strip()
                    try: return float(s)
                    except: return 0.0
        
                cols_numericas = [
                    "COSTO DE FLETE", "FACTURACIÓN", "CAJAS ENVIADAS", "COSTO LOGÍSTICO", 
                    "COSTO POR CAJA", "META INDICADOR", "VALUACION INCIDENCIAS", 
                    "INCREMENTO + VI", "% DE INCREMENTO VS 2024", "COSTO POR CAJA 2024", "PORCENTAJE DE INCIDENCIAS"
                ]
                
                for col in cols_numericas:
                    if col in df.columns:
                        df[col] = df[col].apply(limpiar_a_numero)
                return df
            except Exception as e:
                st.error(f"Error en Motor: {e}")
                return None
        
        # --- 2. FUNCIÓN DE RENDERIZADO BLINDADA ---
        def render_card(label, value, footer, target_val=None, actual_val=None, inverse=False, border_base="border-blue"):
            if target_val is None or actual_val is None:
                color = "#f0f6fc"
                border = border_base
            else:
                is_alert = actual_val > target_val if not inverse else actual_val < target_val
                color = "#fb7185" if is_alert else "#00ffa2"
                border = "border-red" if is_alert else "border-green"
            
            st.markdown(f"""
                <div class='card-container {border}'>
                    <div class='card-label'>{label}</div>
                    <div class='card-value' style='color:{color}'>{value}</div>
                    <div class='card-footer'>{footer}</div>
                </div>
            """, unsafe_allow_html=True)
        
        df_a = cargar_analisis_elite()
        
        if df_a is not None:
            # --- 3. SIDEBAR ---
            st.sidebar.markdown("## ")
            meses_limpios = [m for m in df_a["MES"].unique() if str(m).strip() != ""]
            mes_sel = st.sidebar.selectbox("MES ACTUAL / BASE", meses_limpios)
            df_mes = df_a[df_a["MES"] == mes_sel].iloc[0]
            
            modo_comp = st.sidebar.checkbox("Activar comparativa Mes vs Mes")
            if modo_comp:
                mes_comp = st.sidebar.selectbox("COMPARAR CONTRA:", meses_limpios, index=0)
                df_mes_b = df_a[df_a["MES"] == mes_comp].iloc[0]
        
            # --- 4. CSS PREMIUM ELITE ---
            st.markdown("""
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@400;800&display=swap');
                .premium-header { font-family: 'Orbitron', sans-serif; color: #f8fafc; letter-spacing: 2px; text-transform: uppercase; border-bottom: 2px solid #38bdf8; padding-bottom: 8px; margin: 25px 0; }
                .card-container { background-color: #0d1117; border-radius: 10px; padding: 15px; border: 1px solid #30363d; height: 125px; margin-bottom: 10px; transition: all 0.3s; margin-top: 10px;}
                .card-label { color: #8b949e; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; }
                .card-value { font-size: 1.6rem; font-weight: 800; margin: 4px 0; font-family: 'Inter', sans-serif; }
                .card-footer { color: #484f58; font-size: 0.6rem; font-weight: 600; }
                .border-blue { border-left: 5px solid #38bdf8; } .border-green { border-left: 5px solid #00ffa2; }
                .border-red { border-left: 5px solid #fb7185; } .border-purple { border-left: 5px solid #a78bfa; }
                .border-yellow { border-left: 5px solid #eab308; } .border-pink { border-left: 5px solid #f472b6; }
                .insight-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; margin-top: 10px; }
                .calc-box { background: rgba(56, 189, 248, 0.05); border: 1px dashed #38bdf8; border-radius: 10px; padding: 15px; margin: 20px 0; font-family: 'Inter', sans-serif; color: #94a3b8; font-size: 0.85rem; }
                </style>
            """, unsafe_allow_html=True)

                   
            header_txt = f"Resultados: {mes_sel}" if not modo_comp else f"Comparativa Mode: {mes_sel} VS {mes_comp}"
            st.markdown(f"<h4 class='premium-header'>{header_txt}</h4>", unsafe_allow_html=True)
        
            if not modo_comp:
                # --- VISTA NORMAL 9 TARJETAS ---
                c1, c2, c3 = st.columns(3)
                with c1: render_card("Costo Logístico", f"{df_mes['COSTO LOGÍSTICO']:.1f}%", f"META: {df_mes['META INDICADOR']}%", df_mes['META INDICADOR'], df_mes['COSTO LOGÍSTICO'])
                with c2: render_card("Incremento + VI", f"${df_mes['INCREMENTO + VI']:,.0f}", "Impacto Real", 0, df_mes['INCREMENTO + VI'], inverse=True)
                with c3: render_card("% Incr. vs 2024", f"{df_mes['% DE INCREMENTO VS 2024']:.1f}%", "Inflación", border_base="border-pink")
        
                c4, c5, c6 = st.columns(3)
                with c4: render_card("Costo por Caja", f"${df_mes['COSTO POR CAJA']:.1f}", f"Target 2024: ${df_mes['COSTO POR CAJA 2024']:.1f}", df_mes['COSTO POR CAJA 2024'], df_mes['COSTO POR CAJA'])
                with c5: render_card("Valuación Incidencias", f"${df_mes['VALUACION INCIDENCIAS']:,.0f}", "Mermas", border_base="border-yellow")
                with c6: render_card("% Incidencias", f"{df_mes['PORCENTAJE DE INCIDENCIAS']:.2f}%", "Calidad", border_base="border-purple")
        
                c7, c8, c9 = st.columns(3)
                with c7: render_card("Facturación", f"${df_mes['FACTURACIÓN']:,.0f}", "Venta Mes", border_base="border-blue")
                with c8: render_card("Cajas Enviadas", f"{int(df_mes['CAJAS ENVIADAS']):,.0f}", "Volumen", border_base="border-purple")
                with c9: render_card("Costo de Flete", f"${df_mes['COSTO DE FLETE']:,.0f}", "Inversión", border_base="border-blue")
        
                # --- BLOQUE PREMIUM DE CÁLCULOS ---
                st.markdown(f"""
                <div class="calc-box">
                    <b style="color:#38bdf8; text-transform:uppercase;">Metodología de Cálculo para {mes_sel}:</b><br><br>
                    • <b>Logístico:</b> (${df_mes['COSTO DE FLETE']:,.2f} / ${df_mes['FACTURACIÓN']:,.2f}) = {df_mes['COSTO LOGÍSTICO']:.2f}%<br>
                    • <b>C/Caja:</b> ${df_mes['COSTO DE FLETE']:,.2f} / {int(df_mes['CAJAS ENVIADAS'])} cajas = ${df_mes['COSTO POR CAJA']:.2f}<br>
                    • <b>Impacto:</b> (Ahorro Incidencias) - (Variación Tarifaria vs 2024 * Cajas) = ${df_mes['INCREMENTO + VI']:,.2f}
                </div>
                """, unsafe_allow_html=True)
        
               # --- LÓGICA DE NARRATIVA DINÁMICA (EL CEREBRO DEL CAPITÁN) ---
                impacto_1k = (df_mes['COSTO DE FLETE'] / df_mes['FACTURACIÓN']) * 1000
                eficiencia_vs_meta = df_mes['META INDICADOR'] - df_mes['COSTO LOGÍSTICO']
                
                # Definición de Tono y Mensaje según Desempeño
                if eficiencia_vs_meta >= 0.5:
                    msg_clase = "OPTIMIZACIÓN RADICAL"
                    msg_color = "#00ffa2"
                    msg_desc = f"La operación está en zona de alta rentabilidad. Estamos operando {eficiencia_vs_meta:.1f}% por debajo del techo presupuestal, lo que inyecta liquidez directa al Bottom Line."
                elif eficiencia_vs_meta >= 0:
                    msg_clase = "ESTABILIDAD OPERATIVA"
                    msg_color = "#38bdf8"
                    msg_desc = "Cumplimiento de objetivos en curso. El control de fletes se mantiene alineado con la facturación, asegurando un margen neto previsible."
                else:
                    msg_clase = "EROSIÓN DE MARGEN"
                    msg_color = "#fb7185"
                    msg_desc = f"Alerta roja: La logística está devorando el margen bruto. Superamos el target por {abs(eficiencia_vs_meta):.1f}%, lo que requiere una intervención inmediata en el mix de transporte."
        
                # --- VISUALIZACIÓN DE ANÁLISIS DINÁMICO ---
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f"""<div class="insight-box" style="border-left: 5px solid #38bdf8; height:240px;">
                        <h4 style="color:#38bdf8; margin:0; font-family:Orbitron; font-size:0.9rem;">DEEP DIVE: EFICIENCIA FINANCIERA</h4>
                        <p style="color:#94a3b8; font-size:0.85rem; margin-top:15px; line-height:1.6;">
                        • <b>Métrica de Consumo:</b> Cada <b>$1,000</b> de venta genera un 'impuesto logístico' de <b>${impacto_1k:.2f}</b>.<br>
                        • <b>Punto de Fuga:</b> El desvío tarifario vs 2024 representa una fuga de <b>${abs(df_mes['INCREMENTO + VI']):,.0f}</b>. <br>
                        • <b>Diagnóstico:</b> El costo por unidad está <b>{'sobre la media' if df_mes['COSTO POR CAJA'] > df_mes['COSTO POR CAJA 2024'] else 'bajo control'}</b>, lo que indica una {'necesidad de renegociación' if df_mes['COSTO POR CAJA'] > df_mes['COSTO POR CAJA 2024'] else 'gestión óptima de activos'}.
                        </p></div>""", unsafe_allow_html=True)
                
                with r2:
                    st.markdown(f"""<div class="insight-box" style="border-top: 4px solid {msg_color}; height:240px;">
                        <h4 style="color:{msg_color}; margin:0; font-family:Orbitron; font-size:0.9rem;">🩺 RADIOGRAFÍA: {msg_clase}</h4>
                        <p style="color:#f1f5f9; font-size:0.85rem; margin-top:15px; line-height:1.6;">
                        <b>DICTAMEN TÉCNICO:</b> {msg_desc}<br><br>
                        <b>ANÁLISIS DE BRECHA:</b> Estamos operando con un incremento unitario del <b>{df_mes['% DE INCREMENTO VS 2024']:.1f}%</b>. Este nivel de inflación logística 
                        {'es insostenible' if df_mes['% DE INCREMENTO VS 2024'] > 10 else 'es manejable'} bajo el esquema actual de precios de venta.
                        </p></div>""", unsafe_allow_html=True)
        
            else:
                # --- VISTA COMPARATIVA 3 VS 3 ---
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"#### 📍 {mes_sel}")
                    render_card("Costo Logístico", f"{df_mes['COSTO LOGÍSTICO']:.1f}%", "Actual", df_mes['META INDICADOR'], df_mes['COSTO LOGÍSTICO'])
                    render_card("Costo por Caja", f"${df_mes['COSTO POR CAJA']:.1f}", "Actual", df_mes['COSTO POR CAJA 2024'], df_mes['COSTO POR CAJA'])
                    render_card("Incremento + VI", f"${df_mes['INCREMENTO + VI']:,.0f}", "Actual", 0, df_mes['INCREMENTO + VI'], inverse=True)
        
                with col_b:
                    st.markdown(f"#### 📍 {mes_comp}")
                    render_card("Costo Logístico", f"{df_mes_b['COSTO LOGÍSTICO']:.1f}%", "Comparativo", df_mes_b['META INDICADOR'], df_mes_b['COSTO LOGÍSTICO'])
                    render_card("Costo por Caja", f"${df_mes_b['COSTO POR CAJA']:.1f}", "Comparativo", df_mes_b['COSTO POR CAJA 2024'], df_mes_b['COSTO POR CAJA'])
                    render_card("Incremento + VI", f"${df_mes_b['INCREMENTO + VI']:,.0f}", "Comparativo", 0, df_mes_b['INCREMENTO + VI'], inverse=True)
        
                # --- ANÁLISIS DE COMBATE (DEEP DIVE COMPARATIVO) ---
                delta_log = df_mes["COSTO LOGÍSTICO"] - df_mes_b["COSTO LOGÍSTICO"]
                mejor_mes = mes_sel if delta_log < 0 else mes_comp
                
                st.markdown(f"""
                <div class="insight-box" style="border-top: 5px solid #a78bfa;">
                    <h4 style="color:#a78bfa; margin:0; font-family:Orbitron; font-size:0.9rem;">ANÁLISIS FORENSE: COMPARATIVA DE RENDIMIENTO</h4>
                    <p style="color:#f1f5f9; font-size:0.9rem; margin-top:10px; line-height:1.6;">
                    La telemetría indica que <b>{mejor_mes}</b> es el referente de eficiencia. 
                    <br>• <b>Variación Estratégica:</b> Existe un diferencial de <b>{abs(delta_log):.2f}%</b> en la absorción del costo sobre la venta bruta.<br>
                    • <b>Factor Determinante:</b> La diferencia no es el volumen, sino la <b>densidad de costo por caja</b>. {'Mantener el modelo de ' + mejor_mes if delta_log != 0 else 'Ambos periodos presentan paridad operativa'}.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            def crear_pdf_logistico(df_mes, mes_sel, impacto_1k, veredicto):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # --- ENCABEZADO ---
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, f"REPORTE EJECUTIVO DE LOGISTICA: {mes_sel}", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, "Intelligence Operations Command - Logistic Performance Analysis", ln=True, align='C')
                pdf.ln(5)
                pdf.line(10, 32, 200, 32) # Línea divisoria
                pdf.ln(10)
                
                # --- TABLA DE KPIS CRITICOS ---
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(100, 10, "INDICADOR CLAVE (KPI)", 1, 0, 'C', True)
                pdf.cell(90, 10, "VALOR REPORTADO", 1, 1, 'C', True)
                
                pdf.set_font("Arial", '', 11)
                kpis = [
                    ("Costo Logistico (%)", f"{df_mes['COSTO LOGÍSTICO']:.2f}%"),
                    ("Costo por Caja ($)", f"${df_mes['COSTO POR CAJA']:.2f}"),
                    ("Facturacion Mensual", f"${df_mes['FACTURACIÓN']:,.2f}"),
                    ("Volumen (Cajas)", f"{int(df_mes['CAJAS ENVIADAS']):,.0f}"),
                    ("Fuga de Utilidad (Delta)", f"${abs(df_mes['INCREMENTO + VI']):,.2f}"),
                    ("Inflacion vs 2024", f"{df_mes['% DE INCREMENTO VS 2024']:.1f}%")
                ]
                
                for kpi, valor in kpis:
                    pdf.cell(100, 10, kpi, 1)
                    pdf.cell(90, 10, valor, 1, 1, 'C')
                
                pdf.ln(10)
                
                # --- METODOLOGIA DE CALCULO ---
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "METODOLOGIA DE CALCULO Y AUDITORIA:", ln=True)
                pdf.set_font("Arial", '', 10)
                metodologia = (
                    f"1. Costo Logistico: Se determina dividiendo el gasto total de fletes (${df_mes['COSTO DE FLETE']:,.2f}) "
                    f"entre la facturacion bruta (${df_mes['FACTURACIÓN']:,.2f}).\n"
                    f"2. Costo por Caja: Gasto total entre {int(df_mes['CAJAS ENVIADAS'])} unidades despachadas.\n"
                    f"3. Impacto de Utilidad: Cruce de valuacion de incidencias contra desviacion tarifaria base 2024."
                )
                pdf.multi_cell(0, 8, metodologia)
                pdf.ln(5)
            
                # --- RADIOGRAFIA Y DIAGNOSTICO ---
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "DIAGNOSTICO ESTRATEGICO FINAL:", ln=True)
                pdf.set_fill_color(245, 245, 255)
                pdf.set_font("Arial", 'I', 11)
                diagnostico = (
                    f"Por cada $1,000 MXN de venta, la operacion consume ${impacto_1k:.2f}.\n\n"
                    f"VERDICTO: {veredicto}"
                )
                pdf.multi_cell(0, 10, diagnostico, border=1, fill=True)
                
                return pdf.output()
        
            # --- PROTOCOLO DE EXTRACCIÓN SEGURO (LAS 9 TARJETAS) ---
            st.write("---")

            if not modo_comp:
                if PDF_READY:
                    if st.button("GENERAR REPORTE"):
                        try:
                            st.toast("Compilando información...", icon="⚙️")
                            
                            # RE-CÁLCULO DE SEGURIDAD
                            impacto_1k = (df_mes['COSTO DE FLETE'] / df_mes['FACTURACIÓN']) * 1000 if df_mes['FACTURACIÓN'] > 0 else 0
                            
                            pdf = FPDF()
                            pdf.add_page()
                            
                            # --- ENCABEZADO INSTITUCIONAL ---
                            pdf.set_fill_color(13, 17, 23)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_font("Arial", 'B', 16)
                            pdf.cell(0, 15, f"REPORTE EJECUTIVO DE LOGÍSTICA - {mes_sel}", 0, 1, 'C', True)
                            
                            pdf.ln(5)
                            pdf.set_text_color(0, 0, 0)
                            
                            # --- SECCIÓN 1: RENTABILIDAD (TARJETAS 1, 2, 3) ---
                            pdf.set_font("Arial", 'B', 11)
                            pdf.set_fill_color(240, 240, 240)
                            pdf.cell(0, 8, "  I. INDICADORES DE RENTABILIDAD Y COSTO", 0, 1, 'L', True)
                            pdf.ln(1)
                            pdf.set_font("Arial", '', 10)
                            pdf.cell(63, 10, f"Costo Logistico: {df_mes['COSTO LOGÍSTICO']:.1f}%", 1, 0, 'C')
                            pdf.cell(63, 10, f"Incr. vs 2024: {df_mes['% DE INCREMENTO VS 2024']:.1f}%", 1, 0, 'C')
                            pdf.cell(63, 10, f"Meta Mes: {df_mes['META INDICADOR']}%", 1, 1, 'C')
                            
                            pdf.ln(3)
                            
                            # --- SECCIÓN 2: IMPACTO Y DESVIACIÓN (TARJETAS 4, 5, 6) ---
                            pdf.set_font("Arial", 'B', 11)
                            pdf.cell(0, 8, "  II. IMPACTO EN UTILIDAD Y CALIDAD", 0, 1, 'L', True)
                            pdf.ln(1)
                            pdf.set_font("Arial", '', 10)
                            pdf.cell(63, 10, f"Costo por Caja: ${df_mes['COSTO POR CAJA']:.1f}", 1, 0, 'C')
                            pdf.cell(63, 10, f"Incidencias: {df_mes['PORCENTAJE DE INCIDENCIAS']:.2f}%", 1, 0, 'C')
                            pdf.cell(63, 10, f"Val. Incidencias: ${df_mes['VALUACION INCIDENCIAS']:,.0f}", 1, 1, 'C')
                            
                            pdf.ln(3)

                            # --- SECCIÓN 3: OPERACIÓN (TARJETAS 7, 8, 9) --- [NUEVA SECCIÓN AGREGADA]
                            pdf.set_font("Arial", 'B', 11)
                            pdf.cell(0, 8, "  III. DATOS DE OPERACIÓN Y VOLUMETRÍA", 0, 1, 'L', True)
                            pdf.ln(1)
                            pdf.set_font("Arial", '', 10)
                            pdf.cell(63, 10, f"Facturacion: ${df_mes['FACTURACIÓN']:,.0f}", 1, 0, 'C')
                            pdf.cell(63, 10, f"Cajas Enviadas: {int(df_mes['CAJAS ENVIADAS']):,.0f}", 1, 0, 'C')
                            pdf.cell(63, 10, f"Gasto Flete: ${df_mes['COSTO DE FLETE']:,.0f}", 1, 1, 'C')
                            
                            pdf.ln(6)

                            # --- BLOQUE DE ANÁLISIS ---
                            pdf.set_font("Arial", 'B', 12)
                            pdf.set_text_color(30, 58, 138)
                            pdf.cell(0, 10, "DIAGNÓSTICO ESTRATÉGICO FINAL", ln=True)
                            
                            pdf.set_text_color(0, 0, 0)
                            pdf.set_font("Arial", 'I', 11)
                            pdf.set_fill_color(245, 247, 250)
                            
                            status_txt = "CRÍTICO" if df_mes['COSTO LOGÍSTICO'] > df_mes['META INDICADOR'] else "ÓPTIMO"
                            analisis_pro = (
                                f"En el periodo de {mes_sel}, la operacion registra un estado {status_txt}. "
                                f"Cada $1,000 MXN de venta consumen ${impacto_1k:.2f} de flete. "
                                f"El impacto acumulado por desviacion y mermas asciende a ${abs(df_mes['INCREMENTO + VI']):,.2f} MXN."
                            )
                            pdf.multi_cell(0, 10, analisis_pro, 1, 'L', True)

                            # --- SALIDA SEGURA ---
                            pdf_raw = pdf.output()
                            pdf_final = bytes(pdf_raw) if isinstance(pdf_raw, bytearray) else pdf_raw.encode('latin-1')
                            
                            st.download_button(
                                label="DESCARGAR REPORTE",
                                data=pdf_final,
                                file_name=f"Reporte_Elite_{mes_sel}.pdf",
                                mime="application/pdf"
                            )
                            
                        except Exception as e:
                            st.error(f"Falla en diseño: {e}")
                else:
                    st.warning("⚠️ Sistema PDF no detectado.")
            else:
                st.info("💡 **INFO DE COMANDO:** El PDF requiere una vista de mes individual.")
                  
            

            def generar_grafico_fleteras_elite_v2_vertical():
                import os
                import pandas as pd
                import altair as alt
                import streamlit as st
                
                try:
                    # 1. DETECCIÓN DE ARCHIVO
                    posibles_nombres = ["matriz_mensual.scv", "matriz_mensual.csv"]
                    archivo_encontrado = next((n for n in posibles_nombres if os.path.exists(n)), None)
                    
                    if not archivo_encontrado:
                        st.error("🚨 RADAR: No se encontró la base de datos de fleteras.")
                        return
            
                    # 2. CARGA Y LIMPIEZA
                    df = pd.read_csv(archivo_encontrado, encoding='latin-1')
                    df.columns = [c.strip().upper() for c in df.columns]
                    df['COSTO DE GUIA'] = df['COSTO DE GUIA'].replace('[\$,]', '', regex=True).astype(float).fillna(0)
                    
                    df['FECHA DE FACTURA'] = pd.to_datetime(df['FECHA DE FACTURA'], dayfirst=True, errors='coerce')
                    df = df.dropna(subset=['FECHA DE FACTURA'])
                    df['MES_LABEL'] = df['FECHA DE FACTURA'].dt.strftime('%B').str.upper()
                    df['MES_NUM'] = df['FECHA DE FACTURA'].dt.month
                    
                    # 3. FILTRO INTEGRADO
                    meses_ordenados = df.sort_values('MES_NUM')['MES_LABEL'].unique().tolist()
                    input_dropdown = alt.binding_select(options=meses_ordenados, name="PERIODO: ")
                    seleccion = alt.selection_point(fields=['MES_LABEL'], bind=input_dropdown, value=meses_ordenados[-1])
            
                    # --- CONSTRUCCIÓN VERTICAL RESPONSIVA ---
                    base = alt.Chart(df).transform_filter(seleccion)
            
                    # CAPA 1: Columnas con Bandwidth Automático (Se ajusta a móvil/PC)
                    columnas = base.mark_bar(
                        cornerRadiusTopLeft=10,
                        cornerRadiusTopRight=10,
                        size={'bandwidth': 0.7} # Ocupa el 70% del espacio disponible (evita amontonamiento)
                    ).encode(
                        x=alt.X('FLETERA:N', 
                                title=None, 
                                sort='-y',
                                axis=alt.Axis(labelAngle=-45, labelFontSize=11, labelColor='#FFFFFF', labelFontWeight='bold', labelOverlap='parity')),
                        y=alt.Y('sum(COSTO DE GUIA):Q', 
                                title=None, 
                                axis=alt.Axis(format="$,.0s", gridColor='#262730', labelColor='#94a3b8')), # Formato corto ($300k)
                        color=alt.Color('FLETERA:N', scale=alt.Scale(scheme='goldorange'), legend=None),
                        tooltip=[alt.Tooltip('FLETERA:N'), alt.Tooltip('sum(COSTO DE GUIA):Q', format="$,.2f")]
                    )
            
                    # CAPA 2: Etiquetas Superiores (Formato compacto para móvil)
                    texto = columnas.mark_text(
                        align='center', baseline='bottom', dy=-10, color='#FFFFFF', fontWeight='bold', fontSize=12
                    ).encode(
                        text=alt.Text('sum(COSTO DE GUIA):Q', format="$,.2s") # Muestra $300k en lugar de $300,000
                    )
            
                    grafico_final = (columnas + texto).add_params(seleccion).properties(
                        width='container', height=400,
                        title=alt.TitleParams(text="ESTADO DE INVERSIÓN POR FLETERA", fontSize=20, color='#eab308', anchor='start')
                    ).configure_view(strokeWidth=0)
            
                    st.altair_chart(grafico_final, use_container_width=True)
            
                except Exception as e:
                    st.error(f"⚠️ FALLA EN FLETERAS: {e}")
            
            def generar_ranking_destinos_pro_v2():
                import os
                import pandas as pd
                import altair as alt
                import streamlit as st
                try:
                    archivo = "matriz_mensual.scv" if os.path.exists("matriz_mensual.scv") else "matriz_mensual.csv"
                    if not os.path.exists(archivo):
                        st.error(f"🚨 RADAR: No detectado.")
                        return
            
                    df = pd.read_csv(archivo, encoding='latin-1')
                    df.columns = [c.strip().upper() for c in df.columns]
                    df['VALOR FACTURA'] = df['VALOR FACTURA'].replace('[\$,]', '', regex=True).astype(float).fillna(0)
                    
                    df_geo = df.groupby('ESTADO')['VALOR FACTURA'].sum().reset_index()
                    df_geo = df_geo.sort_values('VALOR FACTURA', ascending=False).head(15)
            
                    # --- DISEÑO VERTICAL RESPONSIVO ---
                    base = alt.Chart(df_geo).encode(
                        x=alt.X('ESTADO:N', title=None, sort='-y',
                                axis=alt.Axis(labelAngle=-45, labelFontSize=10, labelColor='#FFFFFF', labelOverlap='parity')),
                        y=alt.Y('VALOR FACTURA:Q', title=None,
                                axis=alt.Axis(format="$,.0s", grid=True, gridColor='#262730', labelColor='#94a3b8'))
                    )
            
                    columnas = base.mark_bar(
                        cornerRadiusTopLeft=8, cornerRadiusTopRight=8,
                        size={'bandwidth': 0.65} # Ajuste dinámico
                    ).encode(color=alt.value('#EAB308'))
            
                    texto = base.mark_text(
                        align='center', baseline='bottom', dy=-10, color='#FFFFFF', fontWeight='bold', fontSize=11
                    ).encode(text=alt.Text('VALOR FACTURA:Q', format="$,.2s"))
            
                    radar_vertical = (columnas + texto).properties(
                        width='container', height=400,
                        title=alt.TitleParams(text="TOP DESTINOS", fontSize=20, color='#EAB308', anchor='start')
                    ).configure_view(strokeWidth=0)
            
                    st.altair_chart(radar_vertical, use_container_width=True)
            
                except Exception as e:
                    st.error(f"⚠️ FALLA EN DESTINOS: {e}")
            
            # --- EJECUCIÓN ---
            st.write("---")
            generar_grafico_fleteras_elite_v2_vertical()
            st.write("---")
            generar_ranking_destinos_pro_v2()
                        
        
        # --- NAVEGACIÓN NIVEL AMAZON (ESTILO FINAL) ---
        st.divider()
        st.markdown('<div class="nav-container">', unsafe_allow_html=True) 
        
        n1, n2 = st.columns(2)
        with n1:
            if st.button("ESTATUS AAC", use_container_width=True):
                st.session_state.pagina = "principal"
                st.rerun()
        with n2:
            if st.button("SEGUIMIENTO", use_container_width=True):
                st.session_state.pagina = "KPIs"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:#475569; font-size:10px; margin-top:20px;'>LOGISTICS INTELLIGENCE UNIT - CONFIDENTIAL</div>", unsafe_allow_html=True)
        
        
    































































































































































































































































































































































































































































































































































































































































