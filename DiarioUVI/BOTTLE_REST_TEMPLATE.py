import bottle
from bottle import request, response
from bottle import post, get, put, delete


@post('/posturl')
def creation_handler():
    '''Handles creation'''
    pass

@get('/posturl')
def listing_handler():
    '''Handles listing'''
    pass

@put('/posturl/<whatever>')
def update_handler(name):
    '''Handles updates'''
    pass

@delete('/posturl/<whatever>')
def delete_handler(name):
    '''Handles deletions'''
    pass

app = application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000)