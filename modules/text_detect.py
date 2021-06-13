import pytesseract
import platform
import pandas as pd
import numpy as np


class TextDetect():
    def __init__(self, path_cmd):
        if platform.system() == 'Windows':
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

    def join_words(self, data):
        """
        :param data: pandas dataframe with information extracted
        :return: pandas dataframe with words grouped in blocks
        """
        data = pd.DataFrame(data)
        return complete_top(complete_left(data))


def complete_left(data, range_left=1.2, range_top=.5):
    index_completed = []
    for left in data.left.sort_values().values:
        aux_ = data.loc[(data['left'] <= left) & ~data.index.isin(index_completed)]
        for index in aux_.index:
            while True:
                r = data.loc[index]
                next_word = data.loc[
                    data.left.isin(range(r.left + r.width, r.left + r.width + int(r.height * range_left)))&\
                    data.top.isin(range(r.top - int(r.height * range_top), r.top + int(r.height * range_top)))
                ]
                if next_word.shape[0] > 0:
                    next_word = next_word.iloc[0]

                    data.loc[r.name, 'width'] = data.loc[next_word.name, 'left'] - data.loc[r.name, 'left'] + data.loc[next_word.name, 'width']
                    data.loc[r.name, 'height'] = int(np.mean([data.loc[r.name, 'height'], data.loc[next_word.name, 'height']]))
                    data.loc[r.name, 'top'] = int(np.mean([data.loc[r.name, 'top'], data.loc[next_word.name, 'top']]))
                    data.loc[r.name, 'text'] = data.loc[r.name, 'text'] + ' ' + data.loc[next_word.name, 'text']

                    data.drop(index=next_word.name, inplace=True)
                else:
                    index_completed.append(r.name)
                    break
    return data


def complete_top(data, range_left=.5, range_top=1.25):
    index_completed = []
    for left in data.top.sort_values().values:
        aux_ = data.loc[(data['top'] <= left) & ~data.index.isin(index_completed)]
        for index in aux_.index:
            height = data.loc[index].height
            while True:
                r = data.loc[index]
                next_word = data.loc[
                    data.top.isin(range(r.top + 1, r.top + r.height + int(height * range_top)))&\
                    data.left.isin(range(r.left - int(height * range_left), r.left + int(height * range_left)))
                ]
                if next_word.shape[0] > 0:
                    next_word = next_word.iloc[0]

                    data.loc[r.name, 'width'] = max(data.loc[next_word.name, 'width'], data.loc[r.name, 'width'])
                    data.loc[r.name, 'height'] = data.loc[next_word.name, 'top'] - data.loc[r.name, 'top'] + data.loc[next_word.name, 'height']
                    data.loc[r.name, 'left'] = int(np.mean([data.loc[r.name, 'left'], data.loc[next_word.name, 'left']]))
                    data.loc[r.name, 'text'] = data.loc[r.name, 'text'] + ' ' + data.loc[next_word.name, 'text']

                    data.drop(index=next_word.name, inplace=True)
                else:
                    index_completed.append(r.name)
                    break
    return data
