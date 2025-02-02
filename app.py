import streamlit as st
from datetime import datetime
import json

st.set_page_config(layout="wide")

# Inicialización del estado en sesión
if "cerrado" not in st.session_state:
    st.session_state["cerrado"] = True
if "seguro" not in st.session_state:
    st.session_state["seguro"] = True
if "forzado" not in st.session_state:
    st.session_state["forzado"] = False
if "hora_actual" not in st.session_state:
    st.session_state["hora_actual"] = datetime.now().strftime("%H:%M")
if "distancia_max" not in st.session_state:
    st.session_state["distancia_max"] = 0

# Funciones para cargar y guardar usuarios
def cargar_usuarios():
    try:
        with open("usuarios.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"mama": "1234", "papa": "5678", "hijo": "9012"}

usuarios = cargar_usuarios()

def guardar_usuarios():
    with open("usuarios.json", "w") as file:
        json.dump(usuarios, file)

# Definición de ubicaciones y distancias
ubicaciones = {
    "Casa": 0,
    "Lavandería - 2km": 2.0,
    "Mall - 1.6km": 1.6,
    "Farmacia - 1.2km": 1.2,
    "Oficina - 2.5km": 2.5,
    "Aeropuerto - 3km": 3.0
}

st.title("Simulación de Cerradura Digital Inteligente")

# Control de Hora
hora_editable = st.sidebar.time_input("Selecciona la hora", datetime.strptime(st.session_state["hora_actual"], "%H:%M").time())
st.session_state["hora_actual"] = hora_editable.strftime("%H:%M")

# Dividimos la interfaz en dos columnas principales:
# - La columna izquierda se usará para la detección de celulares (ubicación)
# - La columna derecha para la gestión de usuarios y autenticación vía PIN
col_left, col_right = st.columns(2)

# --------------------------
# Columna Izquierda: Ubicación de Celulares
# --------------------------
with col_left:
    st.header("Ubicación de Celulares")
    distancias = []
    # Usamos una clave única para cada selectbox para evitar conflictos
    for celular in ["Cel_mon", "Cel_father", "Cel_son"]:
        ubicacion = st.selectbox(
            f"Ubicación de {celular}",
            options=list(ubicaciones.keys()),
            key=celular
        )
        distancias.append(ubicaciones[ubicacion])
    # Guardamos la distancia máxima (para otros usos) y también dejamos a la mano la lista de distancias
    st.session_state["distancia_max"] = max(distancias)

# --------------------------
# Columna Derecha: Gestión de Usuarios y PIN
# --------------------------
with col_right:
    st.header("Gestión de Usuarios")
    nuevo_usuario = st.text_input("Nuevo usuario")
    nuevo_pin = st.text_input("PIN (para registrar)", type="password", key="nuevo_pin")
    if st.button("Registrar Usuario"):
        if nuevo_usuario and nuevo_pin:
            usuarios[nuevo_usuario] = nuevo_pin
            guardar_usuarios()
            st.success(f"Usuario '{nuevo_usuario}' registrado con éxito")
        else:
            st.error("Ingrese usuario y PIN para el registro")
    
    # Campo para la autenticación vía PIN
    ingresado_pin = st.text_input("Ingrese PIN para abrir", type="password", key="pin_input")

# ---------------------------------------------------
# Primero, evaluamos si se intenta abrir con PIN
# ---------------------------------------------------
if ingresado_pin:
    if ingresado_pin in usuarios.values():
        st.session_state["cerrado"] = False
        st.session_state["seguro"] = False
        st.session_state["forzado"] = False  # Se reinicia el modo forzado
        st.success("Cerradura abierta correctamente mediante PIN")
        st.experimental_rerun()
    else:
        st.error("PIN incorrecto")
# ---------------------------------------------------
# Si no se ha ingresado PIN, se procede a evaluar por la ubicación
# ---------------------------------------------------
elif not st.session_state["forzado"]:
    # Convertir la hora a un entero para la evaluación
    hora_actual_horas = int(st.session_state["hora_actual"].split(":")[0])
    # Evaluación en función de la hora
    if 22 <= hora_actual_horas or hora_actual_horas < 6:
        # Horario nocturno: se cierran ambos, sin importar la ubicación
        st.session_state["cerrado"] = True
        st.session_state["seguro"] = True
    else:
        # Horario diurno: se utiliza la ubicación (celulares)
        # Si TODOS los usuarios están alejados (mínima distancia >= 1.5 km):
        if min(distancias) >= 1.5:
            st.session_state["cerrado"] = True
            st.session_state["seguro"] = True
        else:
            # Si al menos uno está cerca, se cierra la cerradura pero se deja el seguro abierto.
            st.session_state["cerrado"] = True
            st.session_state["seguro"] = False

# --------------------------
# Botón para Forzar Apertura (si se requiere abrir manualmente)
# --------------------------
if st.button("Forzar Apertura"):
    st.session_state["cerrado"] = False
    st.session_state["seguro"] = False
    st.session_state["forzado"] = True
    st.markdown(
        "<h3 style='text-align: center; color: red;'>⚠️ ¡Alerta! Cerradura y seguro forzados. Se ha enviado un mensaje al administrador.</h3>",
        unsafe_allow_html=True
    )

# --------------------------
# Mostrar el estado en dos columnas
# --------------------------
col_estado1, col_estado2 = st.columns(2)
with col_estado1:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Cerradura</h2>
        <h1 style='text-align: center; color:{'red' if st.session_state['cerrado'] else 'green'}; font-weight: bold;'>
        {'Cerrado' if st.session_state['cerrado'] else 'Abierto'}</h1>
    """, unsafe_allow_html=True)
with col_estado2:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Seguro</h2>
        <h1 style='text-align: center; color:{'red' if st.session_state['seguro'] else 'green'}; font-weight: bold;'>
        {'Cerrado' if st.session_state['seguro'] else 'Abierto'}</h1>
    """, unsafe_allow_html=True)

st.subheader("Registro de Estado")
st.json(st.session_state)
