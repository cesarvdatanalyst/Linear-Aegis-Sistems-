import streamlit as rcm_ui
import pandas as pd
import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import plotly.express as px

# --------------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y SISTEMA DE AUTENTICACIÓN
# --------------------------------------------------------------------
rcm_ui.set_page_config(page_title="Linear Aegis Systems | Clinical ETL", layout="wide")

if "autenticado" not in rcm_ui.session_state:
    rcm_ui.session_state["autenticado"] = False

# Credenciales de nivel institucional de acuerdo a la directiva 2026
USUARIO_VALIDO = "auditor_rcm"
CLAVE_VALIDA = "HipaaSecure2026!"

rcm_ui.title("🛡️ LINEAR AEGIS SYSTEMS")
rcm_ui.subheader("Plataforma Inteligente de Integridad de Datos Clínicos & ETL")

# Archivo persistente local para el tracking histórico sin conectarse a internet
HISTORIAL_FILE = "aegis_history_log.json"


def guardar_en_historial(nombre_archivo, total_filas, duplicados, dinero_riesgo):
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "archivo": nombre_archivo,
        "total_registros": total_filas,
        "duplicados_eliminados": duplicados,
        "dinero_en_riesgo": dinero_riesgo,
    }
    historial = []
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception:
            historial = []
    historial.append(registro)
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)


# Bloque de Control de Acceso Perimetral (Fiel al Protocolo HIPAA)
if not rcm_ui.session_state["autenticado"]:
    rcm_ui.write("---")
    rcm_ui.error("🔒 CONTROL DE ACCESO RESTRINGIDO - PROTOCOLO HIPAA")
    rcm_ui.info(
        "Esta terminal procesa Información de Salud Protegida (PHI). Identifíquese para desbloquear el pipeline."
    )

    with rcm_ui.form("formulario_login_aegis"):
        usuario = rcm_ui.text_input("Usuario Operador (Username)", autocomplete="username")
        clave = rcm_ui.text_input(
            "Contraseña de Seguridad (Password)",
            type="password",
            autocomplete="current-password",
        )
        boton_ingresar = rcm_ui.form_submit_button("Verificar Credenciales Aegis")

        if boton_ingresar:
            if usuario == USUARIO_VALIDO and clave == CLAVE_VALIDA:
                rcm_ui.session_state["autenticado"] = True
                rcm_ui.rerun()
            else:
                rcm_ui.error(
                    "❌ Credenciales incorrectas. Acceso denegado de acuerdo a la directiva Linear Aegis."
                )
else:
    # --------------------------------------------------------------------
    # 2. ARQUITECTURA DE LA INTERFAZ LOGUEADA (ESTRUCTURA DE PESTAÑAS)
    # --------------------------------------------------------------------
    rcm_ui.write(
        "Mitigación de Data Mismatch y Auditoría Financiera Automatizada de Reclamaciones Médicas."
    )

    if rcm_ui.sidebar.button("🔒 Cerrar Sesión Segura (Aegis Lock)"):
        rcm_ui.session_state["autenticado"] = False
        rcm_ui.rerun()

    tab_dashboard, tab_historial = rcm_ui.tabs(
        ["📊 Panel de Auditoría", "📂 Historial de Lotes"]
    )

    # Pestaña secundaria: Historial persistente local de auditorías pasadas
    with tab_historial:
        rcm_ui.header("📁 Registro de Auditorías Anteriores")
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
            df_logs = pd.DataFrame(logs)
            rcm_ui.dataframe(df_logs, use_container_width=True)
        else:
            rcm_ui.info(
                "No hay registros de auditorías previas ejecutadas en este nodo local."
            )

    # Pestaña principal: Flujo de trabajo en tiempo real
    with tab_dashboard:
        col_izquierda, col_derecha = rcm_ui.columns([1, 3])

        with col_izquierda:
            rcm_ui.header("⚙️ Controles")
            ejecutar_robot = rcm_ui.button("⚡ Ejecutar Extracción (Selenium Headless)")
            rcm_ui.write("---")
            archivo_manual = rcm_ui.file_uploader(
                "Cargar planilla de facturación (.xlsx, .csv)", type=["xlsx", "csv"]
            )

        datos_crudos = None
        origen_nombre = "Carga Manual"

        # --------------------------------------------------------------------
        # 3. MOTOR DE SCRAPING SEGURO (Selenium Chromium Headless para Linux)
        # --------------------------------------------------------------------
        if ejecutar_robot:
            origen_nombre = f"Robot_Selenium_{datetime.now().strftime('%H%M%S')}"
            with col_derecha:
                with rcm_ui.spinner(
                    "Abriendo Chromium Headless aislado en el núcleo local Linux..."
                ):
                    opciones = Options()
                    opciones.add_argument("--headless=new")
                    opciones.add_argument("--no-sandbox")
                    opciones.add_argument("--disable-dev-shm-usage")
                    opciones.add_argument("--disable-gpu")

                    # Detección automática del binario en Linux Mint / Debian / Ubuntu
                    for ruta_bin in ["/usr/bin/chromium", "/usr/bin/chromium-browser"]:
                        if os.path.exists(ruta_bin):
                            opciones.binary_location = ruta_bin
                            break

                    try:
                        driver = webdriver.Chrome(options=opciones)
                        driver.get("https://example.com")
                        time.sleep(1)
                        driver.quit()
                    except Exception:
                        pass

                    # Banco de pruebas interno para simulación del robot
                    datos_crudos = [
                        {
                            "SSN_ID": " 123-45-6789 ",
                            "Paciente": "Cesar Perez",
                            "Network_Type": "OON",
                            "Status_Cobro": "None",
                        },
                        {
                            "SSN_ID": "987-65-4321",
                            "Paciente": "John Doe",
                            "Network_Type": "In-Network",
                            "Status_Cobro": "150",
                        },
                        {
                            "SSN_ID": " 123-45-6789 ",
                            "Paciente": "Cesar Perez",
                            "Network_Type": "OON",
                            "Status_Cobro": "None",
                        },  # Duplicado
                        {
                            "SSN_ID": "456-11-2222",
                            "Paciente": "Mary Smith",
                            "Network_Type": "OON",
                            "Status_Cobro": "",
                        },  # Vacío
                        {
                            "SSN_ID": "555-66-7777",
                            "Paciente": "ana gomez ",
                            "Network_Type": "In-Network",
                            "Status_Cobro": "300",
                        },
                    ]

        # Intercepción del archivo manual subido por el usuario
        if archivo_manual is not None:
            origen_nombre = archivo_manual.name
            try:
                if archivo_manual.name.endswith(".csv"):
                    datos_df_manual = pd.read_csv(archivo_manual)
                else:
                    datos_df_manual = pd.read_excel(archivo_manual)
                datos_crudos = datos_df_manual.to_dict(orient="records")
            except Exception as e:
                with col_derecha:
                    rcm_ui.error(f"❌ Error al procesar el archivo cargado: {e}")

        # --------------------------------------------------------------------
        # 4. MOTOR ETL CON RESALTADO ESTÉTICO Y VALORIZACIÓN MONETARIA
        # --------------------------------------------------------------------
        if datos_crudos is not None:
            df = pd.DataFrame(datos_crudos)

            columnas_requeridas = {
                "SSN_ID",
                "Paciente",
                "Network_Type",
                "Status_Cobro",
            }
            if not columnas_requeridas.issubset(set(df.columns)):
                with col_derecha:
                    rcm_ui.error(
                        f"❌ El archivo no contiene las columnas obligatorias: {', '.join(columnas_requeridas)}"
                    )
            else:
                total_inicial = len(df)

                # Regla 1: Limpieza de cadenas para remover Data Mismatch invisibles
                df["SSN_ID"] = df["SSN_ID"].astype(str).str.strip()
                df["Paciente"] = df["Paciente"].astype(str).str.strip().str.upper()

                # Regla 2: Mapeo estricto de duplicados antes de remover para marcado cromático
                es_duplicado = df["SSN_ID"].duplicated(keep=False)
                df_unicos = df.drop_duplicates()
                duplicados_eliminados = total_inicial - len(df_unicos)

                # Regla 3: Sanitización y conversión matemática del capital médico en riesgo
                def limpiar_montos(valor):
                    val_str = str(valor).replace("$", "").strip()
                    if val_str in ["", "None", "none", "nan", "NaN"]:
                        return 0.0
                    try:
                        return float(val_str)
                    except Exception:
                        return 0.0

                df["Monto_Numerico"] = df["Status_Cobro"].apply(limpiar_montos)
