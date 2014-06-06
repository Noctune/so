#!/usr/bin/python

import sys, zlib, json, string, thread, subprocess, time, locale, cgi
from urllib import urlencode, quote
from urllib2 import Request, urlopen
from urlparse import urlparse, parse_qsl
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def stackquery(path, query):
    url = 'http://api.stackexchange.com/2.2/' + path + '?' + urlencode(query)
    
    # Stack Overflow always returns compressed data, even if Accept-Encoding
    # does not include it
    response = urlopen(Request(url, headers = {"Accept-Encoding": "gzip"}))
    data = response.read()
    
    if response.info()['Content-Encoding'] and \
       'gzip' in response.info()['Content-Encoding']:
        data = zlib.decompress(data, zlib.MAX_WBITS | 32)
    
    return json.loads(data)

class StackHandler(BaseHTTPRequestHandler):
    def write(self, string):
        self.wfile.write(string.encode('utf8'))
    
    def header(self, title, response = 200):
        self.send_response(response)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.write('<!DOCTYPE HTML><html><head><title>{}</title><body>'
                   .format(title))
    
    def index(self, query):
        self.header('Index')
        self.write('<form action="search">'
                   'Search query: <input type="text" name="q"/>'
                   '<input type="submit"/>'
                   '</form>')
    
    def search(self, query):
        self.header('All posts containing \'' + cgi.escape(query['q']) + '\'')
        templates = {
            'question': '<h2><a href="/question?id={question_id}">'
                        'Q: {title}</a></h2><p>{excerpt}</p>',
            'answer':   '<h2><a href="/question?id={question_id}'
                        '#{answer_id}">A: {title}</a></h2><p>{excerpt}</p>'}
        
        results = stackquery('search/excerpts', query)
        
        for i in results['items']:
            
            # We don't need no stinking CSS
            i['excerpt'] = i['excerpt'].replace('span class="highlight"', 'b')
            
            self.write(templates[i['item_type']].format(**i))
    
    
    def question(self, query):
        query['filter'] = 'withBody'
        query['sort'] = 'votes'
        question = stackquery('questions/' + query['id'], query)['items'][0]
        answers  = stackquery('questions/' + query['id'] + '/answers', query)
        self.header(question['title'])
        self.write('<h1>{title}</h1>{body}'.format(**question))
        
        for i in answers['items']:
            creation_time = time.gmtime(i['creation_date'])
            creation_string = time.strftime('%b %d at %X', creation_time)
            self.write('<hr>{body}<p align="right">'.format(**i))
            self.write('{display_name}, {}</p>'
                       .format(creation_string, **i['owner']))
        
    def do_GET(self):
        handlers = {
            '/':         self.index,
            '/search':   self.search,
            '/question': self.question}
        
        url = urlparse(self.path)
        
        if url.path in handlers:
            query = dict(parse_qsl(url.query))
            query['site'] = 'stackoverflow'
            handlers[url.path](query)
            
            self.write('</body></html>')
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.write('File not found')
    
    # Log messages are silenced, as they will mess up Lynx
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    port = 8484
    
    server = HTTPServer(('localhost', port), StackHandler)
    thread.start_new_thread(server.serve_forever, ())
    
    query = '' if len(sys.argv) == 1 else \
            'search?q=' + string.join(map(quote, sys.argv[1:]), '+')
    
    subprocess.check_call(['lynx', 'localhost:' + str(port) + '/' + query])
