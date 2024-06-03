# pylint: disable=all
# flake8: noqa

import kivy
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import cv2
import pandas as pd

class BarcodeScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Aponte o leitor para um código de barras')
        self.layout.add_widget(self.label)

        self.text_input = TextInput(multiline=False)
        self.layout.add_widget(self.text_input)

        self.button = Button(text='Buscar Nome e Telefone')
        self.button.bind(on_press=self.lookup_name)
        self.layout.add_widget(self.button)
        
        self.clean_button = Button(text='Limpar Campo')
        self.clean_button.bind(on_press=self.clean_input)
        self.layout.add_widget(self.clean_button)

        self.confirm_button = Button(text='Confirmar Presença')
        self.confirm_button.bind(on_press=self.confirm_presence)
        self.layout.add_widget(self.confirm_button)
        
        self.revert_button = Button(text='Reverter Presença')
        self.revert_button.bind(on_press=self.revert_presence)
        self.layout.add_widget(self.revert_button)
        
        self.register_button = Button(text='Cadastrar Novo')
        self.register_button.bind(on_press=self.open_register_popup)
        self.layout.add_widget(self.register_button)
        
        self.result_label = Label(text='')
        self.layout.add_widget(self.result_label)

        # Definir o caminho do arquivo Excel
        self.excel_file_path = 'tabela.xlsx'
        
        # Carregar o arquivo Excel
        self.load_excel()

        return self.layout

    def load_excel(self):
        self.df = pd.read_excel(
            self.excel_file_path, 
            dtype={
                'cpf': str,
                'nome': str,
                'presença': str,
                'telefone': str
            }
        )

    def lookup_name(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = 'Nenhum código escaneado'
            return
        
        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df['cpf'] == code]
        if not record.empty:
            cpf = record.iloc[0]['cpf']
            name = record.iloc[0]['nome']
            telefone = record.iloc[0]['telefone']
            if record.iloc[0]['presença'] == 'Presente':
                self.result_label.text = f'CPF: {cpf}\nNome: {name}\nTelefone: {telefone}\nPresença já confirmada'
                self.current_record = None
            else:
                self.result_label.text = f'Nome: {name}\nTelefone: {telefone}'
                self.current_record = record
        else:
            self.result_label.text = 'Código não encontrado'
            self.current_record = None

    def confirm_presence(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = 'Nenhum código escaneado'
            return

        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df['cpf'] == code]
        if not record.empty:
            if record.iloc[0]['presença'] == 'Presente':
                self.result_label.text = 'Presença já confirmada'
            else:
                idx = record.index[0]
                self.df.at[idx, 'presença'] = 'Presente'
                self.df.to_excel(self.excel_file_path, index=False)
                self.result_label.text = 'Presença confirmada'
        else:
            self.result_label.text = 'Código não encontrado'

    def revert_presence(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = 'Nenhum código escaneado'
            return

        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df['cpf'] == code]
        if not record.empty:
            if record.iloc[0]['presença'] == 'Presente':
                idx = record.index[0]
                self.df.at[idx, 'presença'] = '-'
                self.df['telefone'] = self.df['telefone'].astype(str)
                self.df.to_excel(self.excel_file_path, index=False)
                self.result_label.text = 'Presença revertida'
            else:
                self.result_label.text = 'Presença não estava confirmada'
        else:
            self.result_label.text = 'Código não encontrado'

    def clean_input(self, instance):
        self.text_input.text = ''

    def open_register_popup(self, instance):
        content = GridLayout(cols=2, padding=6)
        content.add_widget(Label(text='CPF:'))
        self.cpf_input = TextInput(multiline=False)
        content.add_widget(self.cpf_input)
        
        content.add_widget(Label(text='Nome:'))
        self.nome_input = TextInput(multiline=False)
        content.add_widget(self.nome_input)
        
        content.add_widget(Label(text='Relacionamento:'))
        self.relacionamento_input = TextInput(multiline=False)
        content.add_widget(self.relacionamento_input)
        
        content.add_widget(Label(text='Telefone:'))
        self.telefone_input = TextInput(multiline=False)
        content.add_widget(self.telefone_input)
        
        save_button = Button(text='Salvar')
        save_button.bind(on_press=self.save_new_entry)
        content.add_widget(save_button)

        self.popup = Popup(title='Cadastro Novo', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def save_new_entry(self, instance):
        new_entry = pd.DataFrame([{
            'cpf': self.cpf_input.text.strip(),
            'nome': self.nome_input.text.strip(),
            'relacionamento': self.relacionamento_input.text.strip(),
            'telefone': self.telefone_input.text.strip(),
            'presença': 'Presente'
        }])
        
        # Adicionar o novo registro ao DataFrame
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.df['telefone'] = self.df['telefone'].astype(str)
        self.df.to_excel(self.excel_file_path, index=False)
        
        self.popup.dismiss()
        self.result_label.text = 'Novo cadastro salvo com presença confirmada'

if __name__ == '__main__':
    BarcodeScannerApp().run()
