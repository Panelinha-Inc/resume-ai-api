import cv2 as cv
from text_detect import TextDetect


dt = TextDetect(r'D:\src\OCR\tesseract.exe')

img = cv.imread('../data_test/exemplos_cvs_imagens/example18.jpg')
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
data = dt.get_data(img)
data = dt.join_words(data)

# Draw
# for r in data:
for r in range(data.shape[0]):
    r = data.iloc[r]
    cv.rectangle(img,
                 pt1=(r['left'], r['top']),
                 pt2=(r['left'] + r['width'], r['top'] + r['height']),
                 color=(0, 255, 0),
                 thickness=1)
    cv.putText(img, r['text'], (r['left'], r['top']), cv.FONT_HERSHEY_SIMPLEX, .6, (255, 0, 0), 1)

img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
p_resize = 700 / img.shape[0]
img = cv.resize(img, (int(img.shape[1] * p_resize), int(img.shape[0] * p_resize)))
cv.imshow('Image', img)
cv.waitKey(0)
