from validator import DesignValidator
from wrapper import DocumentWrapper
import json

from ontospy.gendocs.viz.viz_html_single import *

home = "C:/Users/megera/Documents/UIR3/"
path = "in/1.docx"
print(os.access(path, os.R_OK))
print(os.access(path, os.W_OK))
wrapper = DocumentWrapper(path)

requirements = json.load(open('example_req.json', "r"))
validator = DesignValidator(wrapper, requirements)
validator.validate()
errors, log, warnings, errors_list = validator.result()
print("Errors:")
for i, s in enumerate(errors_list):
    print(i, s)
with open("errors.json", "w") as f:
    json.dump(errors, f)
print("Log:")
for i, s in enumerate(log):
    print(i, s)
with open("warnings.json", "w") as f:
    json.dump(warnings, f)


