from django.shortcuts import render

def index(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        file_names = [file.name for file in files]
        return render(request, 'reader/index.html', {'file_names': file_names})
    
    return render(request, 'reader/index.html')
