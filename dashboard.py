import streamlit as st
import pandas as pd
import altair as alt
import time
import base64
import textwrap

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Control de Envíos", layout="wide", initial_sidebar_state="expanded")

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

# Colores
color_fondo_nativo = "#0e1117" 
color_blanco = "#FFFFFF"
color_verde = "#00FF00" 
color_borde_gris = "#333333"

# Colores Globales
color_fondo_nativo = "#0e1117"
color_blanco = "#FFFFFF"
color_verde = "#00FF00"
color_borde_gris = "#333333"

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
    .login-header {{ text-align: center; color: white; font-family: sans-serif; font-size: 24px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; }}
    input {{ font-family: 'Courier Prime', monospace !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

placeholder = st.empty()

# --------------------------------------------------
# 4. FLUJO DE PANTALLAS
# --------------------------------------------------

# CASO A: LOGIN
if not st.session_state.logueado:
    with placeholder.container():
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown('<div style="height:10vh"></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown('<div class="scene"><div class="cube"><div class="cube-face front"></div><div class="cube-face back"></div><div class="cube-face right"></div><div class="cube-face left"></div><div class="cube-face top"></div><div class="cube-face bottom"></div></div></div>', unsafe_allow_html=True)
                st.markdown('<div class="login-header">Acceso al Sistema</div>', unsafe_allow_html=True)
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
        t_splash = "Cerrando sistema..." if st.session_state.motivo_splash == "logout" else f"Bienvenid@ {st.session_state.usuario_actual}..."
        c_caja = "#FF4B4B" if st.session_state.motivo_splash == "logout" else "#d2a679"
        
        st.markdown(f"""
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
                <div style="color:white; font-family:'Courier Prime'; margin-top:60px; letter-spacing:2px; text-transform: uppercase;">{t_splash}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2.5)
        
        if st.session_state.motivo_splash == "logout":
            st.session_state.logueado = False
            st.session_state.usuario_actual = None
            st.session_state.pagina = "principal" # Reseteo de página
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
        st.markdown("<style>@keyframes floatBox{0%{transform:translateY(0);}50%{transform:translateY(-5px);}100%{transform:translateY(0);}}@keyframes lidOpen{0%,80%{transform:rotateX(0deg);}85%{transform:rotateX(35deg);}90%{transform:rotateX(0deg);}100%{transform:rotateX(0deg);}}</style><h2 style='text-align:center;display:flex;align-items:center;justify-content:center;gap:14px;font-weight:600;color:#FFFFFF;'><svg style='animation:floatBox 3s ease-in-out infinite;' width='36' height='36' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><g style='transform-origin:12px 7px;animation:lidOpen 10s ease-in-out infinite;'><path d='M3 7L12 2L21 7L12 12L3 7Z' stroke='#00FFAA' stroke-width='1.5' stroke-linejoin='round'/></g><path d='M3 7V17L12 22L21 17V7' stroke='#00FFAA' stroke-width='1.5' stroke-linejoin='round'/><path d='M12 12V22' stroke='#00FFAA' stroke-width='1.5'/><path d='M7.5 4.8L16.5 9.3' stroke='#00FFAA' stroke-width='1.1' opacity='0.5'/></svg><span>Control de Embarques</span></h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Logística – Enero 2026</p>", unsafe_allow_html=True)
       
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
        # 1. CÁLCULO DE MÉTRICAS (INDISPENSABLE ANTES DE LAS DONITAS)
        # --------------------------------------------------
        # Aseguramos que 'total' y demás variables existan
        total = len(df_filtrado)
        entregados = (df_filtrado["ESTATUS_CALCULADO"] == "ENTREGADO").sum()
        en_transito = (df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO").sum()
        retrasados = (df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO").sum()
    
        # --------------------------------------------------
        # 2. CONFIGURACIÓN DE COLORES Y FUNCIÓN
        # --------------------------------------------------
        COLOR_AVANCE_ENTREGADOS = "#4CAF50"
        COLOR_AVANCE_TRANSITO   = "#FFC107"
        COLOR_AVANCE_RETRASADOS = "#F44336"
        COLOR_FALTANTE          = "#3A3A3A"
    
        def donut_con_numero(avance, total_val, color_avance, color_faltante):
            porcentaje = int((avance / total_val) * 100) if total_val > 0 else 0
            data_dona = pd.DataFrame({
                "segmento": ["avance", "faltante"],
                "valor": [avance, max(total_val - avance, 0)]
            })
            
            donut = alt.Chart(data_dona).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("valor:Q"),
                color=alt.Color("segmento:N", scale=alt.Scale(range=[color_avance, color_faltante]), legend=None)
            )
            
            texto_n = alt.Chart(pd.DataFrame({"texto": [f"{avance}"]})).mark_text(
                align="center", baseline="middle", fontSize=26, fontWeight="bold", dy=-8, color="white"
            ).encode(text="texto:N")
            
            texto_p = alt.Chart(pd.DataFrame({"texto": [f"{porcentaje}%"]})).mark_text(
                align="center", baseline="middle", fontSize=14, dy=16, color="gray"
            ).encode(text="texto:N")
            
            return (donut + texto_n + texto_p).properties(width=140, height=140)
    
        # --------------------------------------------------
        # 3. RENDERIZADO DE LOS KPIs (Línea 405)
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">Indicadores Generales</div></div>""", unsafe_allow_html=True)
    
        c1, c2, c3, c4 = st.columns(4)
    
        with c1:
            st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Total de pedidos</div>", unsafe_allow_html=True)
            # Ahora 'total' ya está definido arriba
            st.altair_chart(donut_con_numero(total, total, "#FFD700", COLOR_FALTANTE), use_container_width=True)
    
        with c2:
            st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Entregados</div>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(entregados, total, COLOR_AVANCE_ENTREGADOS, COLOR_FALTANTE), use_container_width=True)
    
        with c3:
            st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>En tránsito</div>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(en_transito, total, COLOR_AVANCE_TRANSITO, COLOR_FALTANTE), use_container_width=True)
    
        with c4:
            st.markdown("<div style='text-align:center; color:yellow; font-size:12px;'>Retrasados</div>", unsafe_allow_html=True)
            st.altair_chart(donut_con_numero(retrasados, total, COLOR_AVANCE_RETRASADOS, COLOR_FALTANTE), use_container_width=True)
        
        # --------------------------------------------------
        # TABLA DE ENVÍOS – DISEÑO PERSONALIZADO
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:24px; font-weight:700; margin:10px 0;">Lista de envíos</div></div>""", unsafe_allow_html=True)
    
        hoy_t = pd.Timestamp.today().normalize()
        df_mostrar = df_filtrado.copy()
    
        # Cálculo de días transcurridos y retraso para las columnas de la tabla
        df_mostrar["DIAS_TRANSCURRIDOS"] = (
            (df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy_t) - df_mostrar["FECHA DE ENVÍO"]).dt.days
        )
        df_mostrar["DIAS_RETRASO"] = (
            (df_mostrar["FECHA DE ENTREGA REAL"].fillna(hoy_t) - df_mostrar["PROMESA DE ENTREGA"]).dt.days
        )
        df_mostrar["DIAS_RETRASO"] = df_mostrar["DIAS_RETRASO"].apply(lambda x: x if x > 0 else 0)
    
        # Formateo de fechas para que se vean limpias (DD/MM/YYYY)
        df_mostrar["FECHA DE ENTREGA REAL"] = df_mostrar["FECHA DE ENTREGA REAL"].dt.strftime('%d/%m/%Y').fillna('')
        df_mostrar["FECHA DE ENVÍO"] = df_mostrar["FECHA DE ENVÍO"].dt.strftime('%d/%m/%Y').fillna('')
        df_mostrar["PROMESA DE ENTREGA"] = df_mostrar["PROMESA DE ENTREGA"].dt.strftime('%d/%m/%Y').fillna('')
    
        # --- FUNCIONES DE ESTILO CSS PARA LA TABLA ---
        def colorear_retraso(val):
            # Si hay días de retraso, fondo rojo y texto negro
            return 'background-color: #ff4d4d; color: black; font-weight: bold;' if val > 0 else ''
    
        def zebra_filas(row):
            # Alterna colores entre las filas para facilitar la lectura
            color = '#0E1117' if row.name % 2 == 0 else '#1A1E25'
            return [f'background-color: {color}; color: white;' for _ in row]
    
        # Renderizado de la tabla con los estilos aplicados
        st.dataframe(
            df_mostrar.style.apply(zebra_filas, axis=1)
                            .applymap(colorear_retraso, subset=["DIAS_RETRASO"])
                            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', 'orange'), ('color', 'white'), ('font-weight','bold'), ('font-size','14px')]},
                {'selector': 'td', 'props': [('padding', '12px')]}
            ]),
            use_container_width=True,
            height=520
        )
    
        # --------------------------------------------------
        # GRÁFICOS DE BARRAS POR PAQUETERÍA (CON ETIQUETAS)
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:18px; font-weight:700; margin:10px 0;">Análisis por Paquetería</div></div>""", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
    
        # Gráfico 1: En Tránsito por Fletera
        df_t = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "EN TRANSITO"].groupby("FLETERA").size().reset_index(name="CANTIDAD")
        if not df_t.empty:
            # Definimos la base de la barra
            base_t = alt.Chart(df_t).encode(
                x=alt.X("FLETERA:N", title="Paquetería", sort='-y'),
                y=alt.Y("CANTIDAD:Q", title="Pedidos"),
                tooltip=["FLETERA", "CANTIDAD"]
            )
            
            # Color y forma de la barra
            chart_t = base_t.mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).properties(height=300)
            
            # Etiqueta numérica superior
            text_t = base_t.mark_text(
                align='center', baseline='bottom', dy=-10, fontSize=14, fontWeight='bold', color='white'
            ).encode(text=alt.Text("CANTIDAD:Q"))
            
            g1.markdown("<h5 style='text-align:center; color:yellow;'>En tránsito / En tiempo</h5>", unsafe_allow_html=True)
            g1.altair_chart((chart_t + text_t), use_container_width=True)
    
        # Gráfico 2: Retrasados por Fletera
        df_r = df_filtrado[df_filtrado["ESTATUS_CALCULADO"] == "RETRASADO"].groupby("FLETERA").size().reset_index(name="CANTIDAD")
        if not df_r.empty:
            # Definimos la base de la barra
            base_r = alt.Chart(df_r).encode(
                x=alt.X("FLETERA:N", title="Paquetería", sort='-y'),
                y=alt.Y("CANTIDAD:Q", title="Pedidos"),
                tooltip=["FLETERA", "CANTIDAD"]
            )
            
            # Color y forma de la barra
            chart_r = base_r.mark_bar(color="#F44336", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).properties(height=300)
            
            # Etiqueta numérica superior
            text_r = base_r.mark_text(
                align='center', baseline='bottom', dy=-10, fontSize=14, fontWeight='bold', color='white'
            ).encode(text=alt.Text("CANTIDAD:Q"))
            
            g2.markdown("<h5 style='text-align:center; color:#F44336;'>Sin entregar con retraso</h5>", unsafe_allow_html=True)
            g2.altair_chart((chart_r + text_r), use_container_width=True)
    
        # --------------------------------------------------
        # GRÁFICO: CONTEO DE PEDIDOS ENTREGADOS CON RETRASO (COLOR ROJO)
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:18px; font-weight:700; margin:30px 0 10px 0;">Pedidos Entregados con Retraso por Fletera</div></div>""", unsafe_allow_html=True)
    
        # 1. Filtramos: Solo los entregados donde la fecha real fue después de la promesa
        df_conteo_tarde = df_filtrado[
            (df_filtrado["FECHA DE ENTREGA REAL"].notna()) & 
            (df_filtrado["FECHA DE ENTREGA REAL"] > df_filtrado["PROMESA DE ENTREGA"])
        ].copy()
    
        # 2. Agrupamos por Fletera y contamos pedidos
        df_resumen_conteo = df_conteo_tarde.groupby("FLETERA").size().reset_index(name="CANTIDAD_PEDIDOS")
    
        if not df_resumen_conteo.empty:
            # 3. Gráfica de barras con Color Rojo
            chart_conteo = alt.Chart(df_resumen_conteo).mark_bar(
                color="#FF0000",  # ROJO PURO
                cornerRadiusTopLeft=8, 
                cornerRadiusTopRight=8
            ).encode(
                x=alt.X("FLETERA:N", title="Paquetería", sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y("CANTIDAD_PEDIDOS:Q", title="Número de Pedidos"),
                tooltip=["FLETERA", "CANTIDAD_PEDIDOS"]
            ).properties(height=400)
    
            # 4. Etiqueta con el número de pedidos sobre la barra
            text_conteo = chart_conteo.mark_text(
                align='center', 
                baseline='bottom', 
                dy=-10, 
                fontSize=18, 
                fontWeight='bold', 
                color='white'
            ).encode(text=alt.Text("CANTIDAD_PEDIDOS:Q"))
    
            st.altair_chart((chart_conteo + text_conteo), use_container_width=True)
            st.caption("Gráfico basado en la diferencia entre Fecha Real y Fecha Promesa.")
        else:
            st.success("✅ No hay registros de pedidos entregados tarde.")
        
        # --------------------------------------------------
        # GRÁFICO EXCLUSIVO: RETRASO PROMEDIO (DÍAS) + NOTA
        # --------------------------------------------------
        import datetime
    
        st.markdown("<h5 style='text-align:center; color:white;'>Retraso Promedio por Paquetería</h5>", unsafe_allow_html=True)
    
        # 1. Preparación de datos (Reactivo a df_filtrado)
        df_entregados_p = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        
        if not df_entregados_p.empty:
            # Cálculo de la desviación en días
            df_entregados_p["DIAS_DESVIACION"] = (
                (df_entregados_p["FECHA DE ENTREGA REAL"] - df_entregados_p["PROMESA DE ENTREGA"]).dt.days
            )
    
            # Promedio por Fletera
            df_prom = df_entregados_p.groupby("FLETERA")["DIAS_DESVIACION"].mean().reset_index(name="PROMEDIO")
    
            # 2. Creación del Gráfico Horizontal
            chart_prom = alt.Chart(df_prom).mark_bar(
                cornerRadiusTopRight=8, 
                cornerRadiusBottomRight=8
            ).encode(
                y=alt.Y("FLETERA:N", title=None, sort='-x'),
                x=alt.X("PROMEDIO:Q", title="Días promedio"),
                color=alt.condition(
                    alt.datum.PROMEDIO > 0, 
                    alt.value("#F39C12"), # Naranja si hay retraso
                    alt.value("#2ECC71")  # Verde si es a tiempo/antes
                )
            ).properties(height=400)
            
            # Etiquetas de número con un decimal
            text_prom = chart_prom.mark_text(
                align='left', baseline='middle', dx=5, fontSize=15, fontWeight='bold', color='white'
            ).encode(text=alt.Text("PROMEDIO:Q", format='.1f'))
            
            st.altair_chart((chart_prom + text_prom), use_container_width=True)
    
            # 3. Nota Dinámica Diaria
            fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
            peor_fletera = df_prom.sort_values(by="PROMEDIO", ascending=False).iloc[0]
            
            if peor_fletera["PROMEDIO"] > 0:
                st.error(f"🔍 **Diagnóstico Logístico al {fecha_hoy}:** El mayor impacto en la espera del cliente lo tiene **{peor_fletera['FLETERA']}** con un retraso promedio de **{peor_fletera['PROMEDIO']:.1f} días**.")
            else:
                st.success(f"✨ **Reporte al {fecha_hoy}:** Todas las fleteras están operando a tiempo o antes de lo prometido.")
    
            # Guía visual fija
            st.info("💡 **Guía rápida:** Barras Verdes = Buen servicio | Barras Naranjas = Retraso promedio.")
        else:
            st.warning("No hay datos de entregas finalizadas para calcular el promedio.")
    
        # --------------------------------------------------
        # RANKING DE CALIDAD: MEJOR A PEOR FLETERA (MENOS FALLOS A MÁS)
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:18px; font-weight:700; margin:30px 0 10px 0;">Ranking de Calidad por Paquetería</div></div>""", unsafe_allow_html=True)
    
        # 1. Filtramos los entregados tarde
        df_entregas_tarde = df_filtrado[
            (df_filtrado["FECHA DE ENTREGA REAL"].notna()) & 
            (df_filtrado["FECHA DE ENTREGA REAL"] > df_filtrado["PROMESA DE ENTREGA"])
        ].copy()
    
        # 2. Contamos fallos por fletera
        df_ranking = df_entregas_tarde.groupby("FLETERA").size().reset_index(name="CANTIDAD_FALLOS")
        
        # 3. Incluimos a las fleteras que tienen 0 fallos para que aparezcan como las "mejores"
        todas_las_fleteras = pd.DataFrame(df_filtrado["FLETERA"].unique(), columns=["FLETERA"])
        df_ranking_completo = pd.merge(todas_las_fleteras, df_ranking, on="FLETERA", how="left").fillna(0)
    
        if not df_ranking_completo.empty:
            # 4. Gráfica de barras - Ordenada de Menos Fallos (Mejor) a Más Fallos (Peor)
            chart_ranking = alt.Chart(df_ranking_completo).mark_bar(
                cornerRadiusTopLeft=8, 
                cornerRadiusTopRight=8
            ).encode(
                # sort='y' ordena de menor a mayor (la mejor fletera primero)
                x=alt.X("FLETERA:N", title="Paquetería (Mejor → Peor)", sort='y', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("CANTIDAD_FALLOS:Q", title="Total de Pedidos Tarde"),
                # Color dinámico: Verde si es 0, Rojo si tiene fallos
                color=alt.condition(
                    alt.datum.CANTIDAD_FALLOS == 0,
                    alt.value("#2ECC71"), # Verde para las perfectas
                    alt.value("#FF0000")  # Rojo para las que tienen fallos
                ),
                tooltip=["FLETERA", "CANTIDAD_FALLOS"]
            ).properties(height=400)
    
            # 5. Etiqueta numérica
            text_ranking = chart_ranking.mark_text(
                align='center', baseline='bottom', dy=-10, fontSize=16, fontWeight='bold', color='white'
            ).encode(text=alt.Text("CANTIDAD_FALLOS:Q"))
    
            st.altair_chart((chart_ranking + text_ranking), use_container_width=True)
            st.caption("🏆 Las fleteras a la izquierda son las más cumplidas (menos fallos).")
        
        # --------------------------------------------------
        # SECCIÓN UNIFICADA: ANÁLISIS DE EXPERIENCIA (LUPA)
        # --------------------------------------------------
        st.markdown("""<div style="text-align:center;"><div style="color:white; font-size:18px; font-weight:700; margin:30px 0 10px 0;">Ananlisis por Paquetería: Distribución de Experiencia</div></div>""", unsafe_allow_html=True)
    
        # 1. Selector único para controlar el gráfico
        lista_fleteras = ["TODAS"] + sorted(df_filtrado["FLETERA"].unique().tolist())
        fletera_seleccionada = st.selectbox("Selecciona una paquetería para analizar su detalle de entregas:", lista_fleteras)
    
        # 2. Filtrado dinámico
        df_lupa = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        if fletera_seleccionada != "TODAS":
            df_lupa = df_lupa[df_lupa["FLETERA"] == fletera_seleccionada]
        
        # Cálculo de días de diferencia
        df_lupa["DIAS_DIF"] = (df_lupa["FECHA DE ENTREGA REAL"] - df_lupa["PROMESA DE ENTREGA"]).dt.days
    
        if not df_lupa.empty:
            # 3. Gráfico Único de Distribución
            df_dist_lupa = df_lupa.groupby("DIAS_DIF").size().reset_index(name="PEDIDOS")
            
            chart_lupa = alt.Chart(df_dist_lupa).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X("DIAS_DIF:Q", title="Días de diferencia (Negativo = Antes / Positivo = Retraso)"),
                y=alt.Y("PEDIDOS:Q", title="Número de Entregas"),
                color=alt.condition(
                    alt.datum.DIAS_DIF <= 0,
                    alt.value("#2ECC71"), # Verde: A tiempo
                    alt.value("#E74C3C")  # Rojo: Retraso
                ),
                tooltip=["DIAS_DIF", "PEDIDOS"]
            ).properties(height=400)
    
            # Etiquetas numéricas sobre las barras
            text_lupa = chart_lupa.mark_text(align='center', baseline='bottom', dy=-10, fontWeight='bold', color='white').encode(
                text=alt.Text("PEDIDOS:Q")
            )
    
            st.altair_chart((chart_lupa + text_lupa), use_container_width=True)
    
            # 4. Tip dinámico según la selección
            st.info(f"💡 **Tip de Atención:** Estás viendo la distribución de **{fletera_seleccionada}**. La barra más alta en el lado rojo indica el retraso más frecuente para esta selección.")
        else:
            st.warning("No hay datos disponibles para esta paquetería.")
        
        # --------------------------------------------------
        # TABLA SCORECARD: CALIFICACIÓN DE FLETERAS
        # --------------------------------------------------
        st.markdown("<h5 style='text-align:center; color:white;'>🏆 Scorecard de Desempeño Logístico</h5>", unsafe_allow_html=True)
    
        # 1. Agrupamos métricas clave por fletera
        # Calculamos total de pedidos, cuántos tarde y el promedio de días
        resumen_score = df_filtrado[df_filtrado["FECHA DE ENTREGA REAL"].notna()].copy()
        resumen_score["ES_TARDE"] = (resumen_score["FECHA DE ENTREGA REAL"] > resumen_score["PROMESA DE ENTREGA"])
        resumen_score["DIAS_DIF"] = (resumen_score["FECHA DE ENTREGA REAL"] - resumen_score["PROMESA DE ENTREGA"]).dt.days
    
        df_score = resumen_score.groupby("FLETERA").agg(
            Total_Entregas=('FLETERA', 'count'),
            Pedidos_Tarde=('ES_TARDE', 'sum'),
            Promedio_Dias=('DIAS_DIF', 'mean')
        ).reset_index()
    
        # 2. Calculamos % de Eficiencia (Entregas a tiempo)
        df_score["Eficiencia"] = ((1 - (df_score["Pedidos_Tarde"] / df_score["Total_Entregas"])) * 100).round(1)
        df_score["Promedio_Dias"] = df_score["Promedio_Dias"].round(1)
    
        # 3. Función para asignar Medalla/Calificación
        def asignar_calificacion(row):
            if row["Eficiencia"] >= 95 and row["Promedio_Dias"] <= 0:
                return "⭐ EXCELENTE"
            elif row["Eficiencia"] >= 80:
                return "✅ CONFIABLE"
            elif row["Eficiencia"] >= 60:
                return "⚠️ EN OBSERVACIÓN"
            else:
                return "🚨 CRÍTICO"
    
        df_score["Calificación"] = df_score.apply(asignar_calificacion, axis=1)
    
        # 4. Ordenar por Eficiencia (Mejor a peor)
        df_score = df_score.sort_values(by="Eficiencia", ascending=False)
    
        # 5. Mostrar tabla con estilo
        def color_score(val):
            if "EXCELENTE" in str(val): return 'color: #2ECC71; font-weight: bold'
            if "CONFIABLE" in str(val): return 'color: #3498DB; font-weight: bold'
            if "OBSERVACIÓN" in str(val): return 'color: #F39C12; font-weight: bold'
            if "CRÍTICO" in str(val): return 'color: #E74C3C; font-weight: bold'
            return ''
    
        st.dataframe(
            df_score.style.applymap(color_score, subset=["Calificación"]),
            use_container_width=True,
            hide_index=True
        )
        
        # --------------------------------------------------
        # FINAL DE PÁGINA Y BOTÓN A KPIs
        # --------------------------------------------------
        st.divider()
        col_esp, col_btn = st.columns([4, 1])
        with col_btn:
            # Este es el botón que cambia el estado para ir a la otra página
            if st.button("📊 Ver KPIs Detallados", use_container_width=True):
                st.session_state.pagina = "KPIs"
                st.rerun()
    
        st.markdown("<div style='text-align:center; color:gray;'>© 2026 Logística - Vista Operativa</div>", unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # BLOQUE 9: PÁGINA DE KPIs (Alineado con el IF principal)
    # ------------------------------------------------------------------
    elif st.session_state.pagina == "KPIs":
        st.markdown("<h1 style='text-align:center; color:#00FFAA;'>📈 Análisis Detallado de KPIs</h1>", unsafe_allow_html=True)
        st.divider()
    
        # Métricas ejemplo para la segunda página
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Eficiencia Total", f"{(len(df[df['ESTATUS_CALCULADO'] == 'ENTREGADO']) / len(df) * 100):.1f}%")
        with m2:
            st.metric("Costo Promedio", "$450 MXN", "+5%")
        with m3:
            st.metric("Total General", len(df))
    
        st.write("##")
        st.info("💡 Esta es tu nueva página de KPIs. Aquí puedes agregar análisis gerenciales profundos.")

               
        # Botón para regresar
        if st.button("⬅ Volver al Inicio", use_container_width=True):
            st.session_state.pagina = "principal"
            st.rerun()
    
        st.markdown("<div style='text-align:center; color:gray; margin-top:20px;'>© 2026 Vista Gerencial</div>", unsafe_allow_html=True)




















































































































































































































































































































































































