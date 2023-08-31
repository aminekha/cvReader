import json
import os
import tempfile
from django.http import HttpResponse
import spacy
# import PyPDF2
import fitz
import docx2txt
import re
import shutil

from django.shortcuts import render
from openpyxl import Workbook
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import urllib.parse

# Load spaCy's English model
# nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('fr_core_news_sm')

def extract_data(file_path, file_name, keywords_list, coefficients):
    if file_name.lower().endswith('.pdf'):
        # Extract data from PDF
        doc = fitz.open(file_path)
        content = ""
        for page in doc:
        # with open(file_path, 'rb') as file:
            content += page.get_text()
            # pdf_reader = PyPDF2.PdfReader(file)
            # content = ""
            # for page_num in range(len(pdf_reader.pages)):
            #     page = pdf_reader.pages[page_num]
            #     content += page.extract_text()
    elif file_name.lower().endswith('.docx'):
        # Extract data from DOCX
        try:
            content = docx2txt.process(file_path)
        except Exception as e:
            return None
    else:
        # Unsupported file format
        return None
    
    # Extract keywords
    keyword_counts = {keyword.lower(): 0 for keyword in keywords_list}

    for i, keyword in enumerate(keywords_list):
        pattern = r'\b{}\b'.format(re.escape(keyword.lower()))
        matches = re.findall(pattern, content.lower())
        keyword_counts[keyword.lower()] = len(matches) * int(coefficients[i])


    return keyword_counts


def index(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        # country = request.POST.get('country', '')
        # city = request.POST.get('city', '')
        # age = request.POST.get('age', '')
        # keywords = [keyword.strip() for keyword in request.POST.get('keywords', '').split(',') if keyword.strip()]
        path = request.POST.get('path', '')
        keywords = request.POST.getlist('keywords[]')
        keywords = [keyword.lower() for keyword in keywords]
        coefficients = request.POST.getlist('coefficients[]')
        bonus = request.POST.getlist('bonus[]')
        limit = int(request.POST.get('limit', 500))

        filtered_files = []

        for file in files:
            if file.name.lower().endswith(('.pdf', '.docx')):
                try:
                    # Save the file to a temporary location
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        for chunk in file.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name
                        print(temp_file_path)

                    file_keywords = extract_data(temp_file_path, file.name, keywords, coefficients)
                    if(file_keywords is not None):
                        # print(file_country, file_city, file_age)
                        # print(file_keywords)

                        # Rate the cv
                        total_count = sum(file_keywords.values())

                        # Give bonus if it has more than one keyword
                        num_keywords_with_counts = sum(1 for count in file_keywords.values() if count > 0)  # Count the number of keywords with counts greater than 0
                        b = 0
                        if num_keywords_with_counts == 1:
                            b = 0
                        elif num_keywords_with_counts == 2:
                            b = 1
                        elif num_keywords_with_counts == len(keywords):
                            b = 2

                        total_count += int(bonus[b])

                        file_path = path + "/" + file.name

                        if(total_count > 1):
                            filtered_files.append(
                                {
                                    "file": file.name,
                                    "keyword1_total": file_keywords[keywords[0]],
                                    "keyword2_total": file_keywords[keywords[1]],
                                    "keyword3_total": file_keywords[keywords[2]],
                                    "bonus": bonus[b],
                                    "path": file_path,
                                    "total": total_count
                                }
                            )
                        os.remove(temp_file_path)
                except Exception as e:
                    print("error = ", e)
                    pass
        filtered_files = sorted(filtered_files, key=lambda x: x['total'], reverse=True)[:limit]
        print("filtered data = ", filtered_files)
        return render(request, 'reader/index.html', {'file_names': filtered_files, "keywords": keywords})
    return render(request, 'reader/index.html')

@csrf_exempt
def export_table_as_excel(request):
    file_names_json = request.POST.get('customers_data')
    
    file_names = json.loads(file_names_json)
    # Create a new workbook
    keywords = file_names.pop()
    workbook = Workbook()

    # Get the active sheet
    sheet = workbook.active

    # Add table headers
    headers = [
        'Fichier',
        'LinkedIn',
        keywords["keyword1"],
        keywords["keyword2"],
        keywords["keyword3"],
        'Bonus',
        'Total'
    ]
    sheet.append(headers)

    # Add table data
    for file_name in file_names:
        name = file_name["file"].split(", ")[:-1]
        row = [
            file_name["file"],
            f"https://linkedin.com/in/{name}",
            file_name["keyword1_total"],
            file_name["keyword2_total"],
            file_name["keyword3_total"],
            file_name["bonus"],
            file_name["total"]
        ]
        sheet.append(row)
    
    copy_files_to_new_folder(file_names)

    # Set the response headers for file download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mytable.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response

def copy_files_to_new_folder(files):
    try:
        destination_folder = os.path.join(settings.BASE_DIR, 'export')

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for file_record in files:
            path = file_record["path"].replace("http://127.0.0.1:8000", "")
            decoded_file_path = urllib.parse.unquote(path)
            destination_file = os.path.join(destination_folder, file_record["file"])

            if os.path.exists(decoded_file_path):
                shutil.copy(decoded_file_path, destination_file)

        print("Files copied successfully.") 
    except Exception as e:
        print("Error copying files = ", e)
