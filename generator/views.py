from ipaddress import IPv4Address, IPv6Address
from django.shortcuts import render
from validate_email import validate_email

def email_generator(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company = request.POST.get("company")

        valid_email = ""

        emails = generate_email_patterns(first_name, last_name, company)

        for email in emails:
            is_valid = validate_email(
            email_address=email,
            check_format=True,
            check_blacklist=True,
            check_dns=False,
            dns_timeout=10,
            check_smtp=True,
            smtp_timeout=10,
            smtp_helo_host='my.host.name',
            smtp_from_address='michael_taieb@hotmail.com',
            smtp_skip_tls=False,
            smtp_tls_context=None,
            smtp_debug=False,
            address_types=frozenset([IPv4Address, IPv6Address]))

            if(is_valid):
                print("Valid email = ", email)
                valid_email = email
                break
        
        return render(request, 'generator/index.html', {'emails': emails, "valid": valid_email}) 
    
    return render(request, 'generator/index.html')

def generate_email_patterns(first_name, last_name, company):
    patterns = []
    
    # Append different combinations of first name and last name
    patterns.append(f"{first_name.lower()}@{company.lower()}")
    patterns.append(f"{last_name.lower()}@{company.lower()}")
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
