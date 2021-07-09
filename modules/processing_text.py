import re
import spacy
import fitz
import numpy as np

def extract_info_from_text(text):

    # PHONE
    phones = re.findall('(\([0-9]{2}\) [0-9]{5}-[0-9]{4})|([0-9]{2} [0-9]{5}-[0-9]{4})|(\([0-9]{2}\) [0-9]{4} [0-9]{4})|([0-9]{2} [0-9]{9})|(\([0-9]{2}\) [0-9]{4}-[0-9]{4})', text)
    phones = [str(np.array(phone)[np.array(phone) != ''][0]) for phone in phones] if phones else []
    #print('* TEL: {}'.format(phones))

    # URLs
    urls = re.findall('(\S+@\S+)|((?:#|http)\S+)', text.replace('#.', '# .'))
    urls = [str(np.array(url)[np.array(url) != ''][0]) for url in urls] if urls else []
    contato = {
        'telefones': phones,
        'email': '',
        'github': '',
        'linkedin': '',
        'outros': ''
    }
    for url in urls:
        if 'linkedin' in url:
            contato['linkedin'] = url
        elif 'github' in url:
            contato['github'] = url
        elif '@' in url:
            contato['email'] = url
        else:
            contato['outros'] = url
    #print('* URLs: {}'.format(urls))

    # CEP
    cep = re.findall(r'[0-9]{5}-[0-9]{3} ', text)
    cep = cep[0].strip() if cep else ''
    #print('* CEP: {}'.format(cep))

    return {
        "cep": cep,
        "contato": contato
    }

    # NER
    '''doc = nlp(text)
    if doc.ents:
        for ent in doc.ents:
            print(ent.text, ent.label_)
    else:
        print('Nenhuma entidade encontrada')'''

def extract_info_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ''

        for page in pdf:
            text += page.getText().replace('●', '').replace('�', '').replace('•', '').replace('\u200b', '')

    text =  ' '.join(text.replace('\n', ' ').split())

    info = extract_info_from_text(text)

    dict = {
        "Dados pessoais": {
            "Contato": {
                "email": info["contato"]
            },
            "Endereço": {
                "CEP": info["cep"]
            }
        },
    }

    return dict
