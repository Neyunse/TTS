import os
import json
import pickle
import numpy as np
from pydub import AudioSegment
import config
import traceback

def cargar_modelo_desde_archivo(archivo):
    with open(archivo, 'rb') as f:
        lista_audio = pickle.load(f)
    return lista_audio

def reproducir_audio(audio):
    audio.export(os.path.join("voice", "tts.wav"), format="wav")
    os.system("start "+os.path.join("voice", "tts.wav"))

def encontrar_audio_por_letra(letra, voice_bank):
    for entry in voice_bank:
        if letra.lower() == entry["letra"].lower():
            print(letra + "in" + entry["letra"])
            return entry["audio"]
    return None

if __name__ == "__main__":
    try:
        # Listar modelos de voz disponibles
        modelos_disponibles = [archivo for archivo in os.listdir(config.out_folder) if archivo.endswith(config.bank_file_ext)]

        if not modelos_disponibles:
            print("No hay modelos de voz disponibles en la carpeta /output/.")
            exit()

        # Mostrar modelos disponibles al usuario
        print("Modelos de voz disponibles:")
        for modelo in modelos_disponibles:
            print(f"- {modelo[:-5].split('-')[0]}")

        # Elegir un modelo de voz
        modelo_elegido = input("Ingrese el nombre del modelo de voz que desea utilizar: ")

        # Filtrar modelos que comienzan con el nombre especificado por el usuario
        modelos_disponibles = [modelo for modelo in modelos_disponibles if modelo.startswith(modelo_elegido)]

        # Verificar si el modelo elegido existe
        if not modelos_disponibles:
            print(f"No hay modelos de voz que comiencen con '{modelo_elegido}'.")
            exit()

        print(f"Ruta del modelo seleccionado: {os.path.abspath(os.path.join(config.out_folder, modelos_disponibles[0]))}")

        # Cargar pistas de audio desde el modelo de voz seleccionado
        voice_bank = cargar_modelo_desde_archivo(os.path.join(config.out_folder, modelos_disponibles[0]))

        # Ingresar la palabra o letras a reproducir
        palabra_a_reproducir = input("Ingrese la palabra (sin espacios) a reproducir: ")

        # Dividir el texto en fonemas utilizando pronouncing
        letras = list(palabra_a_reproducir)

        print(voice_bank)

        # Reproducir las pistas de audio secuencialmente
        pistas_audio_palabra = []
        for i in range(0, len(letras), 2):  # Recorrer de 2 en 2 para manejar combinaciones como "KO"
            letra_actual = letras[i]
            if i + 1 < len(letras):
                letra_siguiente = letras[i + 1]
                letra_combinada = letra_actual + letra_siguiente
                pista_audio = encontrar_audio_por_letra(letra_combinada, voice_bank)
                if pista_audio is not None and any(pista_audio):
                    # Crear el objeto AudioSegment
                    audio = AudioSegment(data=pista_audio.tobytes(), 
                                         sample_width=pista_audio.itemsize, 
                                         frame_rate=config.voice_frame_rate, channels=1)
                    pistas_audio_palabra.append(audio)
                    reproducir_audio(audio)
                else:
                    print(f"No se encontró un archivo de voz para la combinación de letras: {letra_combinada}")
            else:
                # Si la palabra tiene un número impar de letras, reproducir la última letra
                pista_audio = encontrar_audio_por_letra(letra_actual, voice_bank)
                if pista_audio is not None and any(pista_audio):
                    audio = AudioSegment(data=pista_audio.tobytes(), 
                                         sample_width=pista_audio.itemsize, 
                                         frame_rate=config.voice_frame_rate, 
                                         channels=1)
                    pistas_audio_palabra.append(audio)
                    reproducir_audio(audio)
                else:
                    print(f"No se encontró un archivo de voz para la letra: {letra_actual}")


    except Exception as e:
        traceback.print_exc()