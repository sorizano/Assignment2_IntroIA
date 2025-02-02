import streamlit as st
import time
from datetime import datetime
import json

st.set_page_config(layout="wide")

# Estado inicial de la cerradura
cerradura_estado = {
    "cerrado": True,
    "seguro": False,
    "usuarios": {},
    "celulares": {
        "Cel_mon": 0,
        "Cel_father": 0,
        "Cel_son": 0
    },
    "hora_actual": datetime.now().strftime("%H:%M")
}

# Cargar usuarios desde un archivo JSON
def cargar_usuarios():
    try:
        with open("usuarios.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"mama": "1234", "papa": "5678", "hijo": "9012"}

cerradura_estado["usuarios"] = cargar_usuarios()

# Guardar usuarios en archivo JSON
def guardar_usuarios():
    with open("usuarios.json", "w") as file:
        json.dump(cerradura_estado["usuarios"], file)

# Definir ubicaciones y distancias
ubicaciones = {
    "Casa": 0,
    "Lavandería - 2km": 2.0,
    "Mall - 1.6km": 1.6,
    "Farmacia - 1.2km": 1.2
}

st.title("Simulación de Cerradura Digital Inteligente")

# Control de Hora
hora_editable = st.sidebar.time_input("Selecciona la hora", datetime.strptime(cerradura_estado["hora_actual"], "%H:%M").time())
cerradura_estado["hora_actual"] = hora_editable.strftime("%H:%M")

# Evaluación de cierre y seguro según la hora
hora_actual_horas = int(cerradura_estado["hora_actual"].split(":")[0])
if 22 <= hora_actual_horas or hora_actual_horas < 6:
    cerradura_estado["cerrado"] = True
    cerradura_estado["seguro"] = True
else:
    cerradura_estado["cerrado"] = False
    cerradura_estado["seguro"] = False

# Simulación de alerta por intento no autorizado
top_alert = ""
if cerradura_estado["cerrado"] and cerradura_estado["seguro"]:
    top_alert = """
    <h2 style='text-align: center; color: red; font-weight: bold;'>
    ¡Alerta! Intento de apertura no autorizado se ha reportado al Administrador
    </h2>
    """
    st.markdown(top_alert, unsafe_allow_html=True)

# Estado de la cerradura en dos columnas
col_estado1, col_estado2 = st.columns(2)
with col_estado1:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Cerradura</h2>
        <h1 style='text-align: center; color:{'red' if cerradura_estado['cerrado'] else 'green'}; font-weight: bold;'>
        {'Cerrado' if cerradura_estado['cerrado'] else 'Abierto'}</h1>
    """, unsafe_allow_html=True)
with col_estado2:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Seguro</h2>
        <h1 style='text-align: center; color:{'red' if cerradura_estado['seguro'] else 'green'}; font-weight: bold;'>
        {'Cerrado' if cerradura_estado['seguro'] else 'Abierto'}</h1>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Ubicación de Celulares")
    for celular in cerradura_estado["celulares"].keys():
        cerradura_estado["celulares"][celular] = st.selectbox(f"Ubicación de {celular}", options=list(ubicaciones.keys()), index=0)

with col2:
    st.header("Gestión de Usuarios")
    st.write("Registro de usuarios en archivo")
    nuevo_usuario = st.text_input("Nuevo usuario")
    nuevo_pin = st.text_input("PIN", type="password")
    if st.button("Registrar Usuario"):
        if nuevo_usuario and nuevo_pin:
            cerradura_estado["usuarios"][nuevo_usuario] = nuevo_pin
            guardar_usuarios()
            st.success(f"Usuario {nuevo_usuario} registrado con éxito")
        else:
            st.error("Ingrese usuario y PIN")
    
    ingresado_pin = st.text_input("Ingrese PIN para abrir", type="password")
    if ingresado_pin in cerradura_estado["usuarios"].values() and not (22 <= hora_actual_horas or hora_actual_horas < 6):
        cerradura_estado["cerrado"] = False
        cerradura_estado["seguro"] = False
        st.success("Cerradura abierta correctamente")
    elif ingresado_pin:
        st.error("PIN incorrecto o no se puede abrir en este horario")

with col3:
    st.header("Forzar Apertura")
    if st.button("Forzar Apertura de Cerradura") and not (22 <= hora_actual_horas or hora_actual_horas < 6):
        cerradura_estado["cerrado"] = False
        st.warning("Cerradura forzada manualmente")
    if st.button("Forzar Apertura de Seguro") and not (22 <= hora_actual_horas or hora_actual_horas < 6):
        cerradura_estado["seguro"] = False
        st.warning("Seguro forzado manualmente")

st.subheader("Registro de Estado")
st.json(cerradura_estado)
