import streamlit as st
from datetime import datetime
import json

st.set_page_config(layout="wide")

# 🔄 Inicialización del estado en sesión
if "cerrado" not in st.session_state:
    st.session_state["cerrado"] = True
if "seguro" not in st.session_state:
    st.session_state["seguro"] = True
if "forzado" not in st.session_state:
    st.session_state["forzado"] = False  # ✅ Nuevo control para bloquear todo
if "hora_actual" not in st.session_state:
    st.session_state["hora_actual"] = datetime.now().strftime("%H:%M")
if "ubicaciones_usuarios" not in st.session_state:
    st.session_state["ubicaciones_usuarios"] = {}
if "pin_correcto" not in st.session_state:
    st.session_state["pin_correcto"] = False

# 📌 Función para cargar usuarios predefinidos
def cargar_usuarios():
    return {"mama": "1234", "papa": "5678", "hijo": "9012"}

usuarios = cargar_usuarios()

# 📌 Definición de ubicaciones y distancias
ubicaciones = {
    "Casa": 0,
    "Lavandería - 2km": 2.0,
    "Mall - 1.6km": 1.6,
    "Farmacia - 1.2km": 1.2,
    "Oficina - 2.5km": 2.5,
    "Aeropuerto - 3km": 3.0
}

st.title("Simulación de Cerradura Digital Inteligente")

# 🔴 Si la cerradura ha sido forzada, deshabilitar todo
desactivar_todo = st.session_state["forzado"]

# ⏰ Control de Hora en la barra lateral (Deshabilitado si la cerradura fue forzada)
hora_editable = st.sidebar.time_input("Selecciona la hora", datetime.strptime(st.session_state["hora_actual"], "%H:%M").time(), disabled=desactivar_todo)
st.session_state["hora_actual"] = hora_editable.strftime("%H:%M")

# 📌 Mostrar los usuarios registrados y sus PINs en la barra lateral
st.sidebar.markdown("### Usuarios Registrados")
usuarios_texto = "\n".join([f"**{usuario}**: {pin}" for usuario, pin in usuarios.items()])
st.sidebar.text_area("Usuarios y PINs", usuarios_texto, height=100, disabled=True)

# 🔄 Dividimos la interfaz en dos columnas principales
col_left, col_right = st.columns(2)

# --------------------------
# 📌 Columna Izquierda: Ubicación de Celulares
# --------------------------
with col_left:
    st.header("Ubicación de Celulares")
    distancias = []
    usuarios_en_casa = []

    for usuario in usuarios.keys():
        ubicacion = st.selectbox(
            f"Ubicación de {usuario}",
            options=list(ubicaciones.keys()),
            key=f"ubicacion_{usuario}",
            disabled=desactivar_todo  # 🔴 Bloquear si la cerradura fue forzada
        )
        st.session_state["ubicaciones_usuarios"][usuario] = ubicacion
        distancia_actual = ubicaciones[ubicacion]
        distancias.append(distancia_actual)

        if ubicacion == "Casa":
            usuarios_en_casa.append(usuario)
    
    st.session_state["distancia_max"] = max(distancias)

# ✅ **Regla Nocturna: Entre 10 PM y 6 AM, la cerradura y el seguro están cerrados**
hora_actual_horas = int(st.session_state["hora_actual"].split(":")[0])
if not desactivar_todo:  # Si la cerradura no ha sido forzada, aplicar reglas normales
    if 22 <= hora_actual_horas or hora_actual_horas < 6:
        st.session_state["cerrado"] = True
        st.session_state["seguro"] = True
    else:
        # ✅ **Regla de Distancia**: Si al menos un usuario está a menos de 1.5 km, el seguro se mantiene abierto.
        if min(distancias) < 1.5:
            st.session_state["seguro"] = False
        else:
            st.session_state["cerrado"] = True
            st.session_state["seguro"] = True

# --------------------------
# 📌 Columna Derecha: Autenticación por PIN
# --------------------------
with col_right:
    st.header("Autenticación de Usuario")
    
    usuario_seleccionado = st.selectbox("Seleccione su usuario:", usuarios_en_casa if usuarios_en_casa else ["(Nadie en casa)"], disabled=desactivar_todo)
    
    ingresado_pin = st.text_input("Ingrese PIN para abrir", type="password", key="pin_input", disabled=desactivar_todo)

# --------------------------
# 📌 Botones alineados horizontalmente
# --------------------------
col_boton1, col_boton2, col_boton3 = st.columns(3)

# ✅ **Botón para validar PIN y abrir la cerradura**
with col_boton1:
    if st.button("🔓 Abrir Casa", disabled=desactivar_todo):  # ❌ Deshabilitado si se usó "Forzar Apertura"
        if ingresado_pin and usuario_seleccionado in usuarios_en_casa:
            if ingresado_pin == usuarios[usuario_seleccionado]:
                st.session_state["cerrado"] = False
                st.session_state["seguro"] = False
                st.session_state["forzado"] = False
                st.session_state["pin_correcto"] = True
                st.success(f"✅ Cerradura abierta correctamente por {usuario_seleccionado}")
            else:
                st.session_state["pin_correcto"] = False
                st.error("❌ PIN incorrecto")
        elif ingresado_pin:
            st.error("❌ Solo los usuarios en casa pueden ingresar su PIN.")

# ✅ **Botón para cerrar la puerta (Solo si el PIN fue correcto)**
with col_boton2:
    if st.button("🔒 Cerrar Puerta", disabled=desactivar_todo or not st.session_state["pin_correcto"]):
        st.session_state["cerrado"] = True
        st.session_state["seguro"] = False
        st.session_state["pin_correcto"] = False
        st.warning("🚪 La puerta ha sido cerrada, pero el seguro sigue abierto.")

# 🔓 **Botón para Forzar Apertura Manual**
with col_boton3:
    if st.button("🔓 Forzar Apertura"):
        st.session_state["cerrado"] = False
        st.session_state["seguro"] = False
        st.session_state["forzado"] = True  # ✅ Activar el bloqueo total
        st.rerun()  # 🔄 Fuerza la recarga inmediata de la interfaz

# --------------------------
# 📌 Estado de la cerradura
# --------------------------
col_estado1, col_estado2 = st.columns(2)
with col_estado1:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Cerradura</h2>
        <h1 style='text-align: center; color:{'red' if st.session_state['cerrado'] else 'green'}; font-weight: bold;'>
        {'🔴 Cerrado' if st.session_state['cerrado'] else '🟢 Abierto'}</h1>
    """, unsafe_allow_html=True)
with col_estado2:
    st.markdown(f"""
        <h2 style='text-align: center;'>Estado de Seguro</h2>
        <h1 style='text-align: center; color:{'red' if st.session_state['seguro'] else 'green'}; font-weight: bold;'>
        {'🔴 Cerrado' if st.session_state['seguro'] else '🟢 Abierto'}</h1>
    """, unsafe_allow_html=True)

st.subheader("Registro de Estado")
st.json(st.session_state)
