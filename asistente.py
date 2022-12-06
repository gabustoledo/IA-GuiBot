import pyttsx3 as voz
import speech_recognition as sr
import subprocess as sub
from datetime import datetime

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
		print(f'Creo que dijiste "{comando}"')

		comando = comando.lower()
		comando = comando.split(' ')

		if 'computadora' in comando:
			if 'abre' in comando or 'abrir' in comando:
				sites={
					'google' : 'google.com',
					'youtube' : 'youtube.com',
					'instagram' : 'instagram.com'
				}

				for i in list(sites.keys()):
					if i in comando:
						sub.call(f'start chrome.exe {sites[i]}', shell=True)
						say(f'Abriendo {i}')

			elif 'hora' in comando:
				time = datetime.now().strftime('%H:%M')
				say(f'Son las {time}')
			for i in ['termina','terminar','termino']:
				if i in comando:
					say('Sesion finalizada')
					inRun = False
	except:
		print('No te entendi, por favor vuelve a internarlo')