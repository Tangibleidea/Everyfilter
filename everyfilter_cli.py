from __future__ import print_function, unicode_literals
from collections import OrderedDict
from PyInquirer import prompt, print_json
from pyfiglet import Figlet
import os, sys

from everyfilter import AddSource, saveTXT, openTXT

# Slpash text
f = Figlet(font='slant')
print(f.renderText('Everyfilter'))
# Group of Different functions for different styles
class style():
    BLACK = lambda x: '\033[30m' + str(x)
    RED = lambda x: '\033[31m' + str(x)
    GREEN = lambda x: '\033[32m' + str(x)
    YELLOW = lambda x: '\033[33m' + str(x)
    BLUE = lambda x: '\033[34m' + str(x)
    MAGENTA = lambda x: '\033[35m' + str(x)
    CYAN = lambda x: '\033[36m' + str(x)
    WHITE = lambda x: '\033[37m' + str(x)
    UNDERLINE = lambda x: '\033[4m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)


FILTERLIST_TXT_PATH = "filterlist.txt"
SUBSCRIPTION_LIST = []

# Search 
def searchList(search_text):
	global FILTERLIST_TXT_PATH

	#dt_where_source_from = {}
	latest_source_from = ""
	for line in openTXT():
		if line.startswith('!'): # comment
			#dt_where_source_from["line"] = idx
			#dt_where_source_from["from"] = line
			latest_source_from = line
		elif search_text in line:
			print(style.YELLOW("[ ") + line + " ]" + style.RESET("")+ " has retrieved in : " + style.GREEN("")+ latest_source_from + style.RESET(""))


# Update filter sources (google sheets, adblockplus's filters.)
def updateList():
	global SUBSCRIPTION_LIST
	list_all = []
	for mylist in SUBSCRIPTION_LIST:
		list_all.extend( AddSource(mylist) )

	list_all_disticted = OrderedDict.fromkeys(list_all).keys()
	saveTXT(list_all_disticted)

# Print out 'SUBSCRIPTION_LIST'
def PrintSubsList():
	global SUBSCRIPTION_LIST

	SUBSCRIPTION_LIST = list(OrderedDict.fromkeys(SUBSCRIPTION_LIST))
	print("Current subscription list : ")
	print(SUBSCRIPTION_LIST)
	print()

# Save 'filters.txt' file.
def saveToFiltersTXT():
	global SUBSCRIPTION_LIST

	# distinction	
	PrintSubsList()

	with open(FILTERLIST_TXT_PATH, 'w', encoding='UTF-8', newline='') as f:
		for item in SUBSCRIPTION_LIST:
			f.write("%s\n" % item)

# Edit 'filters.txt' file.
def ModifySubsList():
	global SUBSCRIPTION_LIST

	while True:
		create_list = [
		{
			'type': 'input',
			'name': 'url',
			'message': 'Please input to filter url to subscribe. (Please enter "x" to stop)'
		}]
		answer = prompt(create_list)["url"]
		#print(answer)
		if answer == 'x':
			break
		else:
			SUBSCRIPTION_LIST.append(answer)
	saveToFiltersTXT()


def main():
	global SUBSCRIPTION_LIST
	print("Checking out [" + FILTERLIST_TXT_PATH + "] ...")

	while True:
		if os.path.exists(FILTERLIST_TXT_PATH):
			with open(FILTERLIST_TXT_PATH, encoding='UTF-8') as file:
				for line in file:
					line = line.strip() #preprocess line
					SUBSCRIPTION_LIST.append(line)

			PrintSubsList()

			menus = ['Search filter.', 'Modify subscribed list.', 'Update all filters.', 'Clear filters.', 'Exit']
			questions = [
			{
				'type': 'list',
				'name': 'menu',
				'message': 'What do you need',
				'choices': menus
			}]
			answer = prompt(questions)["menu"]
			print(answer)
			if answer is menus[0]: # search
				search_prompt = [
				{
					'type': 'input',
					'name': 'target',
					'message': 'Please input a url to retrieve.'
				}]
				answer = prompt(search_prompt)["target"]
				searchList(answer)

			elif answer is menus[1]: # update new
				ModifySubsList()
			elif answer is menus[2]:
				updateList()
			elif answer is menus[3]:
				SUBSCRIPTION_LIST.clear()
				os.remove(FILTERLIST_TXT_PATH)
				print("Successfully deleted: " +FILTERLIST_TXT_PATH)
			elif answer is menus[4]:
				exit()
			else: # do not update.
				print("Okay. Please search a taget domain.")
		else:
			questions = [
			{
				'type': 'confirm',
				'message': 'There is no filter list. Do you want to create one?',
				'name': 'continue',
				'default': True,
			}]
			answer = prompt(questions)
			if answer is False:
				print("It must have a subscription list.")
				exit()

			ModifySubsList()
			updateList()

if __name__ == '__main__':
    main()