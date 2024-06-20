import lxml.etree as et
import re
import zipfile
from number_parser import parse
from nltk import sent_tokenize

# архитектурно хотим легко заменять эвристики на более совершенные алгоритмы
# USE nltk for sentence tokenization

class Requirements:
    # эвристики редактируются пользователем (map) Онтология: (__* - concept (экстенсионал), [...] - интенсионал) +  отношения
    # визуализатор и редактор онтологии - табличный вид
    __recognized_fonts = ['Times New Roman',
                          'Calibri', 'Arial']
    __recognized_lit_templates = ['ГОСТ Р 7.0.100 -2018', 'ГОСТ Р 7.0.5 -2008', 'ГОСТ Р 7.0.5 --2008',
                                  'ГОСТ Р 7.0.5 2008', 'Ванкуверский стиль', 'Vancouver', 'Harvard',
                                  'Council of Biology Editors',
                                  'GSA', 'MLA', 'MHRA', 'Chicago', 'AMS', 'ASME', 'AMA', 'NLM', 'APA', 'APSA', 'ASABE',
                                  'ASA', 'AMA', 'AIP', 'IEEE', 'ALWD', 'NISO Z39.29-2005']
    __recognized_formats = 'xf, plt, gif, cgm, cdr, eps, ps, jpg, jpeg, pcd, pct, drw, jpeg, pcx, png, tif, tiff, tiff-files, tga, dib, bmp, rle, wmf, emf, wpg'.split(
        ', ')
    __recognized_max = ['макс', 'мен', 'ниже', 'короч']
    __recognized_max_inverted = ['не' + sub1 + sub2 for sub1 in [' ', ' должен быть ', ' должен '] for sub2 in
                                 ['бол', 'выш', 'длинн', 'превыш', 'превосход']] + \
                                ['не ' + sub2 for sub2 in ['бол', 'выш', 'длинн', 'превыш', 'превосход']]
    __recognized_min = ['мин', 'бол', 'выш', 'длинн']
    __recognized_min_inverted = ['не' + sub1 + sub2 for sub1 in [' ', ' должен быть ', ' должен '] for sub2 in
                                 ['меньш', 'ниже', 'короч', 'мене']] + \
                                ['не ' + sub2 for sub2 in ['меньш', 'ниже', 'короч', 'менее']]
    __recognized_volume = ['объем', 'объём', 'размер', 'содержа', 'состоя', 'количеств']
    __recognized_volume_unit = ['cтр', 'знаков без пробелов', 'символов без пробелов', 'знаков с пробелам',
                                'символов с пробелам', 'знак', 'символ', 'слов']
    __recognized_article = ['стать', 'документ', 'работ', 'исследовани', 'рукопис']
    __recognized_image = ['графическ', 'иллюстрац', 'рисун', 'фото']
    __recognized_direction = ['верх', 'ниж', 'низ', 'прав', 'лев']
    __recognized_linear_unit = ['см', 'мм', 'дм', 'сантиметр', 'миллиметр', 'децимметр', 'метр', 'м']
    __recognized_field = ['поле', 'поля']
    __recognized_table = ['табл']
    __recognized_formules = ['формул']
    __recognized_authors = ['автор']
    __recognized_affiliation = ['аффили', 'email', 'e-mail', 'организац', 'адрес', 'телефон', 'почт']
    __recognized_lit = ['лит', 'источник', 'используемые публикац', 'используемых публикац']
    __recognized_keywords = ['ключев']
    __recognized_name = ['заглавие', 'заголовок', 'название', ]
    __recognized_common = ['оформление текст', 'основной текст']
    __namespaces = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    lang = 'rus'

    def __init__(self, file):
        z = zipfile.ZipFile('in/' + file)
        marked_up_docx = z.open("word/document.xml")

        self.__etree = et.parse(marked_up_docx)
        self.__root = self.__etree.getroot()
        self.__requirements_general = {
            'format': None,
            'font': None,
            'font_size_general': None,
            'font_size_section_title': None,
            'line_spacing': None,
            'intent_right': None,
            'intent_left': None,
            'intent_up': None,
            'intent_down': None,
            'two_columns': None,
            'column_width': None,
            'one_column_to_annotation': None,
            'annotation_column_width': None,
            'alignment': None,

            'italic_allowed': None,
            'bold_allowed': None,
            'underlined_allowed': None,
            'double_space_allowed': None,
            'tab_as_space_allowed': None,
            'shift_enter_line_break_allowed': None,

            'size_min': None,
            'size_max': None,
            # 'lang': 'rus',
        }
        self.__requirements_image = {
            'number_min': None,
            'number_max': None,
            'dpi_min': None,
            'color_allowed': None,
            'width_max': None,
            'duplicate_as_files': None,
            'file_format': None,
            'links_required': None,
        }
        self.__requirements_table = {
            'width_max': None,
            'links_required': None,
        }
        self.__requirements_UDC = {
            'required': None,
        }
        self.__requirements_title = {
            'words_max': None,
            'font_size_title': None,
        }
        self.__requirements_authors = {
            'num_max': None,
        }
        self.__requirements_affiliation = {
            'required': None,
            'email_required': None,
            'phone_required': None,
            'faculty_required': None,
            'organization_required': None,
            'city_required': None,
            'postal_code_required': None,
            'country_required': None,
        }
        self.__requirements_annotation = {
            'required': None,
            'length_min': None,
            'length_max': None,
            'english_duplicate': None,
        }
        self.__requirements_keywords = {
            'required': None,
            'num_min': None,
            'num_max': None,
            'english_duplicate': None,
        }
        self.__requirements_financing = {
            'required': None,
        }
        self.__requirements_gratitude = {
            'required': None,
        }
        self.__requirements_introduction = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_purpose = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_materials_methods = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_results = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_practical_significance = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_discussion = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_conclusion = {
            'required': None,
            'size_min': None,
            'size_max': None,
        }
        self.__requirements_literature = {
            'required': None,
            'num_min': None,
            'num_max': None,
            'style': None,
            'foreign_part_min': None,
            'foreign_part_max': None,
            'novelty_period': None,
            'new_part_min': None,
            'new_part_max': None,
            'antiquity_period': None,
            'selfcitation_part_min': None,
            'selfcitation_part_max': None,
            'DOI_required': None,
        }
        self.__requirements_authors_info = {
            'required': None,
        }
        self.__requirements_authors_contribution = {
            'required': None,
        }
        self.__requirements_accompanying_documents = {
            'required': None,
        }

    def __get_all_paragraphs(self):
        elements = self.__root.findall('.//w:p', Requirements.__namespaces)
        return elements

    def get_all_paragraphs(self):
        return self.__get_all_paragraphs()

    def __get_text_from_element(self, element):
        # print(element)
        text = element.findall('.//w:t', Requirements.__namespaces)
        txt = ''
        for part in text:
            txt += part.text
        return txt

    def get_text_from_element(self, element):
        return self.__get_text_from_element(element)

    #   !!
    def get_format(self):
        paragraphs = self.__get_all_paragraphs()
        for i, paragraph in enumerate(paragraphs):
            text = self.__get_text_from_element(paragraph)

            text_arr = text.split(' ')
            for i, word in enumerate(text_arr):
                if 'А4' in word or 'А3' in word or 'А0' in word or 'А1' in word or 'А2' in word or 'А5' in word or 'А6' in word:
                    self.__requirements_of_format['Format'] = word

        # print(self.__requirements_of_format)
        return self.__requirements_of_format

    # !
    #  !!
    def get_literature_style(self):
        paragraphs = self.__get_all_paragraphs()
        for i, paragraph in enumerate(paragraphs):
            text = self.__get_text_from_element(paragraph)
            if 'ГОСТ' in text:
                # print(text, style, style in text)
                self.__requirements_literature['style'] = 'ГОСТ Р 7.0.5 -2008'
                style = 'ГОСТ Р 7.0.5 -2008'
                return style
            for style in self.__recognized_lit_templates:
                if style in text:
                    self.__requirements_literature['style'] = style
                    return style

    # ?
    def clean_form_sp(self, text: str):
        # remove non-breaking spaces
        text = text.replace(u'\xa0', u' ')
        text = text.replace(u'\n', u' ')
        n_t = ''
        t = []
        text = text.replace('(', '')
        text = text.replace(')', '')
        text_ar = text.split(' ')
        # print(text_ar)
        i = 0
        while i < len(text_ar) - 1:
            # print(t)
            if len(text_ar[i]) > 0:
                if text_ar[i].isdigit() and text_ar[i + 1].isdigit():
                    t.append(text_ar[i] + text_ar[i + 1])
                    i += 1
                elif text_ar[i][0].isdigit() and '-' in text_ar[i]:
                    dia = text_ar[i].split('-')
                    # print('heres')
                    t.append('от')
                    t.append(dia[0])
                    t.append('до')
                    t.append(dia[1])
                    # i+=1
                elif text_ar[i][0].isdigit() and '–' in text_ar[i]:
                    dia = text_ar[i].split('–')
                    # print('heres')
                    t.append('от')
                    t.append(dia[0])
                    t.append('до')
                    t.append(dia[1])
                else:
                    t.append(text_ar[i])
            i += 1
        t.append(text_ar[-1])
        return ' '.join(t)

    def split_to_sentences(self, text):
        return sent_tokenize(text)

    def __text_contains_word_from_list(self, text: str, list):
        for w in list:
            if w.lower() in text.lower():
                return True
        return False

    def __text_contains_word_from_list_with_word(self, text: str, list):
        for w in list:
            if w.lower() in text.lower():
                return True, w
        return False, ' '

    def __check_min_max_exists(self, text: str):
        min_exists, max_exists = False, False
        word_list = text.split(' ')
        # print(word_list)
        if (self.__text_contains_word_from_list(text.lower(), self.__recognized_min_inverted)):
            min_exists = True
        elif (not min_exists):
            for i, word in enumerate(word_list):
                if (self.__text_contains_word_from_list(word, self.__recognized_min)):
                    ok = True
                    for j in range(1, 5):
                        if (i >= j):
                            if (word_list[i - j].lower() == 'не'):
                                ok = False
                    if (ok):
                        min_exists = True
                        break
        if (self.__text_contains_word_from_list(text.lower(), self.__recognized_max_inverted)):
            max_exists = True
        elif (not max_exists):
            for i, word in enumerate(word_list):
                if (self.__text_contains_word_from_list(word, self.__recognized_max)):
                    # print("OK")
                    ok = True
                    for j in range(1, 5):
                        if (i >= j):
                            if (word_list[i - j].lower() == 'не'):
                                ok = False
                    if (ok):
                        max_exists = True
                        break
        return min_exists, max_exists

    def get_min_max_volume(self):
        # Мин/макс объём текста
        paragraphs = self.__get_all_paragraphs()
        min_volume = None
        max_volume = None
        volume_unit_max = None
        volume_unit_min = None
        volume_unit = None
        for paraph in paragraphs:
            text = self.__get_text_from_element(paraph)
            text = self.clean_form_sp(text)
            if (self.__text_contains_word_from_list(text, self.__recognized_volume) or \
                self.__text_contains_word_from_list(text, self.__recognized_volume_unit)) and \
                    self.__text_contains_word_from_list(text, self.__recognized_article):
                sentence_list = text.split('.')
                for sent in sentence_list:
                    if self.__text_contains_word_from_list(sent, self.__recognized_volume) and \
                            self.__text_contains_word_from_list(sent, self.__recognized_article):

                        sent = parse(sent)
                        # print(sent)
                        min_exists, max_exists = self.__check_min_max_exists(sent)
                        word_list = sent.split(' ')

                        for i, word in enumerate(word_list):
                            # print(word)
                            if i < len(word_list) - 1:
                                if word.isdigit():
                                    min_exists_there, max_exists_there = False, False
                                    if (i > 0 and (word_list[i - 1] == 'от' or word_list[i - 1] == 'c')):
                                        min_exists_there = True
                                    if (i > 0 and (word_list[i - 1] == 'до' or word_list[i - 1] == 'по')):
                                        max_exists_there = True
                                    # print(word_list[i+1])
                                    # print(self.__recognized_volume_unit)
                                    unit_found, unit = self.__text_contains_word_from_list_with_word(word_list[i + 1],
                                                                                                     self.__recognized_volume_unit)
                                    # print(unit_found, unit)
                                    if (unit_found):
                                        match unit:
                                            case 'стр':
                                                volume_unit = 'стр'
                                            case 'знаков без пробелов' | 'символов без пробелов':
                                                volume_unit = 'сбп'
                                            case 'знаков с пробелам' | 'символов с пробелам':
                                                volume_unit = 'ссп'
                                            case 'слов':
                                                volume_unit = 'слов'
                                            case _:
                                                volume_unit = 'ссп'
                                    # print(min_exists)
                                    # print(max_exists)
                                    if (min_exists or min_exists_there):
                                        if (min_volume == None):
                                            min_volume = int(word)
                                            volume_unit_min = volume_unit
                                        else:
                                            # print(min_volume)
                                            if (int(word) > min_volume):
                                                min_volume = int(word)
                                                volume_unit_min = volume_unit
                                    if (max_exists or max_exists_there):
                                        if (max_volume == None):
                                            max_volume = int(word)
                                            volume_unit_max = volume_unit
                                        else:
                                            # print(max_volume)
                                            if (int(word) < max_volume):
                                                max_volume = int(word)
                                                volume_unit_max = volume_unit
        return [min_volume, volume_unit_min, max_volume, volume_unit_max]

    def get_min_max_lit(self):
        paragraphs = self.__get_all_paragraphs()
        min_lit = None
        max_lit = None
        for paraph in paragraphs:
            text = self.__get_text_from_element(paraph)
            text = self.clean_form_sp(text)
            if (self.__text_contains_word_from_list(text, self.__recognized_lit)):
                sentence_list = text.split('.')
                for sent in sentence_list:
                    if (self.__text_contains_word_from_list(sent, self.__recognized_lit)):
                        sent = parse(sent)
                        # print(sent)
                        word_list = sent.split(' ')
                        min_exists, max_exists = self.__check_min_max_exists(sent)

                        for i, word in enumerate(word_list):
                            # print(word)
                            if i < len(word_list):
                                if word.isdigit():
                                    min_exists_there, max_exists_there = False, False
                                    if (i > 0 and (word_list[i - 1] == 'от' or word_list[i - 1] == 'c')):
                                        min_exists_there = True
                                    if (i > 0 and (word_list[i - 1] == 'до' or word_list[i - 1] == 'по')):
                                        max_exists_there = True
                                    # print(word_list[i+1])

                                    # print(min_exists)
                                    # print(max_exists)
                                    if (min_exists or min_exists_there):
                                        if (min_lit == None):
                                            min_lit = int(word)
                                        else:
                                            if (int(word) > min_lit):
                                                min_lit = int(word)
                                    if (max_exists or max_exists_there):
                                        if (max_lit == None):
                                            max_lit = int(word)
                                        else:
                                            if (int(word) < max_lit):
                                                max_lit = int(word)
        return [min_lit, max_lit]

    def get_min_max_image_count(self):
        paragraphs = self.__get_all_paragraphs()
        min_image = None
        max_image = None
        for paraph in paragraphs:
            text = self.__get_text_from_element(paraph)
            text = self.clean_form_sp(text)
            if (self.__text_contains_word_from_list(text, self.__recognized_image)):
                sentence_list = text.split('.')
                for sent in sentence_list:
                    if (self.__text_contains_word_from_list(sent, self.__recognized_image)):
                        sent = parse(sent)
                        print(sent)
                        word_list = sent.split(' ')
                        print(word_list)
                        min_exists, max_exists = self.__check_min_max_exists(sent)

                        for i, word in enumerate(word_list):
                            # print(word)
                            if i < len(word_list) - 1:
                                if word.isdigit():
                                    if (word_list[i + 1].lower() == 'dpi'):
                                        continue
                                    ok = True
                                    for j in range(1, 5):
                                        if (i + j < len(word_list)):
                                            if ('%' in word_list[i + j]):
                                                ok = False
                                                break
                                    if (not ok):
                                        continue
                                    min_exists_there, max_exists_there = False, False
                                    if (i > 0 and (word_list[i - 1] == 'от' or word_list[i - 1] == 'c')):
                                        min_exists_there = True
                                    if (i > 0 and (word_list[i - 1] == 'до' or word_list[i - 1] == 'по')):
                                        max_exists_there = True
                                    # print(word_list[i+1])

                                    # print(min_exists)
                                    # print(max_exists)
                                    if (min_exists or min_exists_there):
                                        if (min_image == None):
                                            min_image = int(word)
                                        else:
                                            if (int(word) > min_image):
                                                min_image = int(word)
                                    if (max_exists or max_exists_there):
                                        if (max_image == None):
                                            max_image = int(word)
                                        else:
                                            if (int(word) < max_image):
                                                max_image = int(word)
        return [min_image, max_image]

    #  !!
    def __get_style_data(self, text):
        text = self.__clean_text(text)
        print(text)
        list_of_sentences = text.split('.')
        data_style = {
            'fields': None}
        inter = 0
        data_fields = {
            'right': None,
            'left': None,
            'top': None,
            'bottom': None,
            'unit': None
        }
        data_indent = {}
        data_inter = {}
        data_jc = {}
        data_font = {}
        kegl = ''
        for i, sent in enumerate(list_of_sentences):
            sent = self.clean_form_sp(sent)
            word_list = sent.split(' ')

            direction_exists, direction = sent.__text_contains_word_from_list_with_word(sent,
                                                                                        self.__recognized_direction)
            if sent.__text_contains_word_from_list(sent, self.__recognized_field) and direction_exist:
                # print('Поля')
                c = 0
                for i, word in enumerate(word_list):
                    c = max(i - 3, 0)
                    direction_here, direction = __text_contains_word_from_list(word, self.__recognized_direction)
                    if direction == 'верх':
                        for j in range(max(c, i - 3), min(i + 5, len(word_list))):
                            if word_list[j][0].isdigit() and data_fields['top'] == None:
                                data_fields['top'] = word_list[j]
                                unit_exists, unit = self.__text_contains_word_from_list(word_list[j],
                                                                                        self.__recognized_linear_unit)
                                if (unit_exists):
                                    data_fields['unit'] = unit
                                elif (j < len(word_list) - 1):
                                    unit_exists, unit = self.__text_contains_word_from_list(word_list[j + 1],
                                                                                            self.__recognized_linear_unit)
                                    if (unit_exists):
                                        data_fields['unit'] = unit
                                c = j
                                break
                    elif direction == 'ниж' or direction == 'низ':
                        for j in range(max(c, i - 3), min(i + 5, len(word_list))):
                            if word_list[j][0].isdigit() and data_fields['bottom'] == None:
                                data_fields['bottom'] = word_list[j]
                                unit_exists, unit = self.__text_contains_word_from_list(word_list[j],
                                                                                        self.__recognized_linear_unit)
                                if (unit_exists):
                                    data_fields['unit'] = unit
                                elif (j < len(word_list) - 1):
                                    unit_exists, unit = self.__text_contains_word_from_list(word_list[j + 1],
                                                                                            self.__recognized_linear_unit)
                                    if (unit_exists):
                                        data_fields['unit'] = unit
                                c = j
                                break
                    elif direction == 'прав':
                        for j in range(max(c, i - 3), min(i + 5, len(word_list))):
                            if word_list[j][0].isdigit() and data_fields['right'] == None:
                                data_fields['right'] = word_list[j]
                                unit_exists, unit = self.__text_contains_word_from_list(word_list[j],
                                                                                        self.__recognized_linear_unit)
                                if (unit_exists):
                                    data_fields['unit'] = unit
                                elif (j < len(word_list) - 1):
                                    unit_exists, unit = self.__text_contains_word_from_list(word_list[j + 1],
                                                                                            self.__recognized_linear_unit)
                                    if (unit_exists):
                                        data_fields['unit'] = unit
                                c = j
                                break
                    elif direction == 'лев':
                        for j in range(max(c, i - 3), min(i + 5, len(word_list))):
                            if word_list[j][0].isdigit() and data_fields['left'] == None:
                                data_fields['left'] = word_list[j]
                                unit_exists, unit = self.__text_contains_word_from_list(word_list[j],
                                                                                        self.__recognized_linear_unit)
                                if (unit_exists):
                                    data_fields['unit'] = unit
                                elif (j < len(word_list) - 1):
                                    unit_exists, unit = self.__text_contains_word_from_list(word_list[j + 1],
                                                                                            self.__recognized_linear_unit)
                                    if (unit_exists):
                                        data_fields['unit'] = unit
                                c = j
                                break
            if (data_style['fields'] == None):
                data_style['fields'] = data_fields
                """
            if 'отступ' in x.lower() and ('первая' in x.lower() or 'первой' in x.lower() or 'красной' in x.lower() or ('начал' in x.lower() and 'абзац' in x.lower())):
                    for i, elem in enumerate(sent_list):
                        if 'отступ' in elem.lower():
                            flag = 0
                            flag2 = 0
                            for j in range(i, len(sent_list)):
                                # print(sent_list[j])
                                if 'абзац' in sent_list[j].lower():
                                    flag2 = 1
                                # print(flag2)
                                if 'первой' in sent_list[j] or 'красной' in sent_list[j] or 'первая' in x.lower():
                                    flag = 1
                                # print(flag)
                                if sent_list[j][0].isdigit() and (('начал' in x.lower() or 'перв' in x.lower()) and 'абзац' in x.lower()) and 'first' not in data_indent.keys():
                                    # print('Отступ красной строки')
                                    # print(sent_list[j])
                                    data_indent['first'] = sent_list[j]
                                    break
                # print('Times New Roman' in x)
            elif 'отступ' in x.lower():
                    # print('Отступ', x)
                    n = 'справа' in x.lower() or 'слева' in x.lower() or 'сверху' in x.lower() or 'снизу' in x.lower()
                    # print(n)
                    if n:
                        for n, elem in enumerate(sent_list):
                            if 'отступ' in elem.lower():
                                for j in range(n, len(sent_list)):
                                    # print(sent_list[j]
                                    if 'справа' in sent_list[j]:
                                        # print('here')
                                        for l in range(j, len(sent_list)):
                                            # print(sent_list[j])
                                            if sent_list[l][0].isdigit() and 'Right' not in data_indent.keys():
                                                # print(sent_list[l])
                                                data_indent['Right'] = sent_list[l]
                                                break
                                    elif 'слева' in sent_list[j]:
                                        print('here')
                                        for l in range(j, len(sent_list)):
                                            # print(sent_list[j])
                                            if sent_list[l][0].isdigit() and 'Left' not in data_indent.keys():
                                                data_indent['Left'] = sent_list[l]
                                                break
                                    elif 'сверху' in sent_list[j]:
                                        print('here')
                                        for l in range(j, len(sent_list)):
                                            # print(sent_list[j])
                                            if sent_list[l][0].isdigit() and 'Top' not in data_indent.keys():
                                                data_indent['Top'] = sent_list[l]
                                                break
                                    elif 'снизу' in sent_list[j]:
                                        print('here')
                                        for l in range(j, len(sent_list)) and 'Low' not in data_indent.keys():
                                            # print(sent_list[j])
                                            if sent_list[l][0].isdigit():
                                                data_indent['Low'] = sent_list[l]
                                                break
                                    
                    else:
                        # print(sent_list)
                        for i, elem in enumerate(sent_list):
                            if 'отступ' in elem.lower():
                                for j in range(i, len(sent_list)):
                                    # print(sent_list[j]
                                    if sent_list[j][0].isdigit() and 'string' not in data_indent.keys():
                                        data_indent['string'] = sent_list[j]
                                        break
            data_style['indent'] = data_indent
            """
            if 'интервал' in sent.lower():
                # print('Межстрочный интервал')
                for j, word in enumerate(word_list):
                    u = 0
                    if 'интервал' in word.lower():
                        t = j
                        fl = 0
                        while word_list[t][-1] != ',':
                            # print(t)
                            if sent_list[t][0].isdigit() and 'string' not in data_inter.keys():
                                fl = 1
                                u = 1
                                # print(sent_list[t])
                                data_inter['string'] = sent_list[t]
                                inter = 1
                                break
                            t += 1
                            if t >= len(sent_list) or len(sent_list[t]) == 0:
                                break

                        if fl == 0 and 'string' not in data_inter.keys():
                            if 'полуторны' in x or 'полтор' in x:
                                data_inter['string'] = '1,5'
                                # print('1,5')
                                u = 1
                                inter = 1.5
                            if 'одинар' in x:
                                data_inter['string'] = '1'
                                u = 1
                                inter = 1
                            if 'двойн' in x:
                                data_inter['string'] = '2'
                                u = 1
                                inter = 2
                            if 'стр' in sent:
                                # print('руку', sent_list[j], sent_list)
                                for k in range(j, len(sent_list)):
                                    if 'строки' in sent_list[k]:
                                        data_inter['string'] = sent_list[k]
                    if u == 1:
                        break
            data_style['inter'] = data_inter
            # 'выравнив' in x.lower() and 

            # print(fl, sent_list, i)
            print('Выравнивание', i)
            l = 0
            for j, word in enumerate(sent_list):
                for k in range(j, len(sent_list)):
                    print(sent_list[k])
                    if 'ширине' in sent_list[k]:
                        data_jc['jc'] = 'both'
                        l = 1
                        # break
                    elif 'левому' in sent_list[k] or 'влево' in sent_list[k]:
                        data_jc['jc'] = 'left'
                        l = 1
                        # break
                    elif 'правому' in sent_list[k] or 'вправо' in sent_list[k]:
                        data_jc['jc'] = 'right'
                        l = 1
                        # break
                    elif 'центру' in sent_list[k]:
                        data_jc['jc'] = 'center'
                        l = 1
                        # break
                # if l == 1:
                #     break
            data_style['jc'] = data_jc
            for font in self.__recognized_fonts:
                if font in x and 'font' not in data_font.keys():
                    data_font['font'] = font
            data_style['font'] = data_font

            for j, word in enumerate(sent_list):
                if 'шрифт' in word.lower() or 'кегль' in word.lower() or 'шрифтом' in word.lower():
                    # print('herere')
                    for k in range(j, len(sent_list)):
                        # print(sent_list[k])
                        if len(sent_list[k]) > 0:
                            if sent_list[k][0].isdigit() and kegl == '':
                                # print('Кегль')
                                # print(sent_list[k])
                                kegl = sent_list[k]
                                n = 0

                                break
            data_style['kegl'] = kegl
        print(data_style)
        return data_style

    #  !!
    def __get_data_of_value(self, text: str):

        list_of_sentences = text.split('.')
        # data = {}
        mesures = ['больше', 'меньше', 'от', 'до', 'более', 'менее', 'превышал', 'превышать', 'должен']
        for j, sent in enumerate(list_of_sentences):
            # print('точников' in sent)
            if 'ключ' in sent.lower() and 'слов' in sent:
                regex = re.compile("(\d )", re.S)
                d = {}
                # x - объединено число в одно
                # x = regex.sub(lambda x: x.group()[0].replace(" ", ""), sent)
                x = self.clean_form_sp(sent)
                sent_list = x.split(' ')
                # print(sent_list)
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and ('слов' in sent_list[i + 1] or 'ключ' in sent_list[i + 1]):
                            val = {'val1': 0, 'val2': 0}
                            # print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                # print(sent_list[n], f)
                                if f == 1:
                                    # print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 'Kw', 'val': val}
            elif 'слов' in sent or 'знак' in sent:
                regex = re.compile("(\d )", re.S)
                d = {}
                # x - объединено число в одно
                # x = regex.sub(lambda x: x.group()[0].replace(" ", ""), sent)
                x = self.clean_form_sp(sent)
                sent_list = x.split(' ')
                # print(sent_list)
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and 'слов' in sent_list[i + 1]:
                            val = {'val1': 0, 'val2': 0}
                            # print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                print(sent_list[n], f)
                                if f == 1:
                                    print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 'W', 'val': val}
            if 'ссылок' in sent or 'точников' in sent:
                x = self.clean_form_sp(sent)
                x = x.replace('–', '')
                sent_list = x.split(' ')
                if '' in sent_list:
                    sent_list.remove('')
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and ('ссылок' in sent_list[i + 1] or 'точников' in sent_list[i + 1]):
                            val = {'val1': 0, 'val2': 0}
                            print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                print(sent_list[n], f)
                                if f == 1:
                                    print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 's', 'val': val}
                        elif word[0].isdigit() and ('ссылок' in sent_list[i - 1] or 'точников' in sent_list[i - 1]):
                            val = {'val1': 0, 'val2': 0}
                            print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                print(sent_list[n], f)
                                if f == 1:
                                    print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 's', 'val': val}

    #   !!
    def __clean_text(self, text: str):
        n_text = ''
        for i, a in enumerate(text):
            if i > 0 and i < len(text) - 1 and a == '.':
                if text[i - 1].isdigit() and text[i + 1].isdigit():
                    n_text += ','
                else:
                    n_text += a
            else:
                n_text += a
        return n_text

    #   !!
    def get_data_for_UDK(self, text):
        data_of_style = self.__get_data_of_style(text)
        return data_of_style

    #  !!

    def get_data_for_auth(self, text):

        data = self.__get_data_of_style(text)
        # print(data)
        return data

    #   !!
    def __get_data_of_additional_pic(self, text: str):
        data = {'formats': []}
        text = text.replace('.', '')
        text = text.replace(',', '')
        text_arr = text.lower().split(' ')
        for format in self.__recognized_formats:
            if format in text_arr:
                data['formats'].append(format)

        # print(data)
        return data

    #  !!
    def get_data_for_pic(self, text):
        data1 = self.__get_data_of_style(text)
        data2 = self.__get_data_of_additional_pic(text)
        return data1, data2

    # !!
    def data_getter_2(self, struct_elem, text: str):
        # data_res = {'УДК': {}, 'Название': {}, 'Автор': {},'Организации': {},'email':{},
        #           'Аннотация':{},'Ключевые слова':{}, 'Текст': {},
        #           'Литература': {}, 'Изобр':{}, 'Формул':{}, 'Таб':{}, 'Заголовки':{}}
        if struct_elem == 'УДК':
            # print(text)

            data1 = self.get_data_for_UDK(text)
            # print(data)

            data2 = self.__get_data_of_value(text)
            return {'style': data1, 'value': data2}
        if struct_elem == 'Название':
            print(text)
            data1 = self.__get_data_of_style(text)
            return {'style': data1}
        if struct_elem == 'email':
            print(text)
            data1 = self.__get_data_of_style(text)
            return {'style': data1}
        if struct_elem == 'Автор':
            # print(text)
            data = self.get_data_for_auth(text)
            return {'style': data}
        if struct_elem == 'Организации':
            data = self.get_data_for_auth(text)
            return {'style': data}
        if struct_elem == 'Аннотация':
            data1 = self.get_data_for_auth(text)
            # print(data)
            data2 = self.__get_data_of_value(text)
            return {'style': data1, 'value': data2}
            # print(data)
        if struct_elem == 'Аффилиация':
            data1 = self.get_data_for_auth(text)
            # print(data)
            data2 = self.__get_data_of_value(text)
            return {'style': data1, 'value': data2}
        if struct_elem == 'Ключевые слова':
            # print(text)
            data1 = self.get_data_for_auth(text)
            # data_res['Ключевые слова']['style'] = data
            # print(data)
            data2 = self.__get_data_of_value(text)
            # data_res['Ключевые слова']['value'] = data
            return {'style': data1, 'value': data2}
            # print(data)
        if struct_elem == 'Текст':
            # print(text)
            data = self.get_data_for_auth(text)
            return {'style': data}
        if struct_elem == 'Литература':
            # print(text)
            data1 = self.get_data_for_auth(text)
            data2 = self.__get_data_of_value(text)
            temp = self.get_literature()
            return {'style': data1, 'value': data2, 'template': temp}
        if struct_elem == 'Изобр':
            # print(text)
            data1, data2 = self.get_data_for_pic(text)

            return {'style': data1, 'add': data2}
        # if struct_elem == 'Заголовки':
        #     print(text)
        #     data = self.work_with_levels(text)
        #     return {'style': data}
        if struct_elem == 'Таб':
            # print(text)
            data = self.__get_data_of_style(text)
            return {'style': data}
        if struct_elem == 'Формул':
            # print(text)
            data = self.__get_data_of_style(text)
            return {'style': data}
        # return data_res

    # !!
    def data_cleaner(self, dict1: dict):
        # print('=============================')
        # print(dict1.keys())
        dict_new = {}
        for key, value in dict1.items():
            # print(key)

            if value is not None and type(value) == dict:
                # print(value)
                for key1, value1 in value.items():

                    if value1 is not None and type(value1) == dict:
                        # print(key1)
                        # print(value1)
                        # print('i am here')
                        for key2, value2 in value1.items():
                            # print(key2, value2)
                            if value2 == '':
                                value1[key2] = None
                            if type(value2) == str and len(value2) > 0:
                                # print('i am here 1')
                                if value2[0].isdigit():
                                    s1 = ''
                                    s2 = ''
                                    i = 0
                                    while i < len(value2):
                                        if value2[i].isdigit():
                                            s1 += value2[i]
                                        elif value2[i] == ',' and value2[i - 1].isdigit():
                                            s1 += '.'
                                        else:
                                            s2 += value2[i]
                                        i += 1
                                    # print(s1, s2, float(s1))
                                    # print('hh', value2, value1[key2])
                                    # if s1[-1] == '.':
                                    #     s1.replace('.','')
                                    if key2 == 'kegl':
                                        s1 = int(float(s1)) * 2

                                    value1[key2] = s1
                                    print('here', value2, value1[key2])
                            elif type(value2) == dict:
                                # print('i am here 2')
                                for key3, value3 in value2.items():
                                    # print(key3, value3)
                                    if value2[key3] == '':
                                        value2[key3] = None
                                    if type(value3) == str:
                                        if '“' in value3:
                                            value3 = value3.replace('“', '')
                                        if '”' in value3:
                                            value3 = value3.replace('“', '')
                                        if len(value3) > 0:
                                            if value3[0].isdigit():
                                                s1 = ''
                                                s2 = ''
                                                # value3 = value3.replace()
                                                i = 0
                                                while i < len(value3):
                                                    if value3[i].isdigit():
                                                        s1 += value3[i]
                                                    elif value3[i] == ',' and value3[i - 1].isdigit():
                                                        s1 += '.'
                                                    else:
                                                        s2 += value3[i]
                                                    i += 1

                                                # print(s1, s2, float(s1))
                                                # print('hh1', value3, value2[key3])
                                                if key3 == 'string':
                                                    # print(key3, s1)
                                                    s1 = int(float(s1) * 240)
                                                # if key3 =='first':
                                                #     s1 = 
                                                if key3 in ['Top', 'Low', 'Left', 'Right', 'first']:
                                                    if 'см' in s2:
                                                        s1 = int(float(s1) * 568)
                                                    if 'мм' in s2:
                                                        s1 = int(float(s1) * 56.8)
                                                value2[key3] = s1
                                                # print('here', value3, value2[key3])
                                    elif type(value3) == dict:
                                        # print(value3)
                                        for key4, value4 in value3.items():
                                            if len(value4) > 0:
                                                if value4[0].isdigit():
                                                    s1 = ''
                                                    s2 = ''
                                                    i = 0
                                                    while i < len(value4):
                                                        if value4[i].isdigit():
                                                            s1 += value4[i]
                                                        elif value4[i] == ',' and value4[i - 1].isdigit():
                                                            s1 += '.'
                                                        else:
                                                            s2 += value4[i]
                                                        i += 1

                                                    # print(s1, s2, float(s1))
                                                    # print('hh1', value3, value3[key4])
                                                    if key4 == 'string' or key4 == 'first':
                                                        # print(key4, s1, key4)
                                                        s1 = int(float(s1) * 240)
                                                    if key4 in ['Top', 'Low', 'Left', 'Right']:
                                                        if 'см' in s2:
                                                            s1 = int(float(s1) * 568)
                                                        if 'мм' in s2:
                                                            s1 = int(float(s1) * 56.8)
                                                    value3[key4] = s1

    # !!
    def get_parts_of_article(self):
        paragraphs = self.__get_all_paragraphs()
        d1 = self.get_format()
        d2 = self.get_value_of_volume()
        count = 0
        text_of_part = ''
        dict_for_struct = {}
        default = ''
        result_data = {}
        for paragraph in paragraphs:
            text = self.__get_text_from_element(paragraph)
            # print(text, default)
            list_of_sentences = text.split('.')
            for text_of_sent in list_of_sentences:
                for elem_of_structure in self.__recognized_struct_elems:
                    if elem_of_structure in text:

                        # print('HERERERE', text_of_part)
                        # print('====')
                        # print(default,text, elem_of_structure, text.find(elem_of_structure), text[text.find(elem_of_structure):text.find(elem_of_structure)+10])
                        if default in dict_for_struct:
                            dict_for_struct[default] += ' ' + text_of_part
                        else:
                            dict_for_struct[default] = text_of_part
                        # print('****')
                        # print(dict_for_struct[default], text_of_part)
                        # print('====')
                        default = elem_of_structure
                        text_of_part = ''
                        count = 0
                # print(count, text_of_part, default)        
                count += 1
                text_of_part += text_of_sent + '.'

        for key, text in dict_for_struct.items():
            # print(key, text)
            for elem_of_structure in self.__recognized_struct_elems:
                if elem_of_structure in text:
                    t1 = text.split('.')
                    for i, sent in enumerate(t1):
                        if elem_of_structure in t1:
                            dict_for_struct[elem_of_structure] += ' ' + ". ".join(t1[i:])

        n_dict = {'УДК': '', 'Название': '', 'Автор': '', 'Аффилиация': '', 'Организации': '', 'email': '',
                  'Аннотация': '', 'Ключевые слова': '', 'Текст': '',
                  'Литература': '', 'Изобр': '', 'Формул': '', 'Таб': '', 'Заголовки': ''}
        for key, value in dict_for_struct.items():
            if key in ['принимаются статьи', 'ОФОРМЛЕНИЕ СТАТЬИ', 'Оформление статьи', 'Текст статьи',
                       'Текст публикации', 'Статья', 'Основной текст статьи', 'текст статьи', '',
                       'содержание публикации', ]:
                n_dict['Текст'] += ' ' + value
            if key == 'УДК':
                n_dict['УДК'] += ' ' + value
            if key in ['Заглавие',

                       'Название статьи', 'Название публикации']:
                n_dict['Название'] += ' ' + value

            if key in ['Список авторов',
                       'Сведения об авторе/авторах', 'Автор', 'Сведения об автор']:
                n_dict['Автор'] += ' ' + value
            if key in ['Список организаций']:
                n_dict['Организации'] += ' ' + value
            if key in ['e-mail', 'mail']:
                n_dict['email'] += ' ' + value
            if key in ['Аннотация']:
                n_dict['Аннотация'] += ' ' + value
            if key in ['Ключевые слова', 'лючевы']:
                n_dict['Ключевые слова'] += ' ' + value
            if key in ['Графический материал', 'рисун', 'Иллюстрации', ]:
                n_dict['Изобр'] += ' ' + value
            if key in ['формул', 'Формул', ]:
                n_dict['Формул'] += ' ' + value
            if key in ['таблиц', 'Таблиц']:
                n_dict['Таб'] += ' ' + value
            if key in ['Списки обозначений и литературы', 'Список литературы', ' ссыл']:
                n_dict['Литература'] += ' ' + value
            if key in ['ффилиаци']:
                n_dict['Аффилиация'] += ' ' + value
        # for key, value in dict_for_struct.items():
        #     if len(value) == 0
        # for key, value in n_dict.items():
        #     # if 'Формул' == key:
        #         print(key, value)
        # print(n_dict.keys())
        # Получить для каждой части стать
        data = {}
        t = ''
        for key, value in n_dict.items():
            # if 'mail' in key:
            t = value.replace('\xa0', ' ')
            # print(key)
            # print(t)
            data[key] = self.data_getter_2(key, t)
        data['format'] = d1
        data['vol'] = d2
        # print(data)
        self.data_cleaner(data)
        # print(t)

        print('===\n', data, '\n====')
        return data

    def split_space_and_num(self, text: str):
        t = ''
        # arr = []
        i = 0
        while i < len(text) - 1:
            if (text[i].isdigit() and (text[i + 1].isalpha() or text[i + 1] in '"‘“”’')) or (
                    text[i + 1].isdigit() and text[i].isalpha()):
                t += text[i]
                t += ' '
            else:
                t += text[i]
            i += 1
        return t

    def clean_form_sp_eng(self, text: str):
        n_t = ''
        t = []
        text = text.replace('(', '')
        text = text.replace(')', '')
        text_ar = text.split(' ')
        # print(text_ar)
        i = 0
        while i < len(text_ar) - 1:
            # print(t)
            if len(text_ar[i]) > 0:
                if text_ar[i].isdigit() and text_ar[i + 1].isdigit():
                    t.append(text_ar[i] + text_ar[i + 1])
                    i += 1
                elif text_ar[i][0].isdigit() and '-' in text_ar[i]:
                    dia = text_ar[i].split('-')
                    print('heres')
                    t.append('from')
                    t.append(dia[0])
                    t.append('to')
                    t.append(dia[1])
                    # i+=1
                elif text_ar[i][0].isdigit() and '–' in text_ar[i]:
                    dia = text_ar[i].split('–')
                    print('heres')
                    t.append('from')
                    t.append(dia[0])
                    t.append('to')
                    t.append(dia[1])
                else:
                    t.append(text_ar[i])

            i += 1
        t.append(text_ar[-1])
        return ' '.join(t)

    def __get_data_of_value_eng(self, text: str):

        list_of_sentences = text.split('.')
        # data = {}
        mesures = ['more', 'less', 'from', 'to']
        for j, sent in enumerate(list_of_sentences):
            if 'keyword' in sent:
                regex = re.compile("(\d )", re.S)
                d = {}
                # x - объединено число в одно
                # x = regex.sub(lambda x: x.group()[0].replace(" ", ""), sent)
                x = self.clean_form_sp(sent)
                sent_list = x.split(' ')
                # print(sent_list)
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and ('keyword' in sent_list[i + 1]):
                            val = {'val1': 0, 'val2': 0}
                            # print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                # print(sent_list[n], f)
                                if f == 1:
                                    # print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 'Kw', 'val': val}
            elif 'words' in sent or 'char' in sent:
                regex = re.compile("(\d )", re.S)
                d = {}
                # x - объединено число в одно
                # x = regex.sub(lambda x: x.group()[0].replace(" ", ""), sent)
                x = self.clean_form_sp(sent)
                sent_list = x.split(' ')
                # print(sent_list)
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and 'words' in sent_list[i + 1]:
                            val = {'val1': 0, 'val2': 0}
                            # print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                print(sent_list[n], f)
                                if f == 1:
                                    print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 'W', 'val': val}
            if 'ref' in sent:
                x = self.clean_form_sp(sent)
                sent_list = x.split(' ')
                print(sent_list)
                # От до проверить
                for i, word in enumerate(sent_list):
                    word = word.replace('(', '')
                    word = word.replace(')', '')
                    if len(word) > 0 and i < len(sent_list) - 1:
                        if word[0].isdigit() and 'ref' in sent_list[i + 1]:
                            val = {'val1': 0, 'val2': 0}
                            # print(word)
                            val['val1'] = int(word)
                            k = i
                            n = i - 1

                            while n > 1:

                                f = 0

                                for mesure in mesures:
                                    if mesure in sent_list[n].lower() or sent_list[n].isdigit():
                                        f = 1
                                print(sent_list[n], f)
                                if f == 1:
                                    print(sent_list[n])
                                    if sent_list[n].isdigit():
                                        val['val2'] = int(sent_list[n])
                                    n -= 1
                                    # break
                                else:
                                    break
                            # n-=1
                            # print(sent_array[n])
                            # if 'не' in sent_list[n]:
                            #     print('не')
                            return {'w': 's', 'val': val}

    def get_data_for_pic_eng(self, text):
        data1 = self.__get_data_of_style_eng(text)
        data2 = self.__get_data_of_additional_pic(text)
        return data1, data2

    def __get_data_of_style_eng(self, text):
        text = self.__clean_text(text)
        # print(text)
        text = text.replace('\xa0', '')
        list_of_sentences = text.split('.')
        data_style = {}
        inter = 0
        data_fields = {}
        data_indent = {}
        data_inter = {}
        data_jc = {}
        data_font = {}
        kegl = ''
        for i, sent in enumerate(list_of_sentences):
            regex = re.compile("(\d )", re.S)
            x = regex.sub(lambda x: x.group()[0].replace(" ", ""), sent)
            x = x.replace('•', '')
            sent_list = x.split(' ')
            # print(sent_list)

            y = ('top' in x.lower() or 'bottom' in x.lower() or 'left' in x.lower() or 'right' in x.lower()) and (
                        'cm' in x.lower() or 'mm' in x.lower())
            # print(y, 'margin' in x.lower(),y)
            if 'margin' in x.lower() and y:

                # print(y)
                print('Поля')
                c = 0
                for i, elem in enumerate(sent_list):
                    # print(elem, elem.lower() == 'верхнее', elem.lower() == 'нижнее', elem.lower() == 'правое', elem.lower() == 'левое')
                    # print(data_fields)
                    if elem.lower() == 'top':
                        # print('heret')
                        for j in range(i, len(sent_list)):
                            # print(sent_list[j], sent_list[j][0].isdigit(), 'Top' not in data_fields.keys(), data_fields)
                            if sent_list[j][0].isdigit():
                                # print(data_fields['Top'][0].isdigit() == False)

                                data_fields['Top'] = sent_list[j]
                                # print('saved')
                                c = 1
                                break
                    elif elem.lower() == 'bottom':
                        print('hereb')
                        for j in range(i, len(sent_list)):
                            if sent_list[j][0].isdigit():
                                # print(sent_list[j])
                                data_fields['Low'] = sent_list[j]
                                c = 1
                                break
                    elif elem.lower() == 'right':
                        print('herer')
                        for j in range(i, len(sent_list)):
                            print(sent_list[j])
                            if sent_list[j][0].isdigit():
                                data_fields['Right'] = sent_list[j]
                                c = 1
                                break
                    elif elem.lower() == 'left':
                        # print('herel')
                        for j in range(i, len(sent_list)):
                            # print(sent_list[j], sent_list[j][0].isdigit(), sent_list[j][0].isdigit(), 'Left' not in data_fields.keys(), data_fields['Left'])
                            if sent_list[j][0].isdigit():
                                data_fields['Left'] = sent_list[j]
                                c = 1
                                break
                        # print(data_fields['Left'])
                    elif y == False:
                        m = 0
                        # print(sent_list)
                        for j, word in enumerate(sent_list):
                            if 'marg' in word.lower():
                                m = j
                            if j > m and word[0].isdigit() and 'cm' in word:
                                print(word)
                                c = 1
                                break
                if c == 0:
                    print('hete')
                    for j, elem in enumerate(sent_list):
                        # print('поле' in sent_list[j], sent_list[j], sent_list[j-1] in ['верхнее', 'нижнее', 'правое', 'левое'])
                        if 'marg' in sent_list[j] and sent_list[j - 1] in ['top', 'bottom', 'right', 'left']:
                            # print(sent_list[j], sent_list[j-1])
                            sent_list[j] = sent_list[j].replace(';', '')
                            qq = sent_list[j].split('marg')
                            # print(qq, sent_list[j-1])
                            if 'top' in sent_list[j - 1] and 'Top' not in data_fields.keys():
                                data_fields['Top'] = qq[1]
                            elif 'bottom' in sent_list[j - 1] and 'Low' not in data_fields.keys():
                                data_fields['Low'] = qq[1]
                            elif 'right' in sent_list[j - 1] and 'Right' not in data_fields.keys():
                                data_fields['Right'] = qq[1]
                            elif 'left' in sent_list[j - 1] and 'Left' not in data_fields.keys():
                                data_fields['Left'] = qq[1]
            elif y == False and 'margin' in x.lower():
                m = 0
                print('here3', 'margin' in x.lower())
                for j, word in enumerate(sent_list):
                    if 'marg' in word.lower():
                        m = j
                    if len(word) > 0:
                        if j > m and word[0].isdigit() and 'cm' in word:
                            data_fields['Top'] = word
                            data_fields['Low'] = word
                            data_fields['Right'] = word
                            data_fields['Left'] = word
                            c = 1
                            break

            data_style['fields'] = data_fields
            if 'first line' in x.lower():
                print('here')
                for i, elem in enumerate(sent_list):
                    if 'line' in elem.lower():
                        print('here')

                        for j in range(i, len(sent_list)):

                            if sent_list[j][0].isdigit() and (
                                    'first' in x.lower() and 'paragraph' in x.lower()) and 'first' not in data_indent.keys():
                                # print('Отступ красной строки')
                                # print(sent_list[j])
                                data_indent['first'] = sent_list[j]
                                break
            sent_list = sent.split(' ')
            # print(sent_list)
            data_style['indent'] = data_indent
            if 'line spac' in x.lower():
                print('here2')
                for i, elem in enumerate(sent_list):
                    if i < len(sent_list) - 1:
                        print(elem, 'line' in elem)
                        if 'line' in elem and 'spac' in sent_list[i + 1]:
                            print('SADSAD', elem, sent_list[i - 1], elem[0].isdigit(),
                                  'string' not in data_inter.keys())
                            if sent_list[i - 1][0].isdigit() and 'string' not in data_inter.keys():
                                data_inter['string'] = sent_list[i - 1]
            data_style['inter'] = data_inter

            sent_list = sent.split(' ')
            # print(sent_list)
            if 'pt' in sent.lower():
                for i, elem in enumerate(sent_list):
                    if 'pt' in elem and i > 1 and kegl == '':
                        # print(sent_list[i-1], sent_list[i])
                        if sent_list[i - 1].isdigit():
                            kegl = sent_list[i - 1]
                            break
                        elif elem[0].isdigit():
                            kegl = elem
            data_style['kegl'] = kegl

            for font in self.__recognized_fonts:
                if font in sent:
                    data_font['Font'] = font
            data_style['font'] = data_font
            if 'justific' in sent.lower():
                if 'both' in sent.lower():
                    data_jc['jc'] = 'both'
                elif 'centr' in sent.lower():
                    data_jc['jc'] = 'centr'
                elif 'right' in sent.lower():
                    data_jc['jc'] = 'right'
                elif 'left' in sent.lower():
                    data_jc['jc'] = 'left'
            data_style['jc'] = data_jc

        return data_style

    def get_value_of_volume_eng(self):
        paragraphs = self.__get_all_paragraphs()
        max_value_of_pg = 0
        max_value_of_smb = 0
        max_value_of_w = 0
        for paraph in paragraphs:

            text = self.__get_text_from_element(paraph)
            # print(text)
            text = self.clean_form_sp(text)
            # print(text)
            if ('length' in text.lower()) and ('manuscript' in text.lower() or 'text' in text.lower()):
                sent_list = text.split('.')
                # print(sent_list)
                for sent in sent_list:
                    # print('here')
                    if ('length' in sent.lower()) and ('manuscript' in sent.lower() or 'text' in sent.lower()):
                        list_sent = sent.split(' ')
                        # if ' ' in list_sent:
                        #     list_sent =list_sent.remove(' ')
                        # print(list_sent)
                        for i, word in enumerate(list_sent):
                            if i < len(list_sent) - 1:
                                # print(word, word.isdigit() and 'сло' in list_sent[i+1])
                                # if word.isdigit():
                                # print(int(word)>max_value_of_smb)
                                if word.isdigit() and (
                                        'pag' in list_sent[i + 1] or 'ful' in list_sent[i + 1] or '' == list_sent[
                                    i + 1]):
                                    print('h')
                                    if int(word) > max_value_of_pg:
                                        max_value_of_pg = int(word)
                                elif word.isdigit() and 'char' in list_sent[i + 1]:
                                    # print('2')
                                    if int(word) > max_value_of_smb:
                                        max_value_of_smb = int(word)
                                elif word.isdigit() and 'word' in list_sent[i + 1]:
                                    # print('3')
                                    # print(max_value_of_pg, max_value_of_smb, max_value_of_w)
                                    if int(word) > max_value_of_w:
                                        max_value_of_w = int(word)
                                    # print(max_value_of_pg, max_value_of_smb, max_value_of_w)
                    # print(t)
        # print(max_value_of_pg, max_value_of_smb)
        return [max_value_of_pg, max_value_of_smb, max_value_of_w]

    def data_getter_eng(self, struct_elem, text: str):
        # n_dict = {'Title': '', 'Author': '','Keywords': '',
        #           'Abstract':'','Affilation':'', 'References': '',
        #           'Illustrations': '','Text':''}
        if struct_elem == 'Title':
            print(text)
            data1 = self.__get_data_of_style_eng(text)
            print(data1)
            return {'style': data1}
        if struct_elem == 'Author':
            print(text)
            data = self.__get_data_of_style_eng(text)
            return {'style': data}

        if struct_elem == 'Abstract':
            print(text)
            data1 = self.__get_data_of_style_eng(text)
            # print(data)
            data2 = self.__get_data_of_value_eng(text)
            return {'style': data1, 'value': data2}
            # print(data)
        if struct_elem == 'Affilation':
            data1 = self.__get_data_of_style_eng(text)
            # print(data)
            data2 = self.__get_data_of_value_eng(text)
            return {'style': data1, 'value': data2}
        if struct_elem == 'Keywords':
            # print(text)
            data1 = self.__get_data_of_style_eng(text)
            # data_res['Ключевые слова']['style'] = data
            # print(data)
            data2 = self.__get_data_of_value_eng(text)
            # data_res['Ключевые слова']['value'] = data
            return {'style': data1, 'value': data2}
            # print(data)
        if struct_elem == 'Text':
            # print(text)
            data = self.__get_data_of_style_eng(text)
            return {'style': data}
        if struct_elem == 'References':
            # print(text)
            data1 = self.__get_data_of_style_eng(text)
            data2 = self.__get_data_of_value_eng(text)
            temp = self.get_literature()
            return {'style': data1, 'value': data2, 'template': temp}
        if struct_elem == 'Illustrations':
            print(text)
            data1, data2 = self.get_data_for_pic_eng(text)

            return {'style': data1, 'add': data2}
        if struct_elem == 'Tables':
            data1 = self.__get_data_of_style_eng(text)
            return {'style': data1}
        if struct_elem == 'Equation':
            data1 = self.__get_data_of_style_eng(text)
            return {'style': data1}

    def get_format_eng(self):
        paragraphs = self.__get_all_paragraphs()
        for i, paragraph in enumerate(paragraphs):
            text = self.__get_text_from_element(paragraph)
            # print(text)
            # pattern = r'a\d\+'
            text_arr = text.split(' ')
            for i, word in enumerate(text_arr):
                # print(word)

                if 'A4' in word or 'A3' in word or 'A0' in word or 'A1' in word or 'A2' in word or 'A5' in word or 'A6' in word:
                    self.__requirements_of_format['Format'] = word

        self.__requirements_of_format['lang'] = 'eng'

        # print(self.__requirements_of_format)
        return self.__requirements_of_format

    def get_parts_of_article_engl(self):
        paragraphs = self.__get_all_paragraphs()
        d1 = self.get_format_eng()
        d2 = self.get_value_of_volume_eng()
        count = 0
        text_of_part = ''
        dict_for_struct = {}
        default = ''
        result_data = {}
        for paragraph in paragraphs:
            text = self.__get_text_from_element(paragraph)
            # list_of_sentences = 
            for elem_of_structure in self.__recognized_struct_elems_eng:
                if elem_of_structure in text:

                    if default in dict_for_struct:
                        dict_for_struct[default] += ' ' + text_of_part
                    else:
                        dict_for_struct[default] = text_of_part

                    default = elem_of_structure
                    text_of_part = ''
                    count = 0
            # print(count)        
            count += 1
            text_of_part += ' ' + text

        # print(dict_for_struct)
        n_dict = {'Title': '', 'Author': '', 'Keywords': '',
                  'Abstract': '', 'Affiliation': '', 'References': '',
                  'Illustrations': '', 'Text': '', 'Tables': '', 'Equation': ''}
        for key, value in dict_for_struct.items():
            if key in ['Manuscript',
                       'manuscript',
                       'text', 'Text', '']:
                n_dict['Text'] += ' ' + value

            if key in ['title',
                       'Title', ]:
                n_dict['Title'] += ' ' + value

            if key in ['author',
                       'Author', ]:
                n_dict['Author'] += ' ' + value

            if key in ['abstract',
                       'Abstract', ]:
                n_dict['Abstract'] += ' ' + value
            if key in ['keyword',
                       'Keyword', ]:
                n_dict['Keywords'] += ' ' + value
            if key in ['Illustrations',
                       'illustrations',
                       'graphics']:
                n_dict['Illustrations'] += ' ' + value

            if key in ['bibliography',
                       'references',
                       'References', ]:
                n_dict['References'] += ' ' + value
            if 'tab' in key:
                n_dict['Tables'] += ' ' + value
            if 'equation' in key:
                n_dict['Equation'] += ' ' + value
            if key in ['affiliation',
                       'Affiliation', ]:
                n_dict['Affiliation'] += ' ' + value

        data = {}
        for key, value in n_dict.items():
            # if 'Text' in key:
            t = value.replace('\xa0', ' ')
            print(key)
            print(t)
            data[key] = self.data_getter_eng(key, t)
        data['format'] = d1
        data['vol'] = d2
        self.data_cleaner_eng(data)
        return data

    def data_cleaner_eng(self, dict1: dict):

        # print('=============================')
        # print(dict1.keys())
        dict_new = {}
        for key, value in dict1.items():
            # print(key)

            if value is not None and type(value) == dict:
                # print(value)
                for key1, value1 in value.items():

                    if value1 is not None and type(value1) == dict:
                        print(key1)
                        print(value1)
                        print('i am here')
                        for key2, value2 in value1.items():
                            print(key2, value2)
                            if value2 == '':
                                value1[key2] = None
                            if type(value2) == str and len(value2) > 0:
                                print('i am here 1')
                                if value2[0].isdigit():
                                    s1 = ''
                                    s2 = ''
                                    i = 0
                                    while i < len(value2):
                                        if value2[i].isdigit():
                                            s1 += value2[i]
                                        elif value2[i] == ',' and value2[i - 1].isdigit():
                                            s1 += '.'
                                        else:
                                            s2 += value2[i]
                                        i += 1
                                    print(s1, s2, float(s1))
                                    print('hh', value2, value1[key2])
                                    # if s1[-1] == '.':
                                    #     s1.replace('.','')
                                    if key2 == 'kegl':
                                        s1 = int(float(s1)) * 2

                                    value1[key2] = s1
                                    print('here', value2, value1[key2])
                            elif type(value2) == dict:
                                print('i am here 2')
                                for key3, value3 in value2.items():
                                    # print(key3, value3)
                                    if value2[key3] == '':
                                        value2[key3] = None
                                    if type(value3) == str:
                                        if '“' in value3:
                                            value3 = value3.replace('“', '')
                                        if '”' in value3:
                                            value3 = value3.replace('“', '')
                                        if len(value3) > 0:
                                            if value3[0].isdigit():
                                                s1 = ''
                                                s2 = ''
                                                # value3 = value3.replace()
                                                i = 0
                                                while i < len(value3):
                                                    if value3[i].isdigit():
                                                        s1 += value3[i]
                                                    elif value3[i] == ',' and value3[i - 1].isdigit():
                                                        s1 += '.'
                                                    else:
                                                        s2 += value3[i]
                                                    i += 1

                                                # print(s1, s2, float(s1))
                                                # print('hh1', value3, value2[key3])
                                                if key3 == 'string':
                                                    # print(key3, s1)
                                                    s1 = int(float(s1) * 240)
                                                # if key3 =='first':
                                                #     s1 = 
                                                if key3 in ['Top', 'Low', 'Left', 'Right', 'first']:
                                                    if 'cm' in s2:
                                                        s1 = int(float(s1) * 568)
                                                    if 'mm' in s2:
                                                        s1 = int(float(s1) * 56.8)
                                                value2[key3] = s1
                                                # print('here', value3, value2[key3])
                                    elif type(value3) == dict:
                                        print(value3)
                                        for key4, value4 in value3.items():
                                            if len(value4) > 0:
                                                if value4[0].isdigit():
                                                    s1 = ''
                                                    s2 = ''
                                                    i = 0
                                                    while i < len(value4):
                                                        if value4[i].isdigit():
                                                            s1 += value4[i]
                                                        elif value4[i] == ',' and value4[i - 1].isdigit():
                                                            s1 += '.'
                                                        else:
                                                            s2 += value4[i]
                                                        i += 1

                                                    print(s1, s2, float(s1))
                                                    print('hh1', value3, value3[key4])
                                                    if key4 == 'string' or key4 == 'first':
                                                        print(key4, s1, key4)
                                                        s1 = int(float(s1) * 240)
                                                    if key4 in ['Top', 'Low', 'Left', 'Right']:
                                                        if 'cm' in s2:
                                                            s1 = int(float(s1) * 568)
                                                        if 'mm' in s2:
                                                            s1 = int(float(s1) * 56.8)
                                                    value3[key4] = s1

    def set_default_values(self, data: dict):
        we_have = {}
        def_fields = {}
        font_def = {}
        def_indent = {}
        def_inter = {}
        def_jc = {}
        def_kegl = {}
        def_lit = {}
        for key, value in data.items():
            if type(value) == dict:
                for key1, value1 in value.items():

                    if key1 == 'style':
                        print(key1, value1)
                        if 'fields' in value1.keys() and len(value1['fields']) > 0:
                            def_fields = value1['fields']
                            def_indent = value1['indent']
                            def_inter = value1['inter']
                            def_jc = value1['jc']
                            def_kegl = value1['kegl']

                        # for key2, value2 in value1.items():
                        #     if
                        if 'font' in value1.keys() and len(value1['font']) > 0:
                            # print(value1['font'])
                            font_def = value1['font']
                    if key1 == 'template':
                        if value[key1] is not None:
                            def_lit['template'] = value['template']
        # print('DATA_DEFAULT')
        if len(def_fields) == 0:
            def_fields = {'Top': 1136, 'Low': 1136, 'Left': 1420, 'Right': 1420}
        if def_kegl == None:
            # print('def_k', def_kegl)

            def_kegl = 24
        elif type(def_kegl) == dict:
            if len(def_kegl) == 0:
                def_kegl = 24

        if len(font_def) == 0:
            font_def['font'] = 'Times New Roman'
        if len(def_indent) == 0:
            def_indent = {}
        if 'first' not in def_indent.keys():
            def_indent['first'] = 280
        if 'Top' not in def_indent.keys():
            def_indent['Top'] = 280
        if 'Low' not in def_indent.keys():
            def_indent['Low'] = 280
        if 'Left' not in def_indent.keys():
            def_indent['Left'] = 280
        if 'Right' not in def_indent.keys():
            def_indent['Right'] = 280
        if 'string' not in def_indent.keys():
            def_indent['string'] = 280
        if len(def_inter) == 0:
            def_inter['string'] = 240
        if len(def_jc) == 0:
            def_jc = {'jc': 'both'}
        if len(def_lit) == 0:
            def_lit['template'] = 'ГОСТ Р 7.0.100 -2018'
        # print(def_fields, font_def, def_indent,def_inter, def_jc)
        def_format = {'Format': 'A4', 'lang': 'rus'}
        data['default'] = [def_fields, def_kegl, font_def, def_indent, def_inter, def_jc, def_lit, def_format]
        return data
