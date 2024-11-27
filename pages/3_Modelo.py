import streamlit as st
import pandas as pd
import pickle
import mysql.connector
from datetime import datetime

# Función para conectar a la base de datos
def conectar_base_datos():
    conn = st.connection('mysql', type='sql')
    return conn


# Función para extraer y mostrar datos
def mostrar_datos(tabla):
    conn = conectar_base_datos()
    query = f"SELECT * FROM {tabla}"
    conn.query(query)  # Consulta SQL
    df = conn.query(query) # Extraer datos como DataFrame

    return df

# Título de la aplicación
st.title("Predicción del Precio al Contado")

tabla = "vista_prestaciones"

st.dataframe(mostrar_datos(tabla))


# MODELO

# Cargar modelo
@st.cache_resource
def load_model():
    with open('notebooks/modelo/mejor_modelo.pkl', 'rb') as file:
        return pickle.load(file)

# Uso del modelo
data = mostrar_datos(tabla)
model = load_model()



# Pedir entrada de usuario para las características
st.header("Introduce las características para la predicción")



# Creamos la columna fecha_matriculacion para calcular la antigüedad del coche en años

data['fecha_matriculacion'] = (
    '01/' + data['mes_matriculacion'].astype(int).astype(str) + 
    '/' + data['ano_matriculacion'].astype(int).astype(str))

data['fecha_matriculacion'] = pd.to_datetime(data['fecha_matriculacion'], format='%d/%m/%Y')
current_date = pd.to_datetime(datetime.now())

data['antiguedad_coche'] = ((current_date - data['fecha_matriculacion']).dt.days / 365.25).round(2)



# Creamos los inputs para el usuario

import streamlit as st
import pandas as pd

categorical_features = ["marca", "modelo", "distintivo_ambiental", "tipo_cambio", "combustible", "num_puertas"]
numeric_features = ["potencia_cv", "antiguedad_coche"]

input_data = {}


for feature in categorical_features:
    input_data[feature] = st.selectbox(f"Selecciona {feature.replace('_', ' ')}:", data[feature].unique())

for feature in numeric_features:
    input_data[feature] = st.number_input(f"Introduce {feature.replace('_', ' ')}:", min_value=0, step=1)

# Botón para guardar los datos en un DataFrame
if st.button("Guardar datos"):
    # Convertir a un DataFrame
    df = pd.DataFrame([input_data])
    st.write("Datos guardados en el DataFrame:")
    st.dataframe(df)



# Convertir los datos ingresados en un DataFrame
input_df = pd.DataFrame([input_data])

# Botón para predecir
if st.button("Predecir"):
    try:
        # Realizar la predicción
        prediction = model.predict(input_df)[0]
        st.success(f"El precio contado predicho es: €{prediction:.2f}")
    except Exception as e:
        st.error(f"Ocurrió un error durante la predicción: {e}")


