# import pdfplumber

# def extract_tables_from_pdf(pdf_path):
#     tables = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table:
#                 tables.append(table)
#     return tables

# # Example usage
# pdf_path = "currency.pdf"
# tables = extract_tables_from_pdf(pdf_path)
# print(tables)
# for table in tables:
#     for row in table:
#         print(row)

import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Example usage
pdf_path = "currency.pdf"
text = extract_text_from_pdf(pdf_path)
header = text.split('\n')[3]
print(header)
for country in text.split('\n')[4:-3]:
    if country.endswith("ISO code"):
        info = country.replace("Country name Currency name Currency ISO code","").split(" ")[-1]
        print(info)
        print(info[0], info[-1])
    else:        
        info = country.split(" ")
        print(info)
        print(info[0], info[-1])

