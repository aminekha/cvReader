import os
import tempfile
import spacy
import PyPDF2
import docx2txt

from django.shortcuts import render


countries = ["France", "Londres"]
france_cities = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
    "Rennes", "Reims", "Saint-Étienne", "Toulon", "Le Havre", "Clermont-Ferrand", "Limoges", "Tours", "Amiens",
    "Metz", "Perpignan", "Besançon", "Orléans", "Mulhouse", "Caen", "Nancy", "Rouen", "Argenteuil", "Saint-Denis",
    "Roubaix", "Tourcoing", "Montreuil", "Avignon", "Asnières-sur-Seine", "Nanterre", "Poitiers", "Versailles",
    "Courbevoie", "Créteil", "Pau", "Colombes", "Vitry-sur-Seine", "Aulnay-sous-Bois", "Marseille 10", "Marseille 11",
    "Marseille 12", "Marseille 13", "Marseille 14", "Marseille 15", "Marseille 16"
]

# List of the biggest 50 cities in London (approximate population)
london_cities = [
    "London", "Croydon", "Bromley", "Barnet", "Enfield", "Harrow", "Wandsworth", "Greenwich", "Lewisham", "Hackney",
    "Haringey", "Newham", "Redbridge", "Havering", "Hillingdon", "Hounslow", "Kingston upon Thames", "Merton",
    "Sutton", "Bexley", "Brent", "Ealing", "Hammersmith and Fulham", "Harrow", "Hillingdon", "Hounslow", "Kensington and Chelsea",
    "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham", "Richmond upon Thames", "Southwark", "Sutton",
    "Tower Hamlets", "Waltham Forest", "Wandsworth", "Westminster"
]

# Combine the city lists
cities = france_cities + london_cities
# Load spaCy's English model
# nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('fr_core_news_sm')

def extract_data(file_path, file_name, keywords_list):
    if file_name.lower().endswith('.pdf'):
        # Extract data from PDF
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text()
    elif file_name.lower().endswith('.docx'):
        # Extract data from DOCX
        content = docx2txt.process(file_path)
    else:
        # Unsupported file format
        return None

    # Process the content using spaCy
    doc = nlp(content)

    # Extract relevant information (country, city, age)
    country = None
    city = None
    age = None

    for ent in doc.ents:
        if ent.label_ == 'LOC' and len(ent.text) > 4:
            if not country and ent.text in countries:
                country = ent.text
            elif not city and ent.text in cities:
                city = ent.text
        elif ent.label_ == 'CARDINAL' and not age:
            age = ent.text
    
    # Extract keywords
    keyword_counts = {keyword: 0 for keyword in keywords_list}

    for keyword in keywords_list:
        keyword_counts[keyword] = content.count(keyword)


    return country, city, age, keyword_counts


def index(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        country = request.POST.get('country', '')
        city = request.POST.get('city', '')
        age = request.POST.get('age', '')
        keywords = [keyword.strip() for keyword in request.POST.get('keywords', '').split(',') if keyword.strip()]

        filtered_files = []

        for file in files:
            if file.name.lower().endswith(('.pdf', '.docx')):
                # Save the file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                file_country, file_city, file_age, file_keywords = extract_data(temp_file_path, file.name, keywords)
                # print(file_country, file_city, file_age)
                print(file_keywords)

                # Rate the cv
                total_count = sum(file_keywords.values())

                # Give bonus if it has more than one keyword
                bonus = 0
                num_keywords_with_counts = sum(1 for count in file_keywords.values() if count > 0)  # Count the number of keywords with counts greater than 0
                if num_keywords_with_counts == 2:
                    bonus = 5
                elif num_keywords_with_counts == len(keywords):
                    bonus = 10

                total_count += bonus

                print(total_count)


                if(file_country):
                    if(file_country.lower() == country.lower()):
                        print(file.name)

                # Filtering based on extracted information
                if(file_country):
                    if country and country.lower() != file_country.lower():
                        os.remove(temp_file_path)
                        continue
                else:
                        os.remove(temp_file_path)
                        continue

                # if city and city != file_city:
                #     os.remove(temp_file_path)
                #     continue
                # if age and age != file_age:
                #     os.remove(temp_file_path)
                #     continue
                # if keywords and not all(keyword.lower() in [kw.lower() for kw in file_keywords] for keyword in keywords):
                #     os.remove(temp_file_path)
                #     continue

                filtered_files.append(
                    {
                        "file": file.name,
                        "total": total_count
                    }
                )
                os.remove(temp_file_path)

        print("filtered data = ", filtered_files)

        return render(request, 'reader/index.html', {'file_names': sorted(filtered_files, key=lambda x: x['total'], reverse=True)})

    return render(request, 'reader/index.html')