"""
App for checking cocco queueus
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, SERIF, BOLD
import requests
from requests.auth import HTTPBasicAuth
import os
import json

import os

final_d = {}
module_dir = os.path.dirname(__file__)  # Path to the directory of the current file
file_path = os.path.join(module_dir, 'resources', 'hasla.txt')

with open (file_path, 'r') as file:
    for line in file.readlines():
        key, value = line.rstrip('\n').split(',')
        final_d[key] = value

username = final_d['bc_username']
user_password = final_d['user_password']
url = final_d['url']
bc_mdms_url = final_d['bc_mdms_url']

def get_data():
    try:
        finallist = []
        numbers = []
        response = requests.get(url, auth=HTTPBasicAuth(username, user_password))
        if response.status_code == 200:
            data = response.json()
            error, on_hold, ready, in_process = 0, 0, 0, 0
            for row in data['value']:
                if row['Status'] == 'Error':
                    finallist.append([row['Object_Caption_to_Run'], row['Description'], row['Error_Message']])
                    error += 1
                elif row['Status'] == 'In Process':
                    in_process += 1
                elif row['Status'] == 'Ready':
                    ready += 1
                elif row['Status'] == 'On Hold':
                    on_hold += 1
            numbers.append([error, on_hold, ready, in_process, len(data['value'])])
        
        return finallist, numbers
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'NoInternet', 'NoInternet'

def greeting(name):
    return f"Hello, {name if name else 'stranger'}"

class Queueschecker(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.button = toga.Button('Wyślij zapytanie', on_press=self.on_button_click, style=Pack(padding=5))
        main_box.add(self.button)

        self.scroll = toga.ScrollContainer(horizontal=False, style=Pack(flex=1))
        self.container = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.scroll.content = self.container
        main_box.add(self.scroll)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def on_button_click(self, widget):
        self.container.clear()
        data, numbers = get_data()
        
        if data == 'NoInternet':
            stats_content = "Problem z odpytaniem, sprawdź połączenie z internetem..."
            stats_label = self.create_multiline_label(stats_content)
            self.container.add(stats_label)
        else:
            if data:
                for item in data:
                    text_content = f"Nazwa: {item[0]}\nOpis: {item[1]}\nBłąd: {item[2]}"
                    label = self.create_multiline_label(text_content)
                    self.container.add(label)
            else:
                text_content = "Brak błędów - możesz zjeść ciastko"
                label = self.create_multiline_label(text_content)
                self.container.add(label)

            stats_content = f"""Liczba kolejek: {numbers[0][4]}\nLiczba błędów: {numbers[0][0]}\nW trakcie: {numbers[0][3]}\nGotowe: {numbers[0][2]}\nWstrzymane: {numbers[0][1]}"""
            stats_label = toga.MultilineTextInput(readonly=True, value=stats_content, style=Pack(padding=5, height=150, font_size = 12))
            self.container.add(stats_label)

    def create_multiline_label(self, text):
        multiline_label = toga.MultilineTextInput(readonly=True, value=text, style=Pack(padding=5, height=150, font_size = 10))
        return multiline_label

def main():
    return Queueschecker()
