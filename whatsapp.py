# pylint: disable=all
# flake8: noqa

import time
import openpyxl
import urllib.parse
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class WhatsAppAutomator:
    def __init__(self) -> None:
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--user-data-dir=./User_Data")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def open_whatsapp(self, link):
        self.driver.get(str(link))

        while True:
            while len(self.driver.find_elements(by=By.XPATH, value='//*[@id="app"]')):
                pass

    def envio_imagens(self):
        link = "https://web.whatsapp.com"
        self.open_whatsapp(link)
        
        path_lista = 'tabela/lista-teste.xlsx'
        
        df = pd.read_excel(path_lista)
        wb = openpyxl.load_workbook(path_lista)
        ws = wb.active
        
        print('Lista aceita')
        time.sleep(2)


if __name__ == "__main__":
    automator = WhatsAppAutomator()
    automator.envio_imagens()

