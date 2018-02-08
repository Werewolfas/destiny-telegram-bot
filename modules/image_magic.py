from io import BytesIO
from PIL import Image
import requests


class ImageMagic:

    def merge_images(self, images, name):
        size = len(images)
        if size % 2 != 0:
            size = size + 1
        size = int(size / 2 * 100)

        result = Image.new("RGB", (size, 200))

        for index, file in enumerate(images):
            response = requests.get(file)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((100, 100), Image.ANTIALIAS)
            x = index // 2 * 100
            y = index % 2 * 100
            w, h = img.size
            result.paste(img, (x, y, x + w, y + h))

        result.save('images/{}.jpg'.format(name))
        return result

