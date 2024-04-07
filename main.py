import os
import subprocess

from requirements import Requirements
from validator import Validator
from wrapper import DocumentWrapper
import json

r = Requirements("30 Digital Diagnostics.docx")
p = r.get_all_paragraphs()
# print(r.get_min_max_image_count())

home = "C:/Users/megera/Documents/UIR3/"
path = "in/result.docx"
print(os.access(path, os.R_OK))
print(os.access(path, os.W_OK))
# os.chown(path, "megera", )
wrapper = DocumentWrapper(path)
'''
for i, section in enumerate(wrapper.iter_sections()):
    print(wrapper.get_section_attributes(section))

'''
print("=====================================================================================")
# for i, paragraph in enumerate(wrapper.iter_paragraphs()):
    # print(wrapper.get_paragraph_attributes(paragraph))
    # print(paragraph)
    # print(wrapper.get_font_attributes(paragraph))
# validate("in/30 Digital Diagnostics.docx", "example_req.json")

requirements = json.load(open('example_req.json', "r"))

validator = Validator(wrapper, requirements)
validator.validate()
errors, log, warnings = validator.result()
print(errors)
print(log)
print(warnings)

