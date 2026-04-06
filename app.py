from flask import Flask, render_template, request, send_file
from PIL import Image

app = Flask(__name__)

# Encode pesan ke gambar
def encode_image(image, message):
    binary_message = ''.join(format(ord(i), '08b') for i in message) + '1111111111111110'
    img = image.copy()
    pixels = img.load()

    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(pixels[x, y])

            for i in range(3):  # RGB
                if data_index < len(binary_message):
                    pixel[i] = pixel[i] & ~1 | int(binary_message[data_index])
                    data_index += 1

            pixels[x, y] = tuple(pixel)

    return img

# Decode pesan dari gambar
def decode_image(image):
    binary_data = ""
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            pixel = pixels[x, y]
            for i in range(3):
                binary_data += str(pixel[i] & 1)

    bytes_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ""

    for byte in bytes_data:
        if byte == '11111110':
            break
        message += chr(int(byte, 2))

    return message


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encode', methods=['POST'])
def encode():
    file = request.files['image']
    message = request.form['message']

    image = Image.open(file)
    encoded = encode_image(image, message)

    output_path = "encoded.png"
    encoded.save(output_path)

    return send_file(output_path, as_attachment=True)


@app.route('/decode', methods=['POST'])
def decode():
    file = request.files['image']
    image = Image.open(file)

    message = decode_image(image)
    return f"Pesan tersembunyi: {message}"


if __name__ == '__main__':
    app.run(debug=True)