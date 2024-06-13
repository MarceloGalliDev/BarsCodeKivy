# pylint: disable=all
# flake8: noqa

import time
from turtle import width
import kivy
import cv2
import pandas as pd
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class qrcodeLayout(GridLayout):
    pass


class RegisterPopup(Popup):
    pass


class RecordsPopup(Popup):
    pass


class qrcode(App):
    def build(self):
        self.excel_file_path = "tabela/tabela.xlsx"
        self.load_excel()
        return qrcodeLayout()
    
    def activate_camera(self):
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise ValueError("Camera not available")
        except:
            self.capture = None
            self.root.ids.result_label.text = "Failed to access camera"
            return
        
        Clock.schedule_interval(self.update_camera, 1.0 / 20.0)

    def update_camera(self, dt):
        if self.capture is None:
            return
        
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.root.ids.camera_image.texture = texture
            
            qr_decoder = cv2.QRCodeDetector()
            data, bbox, _ = qr_decoder.detectAndDecode(frame)
            if bbox is not None and data:
                self.root.ids.cpf_input.text = data
                self.root.ids.capture_image.texture = texture
                self.confirm_presence(data)
                self.lookup_name(data)

    def close_camera(self):
        if self.capture:
            self.capture.release()
        Clock.unschedule(self.update_camera)

    def load_excel(self):
        try:
            self.df = pd.read_excel(
                self.excel_file_path,
                dtype={"codigo": str, "cpf": str, "nome": str, "presença": str, "telefone": str},
                index_col=0
            )
            print("Excel file loaded successfully.")
        except Exception as e:
            self.root.ids.result_label.text = f"Failed to load Excel file: {str(e)}"
            print(f"Failed to load Excel file: {str(e)}")

    def lookup_name(self, code=None):
        if code is None:
            code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.result_label.text = "Nenhum código escaneado"
            return

        self.load_excel()

        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            codigo = record.iloc[0]["codigo"]
            cpf = record.iloc[0]["cpf"]
            name = record.iloc[0]["nome"]
            telefone = record.iloc[0]["telefone"]
            if record.iloc[0]["presença"] == "Presente":
                self.root.ids.result_label.text = f"Código: {codigo}\nCPF: {cpf}\nNome: {name}\nTelefone: {telefone}\nPresença confirmada"
                self.current_record = None
            else:
                self.root.ids.result_label.text = f"Código: {codigo}\nNome: {name}\nTelefone: {telefone}"
                self.current_record = record
        else:
            self.root.ids.result_label.text = "Código não encontrado"
            self.current_record = None

    def confirm_presence(self, code=None):
        if code is None:
            code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.result_label.text = "Nenhum código escaneado"
            return

        self.load_excel()

        try:
            record = self.df.loc[self.df["codigo"] == code]
            if not record.empty:
                if record.iloc[0]["presença"] == "Presente":
                    self.root.ids.result_label.text = "Presença já confirmada"
                else:
                    idx = record.index[0]
                    self.df.at[idx, "presença"] = "Presente"
                    self.df.to_excel(self.excel_file_path, index_label='index')
                    self.root.ids.result_label.text = "Presença confirmada"
            else:
                self.root.ids.result_label.text = "Código não encontrado"
        except KeyError as e:
            self.root.ids.result_label.text = f"Erro ao buscar código: {str(e)}"

    def revert_presence(self):
        code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.result_label.text = "Nenhum código escaneado"
            return

        self.load_excel()

        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            if record.iloc[0]["presença"] == "Presente":
                idx = record.index[0]
                self.df.at[idx, "presença"] = "-"
                self.df["telefone"] = self.df["telefone"].astype(str)
                self.df.to_excel(self.excel_file_path, index_label='index')
                self.root.ids.result_label.text = "Presença revertida"
            else:
                self.root.ids.result_label.text = "Presença não estava confirmada"
        else:
            self.root.ids.result_label.text = "Código não encontrado"

    def clean_input(self):
        self.root.ids.cpf_input.text = ""
        self.root.ids.result_label.text = ""

    def open_register_popup(self):
        self.register_popup = RegisterPopup()
        self.register_popup.open()

    def save_new_entry(self):
        cpf = self.register_popup.ids.cpf_input_register.text.strip()
        nome = self.register_popup.ids.nome_input_register.text.strip()
        relacionamento = self.register_popup.ids.relacionamento_input_register.text.strip()
        telefone = self.register_popup.ids.telefone_input_register.text.strip()

        self.load_excel()

        # Get the last index and increment it
        if self.df.index.size > 0:
            last_index = int(self.df.index.max()) + 1
        else:
            last_index = 0  # Starting value for index

        new_entry = pd.DataFrame(
            {
                "codigo": [f"1000{str(last_index)}"],
                "cpf": [cpf],
                "nome": [nome],
                "relacionamento": [relacionamento],
                "telefone": [telefone],
                "presença": ["Presente"]
            },
            index=[last_index]
        )

        # Concatenate new_entry with self.df
        self.df = pd.concat([self.df, new_entry])
        self.df["telefone"] = self.df["telefone"].astype(str)

        # Save with the index labeled as 'Index'
        self.df.to_excel(self.excel_file_path, index_label='index')

        self.register_popup.dismiss()
        self.root.ids.result_label.text = "Novo cadastro salvo com presença confirmada"

    def view_records(self):
        self.load_excel()

        self.records_popup = RecordsPopup()

        grid = self.records_popup.ids.content_records
        grid.clear_widgets()

        # Define the columns to display
        columns_to_display = ["codigo", "nome", "relacionamento", "telefone", "presença"]
        grid.cols = len(columns_to_display) + 1  # Include index column

        # Add headers
        grid.add_widget(Label(text="Index", size_hint=(None, None), height=40, width=30))
        for column in columns_to_display:
            grid.add_widget(Label(text=column.capitalize(), size_hint_y=None, height=40))

        # Add data rows
        for index, row in self.df.iterrows():
            grid.add_widget(Label(text=str(index), size_hint=(None, None), height=40, width=30))
            for col in columns_to_display:
                grid.add_widget(Label(text=str(row[col]), size_hint_y=None, height=40))

        grid.bind(minimum_height=grid.setter('height'))

        self.records_popup.open()

    def close_popup(self, instance=None):
        if hasattr(self, 'register_popup') and self.register_popup:
            self.register_popup.dismiss()
        if hasattr(self, 'records_popup') and self.records_popup:
            self.records_popup.dismiss()

    def focus_next_input(self, current_input_id):
        input_ids = ['cpf_input_register', 'nome_input_register', 'relacionamento_input_register', 'telefone_input_register']
        next_index = (input_ids.index(current_input_id) + 1) % len(input_ids)
        next_input_id = input_ids[next_index]
        self.register_popup.ids[next_input_id].focus = True


qrcode().run()