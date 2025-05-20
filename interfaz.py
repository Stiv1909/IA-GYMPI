import json
import os
import winsound
from PIL import Image, ImageTk
import queue
import tkinter as tk
import ttkbootstrap as ttk
from ia import (inicializar_modelo, generar_rutina, ajustar_rutina_actual,
                registrar_seguimiento, analizar_historial, generar_grafica)

# Variables globales
modelo = inicializar_modelo()
datos_usuario = {}
rutina_actual = []
historial = []
semana_actual = 1
modo_seguimiento = False
DATA_FILE = "gympi_data.json"

def guardar_datos():
    data = {
        "datos_usuario": datos_usuario,
        "historial": historial,
        "semana_actual": semana_actual,
        "rutina_actual": rutina_actual
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def cargar_datos():
    global datos_usuario, historial, semana_actual, rutina_actual
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            datos_usuario = data.get("datos_usuario", {})
            historial = data.get("historial", [])
            semana_actual = data.get("semana_actual", 1)
            rutina_actual = data.get("rutina_actual", [])
            return True
    return False

# Crear ventana principal
app = ttk.Window(themename="superhero")
mensaje_queue = queue.Queue()
procesando_mensaje = False
app.title("GymPI - Entrenador Virtual")
app.geometry("480x700")   # Tamaño compacto tipo Messenger
app.resizable(False, True)  # Solo permitir scroll vertical

frame_chat = tk.Frame(app, bg="#1a1a1a")
frame_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(frame_chat, bg="#1a1a1a", highlightthickness=0)
scrollbar = ttk.Scrollbar(frame_chat, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

entry_frame = ttk.Frame(app)
entry_frame.pack(fill=tk.X, padx=10, pady=10)

# Funciones

def enviar_mensaje(texto, emisor="bot", delay=10):
    def mostrar():
        nonlocal texto, emisor, delay
        global procesando_mensaje

        contenedor_exterior = tk.Frame(scrollable_frame, bg="#1a1a1a")
        contenedor_exterior.pack(fill="x", pady=5, padx=10)

        contenedor_burbuja = tk.Frame(
            contenedor_exterior,
            bg="#2d2d2d" if emisor == "bot" else "#0084ff",
            bd=2,
            relief="ridge",
            padx=10,
            pady=7
        )

        # Mostrar ícono/avatar del bot
        if emisor == "bot":
            icono = Image.open("bot.png").resize((24, 24))
            icono_tk = ImageTk.PhotoImage(icono)
            label_icono = tk.Label(contenedor_exterior, image=icono_tk, bg="#1a1a1a")
            label_icono.image = icono_tk
            label_icono.pack(side="left", padx=(0, 5))

        contenedor_burbuja.pack(anchor="w" if emisor == "bot" else "e", padx=10)

        texto_label = tk.Label(
            contenedor_burbuja,
            text="",
            bg="#2d2d2d" if emisor == "bot" else "#0084ff",
            fg="white",
            font=("Segoe UI", 10),
            wraplength=350,
            justify="left"
        )
        texto_label.pack()

        def escribir_caracter_por_caracter(indice=0):
            if indice <= len(texto):
                texto_label.config(text=texto[:indice])
                app.update_idletasks()
                canvas.yview_moveto(1)
                contenedor_burbuja.after(delay, escribir_caracter_por_caracter, indice + 1)
            else:
                winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
                app.after(100, procesar_siguiente_mensaje)

        if emisor == "bot":
            escribir_caracter_por_caracter()
        else:
            texto_label.config(text=texto)
            app.update_idletasks()
            canvas.yview_moveto(1)
            winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
            procesar_siguiente_mensaje()

    mensaje_queue.put(mostrar)
    if not procesando_mensaje:
        procesar_siguiente_mensaje()

def procesar_siguiente_mensaje():
    global procesando_mensaje
    if not mensaje_queue.empty():
        procesando_mensaje = True
        funcion = mensaje_queue.get()
        funcion()
    else:
        procesando_mensaje = False

def mostrar_botones_opciones(opciones, comando):
    for widget in entry_frame.winfo_children():
        widget.destroy()

    for opcion in opciones:
        boton = ttk.Button(entry_frame, text=opcion, command=lambda opt=opcion: comando(opt))
        boton.pack(side=tk.LEFT, padx=5)

def pedir_datos_usuario():
    enviar_mensaje("¡Hola! Soy tu entrenador virtual 🤖🏋️‍♂️. Vamos a empezar. ¿Cuál es tu sexo?")
    mostrar_botones_opciones(["Masculino", "Femenino"], capturar_sexo)

def capturar_sexo(sexo):
    datos_usuario['sexo'] = 1 if sexo == "Masculino" else 0
    enviar_mensaje(sexo, emisor="user")
    enviar_mensaje("¿Cuál es tu edad?")
    pedir_input(capturar_edad)

def capturar_edad(valor):
    datos_usuario['edad'] = int(valor)
    enviar_mensaje(valor, emisor="user")
    enviar_mensaje("¿Cuál es tu peso (kg)?")
    pedir_input(capturar_peso)

def capturar_peso(valor):
    datos_usuario['peso'] = int(valor)
    enviar_mensaje(valor, emisor="user")
    enviar_mensaje("¿Cuál es tu altura (cm)?")
    pedir_input(capturar_altura)

def capturar_altura(valor):
    datos_usuario['altura'] = int(valor)
    enviar_mensaje(valor, emisor="user")
    enviar_mensaje("¿Cuál es tu nivel de experiencia?")
    mostrar_botones_opciones(["Principiante", "Intermedio", "Avanzado"], capturar_experiencia)

def capturar_experiencia(nivel):
    niveles = {"Principiante": 0, "Intermedio": 1, "Avanzado": 2}
    datos_usuario['experiencia'] = niveles[nivel]
    enviar_mensaje(nivel, emisor="user")
    enviar_mensaje("¿Cuál es tu objetivo?")
    mostrar_botones_opciones(["Bajar peso", "Ganar músculo", "Mantenerse"], capturar_objetivo)

def capturar_objetivo(objetivo):
    objetivos = {"Bajar peso": 0, "Ganar músculo": 1, "Mantenerse": 2}
    datos_usuario['objetivo'] = objetivos[objetivo]
    enviar_mensaje(objetivo, emisor="user")

    generar_rutina_inicial()

def pedir_input(comando):
    for widget in entry_frame.winfo_children():
        widget.destroy()

    entrada = ttk.Entry(entry_frame)
    entrada.pack(side=tk.LEFT, padx=5)
    entrada.focus()

    def enviar_evento(event=None):
        comando(entrada.get())

    boton = ttk.Button(entry_frame, text="Enviar", command=enviar_evento)
    boton.pack(side=tk.LEFT, padx=5)

    entrada.bind("<Return>", enviar_evento)


def generar_rutina_inicial():
    global rutina_actual
    enviar_mensaje("Generando tu rutina inicial...")
    rutina_actual = generar_rutina(datos_usuario, modelo)
    mostrar_rutina()
    mostrar_boton_siguiente()

def mostrar_rutina():
    enviar_mensaje(f"🏋️‍♂️ Rutina Semana {semana_actual}:")
    for ejercicio in rutina_actual:
        texto = f"- {ejercicio['nombre']}: {ejercicio['repeticiones']} repeticiones x {ejercicio['series']} series"
        enviar_mensaje(texto)
    guardar_datos()

def mostrar_boton_siguiente():
    global modo_seguimiento
    modo_seguimiento = True
    mostrar_botones_opciones(["Siguiente Semana"], avanzar_o_pedir_seguimiento)

def avanzar_o_pedir_seguimiento(opcion):
    global modo_seguimiento
    if modo_seguimiento:
        pedir_seguimiento()
    else:
        avanzar_semana()

def pedir_seguimiento():
    global modo_seguimiento
    modo_seguimiento = False
    enviar_mensaje("¿Cuántos minutos entrenaste por día esta semana?")
    pedir_input(capturar_minutos)

def capturar_minutos(valor):
    global minutos_entrenados
    minutos_entrenados = int(valor)
    enviar_mensaje(valor, emisor="user")
    enviar_mensaje("¿Cuántos ejercicios completaste?")
    pedir_input(capturar_ejercicios)

def capturar_ejercicios(valor):
    global ejercicios_realizados
    ejercicios_realizados = int(valor)
    enviar_mensaje(valor, emisor="user")
    enviar_mensaje("¿Nivel de cansancio esta semana?")
    mostrar_botones_opciones(["1", "2", "3", "4", "5"], capturar_cansancio)

def capturar_cansancio(valor):
    global nivel_cansancio_temp
    enviar_mensaje(valor, emisor="user")
    nivel_cansancio_temp = int(valor)

    enviar_mensaje("¿Cuántos días entrenaste esta semana? (1 a 7)")
    pedir_input(capturar_dias_entrenados)
def capturar_dias_entrenados(valor):
    global dias_entrenados_temp
    enviar_mensaje(valor, emisor="user")
    dias_entrenados_temp = int(valor)

    enviar_mensaje("¿Cuál es tu peso actual esta semana? (kg)")
    pedir_input(capturar_peso_actual)

def capturar_peso_actual(valor):
    enviar_mensaje(valor, emisor="user")
    peso_actual = float(valor)

    registrar_seguimiento(
        historial,
        semana_actual,
        dias_entrenados_temp,
        minutos_entrenados,
        ejercicios_realizados,
        nivel_cansancio_temp,
        peso_actual
    )

    analisis = analizar_historial(historial, datos_usuario["altura"], datos_usuario["objetivo"])
    enviar_mensaje(analisis)

    if semana_actual % 4 == 0:
        enviar_mensaje(f"📊 Semana {semana_actual} finalizada. Aquí tienes tu progreso:")
        generar_grafica(historial)

    mostrar_botones_opciones(["Siguiente Semana"], avanzar_o_pedir_seguimiento)



def avanzar_semana():
    global semana_actual, rutina_actual, modo_seguimiento
    semana_actual += 1
    enviar_mensaje("Actualizando rutina...")
    nivel_cansancio = historial[-1]['nivel_cansancio']
    rutina_actual = ajustar_rutina_actual(rutina_actual, nivel_cansancio, datos_usuario['experiencia'], historial)
    mostrar_rutina()
    mostrar_boton_siguiente()


# Iniciar flujo
if cargar_datos():
    enviar_mensaje("🔁 Datos anteriores cargados. Reanudando donde quedaste...")
    mostrar_rutina()
    mostrar_boton_siguiente()
else:
    pedir_datos_usuario()

# Ejecutar app
app.mainloop()