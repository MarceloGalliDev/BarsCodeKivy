# pylint: disable=all
# flake8: noqa

import os
import logging
import cv2
import kivy
import numpy as np
import pandas as pd
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from pyzbar.pyzbar import decode
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class qrcodeLayout(GridLayout):
    pass

class RegisterPopup(Popup):
    pass

class RecordsPopup(Popup):
    pass

class qrcode(App):
    def build(self):
        self.excel_file_path = "tabela/lista-envio.xlsx"
        self.load_excel()
        self.image_saved = False
        self.excel_google_drive_folder_id = '13FG1hOOEo06iCEeyBYst1lHFS2cwtNmR'
        self.image_google_drive_folder_id = '1kPevvxGN5_jo0dpUETPd9VdTlvxx8P08'
        self.drive_service = self.authenticate_google_drive()
        Clock.schedule_interval(self.upload_periodically, 600)
        return qrcodeLayout()

    def activate_camera(self):
        try:
            self.capture = cv2.VideoCapture(1)
            self.capture.set(3, 640)
            self.capture.set(4, 480)
            if not self.capture.isOpened():
                raise ValueError("Câmera não disponível")
        except:
            self.capture = None
            self.root.ids.result_label.text = "Falha ao acessar câmera"
            return

        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

    def update_camera(self, dt):
        if self.capture is None:
            return

        success, img = self.capture.read()
        if success:
            buf = cv2.flip(img, 0).tobytes()
            texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.root.ids.camera_image.texture = texture

            qr_codes_detected = False

            try:
                for barcode in decode(img):
                    myData = barcode.data.decode('utf-8')
                    self.root.ids.cpf_input.text = myData

                    pts = np.array([barcode.polygon], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(img, [pts], True, (0, 255, 0), 5)
                    pts2 = barcode.rect

                    if not self.image_saved:
                        self.confirm_presence(myData)
                        self.lookup_qrcode(myData)
                        self.save_and_upload_image(img, myData)
                        self.image_saved = True

                    display_text = f"QRCode detectado"
                    cv2.putText(img, display_text, (pts2[0], pts2[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    buf = cv2.flip(img, 0).tobytes()
                    capture_texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
                    capture_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                    self.root.ids.capture_image.texture = capture_texture

                    qr_codes_detected = True

            except Exception as e:
                logging.error(f"Erro decodificador QR code: {e}")
                self.root.ids.result_label.text = f"Erro decodificador QR code: {e}"

            if not qr_codes_detected:
                self.root.ids.result_label.text = "Aguardando QR Code..."
                self.image_saved = False 

    def save_and_upload_image(self, img, code):
        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            name = record.iloc[0]["nome"]
            img_path = os.path.join("static/images", f"{name}.png")
            cv2.imwrite(img_path, img)
            logging.info(f"Imagem salva em: {img_path}")
            self.upload_to_google_drive(img_path, f"{name}.png", self.image_google_drive_folder_id)

    def clear_button_message_label(self, dt):
        self.root.ids.button_message_label.text = ""

    def close_camera(self):
        if self.capture:
            self.capture.release()
        Clock.unschedule(self.update_camera)

    def load_excel(self):
        try:
            self.df = pd.read_excel(
                self.excel_file_path,
                dtype={"codigo": str, "cpf": str, "nome": str, "presenca": str, "celular": str, "link": str},
                index_col=0
            )
        except Exception as e:
            self.root.ids.result_label.text = f"Falha ao acessar excel: {str(e)}"

    def lookup_qrcode(self, code):
        self.load_excel()
        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            codigo = record.iloc[0]["codigo"]
            cpf = record.iloc[0]["cpf"]
            name = record.iloc[0]["nome"]
            celular = record.iloc[0]["celular"]
            presenca = record.iloc[0]["presenca"]
            result_text = f"Código: {codigo}\nNome: {name}\nCelular: {celular}\nPresença: {presenca}"
            self.root.ids.result_label.text = result_text
            self.root.ids.last_result_label.text = result_text
            self.current_record = record
        else:
            self.root.ids.result_label.text = "Código não encontrado"
            self.current_record = None

    def lookup_name(self):
        code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.button_message_label.text = "Nenhum código escaneado"
            Clock.schedule_once(self.clear_button_message_label, 3)
            return

        self.load_excel()

        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            codigo = record.iloc[0]["codigo"]
            cpf = record.iloc[0]["cpf"]
            name = record.iloc[0]["nome"]
            celular = record.iloc[0]["celular"]
            presenca = record.iloc[0]["presenca"]
            result_text = f"Código: {codigo}\nNome: {name}\nCPF: {cpf}\nCelular: {celular}\nPresença: {presenca}"
            self.root.ids.result_label.text = result_text
            self.root.ids.last_result_label.text = result_text
            self.current_record = record
        else:
            self.root.ids.button_message_label.text = "Código não encontrado"
            Clock.schedule_once(self.clear_button_message_label, 3)
            self.current_record = None

    def authenticate_google_drive(self):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        return build('drive', 'v3', credentials=credentials)

    def upload_to_google_drive(self, file_path, file_name, folder_id):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if file_name.endswith('.xlsx') else 'image/png')
        try:
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            logging.info(f'File ID: {file.get("id")} uploaded successfully to Google Drive.')
        except Exception as e:
            logging.error(f"Erro ao enviar para o Google Drive: {e}")

    def upload_periodically(self, dt):
        try:
            self.upload_to_google_drive(self.excel_file_path, 'lista-envio-atualizada.xlsx')
            logging.info("Lista enviado para o Google Drive.")
        except Exception as e:
            logging.error(f"Erro ao enviar para o Google Drive: {e}")

    def confirm_presence(self, code=None):
        if code is None:
            code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.button_message_label.text = "Nenhum código escaneado"
            Clock.schedule_once(self.clear_button_message_label, 3)
            return

        self.load_excel()

        try:
            record = self.df.loc[self.df["codigo"] == code]
            if not record.empty:
                if record.iloc[0]["presenca"] == "Presente":
                    self.root.ids.button_message_label.text = "Presença já confirmada"
                else:
                    idx = record.index[0]
                    self.df.at[idx, "presenca"] = "Presente"
                    self.df.to_excel(self.excel_file_path, index_label='index')
                    self.root.ids.button_message_label.text = "Presença confirmada"
                    # Removido o envio imediato para o Google Drive
            else:
                self.root.ids.button_message_label.text = "Código não encontrado"
        except KeyError as e:
            self.root.ids.button_message_label.text = f"Erro ao buscar código: {str(e)}"

        Clock.schedule_once(self.clear_button_message_label, 3)

    def revert_presence(self):
        code = self.root.ids.cpf_input.text.strip()
        if not code:
            self.root.ids.button_message_label.text = "Nenhum código escaneado"
            Clock.schedule_once(self.clear_button_message_label, 3)
            return

        self.load_excel()

        record = self.df.loc[self.df["codigo"] == code]
        if not record.empty:
            if record.iloc[0]["presenca"] == "Presente":
                idx = record.index[0]
                self.df.at[idx, "presenca"] = "-"
                self.df["celular"] = self.df["celular"].astype(str)
                self.df.to_excel(self.excel_file_path, index_label='index')
                self.root.ids.button_message_label.text = "Presença revertida"
            else:
                self.root.ids.button_message_label.text = "Presença não estava confirmada"
        else:
            self.root.ids.button_message_label.text = "Código não encontrado"

        Clock.schedule_once(self.clear_button_message_label, 3)

    def clean_input(self):
        self.root.ids.cpf_input.text = ""
        self.root.ids.result_label.text = ""
        self.root.ids.button_message_label.text = ""

    def open_register_popup(self):
        self.register_popup = RegisterPopup()
        self.register_popup.open()

    def save_new_entry(self):
        cpf = self.register_popup.ids.cpf_input_register.text.strip()
        nome = self.register_popup.ids.nome_input_register.text.strip()
        relacionamento = self.register_popup.ids.relacionamento_input_register.text.strip()
        celular = self.register_popup.ids.celular_input_register.text.strip()

        self.load_excel()

        if self.df.index.size > 0:
            last_index = int(self.df.index.max()) + 1
        else:
            last_index = 0

        new_entry = pd.DataFrame(
            {
                "codigo": [f"1000{str(last_index)}"],
                "cpf": [cpf],
                "nome": [nome],
                "relacionamento": [relacionamento],
                "celular": [celular],
                "presenca": ["Presente"]
            },
            index=[last_index]
        )

        self.df = pd.concat([self.df, new_entry])
        self.df["celular"] = self.df["celular"].astype(str)

        self.df.to_excel(self.excel_file_path, index_label='index')

        self.register_popup.dismiss()
        self.root.ids.button_message_label.text = "Novo cadastro salvo com presença confirmada"
        Clock.schedule_once(self.clear_button_message_label, 3)

    def view_records(self):
        self.load_excel()

        self.records_popup = RecordsPopup()

        grid = self.records_popup.ids.content_records
        grid.clear_widgets()

        columns_to_display = ["codigo", "nome", "relacionamento", "celular", "presenca"]
        grid.cols = len(columns_to_display) + 1

        grid.add_widget(Label(text="Index", size_hint=(None, None), height=40, width=30))
        for column in columns_to_display:
            grid.add_widget(Label(text=column.capitalize(), size_hint_y=None, height=40))

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
        input_ids = ['cpf_input_register', 'nome_input_register', 'relacionamento_input_register', 'celular_input_register']
        next_index = (input_ids.index(current_input_id) + 1) % len(input_ids)
        next_input_id = input_ids[next_index]
        self.register_popup.ids[next_input_id].focus = True


if __name__ == "__main__":
    qrcode().run()
