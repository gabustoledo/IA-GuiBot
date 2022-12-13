# -*- coding: utf-8 -*-

import pyttsx3 as voz
import speech_recognition as sr
import subprocess as sub
from datetime import datetime
import openai
import requests
import random
import json

# ID_USER = "639173be6139ec1893580416"
ID_USER = ""
ID_PRODUCT = "2222 3333 4444 5555"
GET_RECORDATORIO = "http://localhost:8080/reminder/find/"
GET_SYNC = "http://localhost:8080/product_user/sync?product_number=" + ID_PRODUCT

# Iniciacion de openai
openai.api_key = "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"
conversation = ""

# configuracion de la voz del asistente
voice = voz.init()
voices = voice.getProperty('voices')
voice.setProperty('voice',voices[0].id)
voice.setProperty('rate',170)

def say(text):
	voice.say(text)
	voice.runAndWait()

print("\n\nEsperando sincronizacion...\n\n")
while ID_USER == "":
	x = requests.get(GET_SYNC)
	response = x.content.decode()
	if(response != "No se ha sincronizado un usuario al dispositivo"):
		ID_USER = response
print("Producto correctamente sincronizado\n\n")

POST_RECORDATORIO = "http://localhost:8080/reminder/save/" + ID_USER
POST_CONVERSACION = "http://localhost:8080/conversation/save/" + ID_USER
POST_ALERTA = "http://localhost:8080/alert/save/" + ID_USER
POST_MOVIMIENTO = "http://localhost:8080/movement/save/" + ID_USER
GET_DORECORDATORIO = "http://localhost:8080/reminder/doReminder/" + ID_USER

inRun = True
modoRecordatorio = False
modoRecordatorioDia = False
modoRecordatorioHora = False

recordatorio = ""
fechaRecordatorio = ""
horaRecordatorio = ""
while inRun:

	x = requests.get(GET_DORECORDATORIO)
	response = x.content.decode()
	print(response)
	if response != 'No hay recordatorio activo':
		x = requests.get(GET_RECORDATORIO + response)
		response_recordatorio = x.content.decode()
		response_json = json.loads(response_recordatorio)
		recordatorio_descr = response_json["reminder_description"]

		say("Recuerda que actualmente tienes un recordatorio que dice: " + recordatorio_descr)
		conversation += "\nAI: Recuerda que actualmente tienes un recordatorio que dice: " + recordatorio_descr


	recognizer = sr.Recognizer()

	with sr.Microphone() as source:
		print('Escuchando...')
		audio = recognizer.listen(source, phrase_time_limit=3)

	try:
		comando = recognizer.recognize_google(audio, language='es-CL')

		comando = comando.lower()
		x = requests.post(POST_CONVERSACION + "?message=" + comando + "&who=User")
		comandoSplit = comando.split(' ')

		for i in ['termina','terminar','termino', 'adiós']:
				if i in comandoSplit:
					say('Sesion finalizada')
					conversation += "\n\nSesion finalizada"
					inRun = False
					break

		for i in ['ayuda', 'auxilio', 'muero', 'emergencias', 'emergencia']:
			if i in comandoSplit:
					say('Enviando notificación de alerta')
					alertas = ['Gritos', 'Llantos', 'Persona extraña', 'Golpes', 'Caida']
					x = requests.post(POST_ALERTA + "?alert_description=" + random.choice(alertas))

		if 'movimiento' in comandoSplit:
			for i in ['habitación', 'cocina', 'baño']:
				if i in comandoSplit:
					print('Movimiento a ' + i)
					x = requests.post(POST_MOVIMIENTO + "?place=" + i)
					say("Movimiento almacenado")
					x = requests.post(POST_CONVERSACION + "?message=Movimiento almacenado&who=Bot")


		elif 'recordatorio' in comandoSplit:
			modoRecordatorio = True
			conversation += "\nHumano: " + comando + "\nAI: ¿Qué recordatorio deseas guardar?"
			say("¿Qué recordatorio deseas guardar?")
			x = requests.post(POST_CONVERSACION + "?message=¿Qué recordatorio deseas guardar?&who=Bot")

		elif modoRecordatorio:
			modoRecordatorio = False
			modoRecordatorioDia = True
			recordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: ¿Qué día lo deseas guardar? recuerda mencionar solo la fecha"
			say("¿Qué día lo deseas guardar? recuerda mencionar solo la fecha")
			x = requests.post(POST_CONVERSACION + "?message=¿Qué día lo deseas guardar? recuerda mencionar solo la fecha&who=Bot")

		elif modoRecordatorioDia:
			modoRecordatorioDia = False
			modoRecordatorioHora = True
			fechaRecordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: ¿A qué hora lo deseas guardar? recuerda mencionar solo la hora"
			say("¿A qué hora lo deseas guardar? recuerda mencionar solo la hora")
			x = requests.post(POST_CONVERSACION + "?message=¿A qué hora lo deseas guardar? recuerda mencionar solo la hora&who=Bot")

		elif modoRecordatorioHora:
			modoRecordatorioHora = False
			horaRecordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: Entendido, lo guardaré"
			say("Entendido, lo guardaré")
			x = requests.post(POST_CONVERSACION + "?message=Entendido, lo guardaré&who=Bot")
			x = requests.post(POST_RECORDATORIO + "?description=" + recordatorio + "&date=" + fechaRecordatorio + " " + horaRecordatorio)

		else:
			question = comando
			conversation += "\nHumano: " + question + "\nAI:"
			response = openai.Completion.create(
				model="text-davinci-003",
				prompt = conversation,
				temperature=0.9,
				max_tokens=150,
				top_p=1,
				frequency_penalty=0,
				presence_penalty=0.6,
				stop = ["\n"," Humano:", " AI:"]
			)
			anwer = response.choices[0].text.strip()
			conversation += anwer
			x = requests.post(POST_CONVERSACION + "?message=" + anwer + "&who=Bot")
			say(anwer)

	except:
		print('No te entendi, por favor vuelve a intentarlo')
		say('No te entendi, por favor vuelve a intentarlo')
		x = requests.post(POST_CONVERSACION + "?message=No te entendi, por favor vuelve a intentarlo&who=Bot")

f = open ('conversacion.txt','w')
f.write(conversation)
f.close()