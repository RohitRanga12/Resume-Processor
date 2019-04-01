"""
Rohit Rangarajan
29.3.2019
Abstraction for parsing the text corresponding to a section, to facilitate scoring
"""

import spacy


class SectionsParser:
    nlp = spacy.load('en_core_web_lg')

    def __init__(self):
        self._section_names_and_values_parsed = {} # to cache the parsed values

    def clear(self):
        self._section_names_and_values_parsed = {}

    # given a list of values from params json file, checks if all its elements matches anything in _section_values
    def matches(self, section_name, json_values_list):
        if section_name not in self._section_names_and_values_parsed.keys():
            return False

        # concatenate all elements of the set into a single string for easy search
        values_parsed = ' '.join(self._section_names_and_values_parsed[section_name])

        for json_value in json_values_list:
            json_value_lowercase = json_value.lower().strip()
            if json_value_lowercase not in values_parsed:
                return False
        return True


    # given a section name and its text (from resume), this does the necessary preprocessing to facilitate
    # the calculation to be performed in 'matches()'.
    # For emails, take the first element
    # For the rest, pass through spaCy's NER and noun chunk extractor and save the data in _section_values
    # for subsequent use
    def prepare(self, section_values, section_name):
        val = set()
        if section_name == 'Email Address':
            val.add(section_values[0].lower().strip())
        else:
            for text in section_values:
                doc = SectionsParser.nlp(text)
                for nc in doc.noun_chunks:
                    val.add(str(nc.text).lower().strip())
                for entity in doc.ents:
                    val.add(str(entity.text).lower().strip())

        # cache the parsed values along with section_name and reset _section_values for next section
        self._section_names_and_values_parsed[section_name] = val


