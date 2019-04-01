from sections_extractor import SectionsExtractor
from scorer import JsonBasedScorer
import os
from sections_parser import SectionsParser
from text_extractor import ResumeTextExtractor
import sys

class ResumeProcessor:
    def __init__(self, scorer, model_dir):
        self._scorer = scorer
        self._sections_extractor = SectionsExtractor(model_dir)
        self._text_extractor = None

    def set_text_extractor(self, text_extractor):
        self._text_extractor = text_extractor
        return self

    def _guess_extractor(self, filepath):
        return ResumeTextExtractor.get_extractor(filepath)

    def get_score(self, filepath):
        if self._text_extractor is None:
            text = self._guess_extractor(filepath).extract_text(filepath) # Guess
        else:
            text = self._text_extractor.extract_text(filepath) # Use what is supplied
        sections = self._sections_extractor.extract_sections(text)
        return self._scorer.set_sections_and_values(sections).get_score()


    # given a directory containing resumes, this ranks them in order of score (asc or desc)
    # and returns the list of resume names
    def rank_resumes(self, resumes_dir, order='desc'):
        lst = []
        for filename in os.listdir(resumes_dir):
            filepath = resumes_dir + '/' + filename
            lst.append((filepath, self.get_score(filepath)))
        return sorted(lst, key=lambda x: x[1], reverse = (order == 'desc'))


    def generate_summary(self, filepath):
        # preferred order of reporting
        sections_order = ['Name', 'Location', 'Email Address', 'College Name', 'Degree', 'Graduation year', 'Companies worked at',
                          'Designation', 'Years of experience', 'Skills']

        sections = self._sections_extractor.extract_sections(self._guess_extractor(filepath).extract_text(filepath))
        for section_name in sections_order:
            if section_name in sections.keys():
                values = set(sections[section_name])
                print section_name + ": "
                for value in values:
                    print '\t\t' + str(value)
        print '-----------------------------\nScore: ' + str(self.get_score(filepath))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: " + "python resume_processor.py -summary filepath"
        print "Usage: " + "python resume_processor.py -rank dir"
        exit(-1)

    todo = sys.argv[1]
    input = sys.argv[2]

    sections_parser = SectionsParser()
    json_scorer = JsonBasedScorer("../src/complex_scoring_params.json", sections_parser)
    rp = ResumeProcessor(json_scorer, "../resume_model")

    if todo == '-summary':
        rp.generate_summary(input)

    elif todo == '-rank':
        for elem in rp.rank_resumes(input):
            print elem


