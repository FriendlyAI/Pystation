from http.server import *


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('localhost', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run()

# requests.put('http://localhost:8000/main.mp3', data={'audio/mpeg': chunk}) ? might work
# requests.put('http://localhost:8000/main.mp3',
#              headers={'content-type': 'audio/mpeg', 'content': chunk}) ? might work also
