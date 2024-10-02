"""
App for checking cocco queueus
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, SERIF, BOLD, CENTER
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

mdms_currency = final_d['mdms_currency']
bc_currency = final_d['bc_currency']
nbpEurUrl = final_d['nbpEurUrl']

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
        #MDMS
        response = requests.get(bc_mdms_url, auth=HTTPBasicAuth(username, user_password))
        if response.status_code == 200:
            data = response.json()
            for row in data['value']:
                if row['Status'] == 'Error':
                #if row['Status'] == 'In Process':
                    finallist.append(['MDMS', row['Description'], row['Error_Message']])
                    
        #NBP
        response = requests.get(nbpEurUrl, auth=HTTPBasicAuth(username, user_password))
        if response.status_code == 200:
            data = response.json()     
            nbpEur = data['rates'][0]['mid']
        else:
            nbpEur = "Problem z odpytaniem strony NBP."
            
        #mdms currency
        response = requests.get(mdms_currency, auth=HTTPBasicAuth(username, user_password))
        if response.status_code == 200:
            data = response.json()
            for line in data['value']:
                if line['Code'] == 'EUR':
                    mdms_euro = line['ExchangeRateAmt']
                    break
        else:
            mdms_euro = "Problem z pobraniem EUR MDMS."
            
        #mcdrl currency
        response = requests.get(bc_currency, auth=HTTPBasicAuth(username, user_password))
        if response.status_code == 200:
            data = response.json()
            for line in data['value']:
                if line['Code'] == 'EUR':
                    cdrl_euro = line['ExchangeRateAmt']
                    break
        else:
            cdrl_euro = "Problem z pobraniem EUR CDRL."
        
    
        return finallist, numbers, nbpEur, mdms_euro, cdrl_euro
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'NoInternet', 'NoInternet', 0,0,0
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
        
        screen_width = self.main_window.size[0]
        screen_height = self.main_window.size[1]

    def on_button_click(self, widget):
        
        screen_width = self.main_window.size[0]
        screen_height = self.main_window.size[1]
        
        self.container.clear()
        data, numbers, nbpEur, cdrlEur, mdmsEur = get_data()
        
        if data == 'NoInternet':
            # stats_content = "Problem z odpytaniem, sprawdź połączenie z internetem..."
            # stats_label = self.create_multiline_label(stats_content)
            # self.container.add(stats_label)
            image_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
            image_path = 'resources/net-new.jpg'  # Update the path to your image file
            image = toga.Image(image_path)
            image_view = toga.ImageView(image, style=Pack(width=screen_width * 0.6, height=screen_height * 0.6))
            image_box.add(image_view)
            self.container.add(image_box)
        else:
            if data:
                for item in data:
                    text_content = f"Nazwa: {item[0]}\nOpis: {item[1]}\nBłąd: {item[2]}"
                    label = self.create_multiline_label(text_content)
                    self.container.add(label)
                    # button = toga.Button(f'Podnieś {item[1]}', on_press=self.print_hello, style=Pack(padding=5))
                    # self.container.add(button)
            else:
                #text_content = "Brak błędów - możesz zjeść ciastko"
                #label = self.create_multiline_label(text_content)
                #self.container.add(label)
                image_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
                image_path = 'resources/ez-new.jpg'  # Update the path to your image file
                image = toga.Image(image_path)
                image_view = toga.ImageView(image, style=Pack(width=screen_width * 0.6, height=screen_height * 0.5))
                image_box.add(image_view)
                self.container.add(image_box)

            #currency
            
            stats_content = f"""Kurs euro NBP: {nbpEur}\nCDRL euro: {cdrlEur}\nMDMS euro: {mdmsEur}\n"""
            if nbpEur == cdrlEur == mdmsEur:
                result = 'WSZYSTKO OK'
            else:
                result = "NIE ZGADZA SIĘ"
                
            stats_content += result
            stats_label = toga.MultilineTextInput(readonly=True, value=stats_content, style=Pack(padding=5, height=150, font_size = 12))
            self.container.add(stats_label)
            

            #queues summary
            stats_content = f"""Liczba kolejek: {numbers[0][4]}\nLiczba błędów: {numbers[0][0]}\nW trakcie: {numbers[0][3]}\nGotowe: {numbers[0][2]}\nWstrzymane: {numbers[0][1]}"""
            stats_label = toga.MultilineTextInput(readonly=True, value=stats_content, style=Pack(padding=5, height=150, font_size = 12))
            self.container.add(stats_label)
            
           

    def create_multiline_label(self, text):
        multiline_label = toga.MultilineTextInput(readonly=True, value=text, style=Pack(padding=5, height=150, font_size = 10))
        return multiline_label
    
    #tutaj dodać puta do kolejki
    def print_hello(self, widget):
        print("hello")

def main():
    return Queueschecker()
