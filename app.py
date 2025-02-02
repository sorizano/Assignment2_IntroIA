import streamlit as st
import time
from datetime import datetime
import json

st.set_page_config(layout="wide")

# Inicializar el estado en la sesión si no existe
if "cerrado" not in st.session_state:
    st.session_state["cerrado"] = True
if "seguro" not in st.session_state:
    st.session_state["seguro"] = True  # Asegurar que empiece cerrado por defecto
if "forzado" not in st.session_state:
    st.session_state["forzado"] = False
if "hora_actual" not in st.session_state:
    st.session_state["hora_actual"] = datetime.now().strftime("%H:%M")

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
    "Farmacia - 1.2km": 1.2
}

st.title("Simulación de Cerradura Digital Inteligente")

# Forzar apertura siempre disponible
if st.button("Forzar Apertura"):
    st.session_state["cerrado"] = False
    st.session_state["seguro"] = False
    st.session_state["forzado"] = True
    st.warning("Cerradura y seguro forzados manualmente")
    st.rerun()

# Control de Hora
hora_editable = st.sidebar.time_input("Selecciona la hora", datetime.strptime(st.session_state["hora_actual"], "%H:%M").time())
st.session_state["hora_actual"] = hora_editable.strftime("%H:%M")

# Evaluación de cierre y seguro según la hora (Prioridad Alta)
hora_actual_horas = int(st.session_state["hora_actual"].split(":")[0])
if 22 <= hora_actual_horas or hora_actual_horas < 6:
    st.session_state["cerrado"] = True
    st.session_state["seguro"] = True
    st.session_state["forzado"] = False  # Reset de forzado si cambia la hora a este rango

# Simulación de alerta por intento no autorizado (cuando ambos están abiertos y fue por forzado)
if not st.session_state["cerrado"] and not st.session_state["seguro"] and st.session_state["forzado"]:
    st.markdown("""
    <h2 style='text-align: center; color: red; font-weight: bold;'>
    ¡Alerta! Intento de apertura no autorizado se ha reportado al Administrador
    </h2>
    """, unsafe_allow_html=True)

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

col1, col2 = st.columns(2)

with col1:
    st.header("Ubicación de Celulares")
    for celular in ["Cel_mon", "Cel_father", "Cel_son"]:
        st.selectbox(f"Ubicación de {celular}", options=list(ubicaciones.keys()), index=0)

with col2:
    st.header("Gestión de Usuarios")
    st.write("Registro de usuarios en archivo")
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
    if ingresado_pin in usuarios.values() and not (22 <= hora_actual_horas or hora_actual_horas < 6):
        st.session_state["cerrado"] = False
        st.session_state["seguro"] = False
        st.session_state["forzado"] = False  # No se considera forzado si se ingresó correctamente
        st.success("Cerradura abierta correctamente")
        st.rerun()
    elif ingresado_pin:
        st.error("PIN incorrecto o no permitido en este horario")

st.subheader("Registro de Estado")
st.json(st.session_state)
