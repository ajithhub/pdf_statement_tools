from pypdf import PdfReader
import re
import logging
from os import path
import os
from glob import glob

"""
Script to process a directory of similar PDF files, parse the content inside
the document, and rename the files to organize them

e.g. 40 Charles schwab brokerage statements all named "Report (...).pdf" to be
renamed by year and quarter

Ideas for features:
    - Detect the file type and choose a class automatically
    - better warnings and dry run options for overwriting
    - config file for pattern matching

"""
class PDFRenamer():
    def __init__(self, page=1,pattern=None,output_fmt=None):
        self.page=page
        self.pattern=pattern
        self.output_fmt=output_fmt

    def extract_text(self, file_name):
        reader = PdfReader(file_name)
        number_of_pages = len(reader.pages)
        if number_of_pages < self.page:
            raise(Exception(f"Not enough pages in f{file_name}"))

        page = reader.pages[self.page - 1]
        text = page.extract_text()
        log.info(text)
        return text

    def parse_text(self, text):
        if not self.pattern:
            raise(Exception("Undefined pattern to match"))

        matches = re.search(self.pattern, text)

        if not matches:
            raise(Exception("Not matches found"))
        return matches

    def get_new_filename(self, file_name):
        text = self.extract_text(file_name)
        matches = self.parse_text(text)
        new_file_name = self.transform_matches(matches)
        return new_file_name

    def transform_matches(self, matches):
        raise(NotImplementedError())

    def rename(self, file_name):
        abspath = path.abspath(file_name)
        new_name = self.get_new_filename(abspath)
        log = logging.getLogger("rename")
        dir_name = path.dirname(abspath)
        new_abs_path = path.join(dir_name, new_name)

        if abspath == new_abs_path:
            log.info("Name unchanged: %s", abspath)
            return

        log.info("Renaming %s -> %s", abspath, new_abs_path)
        os.rename(abspath, new_abs_path)


class Schwab401kStatement(PDFRenamer):
    # "Period covered: JANUARY 1,2014 TOMARCH 31,2014 Prepared for: AJITH ANTONY"
    def __init__(self):
        pattern = "Period covered: (\w+) (\d+),(\d{4}) TO\w+ \d+,\d{4} Prepared for: AJITH ANTONY"

        return super().__init__( page=1, pattern=pattern)

    def transform_matches(self, matches):
        start_month = matches.group(1)
        start_day = matches.group(2)
        start_year = matches.group(3)

        log.info("Date is %s %s %s", start_month, start_day, start_year)

        quarter_map = {
                'JANUARY': "Q1",
                'APRIL': "Q2",
                'JULY': "Q3",
                'OCTOBER': "Q4"
                }
        if start_month not in quarter_map:
            raise(Exception(f"Did not understand start month: {start_month}"))

        output_fmt = "{0}-{1}-Schwab-401k.pdf"
        new_file_name = output_fmt.format(start_year, quarter_map[start_month])
        return new_file_name

def get_all_pdfs(directory):
    def find_ext(dr, ext, ig_case=False):
        if ig_case:
            ext =  "".join(["[{}]".format(ch + ch.swapcase()) for ch in ext])
            return glob(path.join(dr, "*." + ext))
    return find_ext(directory, "pdf", True)

def get_abs_paths(files):
    return [path.abspath(f) for f in files]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")

    file_name = "test.pdf"
    dir_name = "."
    log.info(f"Processing {file_name}")

    schwab_renamer = Schwab401kStatement()

    for statement in get_abs_paths(get_all_pdfs(dir_name)):
        schwab_renamer.rename(statement)
