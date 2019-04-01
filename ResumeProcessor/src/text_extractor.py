"""
Rohit Rangarajan
28.3.2019
Abstraction for extracting text from different file formats
"""
import docxpy
import PyPDF2
from tika import parser



class TextExtractor:
    # extracts text from file
    # for now, we are handling only ascii characters!
    def extract_text(self, filepath):
        return self._remove_nonascii_from_str(self.extract_text1(filepath))

    # this needs to be implemented by derived classes
    def extract_text1(self, filepath):
        None

    @staticmethod
    def _remove_nonascii_from_str(str):
        return "".join(char for char in str if ord(char) < 128)


class Docx2TextExtractor(TextExtractor):
    # extracts text from docx file
    def extract_text1(self, filepath):
        return docxpy.process(filepath)


# uses PyPDF
class PyPdfExtractor(TextExtractor):
    # extracts text from PDF file
    def extract_text1(self, filepath):
        with open(filepath, 'rb') as f:
            # creating a pdf reader object
            pdfReader = PyPDF2.PdfFileReader(f)

            # creating a page object
            pageObj = pdfReader.getPage(0)

            # extracting text from page
            return pageObj.extractText()


# uses Tika
class TikaPdfExtractor(TextExtractor):
    def extract_text1(self, filepath):

        # Use Tika to parse the PDF
        parsedPDF = parser.from_file(filepath)

        # Extract the text content from the parsed PDF
        return parsedPDF["content"]



# convenient wrapper for PDF extraction - uses Tika by default
class Pdf2TextExtractor:
    def __init__(self, extractor=TikaPdfExtractor()):
        self._pdf_extractor = extractor

    def extract_text(self, filepath):
        return self._pdf_extractor.extract_text(filepath)


class Txt2TextExtractor(TextExtractor):
    # extracts text from txt file
    def extract_text1(self, filepath):
        with open(filepath) as f:
            return f.read()


"""
Class for obtaining the appropriate instance of TextExtractor based on file name 
"""
class ResumeTextExtractor:
    txt_2_text_extractor = Txt2TextExtractor()
    pdf_2_text_extractor = Pdf2TextExtractor()
    docx_2_text_extractor = Docx2TextExtractor()

    @staticmethod
    def get_extractor(filepath):
        if filepath.endswith('.pdf'):
            return ResumeTextExtractor.pdf_2_text_extractor
        elif filepath.endswith('.docx'):
            return ResumeTextExtractor.docx_2_text_extractor
        elif filepath.endswith('.txt'):
            return ResumeTextExtractor.txt_2_text_extractor
        raise Exception("Unknown resume format!")

