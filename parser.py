__all__ = ['RequirementsReader', 'split_to_sentences']

import lxml.etree as et
import re
import zipfile
from number_parser import parse as parse_numbers
from nltk import sent_tokenize
import re
from owlready2 import *

_namespaces = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_LEFT_RIGHT_IMPORTANCE = 10


def split_to_sentences(text):
    return sent_tokenize(text)


def get_text_from_paragraph(p):
    text = p.findall('.//w:t', _namespaces)
    txt = ''
    for part in text:
        txt += part.text
    return txt


def prepare_text(text: str):
    # remove non-breaking spaces
    text = text.replace(u'\xa0', u' ')
    text = text.replace(u'\n', u' ')
    n_t = ''
    t = []
    text = text.replace('(', '')
    text = text.replace(')', '')
    text_ar = text.split(' ')
    i = 0
    while i < len(text_ar) - 1:
        text_ar[i] = parse_numbers(text_ar[i], "ru")
        if len(text_ar[i]) > 0:
            if text_ar[i].isdigit() and text_ar[i + 1].isdigit():
                t.append(text_ar[i] + text_ar[i + 1])
                i += 1
            elif text_ar[i][0].isdigit() and '-' in text_ar[i]:
                dia = text_ar[i].split('-')
                t.append('от')
                t.append(dia[0])
                t.append('до')
                t.append(dia[1])
            elif text_ar[i][0].isdigit() and '–' in text_ar[i]:
                dia = text_ar[i].split('–')
                t.append('от')
                t.append(dia[0])
                t.append('до')
                t.append(dia[1])
            else:
                t.append(text_ar[i])
        i += 1
    t.append(text_ar[-1])
    return ' '.join(t)


def text_contains_word_from_list(text: str, list):
    for w in list:
        regexp = re.compile(w.lower())
        if regexp.search(text.lower()):
            return True
    return False


def find_numbers_near(text: str, i: int, delta: int, right: bool):
    res = []
    start = i
    end = i
    if right:
        end += delta
    else:
        start -= delta
    regexp = re.compile(r'-?\d+\.\d+|\d+,\d+|\d+')
    tmp = regexp.findall(text, start, end)
    if tmp is None:
        return []
    for t in tmp:
        dist = abs(text.find(t, start, end))
        res.append([t, dist])
    return res


def get_number(text, start_i):
    i = start_i
    s = ""
    while text[i].isspace():
        i += 1
    while text[i].isdigit() or text[i] == '.' or text[i] == ',':
        s += text[i]
        i += 1
    if s == "" or s == "," or s == ".":
        return None
    else:
        return float(s.replace(',', '.'))

def get_quantitative_value(text: str, prop_label_list, value_label_list):
    print(text)
    min_dist = 1000
    res_value = None
    # find prop label i
    for l_p in prop_label_list:
        regexp1 = re.compile(l_p)
        for m1 in regexp1.finditer(text.lower()):
            i = m1.start()
            print(m1)
            i1 = i
            i2 = i
            while i1 > 0 and text[i1] != '.':
                i1 -= 1
            while i2 < len(text) and text[i2] != '.':
                i2 += 1
            for l_v in value_label_list:
                regexp2 = re.compile(l_v)
                for m2 in regexp2.finditer(text.lower(), i1, i2):
                    j = m2.start()
                    dist1 = abs(i - j)
                    k = j-1
                    while k >= 0 and text[k].isspace():
                        k -= 1
                    while k >= 0 and (text[k].isdigit() or text[k] == "," or text[k] == "."):
                        k -= 1
                    value = get_number(text, k)
                    dist = 0
                    if value is None:
                        l = find_numbers_near(text, (j + m2.end()) // 2, 10 + abs(m2.end() - j) // 2, False)
                        if len(l) == 0:
                            continue
                        value, dist = l[0]
                        for v, d in l:
                            if d < dist:
                                value, dist = v, d
                    if dist1 < min_dist:
                        min_dist = dist1
                        res_value = value
                    if res_value is None:
                        for m2 in regexp2.finditer(text.lower()):
                            print(m2)
                            j = m2.start()
                            dist1 = abs(i - j)
                            k = j - 1
                            while k >= 0 and text[k].isspace():
                                k -= 1
                            while k >= 0 and (text[k].isdigit() or text[k] == "," or text[k] == "."):
                                k -= 1
                            value = get_number(text, k)
                            dist = 0
                            if value is None:
                                l = find_numbers_near(text, (j + m2.end()) // 2, 10 + abs(m2.end() - j) // 2, False)
                                if len(l) == 0:
                                    continue
                                value, dist = l[0]
                                for v, d in l:
                                    if d < dist:
                                        value, dist = v, d
                            if dist1 < min_dist:
                                min_dist = dist1
                                res_value = value
    print("Added value, min_dist ", res_value, min_dist)
    return res_value, min_dist


def get_labels_dist(text: str, prop_label_list, value_label_list):
    min_dist = 1000
    min_value_is_right = True
    # find prop label i
    for l_p in prop_label_list:
        regexp1 = re.compile(l_p)
        for m1 in regexp1.finditer(text.lower()):
            i = m1.start()
            for l_v in value_label_list:
                regexp2 = re.compile(l_v)
                for m2 in regexp2.finditer(text.lower()):
                    j = m2.start()
                    if min_value_is_right:
                        if j < i:
                            min_value_is_right = False
                            min_dist = abs(i - j)
                        elif min_dist > abs(i - j):
                            min_dist = abs(i - j)
                    else:
                        if j < i and min_dist > abs(i - j):
                            min_dist = abs(i - j)
    return min_dist, min_value_is_right


def get_applicable_values_from_property(prop):
    prop_name = f"{prop}".split(".")[1]
    request = (f"PREFIX : <file://document#> "
               f"SELECT ?x "
               f"WHERE ""{ ?x :applicableTo "
               f":{prop_name} "
               "}")
    return list(default_world.sparql(request))


def get_values_of_labeled_property_in_sentences(prop, sentences):
    responses = get_applicable_values_from_property(prop)
    values_found = []
    for r in responses:
        value_obj = r[0]
        for s in sentences:
            if text_contains_word_from_list(s, value_obj.label):
                values_found.append(value_obj)
    return values_found


def get_values_of_quantitative_property_in_sentences(prop, sentences):
    #print(prop)
    responses = get_applicable_values_from_property(prop)
    values_found = []
    min_dist = 1000
    nearest_value = None
    for r in responses:
        value_obj = r[0]
        #print(value_obj)
        for s in sentences:
            #print(s)
            if text_contains_word_from_list(s, value_obj.label):
                #print("Labels ", value_obj.label)
                value, distance = get_quantitative_value(s, prop.label, value_obj.label)
                #print("value, distance = ", value, ", ", distance)
                if min_dist > distance and value is not None and value != "":
                    #print("NEW VALUES:", value, distance)
                    min_dist = distance
                    nearest_value = value
                    if nearest_value is not None:
                        #print(value_obj)
                        value_instance = value_obj(f"Actual_{value_obj}"
                                                   f"={nearest_value}_{min_dist}")
                        values_found.append(value_instance)
                    else:
                        #print(value_obj)
                        value_instance = value_obj(f"Actual_{value_obj}"
                                                   f"={nearest_value}_{min_dist}")
                        values_found.append(value_instance)
                if nearest_value is not None:
                    #print(value_obj)
                    value_instance = value_obj(f"Actual_{value_obj}"
                                           f"={nearest_value}_{min_dist}")
                    values_found.insert(0, value_instance)
    return values_found


def get_values_of_permission_property_in_sentences(prop, sentences):
    responses = get_applicable_values_from_property(prop)
    values_found = []
    min_dist_right = 1000
    min_obj_right = None
    min_dist_left = 1000
    min_obj_left = None
    for r in responses:
        value_obj = r[0]
        for s in sentences:
            if text_contains_word_from_list(s, value_obj.label):
                distance, min_value_is_right = get_labels_dist(s, prop.label, value_obj.label)
                if min_value_is_right:
                    if distance < min_dist_right:
                        min_dist_right = distance
                        min_obj_right = value_obj(f"Actual_{value_obj}_{distance}")
                else:
                    if distance < min_dist_left:
                        min_dist_left = distance
                        min_obj_left = value_obj(f"Actual_{value_obj}_{distance}")
    if min_dist_left < min_dist_right + _LEFT_RIGHT_IMPORTANCE:
        values_found.append(min_obj_left)
    else:
        values_found.append(min_obj_right)
    return values_found


def get_topic_values_in_sentences(prop, sentences):
    values_found = []
    # nlp
    return values_found


def get_enum_values_in_sentences(prop, sentences):
    responses = get_applicable_values_from_property(prop)
    values_found = []
    min_dist = 1000
    min_value = None
    for r in responses:
        value_obj = r[0]
        for s in sentences:
            if text_contains_word_from_list(s, value_obj.label):
                distance, t = get_labels_dist(s, prop.label, value_obj.label)
                if min_dist > distance:
                    values_found.append(min_value)
                    min_dist = distance
                    min_value = value_obj(f"Actual_{value_obj}_{distance}")
                else:
                    values_found.append(value_obj(f"Actual_{value_obj}_{distance}"))
    if min_value is not None:
        values_found.insert(0, min_value)
    return values_found


def get_min_values_in_sentences(prop, sentences):
    responses = get_applicable_values_from_property(prop)
    values_found = []
    return values_found
def get_max_values_in_sentences(prop, sentences):
    responses = get_applicable_values_from_property(prop)
    values_found = []
    return values_found

class RequirementsReader:
    def __init__(self, requirements_filename, ontology_filename):
        z = zipfile.ZipFile('in/' + requirements_filename)
        marked_up_docx = z.open("word/document.xml")
        self.__etree = et.parse(marked_up_docx)
        self.__root = self.__etree.getroot()

        self.ontology = get_ontology("file://" + ontology_filename).load()

        self.requirements_decoration = []
        self.requirements_structure = []
        self.requirements_content = []
        self.requirements_quantitative = []
        self.requirements = [self.requirements_decoration,
                             self.requirements_structure,
                             self.requirements_content,
                             self.requirements_quantitative]
        self.text = ""
        for p in self.get_all_paragraphs():
            self.text = self.text + " " + get_text_from_paragraph(p)
        self.text = prepare_text(self.text)
        self.sentences = split_to_sentences(self.text)

    def get_all_paragraphs(self):
        elements = self.__root.findall('.//w:p', _namespaces)
        return elements

    def parse_requirements(self):
        for i, prop_class in enumerate(
                [self.ontology.DecorationProperty, self.ontology.StructureProperty,
                 self.ontology.VolumeProperty]):
            instances = self.ontology.get_instances_of(prop_class)
            next_generation = self.ontology.get_children_of(prop_class)
            while len(next_generation) != 0:
                new_generation = []
                for c in next_generation:
                    instances.extend(self.ontology.get_instances_of(c))
                    new_generation.extend(self.ontology.get_children_of(c))
                next_generation = new_generation
            for prop in instances:
                include_sentences = []
                for s in self.sentences:
                    if text_contains_word_from_list(s, prop.label):
                        include_sentences.append(s)
                if len(include_sentences) == 0: continue
                values_found = []
                if self.ontology.EnumProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_enum_values_in_sentences(prop, include_sentences))
                elif self.ontology.QuantitativeProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_values_of_quantitative_property_in_sentences(prop, include_sentences))
                elif self.ontology.PermissionProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_values_of_permission_property_in_sentences(prop, include_sentences))
                elif self.ontology.TopicProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_topic_values_in_sentences(prop, include_sentences))
                elif self.ontology.LabeledProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_values_of_labeled_property_in_sentences(prop, include_sentences))
                elif self.ontology.MinProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_min_values_in_sentences(prop, include_sentences))
                elif self.ontology.MaxProperty in list(self.ontology.get_parents_of(prop)):
                    values_found.extend(get_max_values_in_sentences(prop, include_sentences))
                if len(values_found) == 0: continue
                self.requirements[i].append([prop, values_found])

    def check_min_max_exists(self, text: str):
        min_exists, max_exists = False, False
        word_list = text.split(' ')
        if text_contains_word_from_list(text.lower(), self.__recognized_min_inverted):
            min_exists = True
        elif not min_exists:
            for i, word in enumerate(word_list):
                if text_contains_word_from_list(word, self.__recognized_min):
                    ok = True
                    for j in range(1, 5):
                        if i >= j:
                            if word_list[i - j].lower() == 'не':
                                ok = False
                    if ok:
                        min_exists = True
                        break
        if text_contains_word_from_list(text.lower(), self.__recognized_max_inverted):
            max_exists = True
        elif not max_exists:
            for i, word in enumerate(word_list):
                if text_contains_word_from_list(word, self.__recognized_max):
                    ok = True
                    for j in range(1, 5):
                        if i >= j:
                            if word_list[i - j].lower() == 'не':
                                ok = False
                    if ok:
                        max_exists = True
                        break
        return min_exists, max_exists
