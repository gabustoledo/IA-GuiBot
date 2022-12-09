# -*- coding: utf-8 -*-

import pyttsx3 as voz
import speech_recognition as sr
import subprocess as sub
from datetime import datetime
import openai
import requests
import random

ID_USER = "639173be6139ec1893580416"
POST_RECORDATORIO = "http://localhost:8080/reminder/save/" + ID_USER
POST_CONVERSACION = "http://localhost:8080/conversation/save/" + ID_USER
POST_ALERTA = "http://localhost:8080/alert/save/" + ID_USER

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

inRun = True
modoRecordatorio = False
modoRecordatorioDia = False
modoRecordatorioHora = False

recordatorio = ""
fechaRecordatorio = ""
horaRecordatorio = ""
while inRun:
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
					alertas = ['Gritos', 'Llantos', 'Persona extraña', 'Alerta1', 'Alerta2', 'Alerta3']
					x = requests.post(POST_ALERTA + "?alert_description=" + random.choice(alertas))

		if 'recordatorio' in comandoSplit:
			modoRecordatorio = True
			conversation += "\nHumano: " + comando + "\nAI: ¿Qué recordatorio deseas guardar?"
			say("¿Qué recordatorio deseas guardar?")

		elif modoRecordatorio:
			modoRecordatorio = False
			modoRecordatorioDia = True
			recordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: ¿Qué día lo deseas guardar? recuerda mencionar solo la fecha"
			say("¿Qué día lo deseas guardar? recuerda mencionar solo la fecha")

		elif modoRecordatorioDia:
			modoRecordatorioDia = False
			modoRecordatorioHora = True
			fechaRecordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: ¿A qué hora lo deseas guardar? recuerda mencionar solo la hora"
			say("¿A qué hora lo deseas guardar? recuerda mencionar solo la hora")

		elif modoRecordatorioHora:
			modoRecordatorioHora = False
			horaRecordatorio = comando
			conversation += "\nHumano: " + comando + "\nAI: Entendido, lo guardaré"
			say("Entendido, lo guardaré")
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

f = open ('conversacion.txt','w')
f.write(conversation)
f.close()