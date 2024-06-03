# pylint: disable=all
# flake8: noqa

import pandas as pd
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView


class BarcodeScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=10)
        self.input_layout = BoxLayout(orientation="horizontal", padding=10)
        self.button_1_layout = BoxLayout(orientation="horizontal", padding=10)
        self.button_2_layout = BoxLayout(orientation="horizontal", padding=10)
        self.button_3_layout = BoxLayout(orientation="horizontal", padding=10)
        
        # campos
        self.title_label = Label(text="Aponte o leitor para um código de barras", size_hint=(1,0.5))
        with self.title_label.canvas.before:
            Color(0, 0, 1, 1)  # Definir RGBA
            self.rect = Rectangle(size=self.title_label.size, pos=self.title_label.pos)
            self.title_label.bind(size=self.update_rect, pos=self.update_rect)
        
        self.cpf_label = Label(text="CPF", size_hint=(1,1), halign="center", valign="center")
        self.cpf_input = TextInput(multiline=False)
        
        self.result_label = Label(text="")

        self.button = Button(text="Buscar Nome e Telefone")
        self.button.bind(on_press=self.lookup_name)

        self.clean_button = Button(text="Limpar Campo")
        self.clean_button.bind(on_press=self.clean_input)
        
        self.confirm_button = Button(text="Confirmar Presença")
        self.confirm_button.bind(on_press=self.confirm_presence)
        
        self.revert_button = Button(text="Reverter Presença")
        self.revert_button.bind(on_press=self.revert_presence)
        
        self.register_button = Button(text="Cadastrar Novo")
        self.register_button.bind(on_press=self.open_register_popup)

        self.view_button = Button(text='Visualizar Registros')
        self.view_button.bind(on_press=self.view_records)

        # layout
        self.layout.add_widget(self.title_label)
        
        self.layout.add_widget(self.result_label)

        self.input_layout.add_widget(self.cpf_label)
        self.input_layout.add_widget(self.cpf_input)
        self.layout.add_widget(self.input_layout)

        self.button_1_layout.add_widget(self.button)
        self.button_1_layout.add_widget(self.clean_button)
        self.layout.add_widget(self.button_1_layout)


        self.button_2_layout.add_widget(self.confirm_button)
        self.button_2_layout.add_widget(self.revert_button)
        self.layout.add_widget(self.button_2_layout)

        self.button_3_layout.add_widget(self.register_button)
        self.button_3_layout.add_widget(self.view_button)
        self.layout.add_widget(self.button_3_layout)

        # Definir o caminho do arquivo Excel
        self.excel_file_path = "tabela.xlsx"

        # Carregar o arquivo Excel
        self.load_excel()

        return self.layout

    def update_rect(self, widget, *args):
        self.rect.pos = widget.pos
        self.rect.size = widget.size

    def load_excel(self):
        self.df = pd.read_excel(
            self.excel_file_path,
            dtype={"cpf": str, "nome": str, "presença": str, "telefone": str},
        )

    def lookup_name(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = "Nenhum código escaneado"
            return

        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df["cpf"] == code]
        if not record.empty:
            cpf = record.iloc[0]["cpf"]
            name = record.iloc[0]["nome"]
            telefone = record.iloc[0]["telefone"]
            if record.iloc[0]["presença"] == "Presente":
                self.result_label.text = f"CPF: {cpf}\nNome: {name}\nTelefone: {telefone}\nPresença já confirmada"
                self.current_record = None
            else:
                self.result_label.text = f"Nome: {name}\nTelefone: {telefone}"
                self.current_record = record
        else:
            self.result_label.text = "Código não encontrado"
            self.current_record = None

    def confirm_presence(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = "Nenhum código escaneado"
            return

        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df["cpf"] == code]
        if not record.empty:
            if record.iloc[0]["presença"] == "Presente":
                self.result_label.text = "Presença já confirmada"
            else:
                idx = record.index[0]
                self.df.at[idx, "presença"] = "Presente"
                self.df.to_excel(self.excel_file_path, index=False)
                self.result_label.text = "Presença confirmada"
        else:
            self.result_label.text = "Código não encontrado"

    def revert_presence(self, instance):
        code = self.text_input.text.strip()
        if not code:
            self.result_label.text = "Nenhum código escaneado"
            return

        # Recarregar a tabela do Excel
        self.load_excel()

        record = self.df.loc[self.df["cpf"] == code]
        if not record.empty:
            if record.iloc[0]["presença"] == "Presente":
                idx = record.index[0]
                self.df.at[idx, "presença"] = "-"
                self.df["telefone"] = self.df["telefone"].astype(str)
                self.df.to_excel(self.excel_file_path, index=False)
                self.result_label.text = "Presença revertida"
            else:
                self.result_label.text = "Presença não estava confirmada"
        else:
            self.result_label.text = "Código não encontrado"

    def clean_input(self, instance):
        self.text_input.text = ""

    def open_register_popup(self, instance):
        content = GridLayout(cols=2, padding=6)

        content.add_widget(Label(text="CPF:"))
        self.cpf_input = TextInput(multiline=False)
        content.add_widget(self.cpf_input)

        content.add_widget(Label(text="Nome:"))
        self.nome_input = TextInput(multiline=False)
        content.add_widget(self.nome_input)

        content.add_widget(Label(text="Relacionamento:"))
        self.relacionamento_input = TextInput(multiline=False)
        content.add_widget(self.relacionamento_input)

        content.add_widget(Label(text="Telefone:"))
        self.telefone_input = TextInput(multiline=False)
        content.add_widget(self.telefone_input)

        save_button = Button(text="Salvar")
        save_button.bind(on_press=self.save_new_entry)
        content.add_widget(save_button)

        cancel_popup_button = Button(text="Cancelar")
        cancel_popup_button.bind(on_press=self.close_popup)
        content.add_widget(cancel_popup_button)

        self.popup = Popup(title="Cadastro Novo", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def save_new_entry(self, instance):
        new_entry = pd.DataFrame(
            [
                {
                    "cpf": self.cpf_input.text.strip(),
                    "nome": self.nome_input.text.strip(),
                    "relacionamento": self.relacionamento_input.text.strip(),
                    "telefone": self.telefone_input.text.strip(),
                    "presença": "Presente",
                }
            ]
        )

        # Adicionar o novo registro ao DataFrame
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.df["telefone"] = self.df["telefone"].astype(str)
        self.df.to_excel(self.excel_file_path, index=False)

        self.popup.dismiss()
        self.result_label.text = "Novo cadastro salvo com presença confirmada"

    def view_records(self, instance):
        self.load_excel()

        self.main_layout = BoxLayout(orientation='vertical')

        self.content = GridLayout(cols=len(self.df.columns), padding=2, spacing=2, size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.content_button = GridLayout(cols=1)
        
        for column in self.df.columns:
            if column == 'presença':
                self.content.add_widget(Label(text=column, size_hint_y=None, height=40, size_hint_x=None, width=80))
            else:
                self.content.add_widget(Label(text=column, size_hint_y=None, height=40))

        for index, row in self.df.iterrows():
            for col, value in row.items():
                if col == 'presença':
                    self.content.add_widget(Label(text=str(value), size_hint_y=None, height=40, size_hint_x=None, width=80))
                else:
                    self.content.add_widget(Label(text=str(value), size_hint_y=None, height=40))

        self.scroll_view = ScrollView(size_hint=(1, 1))
        
        self.scroll_view.add_widget(self.content)

        # Adicione o ScrollView ao layout principal
        self.main_layout.add_widget(self.scroll_view)

        self.popup = Popup(title='Registros', content=self.main_layout, size_hint=(1, 1))
        
        self.cancel_popup_button_2 = Button(text="Voltar", size_hint=(None, None), size=(200, 50))
        self.cancel_popup_button_2.bind(on_press=self.close_popup)
        self.main_layout.add_widget(self.cancel_popup_button_2)
        
        self.content.add_widget(self.content_button)
        
        self.popup.open()

    def close_popup(self, instance):
        self.popup.dismiss()


if __name__ == "__main__":
    BarcodeScannerApp().run()
