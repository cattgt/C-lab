import streamlit as st
import datetime as dt
import pytz
from calendar_clab import GoogleCalendarManager

# Crear instancia del manejador de Google Calendar
calendar = GoogleCalendarManager()

# Mostrar logo (asegúrate de que el archivo esté en la misma carpeta)
st.image("logo_11.png", width=200)

# Título de la aplicación
st.title("Reserva de Horas C-LAB")

# Formulario para agendar
with st.form(key='appointment_form'):
    nombre = st.text_input("Ingresa tu nombre")
    motivo = st.text_input("Motivo de reserva")
    
    equipos = st.multiselect(
        "Selecciona los equipos que vas a utilizar:",
        [
            "MediaRecorder", "FaceReader", "The Observer XT", 
            "Tobii Glasses 3", "Tobii Glasses 2", "Tobii Spectrum", 
            "Biopac Acqknowledge", "Computadores", "Otro/no lo sé", "Ninguno"     
        ]
    )
    
    fecha = st.date_input("Selecciona el día de tu reserva", dt.date.today())
    hora_inicio = st.time_input("Hora de inicio", dt.time(9, 0))
    hora_fin = st.time_input("Hora de fin", dt.time(10, 0))
    
    submitted = st.form_submit_button("Agendar hora")

# Si se envía el formulario
if submitted:
    # Validación de campos
    if not nombre or not motivo:
        st.error("Por favor, completa todos los campos obligatorios: nombre y motivo.")
    elif hora_fin <= hora_inicio:
        st.error("La hora de fin debe ser posterior a la hora de inicio.")
    else:
        # Convertir datos a datetime con zona horaria
        tz = pytz.timezone('America/Santiago')
        start_datetime = tz.localize(dt.datetime.combine(fecha, hora_inicio))
        end_datetime = tz.localize(dt.datetime.combine(fecha, hora_fin))

        # Verificar que la fecha y hora no estén en el pasado
        if start_datetime < dt.datetime.now(tz):
            st.warning("No puedes agendar en una hora pasada.")
        else:
            resumen = f"{nombre} - {motivo} | Equipos: {', '.join(equipos)}"

            try:
                # Crear evento en Google Calendar
                calendar.create_event(
                    summary=resumen,
                    start_time=start_datetime.isoformat(),
                    end_time=end_datetime.isoformat(),
                    timezone='America/Santiago'
                )
                st.success(f"Reserva creada exitosamente para {nombre} el {fecha} de {hora_inicio} a {hora_fin}")
            except Exception as e:
                st.error(f"Ocurrió un error al crear la reserva: {e}")

