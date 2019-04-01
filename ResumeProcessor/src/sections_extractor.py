"""
Rohit Rangarajan
28.3.2019
Abstraction for extracting sections from resume text
"""
import spacy
from text_extractor import Docx2TextExtractor, Pdf2TextExtractor, Txt2TextExtractor
nlp = spacy.load('en_core_web_lg')

class SectionsExtractor:

    def __init__(self, model_dir):
        self._model_dir = model_dir

    # given the text of resume, returns the extracted sections
    def extract_sections(self, text):
        model = spacy.load(self._model_dir)
        doc = model(unicode(text))
        sections = {}
        for entity in doc.ents:
            sections[entity.label_] = []
        for entity in doc.ents:
            sections[entity.label_].append(entity.text)
        return sections


# for testing purpose
# given a file, print the sections
def test_sections_extractor(text_extractor, filepath):
    sections_extractor = SectionsExtractor("../resume_model")
    text = text_extractor.extract_text(filepath)

    sections = sections_extractor.extract_sections(text)
    for section in sections.keys():
        values = sections[section]
        print section + ": " + str(values)
        for text in values:
            doc = nlp(text)
            print 'Noun chunks:'
            for nc in doc.noun_chunks:
                print nc.text
            print 'NER:'
            for entity in doc.ents:
                print entity.text
        print '-------------------------------------'

