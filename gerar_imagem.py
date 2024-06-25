# pylint: disable=all
# flake8: noqa

import os
import qrcode
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer


def gerando_dados():
    excel_file_path = "tabela/tabela.xlsx"
    df = pd.read_excel(
        excel_file_path,
        dtype={
            "codigo": str,
            "cpf": str,
            "nome": str,
            "presença": str,
            "telefone": str
        }
    )

    for index, row in df.iterrows():
        codigo = row["codigo"]
        cpf = row["cpf"]
        nome = row["nome"]
        telefone = row["telefone"]
        text = f"Código: {codigo}\nNome: {nome}\nCPF: {cpf}\nTelefone: {telefone}"
        
        create_text_image(text, codigo)
        create_qrcode_image(codigo)
        insert_qr_code(codigo)
        

def create_text_image(text, codigo_qr):
    font_size = 32
    image_width = 600
    image_height = 200

    image = Image.new('RGBA', (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    
    font_path = os.path.join(os.getcwd(), "assets/Roboto-Regular.ttf")
    output_image_path = f"qrcodes/dados/dados_{codigo_qr}.png"

    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Não foi possível carregar a fonte {font_path}. Usando a fonte padrão.")
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    text_lines = text.split('\n')
    line_height = font_size + 5
    total_text_height = line_height * len(text_lines)

    y_start = (image_height - total_text_height) // 2
    for i, line in enumerate(text_lines):
        text_width = draw.textbbox((0, 0), line, font=font)[2]
        x_position = (image_width - text_width) // 2
        y_position = y_start + i * line_height
        draw.text((x_position, y_position), line, font=font, fill="black")

    image.save(output_image_path)


def create_qrcode_image(codigo_qr):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=17,
        border=1,
    )
    qr.add_data(codigo_qr)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.7)
    )
    img.save(f"qrcodes/qrcode/qr_{codigo_qr}.png")


def insert_qr_code(codigo_qr):
    base_image_path = "assets/imagem-convite.png"
    text_image_path = f"qrcodes/dados/dados_{codigo_qr}.png"
    qrcode_image_path = f"qrcodes/qrcode/qr_{codigo_qr}.png"
    output_image_path = f"qrcodes/final/final_{codigo_qr}.png"
    
    base_image = Image.open(base_image_path)
    qr_image = Image.open(qrcode_image_path)
    qr_dados = Image.open(text_image_path)
    
    base_width, base_height = base_image.size
    qr_width, qr_height = qr_image.size

    position1 = ((base_width - qr_width) - 890, base_height - qr_height - 10)
    position2 = ((base_width - qr_width) - 300, base_height - qr_height + 150)

    # Inserir o QR code na posição especificada
    base_image.paste(qr_image, position1)
    base_image.paste(qr_dados, position2)

    # Salvar a imagem final
    base_image.save(output_image_path)


gerando_dados()