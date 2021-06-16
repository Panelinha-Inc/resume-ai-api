from pdf2image import convert_from_path
import os

# Referência lib de conversão: https://pypi.org/project/pdf2image/
# Referência para as imagens resultantes: https://pillow.readthedocs.io/en/stable/reference/Image.html

def pdfConverter(input_path, output_path='images', form='png', dpi=300, poppler_path=None):

    """ Converts each page of a PDF document into an image, 
    saves the images to the device, and returns a list with 
    each page being an object of the PIL type.

    Parameters:
        input_path: str, required
            String with the path to the file to be converted.

        output_path: str, default 'images'
            String with the path to the directory where the images should be saved.

        form: str, dafault 'png'
            Format in which the image should be saved.

        dpi: int, default 300
            Measure of image print quality, in dots per inch.

        save_in_folder: bool, default False
            Indicates if the images should be saved in a folder.

    Returns:
        images: list
            List of PIL objects. Each object brings one page from the original PDF file. 

    """
    images = convert_from_path(input_path, fmt=form, dpi=dpi, poppler_path=poppler_path)

    if output_path:

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        filename = input_path.split('/')[-1].split('.')[0]

        for i, im in enumerate(images):
            im.save(output_path+'/'+filename+'_0'+str(i)+'.'+form)
    
    return images