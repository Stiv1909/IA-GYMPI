# ia.py - Inteligencia adaptativa avanzada

import numpy as np
import random
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers

catalogo = [
    "Sentadillas", "Burpees", "Plancha", "Flexiones", "Peso muerto",
    "Zancadas", "Dominadas", "Mountain Climbers", "Abdominales", "Press Militar"
]

# ==========================
# Inicializar el modelo
# ==========================

def inicializar_modelo():
    model = keras.Sequential([
        layers.LSTM(64, input_shape=(3, 9)),
        layers.Dense(32, activation='relu'),
        layers.Dense(10, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ==========================
# Configurar ejercicios adaptativos
# ==========================

def configurar_ejercicio(nombre_ejercicio, experiencia, peso):
    if peso > 100 and nombre_ejercicio in ["Burpees", "Mountain Climbers"]:
        return None  # evitar ejercicios de impacto alto para personas con sobrepeso

    if experiencia == 0:
        repeticiones = 8
        series = 3
    elif experiencia == 1:
        repeticiones = 10
        series = random.choice([3, 4])
    else:
        repeticiones = 12
        series = 4
    return {"nombre": nombre_ejercicio, "repeticiones": repeticiones, "series": series}

# ==========================
# Generar rutina inicial
# ==========================

def generar_rutina(datos_usuario, modelo):
    secuencia = []
    for _ in range(3):
        tiempo_entrenamiento = random.randint(20, 90)
        ejercicios_realizados = random.randint(3, 10)
        nivel_cansancio = random.randint(1, 5)
        semana = [tiempo_entrenamiento, ejercicios_realizados, nivel_cansancio,
                  datos_usuario['edad'], datos_usuario['peso'], datos_usuario['altura'],
                  datos_usuario['sexo'], datos_usuario['experiencia'], datos_usuario['objetivo']]
        secuencia.append(semana)

    entrada_usuario = np.array([secuencia])
    prediccion = modelo.predict(entrada_usuario)[0]

    rutina_basica = []
    for i, p in enumerate(prediccion):
        if p > 0.5:
            ejercicio = configurar_ejercicio(catalogo[i], datos_usuario['experiencia'], datos_usuario['peso'])
            if ejercicio:
                rutina_basica.append(ejercicio)
    return rutina_basica

# ==========================
# Ajustar rutina cada semana
# ==========================

def ajustar_rutina_actual(rutina_actual, nivel_cansancio, experiencia, historial):
    max_reps = 15
    min_reps = 6
    nueva_rutina = rutina_actual.copy()

    # detectar cansancio alto prolongado
    cansancio_alto = [h for h in historial[-2:] if h['nivel_cansancio'] >= 4]

    if nivel_cansancio == 5 or len(cansancio_alto) >= 2:
        # reducción drástica
        nueva_rutina = [
            {"nombre": ej["nombre"],
             "repeticiones": max(min_reps, ej["repeticiones"] - 2),
             "series": max(2, ej["series"] - 1)}
            for ej in nueva_rutina
        ]
        if len(nueva_rutina) > 2:
            nueva_rutina.pop()
    elif nivel_cansancio <= 2:
        for ejercicio in nueva_rutina:
            if ejercicio['repeticiones'] < max_reps:
                ejercicio['repeticiones'] += 1
        if len(nueva_rutina) < 6:
            disponibles = [e for e in catalogo if e not in [ej['nombre'] for ej in nueva_rutina]]
            nuevo = random.choice(disponibles)
            extra = configurar_ejercicio(nuevo, experiencia, historial[-1]['peso'])
            if extra:
                nueva_rutina.append(extra)

    return nueva_rutina

# ==========================
# Registrar seguimiento
# ==========================

def registrar_seguimiento(historial, semana, dias, minutos_dia, ejercicios_realizados, nivel_cansancio, peso_actual):
    historial.append({
        "semana": semana,
        "dias_entrenados": dias,
        "minutos_promedio": minutos_dia,
        "ejercicios_realizados": ejercicios_realizados,
        "nivel_cansancio": nivel_cansancio,
        "peso": peso_actual
    })

# ==========================
# Análisis de progreso
# ==========================

def analizar_historial(historial, altura, objetivo):
    if len(historial) < 2:
        return "➖ Aún no hay suficiente información para analizar el progreso."

    progreso_texto = ""
    peso_inicial = historial[0]['peso']
    peso_actual = historial[-1]['peso']
    imc = lambda peso: peso / ((altura / 100) ** 2)

    if objetivo == 0 and peso_actual < peso_inicial:
        progreso_texto += "✅ ¡Vas bajando de peso como esperabas!\n"
    elif objetivo == 1 and peso_actual > peso_inicial:
        progreso_texto += "✅ ¡Has ganado peso, buena señal para aumentar músculo!\n"
    elif objetivo == 2 and abs(peso_actual - peso_inicial) < 1:
        progreso_texto += "✅ Tu peso se mantiene estable, buen trabajo.\n"
    else:
        progreso_texto += "⚠️ Tu peso no evoluciona según tu objetivo.\n"

    # analizar días de entrenamiento
    dias = historial[-1]['dias_entrenados']
    if dias < 2:
        progreso_texto += "📉 Entrenas muy pocos días. Intenta llegar a al menos 3 días.\n"
    elif dias > 5:
        progreso_texto += "🛑 Estás entrenando demasiado seguido. Asegura al menos 2 días de descanso.\n"
    else:
        progreso_texto += "📆 Buena frecuencia de entrenamiento semanal.\n"

    return progreso_texto

# ==========================
# Generar gráfica de progreso
# ==========================

def generar_grafica(historial):
    semanas = [h['semana'] for h in historial]
    ejercicios = [h['ejercicios_realizados'] for h in historial]
    peso = [h['peso'] for h in historial]

    plt.style.use("ggplot")
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Línea de ejercicios realizados
    ax1.plot(semanas, ejercicios, color='skyblue', linewidth=2, marker='o', label='Ejercicios Realizados')
    ax1.fill_between(semanas, ejercicios, color='skyblue', alpha=0.2)
    ax1.set_xlabel("Semana")
    ax1.set_ylabel("Ejercicios Realizados", color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')

    # Línea de peso corporal
    ax2 = ax1.twinx()
    ax2.plot(semanas, peso, color='orange', linestyle=':', marker='s', label='Peso (kg)')
    ax2.set_ylabel("Peso Corporal (kg)", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Título y leyenda
    plt.title("📈 Progreso de Entrenamiento")
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))
    plt.tight_layout()
    plt.show()
