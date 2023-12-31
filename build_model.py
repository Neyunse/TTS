import os
import json
import pickle
import numpy as np
from pydub import AudioSegment
import config
from iso import iso_mapping_keys

def cargar_pistas_desde_archivo(archivo):
    with open(archivo, 'rb') as f:
        voice_bank = pickle.load(f)

    # Verificar que cada entrada tenga las claves necesarias
    for entry in voice_bank:
        if "letra" not in entry or "audio" not in entry:
            raise ValueError("Cada entrada en voice_bank debe tener las claves 'letra' y 'audio'.")

    return voice_bank

def compilar_archivos_wav(archivos_entrada, archivo_salida):
    lista_audio = []

    for archivo_entrada in archivos_entrada:
        letra = os.path.basename(archivo_entrada).split('.')[0]
        audio = AudioSegment.from_wav(archivo_entrada)
        # Agregar entrada al formato voice_bank
        entrada = {"letra": letra, "audio": np.array(audio.get_array_of_samples())}
        lista_audio.append(entrada)

    with open(archivo_salida, 'wb') as f:
        pickle.dump(lista_audio, f)

if __name__ == "__main__":
    # Lista de carpetas dentro de la carpeta principal
    carpetas_modelos = [nombre for nombre in os.listdir(config.srv_folder) if os.path.isdir(os.path.join(config.srv_folder, nombre))]

    for carpeta_modelo in carpetas_modelos:
        # Ruta al archivo JSON que contiene información sobre el modelo
        ruta_modelo_json = os.path.join(config.srv_folder, carpeta_modelo, "model.json")

        # Cargar información del modelo desde el archivo JSON
        with open(ruta_modelo_json, 'r') as json_file:
            info_modelo = json.load(json_file)

        # Nombre del modelo y código de lenguaje obtenidos del archivo JSON
        nombre_modelo = info_modelo["model"]
        lang_iso = info_modelo["lag_iso"]

        if lang_iso not in iso_mapping_keys:
            print(f"El iso {lang_iso} en model.json no es correcto, utiliza ISO 639-1")
            exit()

        # Lista de archivos .wav presentes en la carpeta del modelo
        archivos_wav = [os.path.join(config.srv_folder, carpeta_modelo, archivo) for archivo in os.listdir(os.path.join(config.srv_folder, carpeta_modelo)) if archivo.endswith(".wav")]

        # Generar el nombre del archivo de salida
        nombre_archivo_salida = f"{nombre_modelo}-{lang_iso}{config.bank_file_ext}"

        # Compilar los archivos .wav en un solo archivo con el nombre del modelo y el código de lenguaje
        compilar_archivos_wav(archivos_wav, os.path.join(config.out_folder, nombre_archivo_salida))
