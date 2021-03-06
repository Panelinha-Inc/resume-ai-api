import re
import spacy
import fitz
import numpy as np

nlp1 = spacy.load('modules/ner_model/model-best') #load the best model

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_phones(text):
    # PHONE
    phones = re.findall('(\([0-9]{2}\) [0-9]{5}-[0-9]{4})|([0-9]{2} [0-9]{5}-[0-9]{4})|(\([0-9]{2}\) [0-9]{4} [0-9]{4})|([0-9]{2} [0-9]{9})|(\([0-9]{2}\) [0-9]{4}-[0-9]{4})', text)
    phones = [str(np.array(phone)[np.array(phone) != ''][0]) for phone in phones] if phones else []
    return phones

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_urls(text):
    # URLs
    urls = re.findall('(\S+@\S+)|((?:#|http)\S+)|((?:#|www)\S+)', text.replace('#.', '# .').replace(' github.com', ' https://github.com'))
    urls = [str(np.array(url)[np.array(url) != ''][0]) for url in urls] if urls else []
    return urls

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_cep(text):
    # CEP
    cep = re.findall(r'[0-9]{5}-[0-9]{3} ', text)
    cep = cep[0].strip() if cep else ''
    return cep

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_data_nasc(text):
    # DATA NASC
    data_nasc = re.findall('([0-9]{2}/[0-9]{2}/[0-9]{4} )|([0-9]{2}/[0-9]{2}/[0-9]{2} )', text)
    data_nasc = [str(np.array(data)[np.array(data) != ''][0]) for data in data_nasc] if data_nasc else []
    data_nasc = data_nasc[0].strip() if data_nasc else ''
    return data_nasc

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_idiomas(text):
    # IDIOMAS
    main_languages = set(['ingl??s', 'espanhol', 'portugu??s', 'franc??s', 'libras', 'italiano', 'chin??s', 'mandarim chin??s', 'japon??s', 'hindi', '??rabe', 'russo', 'indon??sio', 'coreano', 'alem??o'])
    languages = []
    pos = re.search(r"(\bidioma\b)|(\bidiomas\b)|(\blanguages\b)|(\blinguagens\b)", text.lower())
    pos = pos.start() if pos else -1

    if pos:
        sentences = text[pos:].split()[1:]
        important_words = []
        flag_parenthesis = 0

        # Pegando as palavras importantes deste trecho, ou seja, pegando as palavas at?? que seja encontrado uma palavra em caixa alta
        for i, sent in enumerate(sentences):

            word = sent.replace('.', '').replace(';', '')
            
            if word.isupper():
                break
            
            # Tratando casos como ['(Limited', 'Working)'], que fazem parte da mesma senten??a
            elif '(' in word and ')' not in word:
                flag_parenthesis = 1
                continue

            # Tratando casos como ['(Limited', 'Working)'], que fazem parte da mesma senten??a
            elif ')' in word and '(' not in word:
                flag_parenthesis = 0
                important_words.append(f'{sentences[i-1]} {word}')
                continue
            
            important_words.append(word)

        # Tratando as palavras importantes, pois pode ser que tenha vindo alguma palavra que n??o faz parte dos idiomas
        for i, word in enumerate(important_words):
            
            if word.lower() in main_languages:
                languages.append(word)

            elif important_words[i-1].lower() in main_languages:
                languages[-1] = f'{languages[-1]} {word}'
            else:
                break

    return languages

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_experiencias(text):

    months = ['janeiro', 'fevereiro', 'mar??o', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    
    pos = re.search(r"(\bEXPERI??NCIA PROFISSIONAL\b)|(\bEXPERI??NCIA\b)|(\bEXPERI??NCIAS\b)", text)
    if not pos:
        pos = re.search(r"(\bExperi??ncia\b)|(\bExperi??ncias\b)", text)
    pos = pos.start() if pos else -1

    sentences = text[pos:]
    if sentences.split()[1].islower():
        experiencias = []
    else:
        if 'EXPERI??NCIA PROFISSIONAL' in sentences:
            sentences = sentences.split('EXPERI??NCIA PROFISSIONAL')[-1].split()
        elif 'EXPERI??NCIAS PROFISSIONAIS' in sentences:
            sentences = sentences.split('EXPERI??NCIAS PROFISSIONAIS')[-1].split()
        elif 'Experi??ncias Profissionais' in sentences:
            sentences = sentences.split('Experi??ncias Profissionais')[-1].split()
        else:
            sentences = sentences.split()[1:]

        if not sentences[0].isalpha(): sentences = sentences[1:]

        experiencias = []
        for i, word in enumerate(sentences):
            try:
                if (word.isupper() and sentences[i+1].lower() in months) or (word.upper() and word.lower() in months):
                    experiencias.append(word)
                elif (word.isupper() and word.isalpha() and sentences[i+1][0].isupper() and sentences[i-1][-1] != ',' and len(word) > 3) or \
                    (word == 'Forma????o' and sentences[i+1] == 'acad??mica'):
                    break
                else:
                    experiencias.append(word)
            except:
                continue

    return ' '.join(experiencias)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def extract_info_from_text(text):

    phones = get_phones(text)
    urls = get_urls(text)
    cep = get_cep(text)
    data_nasc = get_data_nasc(text)
    idiomas = get_idiomas(text)
    experiencias = get_experiencias(text)

    contato = {
        'Telefones': phones,
        'Email': '',
        'GitHub': '',
        'LinkedIn': '',
        'Outros': []
    }

    for url in urls:
        if 'linkedin' in url:
            contato['LinkedIn'] = url
        elif 'github' in url:
            contato['GitHub'] = url
        elif '@' in url:
            contato['Email'] = url
        else:
            contato['Outros'].append(url)

    return {
        "data_nasc": data_nasc,
        "cep": cep,
        "contato": contato,
        "idiomas": idiomas,
        "experiencias": experiencias
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
            text += page.getText().replace('???', '').replace('???', '').replace('???', '').replace('\u200b', '')

    doc = nlp1(text)
    text =  ' '.join(text.replace('\n', ' ').split()).replace('. com', '.com')
    
    for  i in range(97, 123):
        letter = chr(i)
        text = text.replace(f'{letter}- ', f'{letter}-')

    info = extract_info_from_text(text)
    nome = ''
    endereco = ''
    cursos = []

    for ent in doc.ents:
        text_ent = ent.text.replace('\n', ' ').replace('\xa0', ' ')
        text_ent = ' '.join(text_ent.replace('\n', ' ').split())

        if not nome and ent.label_ == 'nome':
            nome = text_ent

        if not endereco and ent.label_ == 'endereco':
            endereco = text_ent

        if ent.label_ == 'curso':
            cursos.append(text_ent)

    return {
        "Dados pessoais": {
            "Nome": nome,
            "Data de nascimento": info["data_nasc"],
            "Contato": info["contato"],
            "Endere??o": {
                "Endere??o": endereco,
                "CEP": info["cep"]
            }
        },
        "Idiomas": info["idiomas"],
        "Experi??ncias profissionais": info["experiencias"],
        "Forma????o": cursos
    }