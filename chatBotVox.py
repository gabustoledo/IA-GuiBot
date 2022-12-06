# -*- coding: utf-8 -*-

import pyttsx3 as voz
import speech_recognition as sr
import subprocess as sub
from datetime import datetime
import openai

# Iniciacion de openai
openai.api_key = "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"
conversation = ""

# configuracion de la voz del asistente
voice = voz.init()
voices = voice.getProperty('voices')
voice.setProperty('voice',voices[0].id)
voice.setProperty('rate',140)

def say(text):
	voice.say(text)
	voice.runAndWait()

inRun = True
while inRun:
	recognizer = sr.Recognizer()

	with sr.Microphone() as source:
		print('Escuchando...')
		audio = recognizer.listen(source, phrase_time_limit=3)

	try:
		comando = recognizer.recognize_google(audio, language='es-MX')

		comando = comando.lower()
		comandoSplit = comando.split(' ')

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
		say(anwer)

		for i in ['termina','terminar','termino', 'adiós']:
				if i in comandoSplit:
					say('Sesion finalizada')
					conversation += "\n\nSesion finalizada"
					inRun = False
	except:
		print('No te entendi, por favor vuelve a intentarlo')
		say('No te entendi, por favor vuelve a intentarlo')

f = open ('conversacion.txt','w')
f.write(conversation)
f.close()