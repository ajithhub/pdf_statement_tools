from pypdf import PdfReader, PdfWriter

"""
Hmm, some pdf aren't readable.
Some PDF we only want small bits of.
Some PDFs should justbe concatenated together.
"""

pdfs = [
        { "name": 'hill.pdf', "pages": [1]},
        { "name": 'columbia.pdf', "pages": [1]}
        ]


output = PdfWriter()
output_filename = "2023-1098-Fidelity_Bank-Hill-Columbia.pdf"

for pdf in pdfs:
    infile = PdfReader(pdf['name'])
    for page in pdf['pages']:
        output.add_page(infile.pages[page-1])

with open(output_filename,'wb') as f:
    output.write(f)
