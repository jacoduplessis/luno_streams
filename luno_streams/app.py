from wsgiref.simple_server import make_server
import pathlib


def get_server(address, port):

    def app(environ, start_response):

        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return open(pathlib.Path(__file__).parent / 'app.html', 'rb')

    return make_server(address, port, app)

