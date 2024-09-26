# imports
from os import name as os_name, system as os_system
from os.path import exists as file_exists

from json import loads as json_decode, dumps as json_dumps
from colorama import Fore as color
from random import sample as random_sample

# chemin du fichier contenant les questions/réponses
data_path = "data.json"
err_sep = "=" * 14

# ouvre un menu et ses sous-menu
def open_menu(data, prefix = "", is_parent = True):
	clear()
	global err_sep
	actions = data["actions"]

	# ajout de l'action quitter/retour selon s'il s'agit d'un menu ou d'un sous-menu
	key = ["Quitter" if is_parent else "Retour"][0]
	actions[key] = None
	keys = tuple(actions.keys())

	# valeur max pour vérification du choix (range)
	_max = len(actions.keys()) + 1

	while True:
		try:
			msg = prefix + color.CYAN + "--- " + data["title"] + " ---\n\n"

			# construire l'énumération
			for i, action in enumerate(keys):
				msg += color.YELLOW + str(i + 1) + ". " + color.RESET + action + "\n"

			# si on trouve un suffix on l'applique
			if ("suffix" in data.keys()):
				suffix = data["suffix"]

				# adapter la valeur du suffix selon si c'est une fonction ou non
				suffix = [suffix() if callable(suffix) else suffix][0]
				# espacement
				msg += "\n" + suffix + "\n"

			msg += "\n> "
			action = input(msg)

			# Vérification du type
			action = int(action)

			# Vérification du choix
			if (action not in range(1, _max)): raise AssertionError
			else:
				clear()
				# si l'utilisateur choisi de quitter le menu
				if (action == _max - 1): break

				# récupération du choix
				key = keys[action - 1]
				action = actions[key]

				# si c'est un object, on ouvre le sous-menu
				if (type(action) == dict): open_menu(action, prefix, False)

				# sinon, si c'est une fonction, on l'appelle
				elif (callable(action)): action()

		# Cas d'erreur
		except (ValueError, AssertionError):
			clear()
			print(color.LIGHTRED_EX + err_sep + "\nChoix invalide\n" + err_sep + color.RESET)
			continue

# construit un tableau
def generate_table(data, header):
	border = color.LIGHTBLACK_EX + "█" + color.RESET

	# ajouter l'entête aux données (pour adapter la largeur et simplifier la génération)
	data.insert(0, header)

	# construction de la largeur max de chaque colonnes
	keys = header.keys()
	widths = {}
	for k in keys: widths[k] = 0

	for line in data:
		for key in keys:
			width = len(str(line[key]).strip())
			if (width > widths[key]): widths[key] = width

	# construction du tableau
	res = ""

	for i, line in enumerate(data):
		# définir le caractère utilisé pour l'espace vide
		space = [color.LIGHTBLACK_EX + "-" + color.RESET if i == 0 else " "][0]

		for key in keys: res += border * (widths[key] + 4)
		res += "\n"

		for key in keys: res += border + (space * (widths[key] + 2))
		res += space + border + "\n"

		for cell in line:
			txt = str(line[cell])
			width = widths[cell]
			pad = (width - len(txt)) * space

			# cas particulier, on colore si la clé est "i"
			if (cell == "i"): txt = color.GREEN + txt + color.RESET

			# ajout du texte dans la cellule
			res += border + space + txt + pad + space

		res += space + border + "\n"

		for key in keys: res += border + (space * (widths[key] + 2))
		res += space + border + "\n"

	for key in keys: res += border * (widths[key] + 4)
	res += "\n"

	return res

# construit un tableau qui contient les questions/réponses
def generate_questions_table():
	global data_path
	header = {
		"i": "Numéro",
		"question": "Question",
		"answer": "Réponse"
	}

	# si le fichier des questions/réponses éxiste et n'est pas vide ou invalide, on récupère ces données dans le fichier
	invalid = True

	if (file_exists(data_path)):
		with open(data_path, "r", encoding = "utf-8") as file:
			try:
				# on récupère la liste et vérifie qu'elle n'est pas vide
				data = json_decode(file.read())
				if (len(data) > 0): invalid = False

			except ValueError:
				pass

	# sinon, on créé le fichier et indique dans le tableau qu'il n'y a pas de données
	if (invalid):
		with open(data_path, "w", encoding = "utf-8") as file:
			file.write("[]")

		# valeur par défaut (pas de données)
		data = header.copy()

		for key in data.keys():
			data[key] = "*Aucune données*"

		data = [data]

	# générer un tableau avec les données et retourner le tableau
	res = color.CYAN + "--- Liste des questions/réponses enregistrés ---\n\n" + color.RESET + generate_table(data, header)
	return res

# récupère les questions
def get_questions():
	global data_path

	if (not file_exists(data_path)):
		with open(data_path, "w", encoding = "utf-8") as file:
			file.write("[]")

	with open(data_path, "r", encoding = "utf-8") as file:
		return json_decode(file.read())

# met à jour les questions
def update_questions(questions):
	global data_path
	questions = json_encode(questions)

	# mise à jour du fichier
	with open(data_path, "w", encoding = "utf-8") as file:
		file.write(questions)

# permet d'ajouter une question/réponse
def add_question():
	global err_sep

	# on définit les paramètres demandés
	inputs = [
		{"key": "question", "word": "question"},
		{"key": "answer", "word": "réponse"}
	]
	data = {"i": 0}

	# on boucle sur ces paramètres et alimente une donnée avec une saisie utilisateur
	for i in range(len(inputs)):
		clear()

		while True:
			res = input("Saisissez votre " + inputs[i]["word"] + " :\n> ").strip()

			# gestion d'erreur (saisie vide)
			if (res == ""):
				clear()
				print(color.LIGHTRED_EX + err_sep + "\nChoix invalide\n" + err_sep + "\n" + color.RESET)

			else:
				data[inputs[i]["key"]] = res
				break

	# on récupère la liste des questions/réponses
	questions = get_questions()

	# on définit le numéro de l'ajout par rapport à ceux éxistants
	num = 0

	for question in questions:
		num = int(question["i"])
		if (num > data["i"]): data["i"] = num

	data["i"] = num + 1

	# ajout de la question à la liste
	questions.append(data)

	# mise à jour du fichier
	update_questions(questions)

	# message de confirmation d'ajout
	clear()
	print(color.GREEN + "Question ajoutée avec succès !\n--------------------\n" + color.RESET)

# permet de supprimer une question/réponse
def remove_question():
	global err_sep, data_path
	clear()

	# on teste si des questions/réponses éxistent
	valid = False

	# on récupère la liste et vérifie qu'elle n'est pas vide
	questions = get_questions()
	if (len(questions) > 0): valid = True

	# s'il y en a, alors on propose une suppression
	while valid:
		try:
			# demande de saisie de numéro
			num = int(input("Saisissez le numéro de la question/réponse que vous souhaitez supprimer :\n\n" + generate_questions_table() + "\n> ").strip())
			found = False

			# on teste la validité du numéro
			for i in range(len(questions)):
				if (num == questions[i]["i"]):
					found = True

					# suppression de la question de la liste
					del questions[i]

					# mise à jour du fichier
					update_questions(questions)

					# message de confirmation de suppression
					clear()
					print(color.GREEN + "Question supprimée avec succès !\n--------------------\n" + color.RESET)
					valid = False
					break

			if (found == False): raise ValueError

		except ValueError:
			clear()
			print(color.LIGHTRED_EX + err_sep + "\nChoix invalide\n" + err_sep + "\n" + color.RESET)

# démarre le quiz
def start_quiz():
	questions = get_questions()

	# vérification qu'il y a au moins une question/réponse disponible
	if (len(questions) > 0):
		# configuration du quiz
		while True:
			try:
				# demande de saisie d'un nombre
				count = int(input("Combien de questions souhaitez vous répondre ?\n> ").strip())

				# on teste la validité du nombre
				if (count <= len(questions) and count > 0):
					clear()
					break

				else: raise ValueError

			except ValueError:
				clear()
				print(color.LIGHTRED_EX + err_sep + "\nChoix invalide\n" + err_sep + "\n" + color.RESET)

		# choix aléatoire des questions (on utilise sample pour éviter les doublons)
		score, questions = 0, random_sample(questions, k = count)

		# pour chaques questions/réponses
		for i in range(len(questions)):
			# on pose la question
			ans = input("\n" + questions[i]["question"] + "\n> ")

			# si la réponse est bonne
			if (ans.lower().strip() == questions[i]["answer"].lower().strip()):
				score += 1
				questions[i]["correct"] = color.GREEN + "Bonne réponse" + color.RESET

			# sinon
			else:
				questions[i]["correct"] = color.RED + "Mauvaise réponse" + color.RESET

		# résumé + score
		header = {
			"i": "Numéro",
			"question": "Question",
			"answer": "Réponse",
			"correct": "Correct ?"
		}
		input("\n\n" + ("-" * 30) + "\n\n\nscore : " + str(score) + "/" + str(count) + "\n\n" + generate_table(questions, header))
		clear()

# formatage json
json_encode = lambda json: json_dumps(json, indent = 4)

# efface l'écran
if (os_name == "nt"):
	clear = lambda: os_system("cls")
else:
	clear = lambda: os_system("clear")

data = {
	"title": "Menu principal",
	"actions": {
		"Accéder aux questions/réponses disponibles": {
			"title": "Menu des questions/réponses",
			"actions": {
				"Ajouter une question/réponse": add_question,
				"Supprimer une question/réponse": remove_question
			},
			"suffix": generate_questions_table
		},
		"Lancer le questionnaire": start_quiz
	}
}
prefix = color.GREEN + """
 ██████╗ ██╗   ██╗███████╗███████╗████████╗██╗ ██████╗ ███╗   ██╗███╗   ██╗ █████╗ ██╗██████╗ ███████╗
██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║████╗  ██║██╔══██╗██║██╔══██╗██╔════╝
██║   ██║██║   ██║█████╗  ███████╗   ██║   ██║██║   ██║██╔██╗ ██║██╔██╗ ██║███████║██║██████╔╝█████╗  
██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   ██║██║   ██║██║╚██╗██║██║╚██╗██║██╔══██║██║██╔══██╗██╔══╝  
╚██████╔╝╚██████╔╝███████╗███████║   ██║   ██║╚██████╔╝██║ ╚████║██║ ╚████║██║  ██║██║██║  ██║███████╗
 ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝\n\n""" + color.RESET

open_menu(data, prefix)
