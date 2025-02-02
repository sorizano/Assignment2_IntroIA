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

# Estado de la cerradura en dos columnas
col_estado1, col_estado2 = st.columns(2)
with col_estado1:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de la Cerradura</h2>
        <h1 style='text-align: center;'>Cerrado: <span style='color:{'green' if not cerradura_estado['cerrado'] else 'red'}; font-weight: bold;'>{'Sí' if cerradura_estado['cerrado'] else 'No'}</span></h1>
    """, unsafe_allow_html=True)
with col_estado2:
    st.markdown(f"""
        <h1 style='text-align: center;'>Seguro: <span style='color:{'green' if not cerradura_estado['seguro'] else 'red'}; font-weight: bold;'>{'Sí' if cerradura_estado['seguro'] else 'No'}</span></h1>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Control de Hora")
    hora_editable = st.time_input("Selecciona la hora", datetime.strptime(cerradura_estado["hora_actual"], "%H:%M").time())
    cerradura_estado["hora_actual"] = hora_editable.strftime("%H:%M")
    st.text(f"Hora actual: {cerradura_estado['hora_actual']}")

with col2:
    st.header("Ubicación de Celulares")
    for celular in cerradura_estado["celulares"].keys():
        cerradura_estado["celulares"][celular] = st.selectbox(f"Ubicación de {celular}", options=list(ubicaciones.keys()), index=0)

with col3:
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
    if ingresado_pin in cerradura_estado["usuarios"].values():
        cerradura_estado["cerrado"] = False
        cerradura_estado["seguro"] = False
        st.success("Cerradura abierta correctamente")
    elif ingresado_pin:
        st.error("PIN incorrecto")

# Evaluación de cierre y seguro
celulares_distancias = [ubicaciones[cerradura_estado["celulares"][c]] for c in cerradura_estado["celulares"]]

todos_fuera = all(d >= 1.5 for d in celulares_distancias)
algunos_cerca = any(d < 1.5 for d in celulares_distancias)

# Condiciones de horario
hora_actual_horas = int(cerradura_estado["hora_actual"].split(":")[0])
if 22 <= hora_actual_horas or hora_actual_horas < 6:
    cerradura_estado["cerrado"] = True
    cerradura_estado["seguro"] = True
elif todos_fuera:
    cerradura_estado["seguro"] = True
    cerradura_estado["cerrado"] = True
elif algunos_cerca:
    cerradura_estado["seguro"] = False
    cerradura_estado["cerrado"] = True

# Simulación de alerta por intento no autorizado
if not cerradura_estado["cerrado"] and ingresado_pin not in cerradura_estado["usuarios"].values():
    st.warning("¡Alerta! Intento de apertura no autorizado")

st.subheader("Registro de Estado")
st.json(cerradura_estado)
