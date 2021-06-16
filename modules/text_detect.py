import pytesseract
import pandas as pd


class TextDetect():
    def __init__(self, path_cmd):
        pytesseract.pytesseract.tesseract_cmd = path_cmd

    def get_data(self, image, join=True):
        """
        :param image: image for text detection
        :param join: dafault True: apply data to join_word
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
        if join:
            return self.join_words(pd.DataFrame(data))
        return data

    def join_words(self, data):
        """
        :param data: a dataframe pandas
        :return: a dataframe pandas
        """
        data['order'] = data.apply(lambda x: x.par_num * 100 + x.line_num * 10 + x.word_num, axis=1)
        data['width_s'] = data.apply(lambda x: x.width + x.left, axis=1)
        data['height_s'] = data.apply(lambda x: x.height + x.top, axis=1)

        words_ = dict(left=[], top=[], width=[], height=[], text=[])
        for bn in data.block_num.unique():
            aux_ = data[data.block_num == bn].sort_values('order')
            words_['text'].append(' '.join(aux_.text.values))
            words_['left'].append(aux_.left.min())
            words_['top'].append(aux_.top.min())
            words_['width'].append(aux_.width_s.max() - words_['left'][-1])
            words_['height'].append(aux_.height_s.max() - words_['top'][-1])

        return pd.DataFrame(words_)
