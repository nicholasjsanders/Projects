from http.server import BaseHTTPRequestHandler, HTTPServer

from pandas import DataFrame
from pandas.io.parsers import TextFileReader
from typing import Any, Union
from urllib import parse
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os import listdir
import string





def annotation(keyword, NER):
    """For a given keyword and NER class extracts all the sentences in which keyword appears as that NER class. Returns a list of sentences"""
    annotation_dir = "./Final_Annotation_.csv"
    annotation_data = pd.read_csv(annotation_dir, sep=",")
    sentences = set()
    output_set = set()
    NER = NER.capitalize()
    invalid_start = set(['"',"'"])

    #output_set = set()

    for sentence in annotation_data['Sentence']:
        for char in sentence.split(' '):
            NER_column = annotation_data[NER]
            for NER_tag in NER_column:
                if type(NER_tag) != float:
                    NER_tag = NER_tag.replace("@", "")
                    for new_char in NER_tag.split("#"):
                        if new_char == keyword:
                            sentences.add(sentence)

    for sentence in sentences:
        for char in sentence.split(' '):
            if keyword in char and not char.endswith('인') and char[0] not in invalid_start:
                if char[0] in invalid_start and char[-1] not in invalid_start:
                    continue
                if char[0] not in keyword and char[0] not in string.punctuation:
                    continue
                else:
                   new_char = "<span class='highlight'>" + keyword +"</span>"
                   res = sentence.replace(keyword, new_char)
                   output_set.add(res)
    return output_set

def news_corpus():
    """
    Load the whole corpus, store all the body content into a list for keyword search.
    """
    news_directory = "./Naver_news/"
    files = [f for f in listdir(news_directory) if f.endswith("txt")]
    news_body = dict()
    for f in files:
        with open(news_directory + f, encoding = 'utf-8') as news:
            raw = news.readlines()
            if raw[6] == '\t\n': # some news has its body content starting with an empty line
                body = raw[7]
            else: 
                body = raw[6] # news without an empty line over its body content
        news_body[f] = body
    return news_body


def get_news(keyword, corpus = news_corpus()):
    """
    For a given keyword, search over the whole corpus and extract the top 10 relevant articles
    based on keyword frequency.
    """
    to_search = []
    if " " in keyword: # check if there are multiple keywords in the query
        to_search.extend(word for word in keyword.split(" "))
    else:
        to_search.append(keyword)
    
    matches = dict()
    for filename, news in corpus.items():
        if all(word in news for word in to_search): # allow to search for multiple keywords
            count = 0
            for word in to_search:
                count += news.count(word) 
            matches[filename] = count 
    
    top_relevant = []

    for idx in sorted(matches, key=matches.get, reverse=True):
        top_relevant.append(idx)
    print(top_relevant[:10])
    return top_relevant[:10]


class MyWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        query = parse.urlsplit(self.path).query
        query_dict = parse.parse_qs(query)
        
        invalid_start = set(['"',"'"])

        if "frontend.css" in self.path:
            self.send_header('Content-type','text/css; charset=utf-8')
            self.end_headers()
            f = open("frontend.css", encoding="utf-8")
            html = f.read()
            f.close()
            self.wfile.write(html.encode("utf-8"))
        elif "frontend.js" in self.path:
            self.send_header('Content-type','text/javascript; charset=utf-8')
            self.end_headers()
            f = open("frontend.js", encoding="utf-8")
            html = f.read()
            f.close()
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/":
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            f = open("frontend.html", encoding="utf-8")
            html = f.read()
            f.close()
            self.wfile.write(html.encode("utf-8"))
            
        elif 'text' in query_dict.keys():
            if {'organization', 'person', 'place'} & set(query_dict.keys()) == set(): 
                self.send_header('Content-type','text/html; charset=utf-8')
                self.end_headers()
                result = get_news(query_dict['text'][0])
                separation = "-" * 225
                for n in result:
                    news_directory = "./Naver_news/"
                    f = open(news_directory+n, encoding = 'utf-8')
                    news = f.readlines()
                    f.close()
                    for line in news:
                        if not line.startswith("URL"):
                            self.wfile.write(b"<html>" + line.encode("utf-8") +  b"</html>")
                            self.wfile.write(b"<br />" + b"<br />")
                    self.wfile.write(b"<html>" + separation.encode("utf-8") +  b"</html>")
                    self.wfile.write(b"<br />" + b"<br />")
                
            if {'organization', 'person', 'place'} & set(query_dict.keys()) == {'organization'}:
                if query_dict['organization'] == ['on']:
                    keyword = query_dict['text'][0]
                    NER_class = 'organization'
                    result = annotation(keyword, NER_class)

                    top_result = get_news(query_dict['text'][0])
                    separation = "-" * 225
                    header = 'Source Annotated Sentence:\n'
                    
                if len(result) > 0:
                    for sent in result:
                        self.wfile.write(b"<html>" + header.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<html>" + sent.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")
                        
                    for n in top_result:
                        news_directory = "./Naver_news/"
                        f = open(news_directory+n, encoding = 'utf-8')
                        news = f.readlines()
                        f.close()

                        for line in n:
                            if not line.startswith("URL"):
                                for line in news:
                                    new_line = line
                                    if not line.startswith("URL"):
                                        for char in line.split(' '):
                                            if keyword in char and not char.endswith('인') and char[0] not in invalid_start:
                                                if char[0] in invalid_start and char[-1] not in invalid_start:
                                                    continue
                                                if char[0] not in keyword and char[0] not in string.punctuation:
                                                    continue
                                                else:
                                                    new_char = "<span class='highlight'>" + keyword +"</span>"
                                                    new_line = new_line.replace(keyword, new_char)
                                        self.wfile.write(b"<html>" + str(new_line).encode("utf-8") +  b"</html>")
                                        self.wfile.write(b"<br />" + b"<br />")    
                        self.wfile.write(b"<html>" + separation.encode("utf-8") +  b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")


            if {'organization', 'person', 'place'} & set(query_dict.keys()) == {'person'}:
                if query_dict['person'] == ['on']:
                    keyword = query_dict['text'][0]
                    NER_class = 'person'
                    result = annotation(keyword, NER_class)

                    top_result = get_news(query_dict['text'][0])
                    separation = "-" * 225
                    header = 'Source Annotated Sentence:\n'
                    
                if len(result) > 0:
                    for sent in result:
                        self.wfile.write(b"<html>" + header.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<html>" + sent.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")
                        
                    for n in top_result:
                        news_directory = "./Naver_news/"
                        f = open(news_directory+n, encoding = 'utf-8')
                        news = f.readlines()
                        f.close()

                        for line in n:
                            if not line.startswith("URL"):
                                for line in news:
                                    new_line = line
                                    if not line.startswith("URL"):
                                        for char in line.split(' '):
                                            if keyword in char and not char.endswith('인') and char[0] not in invalid_start:
                                                if char[0] in invalid_start and char[-1] not in invalid_start:
                                                    continue
                                                if char[0] not in keyword and char[0] not in string.punctuation:
                                                    continue
                                                else:
                                                    new_char = "<span class='highlight'>" + keyword +"</span>"
                                                    new_line = new_line.replace(keyword, new_char)
                                        self.wfile.write(b"<html>" + str(new_line).encode("utf-8") +  b"</html>")
                                        self.wfile.write(b"<br />" + b"<br />")    
                        self.wfile.write(b"<html>" + separation.encode("utf-8") +  b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")


            if {'organization', 'person', 'place'} & set(query_dict.keys()) == {'place'}:
                if query_dict['place'] == ['on']:
                    keyword = query_dict['text'][0]
                    NER_class = 'place'
                    result = annotation(keyword, NER_class)

                    top_result = get_news(query_dict['text'][0])
                    separation = "-" * 225
                    header = 'Source Annotated Sentence:\n'
                    
                if len(result) > 0:
                    for sent in result:
                        self.wfile.write(b"<html>" + header.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<html>" + sent.encode("utf-8") + b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")
                        
                    for n in top_result:
                        news_directory = "./Naver_news/"
                        f = open(news_directory+n, encoding = 'utf-8')
                        news = f.readlines()
                        f.close()

                        for line in n:
                            if not line.startswith("URL"):
                                for line in news:
                                    new_line = line
                                    if not line.startswith("URL"):
                                        for char in line.split(' '):
                                            if keyword in char and not char.endswith('인') and char[0] not in invalid_start:
                                                if char[0] in invalid_start and char[-1] not in invalid_start:
                                                    continue
                                                if char[0] not in keyword and char[0] not in string.punctuation:
                                                    continue
                                                else:
                                                    new_char = "<span class='highlight'>" + keyword +"</span>"
                                                    new_line = new_line.replace(keyword, new_char)
                                        self.wfile.write(b"<html>" + str(new_line).encode("utf-8") +  b"</html>")
                                        self.wfile.write(b"<br />" + b"<br />")    
                        self.wfile.write(b"<html>" + separation.encode("utf-8") +  b"</html>")
                        self.wfile.write(b"<br />" + b"<br />")


        return
    
if __name__ == "__main__":
    http_port=9997
    server = HTTPServer(('localhost', http_port),  MyWebServer)
    server.serve_forever()

