import streamlit as st
from datetime import datetime
import json

st.set_page_config(layout="wide")

# Inicializar el estado en la sesión si no existe
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

# Cargar usuarios desde un archivo JSON
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

# Definir ubicaciones y distancias
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

# Determinar la distancia máxima de los celulares
distancias = []
col1, col2 = st.columns(2)
with col1:
    st.header("Ubicación de Celulares")
    for celular in ["Cel_mon", "Cel_father", "Cel_son"]:
        ubicacion = st.selectbox(f"Ubicación de {celular}", options=list(ubicaciones.keys()), index=0)
        distancias.append(ubicaciones[ubicacion])

st.session_state["distancia_max"] = max(distancias)

# Evaluación de cierre y seguro según la hora y distancia
hora_actual_horas = int(st.session_state["hora_actual"].split(":")[0])
if 22 <= hora_actual_horas or hora_actual_horas < 6:
    if not st.session_state["forzado"]:
        st.session_state["cerrado"] = True
        st.session_state["seguro"] = True
elif st.session_state["distancia_max"] >= 2.5:
    st.session_state["cerrado"] = True
    st.session_state["seguro"] = True
elif st.session_state["distancia_max"] >= 1.5:
    st.session_state["cerrado"] = True
    st.session_state["seguro"] = False
else:
    if not st.session_state["forzado"]:
        st.session_state["cerrado"] = False

# Estado de la cerradura en dos columnas
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

# Forzar apertura SIEMPRE DISPONIBLE
if st.button("Forzar Apertura"):
    st.session_state["cerrado"] = False
    st.session_state["seguro"] = False
    st.session_state["forzado"] = True
    st.warning("Cerradura y seguro forzados manualmente")
    st.markdown("""
    <h3 style='text-align: center; color: red;'>⚠️ ¡Alerta! Cerradura y seguro forzados. Se ha enviado un mensaje al administrador.</h3>
    """, unsafe_allow_html=True)
    st.rerun()

# Gestión de usuarios
with col2:
    st.header("Gestión de Usuarios")
    nuevo_usuario = st.text_input("Nuevo usuario")
    nuevo_pin = st.text_input("PIN", type="password")
    if st.button("Registrar Usuario"):
        if nuevo_usuario and nuevo_pin:
            usuarios[nuevo_usuario] = nuevo_pin
            guardar_usuarios()
            st.success(f"Usuario {nuevo_usuario} registrado con éxito")
        else:
            st.error("Ingrese usuario y PIN")
    
    ingresado_pin = st.text_input("Ingrese PIN para abrir", type="password")
    if ingresado_pin in usuarios.values():
        st.session_state["cerrado"] = False
        st.session_state["seguro"] = False
        st.session_state["forzado"] = False  # No se considera forzado si se ingresó correctamente
        st.success("Cerradura abierta correctamente")
        st.rerun()
    elif ingresado_pin:
        st.error("PIN incorrecto")

st.subheader("Registro de Estado")
st.json(st.session_state)