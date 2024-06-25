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
        
        try:
            indice = df[df['sequencia'] != '-'].iloc[-1]['sequencia']
            sequencia = indice
        except:
            indice = 0
            sequencia = 0
        
        for i in range(indice, len(df)):
            index = df.loc[i, "indice"]
            nome = df.loc[i, "nome"]
            celular = df.loc[i, "celular"]
            dataAtualCobranca = datetime.now().strftime("%d/%m/%Y %H:%M")
            status_200 = "Ok!"
            status_400 = "Inválido!"
            status_404 = "Erro!"

    
            send_text = f'''
            Olá *{nome}* 🤩
            Seu convite do *Arráia Dusnei* CHEGOU!!! 🎉
            '''

            time.sleep(2)
            
            texto_codificado = urllib.parse.quote(send_text)
            link = f"https://web.whatsapp.com/send?phone={celular}&text={texto_codificado}"
            self.driver.get(link)
            
            self.driver.find_element(by=By.CSS_SELECTOR)

            time.sleep(2)

            while True:
                while len(self.driver.find_elements(by=By.XPATH, value='//*[@id="app"]')):
                    pass

                while len(self.driver.find_elements(by=By.ID, value='side')) < 1:
                    pass
                
                if len(self.driver.find_elements(by=By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/div/span/svg')) < 1:
                    time.sleep(4)
                    try:
                        self.driver.find_element(
                            by=By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/div/span/svg').click()
                    except:
                        time.sleep(2)
                        self.driver.find_element(
                            by=By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/div/span/svg').click()

                    print('enviado')
                    time.sleep(2)


if __name__ == "__main__":
    automator = WhatsAppAutomator()
    automator.envio_imagens()

