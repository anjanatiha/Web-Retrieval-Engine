#!C:/Users/Anjana/Anaconda3/python.exe
from django.shortcuts import render
from query import search

def index(request):
	return render(request, 'personal/home.html', )
	
def contact(request):
	return render(request, 'personal/basic.html', {'content': ['If you would like to contact me, email me at', 'atiha@memphis.edu']})
	
def submit(request):
	info=request.POST.get('info')
	url_list = search(info)
	return render(request, 'personal/home.html', {'search_string': url_list})
	
	