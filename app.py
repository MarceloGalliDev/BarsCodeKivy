# pylint: disable=all
# flake8: noqa

from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Diretório onde as imagens estão armazenadas
IMAGE_DIRECTORY = 'static/images'

# Página inicial com links para as imagens
@app.route('/')
def index():
    # Lista de imagens no diretório
    import os
    images = os.listdir(IMAGE_DIRECTORY)

    # Gerar links HTML para download
    image_links = [f'<a href="/download/{img}">{img}</a>' for img in images]
    return render_template_string('<br>'.join(image_links))


# Rota para download das imagens
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(IMAGE_DIRECTORY, filename)


if __name__ == '__main__':
    app.run(debug=True)