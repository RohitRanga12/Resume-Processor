"""
Rohit Rangarajan
29.3.2019
Abstraction for scoring logic
"""

import json

# abstract class
class ResumeScorer:
    def __init__(self):
        # let us assume some default sections to be considered
        self._sections_for_scoring = ["Skills", "Companies worked at", "Designation", "College Name", "Degree",
                                      "Years of Experience"]

    # sections_and_values is the output of SectionsExtractor, a dictionary of section names with their values
    def set_sections_and_values(self, sections_and_values):
        self._sections_and_values = sections_and_values
        return self

    def set_sections_for_scoring(self, sections_for_scoring):
        self._sections_for_scoring = sections_for_scoring
        return self


    def get_score(self):
        score = 0.0
        section_names = self._sections_and_values.keys() # section names identified in resume
        for section_name in section_names:
            if section_name in self._sections_for_scoring:
                score += self._get_section_score(section_name)
        return score


    # given a section name and the dictionary 'sections_and_values', give the score corresponding to that section
    def _get_section_score(self, section_name):
        None


# This class scores a resume based on parameters defined in a json file
# For flexibility, this uses an instance of SectionsParser
class JsonBasedScorer(ResumeScorer):
    def __init__(self, json_file, sections_parser):
        ResumeScorer.__init__(self)
        self._sections_parser = sections_parser
        with open(json_file) as f:
            self._scoring_params = json.load(f)

    def _get_section_score(self, section_name):
        return 0


    def _get_rule_score(self, rule_array):
        for elem in rule_array:
            requirements = elem["and"]
            score = elem['score']
            all_requirements_satisfied = True
            for section_name, values in requirements.iteritems():
                if self._sections_parser.matches(section_name, values):
                    continue
                else:
                    all_requirements_satisfied = False
                    break
            if all_requirements_satisfied:
                return score
            continue
        return 0.0

    def get_score(self):
        score = 0.0

        self._sections_parser.clear()

        for section_name, values in self._sections_and_values.iteritems():
            self._sections_parser.prepare(values, section_name)

        # each 'elem' is json object containing 'Rule' as field
        for elem in self._scoring_params["Rules"]:
            score += self._get_rule_score(elem['Rule'])
        return score


