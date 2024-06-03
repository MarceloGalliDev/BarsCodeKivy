# pylint: disable=all

import kivy  # noqa: F401
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# Dicionário de exemplo com códigos de barras e nomes
barcode_to_name = {
    '1000000000016': 'Marcelo',
    '123456789103': 'Bob',
    '123456789104': 'Charlie',
}


class BarcodeScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Escaneie o código de barras')
        self.layout.add_widget(self.label)

        self.text_input = TextInput(multiline=False)
        self.layout.add_widget(self.text_input)

        self.button = Button(text='Buscar Nome')
        self.button.bind(on_press=self.lookup_name)
        self.layout.add_widget(self.button)

        self.result_label = Label(text='')
        self.layout.add_widget(self.result_label)

        return self.layout

    def lookup_name(self, instance):
        code = self.text_input.text.strip()
        name = barcode_to_name.get(code, 'Código não encontrado')
        self.result_label.text = f'Nome: {name}'


if __name__ == '__main__':
    BarcodeScannerApp().run()
