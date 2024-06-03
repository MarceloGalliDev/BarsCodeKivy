# pylint: disable=all
# flake8: noqa

import kivy  # noqa: F401
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import cv2
import pandas as pd


class BarcodeScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
    
        self.label = Label(text='Aponte a câmera para um código de barras')
        self.layout.add_widget(self.label)

        self.image = Image()
        self.layout.add_widget(self.image)

        self.text_input = TextInput(multiline=False)
        self.layout.add_widget(self.text_input)

        self.button = Button(text='Buscar Nome')
        self.button.bind(on_press=self.lookup_name)
        self.layout.add_widget(self.button)

        self.confirm_button = Button(text='Confirmar Presença')
        self.confirm_button.bind(on_press=self.confirm_presence)
        self.layout.add_widget(self.confirm_button)

        self.result_label = Label(text='')
        self.layout.add_widget(self.result_label)

        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        # Carregar a tabela do Excel
        self.df = pd.read_excel('tabela.xlsx')

        return self.layout

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Converte a imagem do OpenCV para um formato que o Kivy pode usar
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

            # Detecta códigos de barras na imagem
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcode_detector = cv2.QRCodeDetector()
            retval, decoded_info, points, _ = barcode_detector.detectAndDecodeMulti(gray)
            if retval:
                code = decoded_info[0]
                self.text_input.text = code

    def lookup_name(self, instance):
        code = self.text_input.text.strip()
        record = self.df.loc[self.df['codebar'] == code]
        if not record.empty:
            name = record.iloc[0]['nome']
            self.result_label.text = f'Nome: {name}'
            self.current_record = record
        else:
            self.result_label.text = 'Código não encontrado'
            self.current_record = None

    def confirm_presence(self, instance):
        if self.current_record is not None:
            idx = self.current_record.index[0]
            self.df.at[idx, 'presença'] = 'Presente'
            self.df.to_excel('tabela_atualizada.xlsx', index=False)
            self.result_label.text += '\nPresença confirmada'
        else:
            self.result_label.text = 'Nenhum registro para confirmar'

    def on_stop(self):
        self.capture.release()

if __name__ == '__main__':
    BarcodeScannerApp().run()
