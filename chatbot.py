import openai

openai.api_key = "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"

conversation = ""

inRun = True

while inRun:
	question = input("Humano: ")
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
	print("AI: " + anwer + "\n")