from django.shortcuts import render

def email_generator(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company")

        emails = generate_email_patterns(first_name, last_name, company)
        return render(request, 'generator/index.html', {'emails': emails}) 
    
    return render(request, 'generator/index.html')

def generate_email_patterns(first_name, last_name, company):
    patterns = []
    
    # Append different combinations of first name and last name
    patterns.append(f"{first_name.lower()}{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()}.{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()}_{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()}{last_name.lower()[0]}@{company.lower()}")
    patterns.append(f"{first_name.lower()}_{last_name.lower()[0]}@{company.lower()}")

    # Append different combinations of last name and first name
    patterns.append(f"{last_name.lower()}{first_name.lower()}@{company.lower()}")
    patterns.append(f"{last_name.lower()}.{first_name.lower()}@{company.lower()}")
    patterns.append(f"{last_name.lower()}_{first_name.lower()}@{company.lower()}")
    patterns.append(f"{last_name.lower()}{first_name.lower()[0]}@{company.lower()}")
    patterns.append(f"{last_name.lower()}_{first_name.lower()[0]}@{company.lower()}")

    # Append other common patterns
    patterns.append(f"{first_name.lower()[:1]}{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()[0]}{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()[:1]}.{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()[0]}.{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()[:1]}_{last_name.lower()}@{company.lower()}")
    patterns.append(f"{first_name.lower()[0]}_{last_name.lower()}@{company.lower()}")

    return patterns
