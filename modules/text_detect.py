import pytesseract

class TextDetect():
    def __init__(self, path_cmd):
        pytesseract.pytesseract.tesseract_cmd = path_cmd

    def get_data(self, image):
        """
        :param image: image for text detection
        :return: list of dictionaries with information extracted by tesseract
        """
        boxes = pytesseract.image_to_data(image, lang='por')
        rows = boxes.splitlines()
        columns = rows[0].split()
        to_int = columns[:-1]
        data = []
        for r in rows[1:]:
            info = r.split()
            if len(info) < 12:
                continue
            data.append(dict(zip(columns, info)))
            for k in to_int:
                data[-1][k] = int(data[-1][k])
        return data
