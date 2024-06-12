# pylint: disable=all
# flake8: noqa

import time
import kivy
import cv2
import pandas as pd
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.graphics.texture import Texture


class qrcodeLayout(GridLayout):
    pass


class qrcode(App):
    def build(self):
        return qrcodeLayout()
    
    
    
    def activate_camera(self):
        try:
            self.capture = cv2.VideoCapture(0)  # Default to camera index 0
            if not self.capture.isOpened():
                raise ValueError("Camera not available")
        except:
            self.capture = None
            self.root.ids.result_label.text = "Failed to access camera"
            return
        
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

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
                self.root.ids.result_label.text = "QR Code detectado"
                self.root.ids.capture_image.texture = texture

    def close_camera(self):
        if self.capture:
            self.capture.release()
        Clock.unschedule(self.update_camera)


qrcode().run()