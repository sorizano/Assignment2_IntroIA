import streamlit as st
import time
from datetime import datetime
import random

st.set_page_config(layout="wide")

# Estado inicial de la cerradura
cerradura_estado = {
    "cerrado": True,
    "seguro": False,
    "usuarios": {
        "mama": "1234",
        "papa": "5678",
        "hijo": "9012"
    },
    "celulares": {
        "Cel_mon": 0,
        "Cel_father": 0,
        "Cel_son": 0
    },
    "hora_actual": datetime.now().strftime("%H:%M")
}

# Definir ubicaciones y distancias
ubicaciones = {
    "Casa": 0,
    "Lavandería": 2.0,
    "Mall": 1.6,
    "Farmacia": 1.2
}

st.title("Simulación de Cerradura Digital Inteligente")

# Estado de la cerradura en grande
st.markdown("""
    <h2 style='text-align: center;'>Estado de la Cerradura</h2>
    <h1 style='text-align: center;'>Cerrado: <span style='color:{}; font-weight: bold;'>{}</span></h1>
    <h1 style='text-align: center;'>Seguro: <span style='color:{}; font-weight: bold;'>{}</span></h1>
""".format(
    "red" if cerradura_estado["cerrado"] else "green", "Sí" if cerradura_estado["cerrado"] else "No",
    "red" if cerradura_estado["seguro"] else "green", "Sí" if cerradura_estado["seguro"] else "No"
), unsafe_allow_html=True)

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
    st.header("Usuarios y PINs")
    usuarios = cerradura_estado["usuarios"]
    for user, pin in usuarios.items():
        st.text(f"{user}: {pin}")
    ingresado_pin = st.text_input("Ingrese PIN", type="password")
    if ingresado_pin in usuarios.values():
        cerradura_estado["cerrado"] = False
        cerradura_estado["seguro"] = False
        st.success("Cerradura abierta correctamente")
    elif ingresado_pin:
        st.error("PIN incorrecto")

# Evaluación de cierre y seguro
celulares_distancias = [ubicaciones[cerradura_estado["celulares"][c]] for c in cerradura_estado["celulares"]]

todos_fuera = all(d >= 1.5 for d in celulares_distancias)
algunos_cerca = any(d < 1.5 for d in celulares_distancias)

if todos_fuera:
    cerradura_estado["seguro"] = True
    cerradura_estado["cerrado"] = True
elif algunos_cerca:
    cerradura_estado["seguro"] = False
    cerradura_estado["cerrado"] = True

# Condiciones de horario
if cerradura_estado["hora_actual"] == "06:00":
    cerradura_estado["seguro"] = False
elif cerradura_estado["hora_actual"] == "22:00":
    cerradura_estado["cerrado"] = True
    cerradura_estado["seguro"] = True

# Simulación de alerta por intento no autorizado
if not cerradura_estado["cerrado"] and ingresado_pin not in usuarios.values():
    st.warning("¡Alerta! Intento de apertura no autorizado")

st.subheader("Registro de Estado")
st.json(cerradura_estado)
