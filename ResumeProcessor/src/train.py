"""
Rohit Rangarajan
28.3.2019
This is based on this code: https://github.com/DataTurks-Engg/Entity-Recognition-In-Resumes-SpaCy
"""

import json
import random
import logging
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from sklearn.metrics import accuracy_score
import spacy

# Creates NER training data in Spacy format from JSON downloaded from Dataturks
# Outputs the Spacy training data which can be used for Spacy training
def convert_dataturks_to_spacy(dataturks_JSON_FilePath):
    try:
        training_data = []
        with open(dataturks_JSON_FilePath, 'r') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                # only a single point in text annotation.
                point = annotation['points'][0]
                labels = annotation['label']

                # handle both list of labels or a single label.
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    # dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                    entities.append((point['start'], point['end'] + 1, label))

            training_data.append((text, {"entities" : entities}))
        return training_data

    except Exception as e:
        logging.exception("Unable to process " + dataturks_JSON_FilePath + "\n" + "error = " + str(e))
        return None


# Train Spacy NER model
def train_spacy(training_data_filepath, saved_model_dir):

    TRAIN_DATA = convert_dataturks_to_spacy(training_data_filepath)
    nlp = spacy.blank('en')  # create blank Language class

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)

    # add labels
    for _, annotations in TRAIN_DATA:
         for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(10):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.2,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)
        nlp.to_disk(saved_model_dir)
    return nlp


# test the model and evaluate it
def test_model(model, test_data_filepath, test_results_dir):
    examples = convert_dataturks_to_spacy(test_data_filepath)
    c = 0
    for text, annot in examples:
        print text
        f = open(test_results_dir + "resume" + str(c) + ".txt", "w")
        with open(test_results_dir + "resume_text" + str(c) + ".txt", "w") as f1:
            f1.write(text.encode('utf-8'))
        doc_to_test = model(unicode(text))
        d = {}
        for ent in doc_to_test.ents:
            d[ent.label_] = []
        for ent in doc_to_test.ents:
            d[ent.label_].append(ent.text)
        for i in set(d.keys()):
            f.write("\n\n")
            f.write(i + ":" + "\n")
            for j in set(d[i]):
                temp = j.replace('\n', '')
                temp = temp + "\n"
                f.write(temp.encode('utf-8'))
        d = {}
        for ent in doc_to_test.ents:
            d[ent.label_] = [0, 0, 0, 0, 0, 0]
        for ent in doc_to_test.ents:
            doc_gold_text = model.make_doc(text)
            gold = GoldParse(doc_gold_text, entities=annot.get("entities"))
            y_true = [ent.label_ if ent.label_ in x else 'Not '+ent.label_ for x in gold.ner]
            y_pred = [x.ent_type_ if x.ent_type_ == ent.label_ else 'Not '+ent.label_ for x in doc_to_test]
            if d[ent.label_][0] == 0:
                (p, r, f, s) = precision_recall_fscore_support(y_true, y_pred, average='weighted')
                a = accuracy_score(y_true, y_pred)
                d[ent.label_][0] = 1
                d[ent.label_][1] += p
                d[ent.label_][2] += r
                d[ent.label_][3] += f
                d[ent.label_][4] += a
                d[ent.label_][5] += 1
        c += 1
    for i in d:
        print("\n For Entity " + i + "\n")
        print("Accuracy : " + str((d[i][4]/d[i][5])*100) + "%")
        print("Precision : " + str(d[i][1]/d[i][5]))
        print("Recall : " + str(d[i][2]/d[i][5]))
        print("F-score : " + str(d[i][3]/d[i][5]))


if __name__ == '__main__':
    train_spacy("src/traindata.json", "resume_model/")
    model = spacy.load("resume_model")
    test_model(model, "src/testdata.json", "test_results/")
