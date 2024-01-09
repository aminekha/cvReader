import json
import os
import tempfile
from django.http import HttpResponse, FileResponse
import fitz
import docx2txt
import re
import shutil, time

from django.shortcuts import render
from openpyxl import Workbook
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import urllib.parse
from multiprocessing import Pool
import threading
import os
from supabase import create_client, Client
from reader.models import Resume

from reader.utils import read_file

url: str = "https://osijypnfegeucpobzrwb.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zaWp5cG5mZWdldWNwb2J6cndiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI2NDg5MTAsImV4cCI6MjAxODIyNDkxMH0.e5p-IFHxbYFOuc-wW_r7GVUYT63p7-CRHFtuRMLTARA"
supabase: Client = create_client(url, key)

def extract_data(content, file_name, keywords_list, coefficients):
    # if file_name.lower().endswith('.pdf'):
    #     # doc = fitz.open(file_path)
    #     content = ''.join(page.get_text() for page in fitz.open(file_path))
    # elif file_name.lower().endswith('.docx'):
    #     try:
    #         content = docx2txt.process(file_path)
    #     except Exception as e:
    #         return None
    # else:
    #     # Unsupported file format
    #     return None
    
    # Extract keywords
    keyword_counts = {keyword.lower(): 0 for keyword in keywords_list}

    lowercase_content = content.lower()
    compiled_patterns = [re.compile(r'\b{}\b'.format(re.escape(keyword.lower()))) for keyword in keywords_list]
    for i, pattern in enumerate(compiled_patterns):
        matches = pattern.finditer(lowercase_content)
        keyword_counts[keywords_list[i].lower()] = sum(1 for _ in matches) * int(coefficients[i])


    # Extract groups
    groups_index = content.find("groups")
    groups = ""
    if groups_index != -1:
        groups = content[groups_index:]
    
    return keyword_counts, groups

def process_file(args):
    file_path, file_name, keywords, coefficients = args
    file_keywords, groups = extract_data(file_path, file_name, keywords, coefficients)

def thread_function(list, db_folder_path, keywords, coefficients):
    for file1 in list:
        # print(file1)
        file_path = os.path.join(db_folder_path, file1)
        file_keywords, groups = extract_data(file_path, file1, keywords, coefficients)

    
def index(request):
    if request.method == 'POST':
        # files = request.FILES.getlist('files')
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
                
        start_time = time.time()
        
        resumes = Resume.objects.filter(content__contains=keywords[0])
        for value in keywords[1:]:
            resumes = resumes | Resume.objects.filter(content__contains=value)

        for resume in resumes:
            # file_path = os.path.join(db_folder_path, file4)
            file_keywords, groups = extract_data(resume.content, resume.title, keywords, coefficients)
            if(file_keywords is not None):
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

                if(total_count > 1):
                    filtered_files.append(
                        {
                            "file": resume.title,
                            "keyword1_total": file_keywords[keywords[0]],
                            "keyword2_total": file_keywords[keywords[1]],
                            "keyword3_total": file_keywords[keywords[2]],
                            "bonus": bonus[b],
                            "path": f"{path}/{resume.title}",
                            "total": total_count,
                            "person": resume.category,
                            "groups": groups,
                        }
                    )
        
        # Time
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'The operation took {elapsed_time} seconds to execute.')
            
        filtered_files = sorted(filtered_files, key=lambda x: x['total'], reverse=True)[:limit]
        return render(request, 'reader/index.html', {'file_names': filtered_files, "keywords": keywords})
    return render(request, 'reader/index.html')

from io import BytesIO

@csrf_exempt
def export_table_as_excel(request):
    file_names_json = request.POST.get('customers_data')
    
    file_names = json.loads(file_names_json)
    keywords = file_names.pop()

    # Create a new workbook
    workbook = Workbook()

    # Get the active sheet
    sheet = workbook.active

    # Add table headers
    headers = [
        'Salarié',
        'Pays',
        'Ville',
        'LinkedIn',
        'Path',
        keywords["keyword1"],
        keywords["keyword2"],
        keywords["keyword3"],
        'Bonus',
        'Total',
        'Groupes',
    ]
    sheet.append(headers)
    
    # Add table data
    for file_name in file_names:
        file_split = file_name["file"].split(", ")
        name = file_split[-1].replace(".pdf", "").replace(".docx", "")
        row = [
            file_split[0],
            file_split[1],
            file_split[2],
            f"https://linkedin.com/in/{name}",
            file_name["path"].replace("file:///", "").replace("%20", " "),
            file_name["keyword1_total"],
            file_name["keyword2_total"],
            file_name["keyword3_total"],
            file_name["bonus"],
            file_name["total"],
            file_name["groups"],
        ]
        sheet.append(row)

    # Save workbook to BytesIO
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Create a response with the BytesIO content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mytable.xlsx'
    response.write(buffer.read())

    return response

def copy_files_to_new_folder(files):
    try:
        destination_folder = os.path.join(settings.BASE_DIR, 'export')

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for file_record in files:
            path = file_record["path"].replace("http://127.0.0.1:8000", "")
            decoded_file_path = urllib.parse.unquote(path).replace("file:///", "")
            destination_file = os.path.join(destination_folder, file_record["file"])

            if os.path.exists(rf"{decoded_file_path}"):
                shutil.copy(decoded_file_path, destination_file)

        print("Files copied successfully.") 
    except Exception as e:
        print("Error copying files = ", e)
        
def add_cv(request):
    if request.method == "POST":
        # files = request.FILES.getlist('files')
        path = request.POST.get('path', '')
        files = os.listdir(path)
        progress = 0
        total = len(files)
        for file in files:
            if (((progress/total) * 100) % 10 == 0):
                print("Progress:", (progress/total) * 100, "%")
            if not Resume.objects.filter(title=file).exists():
                if file.lower().endswith(('.pdf', '.docx')):
                    category = file.split(", ")[0]
                    try:
                        # Save the file to a temporary location
                        file_path = os.path.join(path, file)
                        with open(file_path, 'rb') as source_file, tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            for chunk in iter(lambda: source_file.read(4096), b''):
                                temp_file.write(chunk)
                            temp_file_path = temp_file.name
                            # print(temp_file_path)
                            
                        content = read_file(temp_file_path, file.lower())
                        
                        resume = Resume(
                            title=file,
                            content=content,
                            category=category
                        )
                        resume.save()
                            
                    except Exception as e:
                        print(e)
            progress += 1
        return render(request, 'reader/add.html', {'message': "success",})
    return render(request, 'reader/add.html')