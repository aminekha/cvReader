import os, docx2txt
from supabase import create_client, Client

url: str = "https://osijypnfegeucpobzrwb.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zaWp5cG5mZWdldWNwb2J6cndiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI2NDg5MTAsImV4cCI6MjAxODIyNDkxMH0.e5p-IFHxbYFOuc-wW_r7GVUYT63p7-CRHFtuRMLTARA"
supabase: Client = create_client(url, key)

def extract_content(file_path, file_name):
    content = docx2txt.process(file_path)
    category = file_name.split(", ")[0]
    return {"content": content.lower(), "category": category, "title": file_name}

def chunk_list(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def add_new_resumes():
    files_to_add = list()
    db_folder_path = "C:/Users/amine/OneDrive/Documents/LinkedIn-robot/sandrine"
    docx_files = [f for f in os.listdir(db_folder_path) if f.endswith(".docx")]
    
    for file in docx_files:
        file_path = os.path.join(db_folder_path, file)
        files_to_add.append(
            extract_content(file_path, file)
        )
    print(len(files_to_add))
    chunk_size = 100
    result = chunk_list(files_to_add, chunk_size)
    for chunk in result:
        supabase.table('resumes').insert(chunk).execute()
    return

add_new_resumes()