
# coding: utf-8

# In[120]:

'''
* Name        : Assignment6, pdf2text
* Course      : Inform Retrieval/Web Search
* Assignment  : Assignment 6
* Description : Collects 10, 000 documents from "www.memphis.edu" and preproces, then builds inverted index.
* Author      : Anjana Tiha
* Date        : 11.09.2017
* Comments    : Please use Anaconda editor
'''


# In[121]:

### Import modules

import urllib
from urllib.parse import urlsplit
import os, errno
import time
import operator 
import collections
import queue
from collections import OrderedDict
import shutil
import pickle
import requests
from bs4 import BeautifulSoup
import re
from nltk.stem.porter import PorterStemmer
from collections import deque


# In[122]:


# global Hashmaps, variables
stopwords = {}
inv_ind = {}
page_doc_map = {}
page_ref_count = {}
doc_count = 0
link_queue = queue.Queue()
last_doc_index = -1


# In[123]:


crawled_web_dir = "web_text_crawled"
crawled_web_dir_conv_need = "web_docs_crawled"
crawled_web_dir_preprocessed = "web_text_preprocessed"
output_web_dir = "output"

stopword_path = "english.stopwords.txt"

list_dir = [crawled_web_dir, crawled_web_dir_conv_need, crawled_web_dir_preprocessed]

url = "http://www.memphis.edu/"
domain = "memphis.edu"
#url = "http://www.cs.memphis.edu/~vrus/teaching/ir-websearch/"
#url = "http://www.cs.memphis.edu/"



# In[124]:


#Create/Delete/Load stop words/

#take input
def input_file_dir():
    url = input("Enter URL: ")  
    web_text_dir = input("Enter Directory Name For Saving Fetched Web Documents In Text Format: ")
    web_other_doc_dir = input("Enter Directory Name For Saving Fetched PDF/Other Documents: ")
    web_preprocessed_dir = input("Enter Directory Name For Saving Text Files After Preprocessing: ")
    web_output_dir = input("Enter Output Directory Name: ")
    stopword_path = input("Enter Path Of File Containg Stopwords: ")

    print("I will fetch web documents from -->"+url+"\nDocuments Will be fetched and parsed and saved in -->"+ web_text_dir + "\nPDF or Other Documents will be saved in --> "
      + web_other_doc_dir + "\nAfter preprocessing files will be saved in -->" + web_preprocessed_dir + "\nStop words are in file -->" + stopword_path)
    
    
# create one single directory
def create_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if(e.errno != errno.EEXIST):
            raise
    pass 


# create a list of directories
def create_directories(list_dir):
    for dir_i in list_dir:
        print(dir_i)
        create_directory(dir_i) 
        
# delete one single directory
def delete_directory(dir_name):
    if(os.path.isdir(dir_name)):
        try:
            shutil.rmtree(dir_name)
        except OSError as e:
            if(e.errno != errno.EEXIST):
                raise
        pass 

# delete a list of directories
def delete_directories(list_dir):
    for dir_i in list_dir:
        print(dir_i)
        delete_directory(dir_i)

        
#delete if file is empty
def delete_file(path):
    try:
        os.remove(path)
        return 1
    except OSError:
        return 0
    

#delete if file is empty
def delete_empty_file(path):
    if(os.path.getsize(path) == 0):
        try:
            print("deleting: "+ path)
            os.remove(path)
            print("deleted: "+ path)
            return 1
        except WindowsError:
            return -1
    else:
        return 0

    
#save text in given path with given file name
def saveText(text, dir_path, file_name):
    text_file = open(dir_path+"\\"+file_name, "w")
    text_file.write(text)
    
    
#load stop words from given file path
def load_stopwords(filepath):
    with open(filepath, 'r') as content_file:
                for line in content_file:
                    line = line.strip()
                    stopwords[line] = 1

                    
# save object in pickle
def save_obj(obj, name, key_or_val, order):
    if(key_or_val == "key" and order == "auto"):
        sorted_x = sorted(obj.items(), key=operator.itemgetter(0))
    elif(key_or_val == "key" and order == "reverse"):
        sorted_x = sorted(obj.items(), key=operator.itemgetter(0), reverse=True)
    elif(key_or_val == "value" and order == "auto"):
        sorted_x = sorted(obj.items(), key=operator.itemgetter(1))
    elif(key_or_val == "value" and order == "reverse"):
        sorted_x = sorted(obj.items(), key=operator.itemgetter(1), reverse=True)
    pickle.dump( obj, open( name + ".p", "wb" ) )


#load object from pickle file
def load_obj(name):
    file = open(name,'rb')
    object_file = pickle.load(file)
    return object_file
  
        
#print elapsed time in hh:mm:ss format
def format_time(start_time, end_time):
    elsapsed_time = end_time - start_time
    hr = int(elsapsed_time)//3600
    min_ = (int(elsapsed_time) - (hr * 3600))/60
    sec = int(elsapsed_time) - hr * 3600 - min_ * 60
    print("HH:Min:Sec > " + str(hr) +" hr " + str(min_) + " min "+ str(sec) + "sec")
    


# In[125]:


#print hashmap sorted by key or value
def print_hashmap(hashmap, type_s):
    if(type_s == 'key'):
        hashmap = OrderedDict(sorted(hashmap.items(), key=lambda t: t[0]))
    else:
        hashmap = OrderedDict(sorted(hashmap.items(), key=lambda t: t[1], reverse=True))
    for i in hashmap:
        print(i, " : ", hashmap[i])
        


# In[126]:


# URLS and Text preprocessing functions

# remove fragment identifier #
def remove_url_frag_id(url):
    url = url.split('#')[0]
    return url


# remove http or https from webpage urls
def strip_http_s(url):    
    url = url.replace("https://","")
    url = url.replace("http://","")
    return url


# check if url is in domain name
def check_if_in_domain(url, domain):
    if(domain in url):
        return 1
    else:
        return 0
    
    
#fix URL with same name "/"
def fix_url(url):
    webpage_url = url.rsplit('/', 1)[0]
    return webpage_url  


#check whether URL is valid
def check_valid_URL(url):
    url_reg = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    is_valid = url_reg.match(url)
    return is_valid


#get extention of link to check the link type(.txt, .pdf, or html) 
def get_page_extention(url):
    weblink_extention = url.rsplit('.', 1)[-1]
    return weblink_extention


#remove hyperlink from web page text for preprocessing
def remove_hyper_link(text):
    URLless_string = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
    return URLless_string




#remove special character in single line
def remove_special_char(line):
    line = re.sub('[^a-zA-Z]+', ' ', line)
    return line

        
# get all the url/links to other pages from current pages        
def get_all_links(html):
    links_list = []
    soup = BeautifulSoup(html)
    links = soup.find_all('a')

    for tag in links:
        link = tag.get('href',None)
        if link is not None:
            links_list.append(link)
    return links_list   



# In[127]:


# converts from pdf txt and html

# convert pdf to text using "pdf2text"
def pdf_to_text(input_pdf, output_dir, file_name):
    os.system(("pdftotext %s %s") %( input_pdf, output_dir+"//"+file_name))

    
#import text from url/single web link and convert to text and save in directory
def import_convert_preprocess_pdf(url, pdf_directory, output_dir):
    global doc_count
    global crawled_web_dir
    print("Extracting PDF............................................................................")
    url_map_name = strip_http_s(url)
    print(url_map_name)
    if(url_map_name not in page_doc_map):
        page_doc_map[url_map_name] = -1
        page_ref_count[url_map_name] = 1
        
        try:
            doc_count_temp = doc_count + 1
            book_name = str(doc_count_temp) + ".pdf"
            book_path = pdf_directory + "/" + book_name
            a = requests.get(url, stream=True)
            
            with open(book_path, 'wb') as book:
                book.write( url + "\n")
                
                for block in a.iter_content(512):
                    if not block:
                        break
                    book.write(block)

            file_name = str(doc_count_temp)+".txt"
            pdf_to_text(book_path, output_dir, file_name)
            
            
            file_path = crawled_web_dir +"\\" + file_name

            #checks if number of token > 50
            is_valid_for_indexing = preprocess_one_doc(crawled_web_dir, file_name, crawled_web_dir_preprocessed)

            if(is_valid_for_indexing != 1):
                delete_file(file_path)
                page_doc_map[url_map_name] = -2

            else:
                doc_count = doc_count + 1
                page_doc_map[url_map_name] = doc_count
                page_ref_count[url_map_name] = 1
        
        except IOError:
            page_doc_map[url_map_name]= -1
            return ""
    else:
        page_ref_count[url_map_name] = page_ref_count[url_map_name] + 1
        
        
#remove all html and scripting
def clean_html(html_text):
    global crawled_web_dir
    soup = BeautifulSoup(html_text)

    # removes scripts and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # get text
    clean_text = soup.get_text()
    return clean_text


# preprocess files in a folder to remove punctuations, digits, special characters, url/web links
# removes stop words given in file
# convert to origin word/ do stemming

def preprocess_one_doc(input_dir, input_filename, output_dir):
    ps = PorterStemmer()
    input_file_path = input_dir + "\\"+ input_filename
    text = ""
    count = 0
    try:
        with open(input_file_path, 'r') as content_file:
            for line in content_file:
                if(line in ['\n', '\r\n','\r']):
                    continue
                line = line.strip()
                line = remove_hyper_link(line)
                line = remove_special_char(line)
                line = line.lower()
                line = re.sub(' +',' ',line)
                words = line.split(" ")

                for word in words:
                    word = word.strip()
                    word = remove_special_char(word)
                    word = re.sub(' +','',word)
                    
                    if word not in stopwords and word != " " and word != "":
                        stem_word = ps.stem(word)
                        text = text + " " + stem_word
                        count = count + 1
            if(count > 50):
                saveText(text, output_dir, input_filename)
                return 1
            else:
                return 0
    except:
        print("Error in : " + filepath)
        return 0
            
        
        

# import text from single web page
def fetch_extract_html_txt(url):
    global doc_count
    global domain
    
    if(check_if_in_domain(url, domain) == 0):
        return ""
    url_map_name = strip_http_s(url)
    
    if(url_map_name in page_doc_map):
        page_ref_count[url_map_name] = page_ref_count[url_map_name] + 1
        return ""
    
    else:
        page_doc_map[url_map_name] = -1
        page_ref_count[url_map_name] = 1
        
        try: 
            html = urllib.request.urlopen(url) 
            html_text = html.read()  
            
            if(html_text == ""):
                return ""
            
            clean_text = clean_html(html_text)
            doc_count = doc_count + 1
            page_doc_map[url_map_name] = doc_count
            clean_text = url + "\n" + clean_text 
            saveText(clean_text, crawled_web_dir, str(doc_count)+".txt")
            
            path = crawled_web_dir +"\\" + str(doc_count)+".txt"

            #checks if number of token >= 50
            is_valid_for_indexing = preprocess_one_doc(crawled_web_dir, str(doc_count)+".txt", crawled_web_dir_preprocessed)

            if(is_valid_for_indexing != 1):
                delete_file(path)
                page_doc_map[url_map_name] = -2
                doc_count = doc_count - 1
                
            links = get_all_links(html_text)
            return links
        
        except IOError:
            page_doc_map[url_map_name]= -1
            return ""


# In[128]:


# crawl through whole website
def webpage_crawler(doc_size):
    global doc_count 
    global link_queue
    global last_doc_index
    
    if(doc_count % 10 == 0 and last_doc_index != doc_count):
        print("Extracted Documents: " + str(doc_count))
        last_doc_index = doc_count

    url = link_queue.get()
    links = []
    
    try:
        link_extention = get_page_extention(url)
        
        if(link_extention == "" or link_extention == "ppt"):
            a=1

        elif(link_extention == "pdf"):
            link_queue.put(link_q)
            import_convert_preprocess_pdf(url, crawled_web_dir_conv_need, crawled_web_dir)
            
        elif(link_extention == "txt"):
            fetch_extract_html_txt(url)
            
        else:
            url = remove_url_frag_id(url)
            links = fetch_extract_html_txt(url)

    except Exception:
        pass  
    
    if(links):
        for link in links:
            try:
                link_extention = get_page_extention(link)
                if(link_extention == "" or link_extention == "ppt"):
                    a=1

                elif(link_extention == "pdf"):
                    url_new = fix_url(url)
                    pdf_url = url_new  + link
                    link_queue.put(pdf_url)

                elif(link_extention == "txt"):
                    if(check_valid_URL(link)):
                        link_queue.put(link)
                        
                    else:
                        url_new = fix_url(url)
                        modified_link = url_new + link  
                        
                        if(check_valid_URL(modified_link)):
                            link_queue.put(modified_link)
                else:
                    is_valid = check_valid_URL(link)
                    
                    if(is_valid):
                        modified_link = fix_url(url)
                        link_queue.put(modified_link)
                    else:
                        #modified_link = fix_url(url)
                        modified_link = modified_link + link 
                        
                        if(check_valid_URL(modified_link)):
                            link_queue.put(modified_link)        
            except Exception:
                pass  

            
def website_crawler(doc_size):
    while(doc_count <= doc_size):
        if(link_queue.empty()):
            return
        webpage_crawler(doc_size)

    save_obj(page_doc_map, "url_doc_map", "value", "auto")
    save_obj(page_ref_count, "page_ref_count", "value", "reverse")

    


# In[129]:


#build inverted index for all files present in preprocessed file directory
def build_inv_file(path):
    dirs = os.listdir( path )
    i = 0 
    
    for file in dirs:
        filepath = path + "\\"+ file
        text = ""
        i = i + 1
        
        if(i % 50 == 0):
            print("Building inverse document index for file no: "+str(i))
            
        try:
            with open(filepath, 'r') as content_file:
                for line in content_file:
                    line = line.strip()
                    words = line.split(" ")
                    
                    for word in words:
                        if word not in inv_ind:
                            doc_ind = {}
                            doc_ind[str(file)[:-4]] = 1
                            doc_ind["Total Count"] = 1
                            inv_ind[word] = doc_ind
                            
                        else:
                            doc_ind = inv_ind[word]
                            
                            if file not in doc_ind:
                                doc_ind[str(file)[:-4]] = 1
                                doc_ind["Total Count"] = doc_ind["Total Count"] + 1
                                inv_ind[word] = doc_ind
                                
                            else:
                                doc_ind[str(file)[:-4]] = doc_ind[str(file)[:-4]] + 1
                                doc_ind["Total Count"] = doc_ind["Total Count"] + 1
                                inv_ind[word] = doc_ind 
        
        except:
            print("Error in : " + filepath)
                

#print inverted index of all terms present
def print_inv_index():
    for key in sorted(inv_ind):
        print(key)
        for key2 in sorted(inv_ind[key]):
            print(str(key2) + " : " +  str(inv_ind[key][key2]))
        print("----------------------------------------------------------------")


# In[130]:


start_time = time.time()


# In[131]:


load_stopwords(stopword_path)

delete_directories(list_dir)

create_directories(list_dir)

link_queue.put(url)

doc_size = 10000

website_crawler(doc_size)


# In[132]:


format_time(start_time, time.time())


# In[133]:


build_inv_file(crawled_web_dir_preprocessed)
#save_obj(inv_ind, "inv_ind", "value", "reverse")
#print_inv_index()


# In[ ]:



