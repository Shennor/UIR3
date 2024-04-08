__all__ = ['Validator']

import re

import jsonschema
import logging
import math
import docx

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, Cm
from chardet import detect

from wrapper import DocumentWrapper
from schema import RequirementsSchema

logger = logging.getLogger(__name__)


class Validator(object):
    """Class for validating docx document."""

    def __init__(self, wrapper, requirements):
        """
        :param wrapper: Wrapper
        :param requirements: json
        """
        try:
            jsonschema.validate(instance=requirements, schema=RequirementsSchema().requirements_schema)
        except jsonschema.exceptions.ValidationError as err:
            print(f"Requirements file invalid: {err.message}")
        self._title_first_centered = True
        self._make_changes = True
        self._log = []
        self._docx = wrapper
        self._requirements = requirements
        self._errors = {
            "requirements": [],
            "general": {
                "font": [],
                "font_size": [],
                "interval": [],
                "alignment": [],
                "columns": [],
                "italic_allowed": [],
                "bold_allowed": [],
                "underlined_allowed": [],
                "double_space_allowed": [],
                "size_min": [],
                "size_max": []
            },
            "images": {
                "num_min": [],
                "num_max": [],
                "width_max": [],
                "dpi_min": [],
                "color_allowed": [],
                "links_required": []
            },
            "tables": {
                "font_size": [],
                "alignment": [],
                "width_max": [],
                "links_required": []
            },
            "keywords": {
                "required": [],
                "num_min": [],
                "num_max": [],
                "english": []
            },
            "UDC": []
        }
        self._warnings = {
            "images": {
                "links": []
            }
        }

    def _check_font(self, paragraph, p_i=None):
        if self._requirements['general']['font'] is None and \
                self._requirements['general']['font_size'] is None:
            return
        name_changes = 0
        size_changes = 0
        for j, run in enumerate(paragraph.runs):
            # print(run.text)
            name = (run.font.name or self._docx.find_paragraph_attribute(paragraph.style, 'font', 'name'))
            size = (getattr(run.font.size, 'pt', self._requirements['general']['font_size']) or \
                    self._docx.find_paragraph_attribute(paragraph.style, 'font', 'size').pt)
            if not self._make_changes:
                name_ok = True
                size_ok = True
                if self._requirements['general']['font'] is not None and \
                        name != self._requirements['general']['font'] and name_ok:
                    self._errors['general']['font'].append({"paragraph": p_i,
                                                            "expected": self._requirements['general']['font'],
                                                            "found": name
                                                            })
                    name_ok = False
                if self._requirements['general']['font_size'] is not None and \
                        size != self._requirements['general']['font_size'] and size_ok:
                    self._errors['general']['font_size'].append({"paragraph": p_i,
                                                                 "expected": self._requirements['general']['font_size'],
                                                                 "found": size
                                                                 })
                    size_ok = False
                if not name_ok and not size_ok:
                    break
            else:
                if self._requirements['general']['font'] is not None and \
                        name != self._requirements['general']['font']:
                    self._errors['general']['font'].append({"paragraph": p_i,
                                                            "expected": self._requirements['general']['font'],
                                                            "found": name
                                                            })
                    if self._requirements['general']['font'] in ["Times New Roman", "Arial", "Cambria", "Calibri"]:
                        run.font.name = self._requirements['general']['font']
                        name_changes += 1
                    else:
                        self._log.append(f"Error while set font name in paragraph {p_i}: "
                                         f"{self._requirements['general']['font']} "
                                         f"is out of normal {['Times New Roman', 'Arial', 'Cambria', 'Calibri']}")
                if self._requirements['general']['font_size'] is not None and \
                        size != self._requirements['general']['font_size']:
                    self._errors['general']['font_size'].append({"paragraph": p_i,
                                                                 "expected": self._requirements['general']['font_size'],
                                                                 "found": size
                                                                 })
                    if 5 < self._requirements['general']['font_size'] < 50:
                        run.font.size = Pt(self._requirements['general']['font_size'])
                        size_changes += 1
                    else:
                        self._log.append(f"Error while set font size in paragraph {p_i}: "
                                         f"{self._requirements['general']['font_size']} "
                                         f"is out of normal {range(5, 40)}")
        if name_changes > 0:
            self._log.append(f"Change font name {name_changes} times in paragraph {p_i} "
                             f"to {self._requirements['general']['font']}")
        if size_changes > 0:
            self._log.append(f"Change font size {size_changes} times in paragraph {p_i} "
                             f"to {self._requirements['general']['font_size']}")

    def _check_interval(self, paragraph, p_i=None):
        """
        :param paragraph: docx.Document.paragraph
        :param p_i: paragraph index for logging
        """
        interval = paragraph.paragraph_format.line_spacing
        if interval != self._requirements['general']['interval']:
            self._errors['general']['interval'].append({"paragraph": p_i,
                                                        "expected": self._requirements['general']['interval'],
                                                        "found": interval
                                                        })
            if self._make_changes:
                if self._requirements['general']['interval'] in [1.0, 1.15, 1.5, 2.0, 2.5, 3.0, 1, 2, 3]:
                    paragraph.paragraph_format.line_spacing = self._requirements['general']['interval']
                    self._log.append(f"Change of line_spacing of paragraph {p_i} from {interval} "
                                     f"to {self._requirements['general']['interval']}")
                else:
                    self._log.append(f"Error while set line_spacing of paragraph {p_i}: "
                                     f"{self._requirements['general']['interval']} "
                                     f"is out of normal {[1.0, 1.15, 1.5, 2.0, 2.5, 3.0, 1, 2, 3]}")

    def _check_alignment(self, paragraph, p_i=None):
        """
        :param paragraph: docx.Document.paragraph
        :param p_i: paragraph index for logging
        """
        alignment = paragraph.paragraph_format.alignment
        if not self._requirements['general']['alignment'].lower() in str(alignment).lower():
            self._errors['general']['alignment'].append({"paragraph": p_i,
                                                         "expected": self._requirements['general']['alignment'],
                                                         "found": alignment
                                                         })
            if self._make_changes:
                if self._requirements['general']['alignment'] in ["justify", "center", "left", "right"]:
                    if self._requirements['general']['alignment'] == "justify":
                        paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
                    elif self._requirements['general']['alignment'] == "center":
                        paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    elif self._requirements['general']['alignment'] == "left":
                        paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    elif self._requirements['general']['alignment'] == "right":
                        paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                    self._log.append(f"Change of alignment of paragraph {p_i} from {alignment} "
                                     f"to {self._requirements['general']['alignment']}")
                else:
                    self._log.append(f"Error while set alignment of paragraph {p_i}: "
                                     f"{self._requirements['general']['alignment']} "
                                     f"is out of normal {['justify', 'center', 'left', 'right']}")

    # TODO _check_columns
    def _check_columns(self):
        pass

    def _check_styles_allowed(self, paragraph, p_i):
        if self._requirements['general']['italic_allowed'] and \
                self._requirements['general']['bold_allowed'] and \
                self._requirements['general']['underlined_allowed']:
            return
        italic_changes = 0
        bold_changes = 0
        underlined_changes = 0
        for j, run in enumerate(paragraph.runs):
            if run.italic and not self._requirements['general']['italic_allowed']:
                self._errors['general']['italic_allowed'].append({"paragraph": p_i,
                                                                  "run": j,
                                                                  "expected": self._requirements['general'][
                                                                      'italic_allowed'],
                                                                  "found": True
                                                                  })
                if self._make_changes:
                    run.italic = False
                    italic_changes += 1
            if run.bold and not self._requirements['general']['bold_allowed']:
                self._errors['general']['bold_allowed'].append({"paragraph": p_i,
                                                                "run": j,
                                                                "expected": self._requirements['general'][
                                                                    'bold_allowed'],
                                                                "found": True
                                                                })
                if self._make_changes:
                    run.bold = False
                    bold_changes += 1
            if run.underline and not self._requirements['general']['underlined_allowed']:
                self._errors['general']['underlined_allowed'].append({"paragraph": p_i,
                                                                      "run": j,
                                                                      "expected": self._requirements['general'][
                                                                          'underlined_allowed'],
                                                                      "found": True
                                                                      })
                if self._make_changes:
                    run.underline = False
                    underlined_changes += 1
        if italic_changes > 0:
            self._log.append(f"Change italic to normal {italic_changes} times in paragraph {p_i}")
        if bold_changes > 0:
            self._log.append(f"Change bold to normal {bold_changes} times in paragraph {p_i}")
        if underlined_changes > 0:
            self._log.append(f"Change underlined to normal {underlined_changes} times in paragraph {p_i}")

    def _check_spaces(self, paragraph, p_i):
        text = paragraph.text
        if self._requirements['general']['double_space_allowed'] is None:
            return
        if not self._requirements['general']['double_space_allowed']:
            if "  " in text:
                self._errors['general']['double_space_allowed'].append({"paragraph": p_i,
                                                                        "expected": self._requirements['general'][
                                                                            'double_space_allowed'],
                                                                        "found": True
                                                                        })
                if self._make_changes:
                    paragraph.text = text.replace("  ", ' ')
                    self._log.append(f"Removed double spaces in paragraph {p_i}")

    # TODO _check_size doesnt work correctly
    def _check_size(self):
        # print(f"In docx {self._docx.get_word_count()} words, {self._docx.get_symbol_count_with_spaces_count()}"
        #      f" ссп и {self._docx.get_symbol_count_without_spaces_count()} сбп")

        cnt = 0
        if not self._requirements['general']['size_min'] is None:
            if cnt < self._requirements['general']['size_min']:
                self._errors['general']['size_min'].append({"expected": self._requirements['general']['size_min'],
                                                            "found": cnt
                                                            })
        if not self._requirements['general']['size_max'] is None:
            if cnt > self._requirements['general']['size_max']:
                self._errors['general']['size_max'].append({"expected": self._requirements['general']['size_max'],
                                                            "found": cnt
                                                            })

    def validate_general_requirements(self):
        """Validate general requirements."""

        title_found = False
        for i, paragraph in enumerate(self._docx.iter_paragraphs()):
            # find and skip title
            if self._title_first_centered and not title_found:
                if "center" in str(paragraph.paragraph_format.alignment).lower():
                    title_found = True
                continue
            self._check_font(paragraph, i)
            self._check_interval(paragraph, i)
            self._check_alignment(paragraph, i)
            self._check_styles_allowed(paragraph, i)
            self._check_spaces(paragraph, i)

        # TODO columns checking
        title_found = False
        for i, section in enumerate(self._docx.iter_sections()):
            if section.start_type == WD_SECTION_START.NEW_COLUMN:
                if not self._requirements['general']['columns']:
                    self._errors['general']['columns'].append({"section": i,
                                                               "expected": self._requirements['general']['columns'],
                                                               "found": True
                                                               })
            else:
                if self._requirements['general']['columns']:
                    self._errors['general']['columns'].append({"section": i,
                                                               "expected": self._requirements['general']['columns'],
                                                               "found": False
                                                               })
        self._check_size()

    def _check_images_count(self, images):
        if not self._requirements['images']['num_min'] is None \
                and not self._requirements['images']['num_max'] is None:
            if self._requirements['images']['num_min'] > self._requirements['images']['num_max']:
                self._errors["requirements"].append(f"Minimal image number {self._requirements['images']['num_min']} "
                                                    f"is bigger than maximal number "
                                                    f"{self._requirements['images']['num_max']}")
                return
        if not self._requirements['images']['num_min'] is None:
            if len(images) < self._requirements['images']['num_min']:
                self._errors['images']['num_min'].append({"num_min": self._requirements['images']['num_min'],
                                                          "found": len(images)
                                                          })
        if not self._requirements['images']['num_max'] is None:
            if len(images) > self._requirements['images']['num_max']:
                self._errors['images']['num_max'].append({"num_max": self._requirements['images']['num_max'],
                                                          "found": len(images)
                                                          })

    def _check_image_width(self, image, i=None):
        # Using cm
        if self._requirements['images']['width_max'] is None:
            return
        if image.width.cm > self._requirements['images']['width_max']:
            self._errors['images']['width_max'].append({"image": i,
                                                        "width_max": self._requirements['images']['width_max'],
                                                        "found": image.width.cm
                                                        })
            width = image.width.cm
            if self._make_changes:
                image.width = Cm(self._requirements['images']['width_max'])
                self._log.append(f"Resized image {i} width from {width} to {image.width.cm}")

    def _check_image_dpi(self, image, i=None):
        if self._requirements['images']["dpi_min"] is None:
            return
        if image.info["dpi"][0] < self._requirements['images']["dpi_min"] or \
                image.info["dpi"][1] < self._requirements['images']["dpi_min"]:
            self._errors['images']['dpi_min'].append({"image": i,
                                                      "dpi_min": self._requirements['images']['dpi_min'],
                                                      "found": image.info["dpi"]
                                                      })

    def _check_image_color(self, images):
        if self._requirements['images']['color_allowed']:
            return
        ok = True
        for i, image in enumerate(images):
            if image.mode not in ["L", "P"]:
                self._errors['images']['color_allowed'].append({"image": i,
                                                                "color_allowed": self._requirements['images'][
                                                                    'color_allowed'],
                                                                "found": True
                                                                })
                ok = False
        if self._make_changes:
            if not ok:
                self._docx.grayscale_images()

    def _check_image_link(self, count):
        for j in range(1, count):
            for i, paragraph in enumerate(self._docx.iter_paragraphs()):
                if f"Рисунок {j}" in paragraph.text:
                    success = False
                    found_i = 0
                    for k, paragraph_ in enumerate(self._docx.iter_paragraphs()):
                        if f"рис. {j}" in paragraph_.text.lower() \
                                or f"рис {j}" in paragraph_.text.lower() \
                                or f"рисунок {j}" in paragraph_.text.lower() \
                                or f"рисунке {j}" in paragraph_.text.lower() \
                                or f"рисунок {j}" in paragraph_.text.lower() \
                                or f"рисунка {j}" in paragraph_.text.lower():
                            if not k == i:
                                success = True
                                found_i = k
                                break
                    if success:
                        if i > found_i:
                            self._warnings["images"]["links"].append(f"Image {j} linked in paragraph {found_i} "
                                                                     f"before definition in paragraph {i}")
                    else:
                        self._errors["images"]["links_required"].append(f"Image {j} defined in paragraph {i}"
                                                                        f" haven't linked")

    def validate_images_requirements(self):
        image_shapes = self._docx.get_images_shapes()
        self._check_images_count(image_shapes)
        for i, image in enumerate(image_shapes):
            self._check_image_width(image, i)
        image_files = self._docx.get_images_files()
        for i, image in enumerate(image_files):
            self._check_image_dpi(image)
        self._check_image_color(image_files)
        self._check_image_link(len(image_shapes))

    # TODO
    def _check_table_font(self, table, i=None):
        pass

    # TODO
    def _check_table_alignment(self, table, i=None):
        if self._requirements['tables']['alignment'] is None:
            return

    # TODO
    def _check_table_width(self, table, i=None):
        pass

    # TODO
    def _check_table_link(self, table, i=None):
        pass

    # TODO
    def validate_tables_requirements(self):
        tables = self._docx.get_tables()
        for i, table in enumerate(tables):
            self._check_table_font(table)

    def _check_keywords_num(self, keywords):
        if self._requirements["keywords"]["num_min"] is None \
                or self._requirements["keywords"]["num_max"] is None:
            return
        if not self._requirements["keywords"]["num_min"] is None \
                and not self._requirements["keywords"]["num_max"] is None \
                and self._requirements["keywords"]["num_min"] > self._requirements["keywords"]["num_max"]:
            self._errors["requirements"].append(f"Minimal keywords number {self._requirements['keywords']['num_min']} "
                                                f"is bigger than maximal number "
                                                f"{self._requirements['keywords']['num_max']}")
            return
        cnt = len(keywords)
        if self._requirements["keywords"]["english"] == "duplicate":
            cnt /= 2.0
        if not self._requirements['keywords']['num_min'] is None:
            if cnt < self._requirements['keywords']['num_min']:
                self._errors['keywords']['num_min'].append({"num_min": self._requirements['keywords']['num_min'],
                                                            "found": cnt
                                                            })
        if not self._requirements['keywords']['num_max'] is None:
            if cnt > self._requirements['keywords']['num_max']:
                self._errors['keywords']['num_max'].append({"num_max": self._requirements['keywords']['num_max'],
                                                            "found": cnt
                                                            })

    def _check_keywords_lang(self, keywords):
        if self._requirements["keywords"]["english"] == "only":
            for i, w in enumerate(keywords):
                lang = detect(w.encode('cp1251'))["language"]
                if lang == "Russian":
                    self._errors["keywords"]["english"].append({
                        "english": self._requirements["keywords"]["english"],
                        "found": w
                    })
                    break
        elif self._requirements["keywords"]["english"] == "no":
            for i, w in enumerate(keywords):
                if not re.match(r"[A-Za-z]+", w) is None:
                    self._errors["keywords"]["english"].append({
                        "english": self._requirements["keywords"]["english"],
                        "found": w
                    })
                    break
        elif self._requirements["keywords"]["english"] == "duplicate":
            eng_num = 0
            rus_num = 0
            for i, w in enumerate(keywords):
                lang = detect(w.encode('cp1251'))["language"]
                # print(w, lang)
                if lang == "Russian":
                    rus_num += 1
                else:
                    eng_num += 1
            if not eng_num == rus_num:
                self._errors["keywords"]["english"].append({
                    "english": self._requirements["keywords"]["english"],
                    "eng_num": eng_num,
                    "rus_num": rus_num
                })

    def validate_keywords(self):
        words = []
        k = 0
        for i, paragraph in enumerate(self._docx.iter_paragraphs()):
            if "ключевые слова" in paragraph.text.lower() \
                    or "keywords" in paragraph.text.lower():
                if k >= 2:
                    break
                k += 1
                i = paragraph.text.lower().find("слова")
                if i == -1:
                    i = paragraph.text.lower().find("keywords")
                    i += 9
                else:
                    i += 5
                words.extend(list(filter(lambda x: not x == "",
                                         [re.sub(r'[^A-Za-zА-Яа-я]+', '', s) for s
                                          in re.split(r'[,;]', paragraph.text.lower()[i:])])))
        # print(words)
        if len(words) == 0:
            if self._requirements["keywords"]["required"]:
                self._errors["keywords"]["required"].append({"required": self._requirements['keywords']['required'],
                                                             "found": False
                                                             })
                return
        self._check_keywords_num(words)
        self._check_keywords_lang(words)

    def validate_udc(self):
        if not self._requirements["UDC"]["required"]:
            return
        found_udc = False
        see_next = False
        i = 0
        for j, paragraph in enumerate(self._docx.iter_paragraphs()):
            if "УДК" in paragraph.text:
                # print(1)
                i = paragraph.text.find(" ", paragraph.text.find("УДК"))
                if i is None:
                    see_next = True
            elif see_next:
                # print(2)
                i = 0
                """
                i = paragraph.text.find(" ")
                if i is None:
                    see_next = False
                """
            else:
                # print(3)
                i = 0
            if ("УДК" in paragraph.text or see_next) and i is not None:
                # print(f"i = {i}")
                # print(paragraph.text[i:])
                udc = re.findall(r'[0-9]+[0-9.+*:/\\\[\]]*[A-Z]*', paragraph.text[i:])
                # print(udc)
                if len(udc) == 1:
                    found_udc = True
                    self._log.append(f"Found UDC {udc[0]} in paragraph {j}")
                elif len(udc) > 0:
                    self._log.append(f"Found multiple matches for UDC: {udc} in paragraph {j}")
                elif not see_next:
                    see_next = True
                elif see_next:
                    see_next = False
            if found_udc:
                break
        if not found_udc:
            self._errors["UDC"].append("UDC not found but required")

    def validate_literature(self):
        pass

    def result(self):
        if self._make_changes:
            grayscale_image_num = self._docx.save_as("out/result.docx")
            self._log.append(
                f"Grayscale succeed on {grayscale_image_num} images from {len(self._docx.get_images_shapes())}")
        return self._errors, self._log, self._warnings

    def validate(self):
        self.validate_general_requirements()
        self.validate_images_requirements()
        self.validate_tables_requirements()
        self.validate_keywords()
        self.validate_udc()
