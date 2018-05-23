#!C:/Users/Anjana/Anaconda3/python.exe

import search_engine as se
Max_Count = 50
def search(string):
	url_list = se.search_engine_final_main(string, Max_Count)
	return url_list