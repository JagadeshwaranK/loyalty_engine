import json
import os
import sys
from io import BytesIO

if sys.path[0] != os.path.dirname(os.path.dirname(os.path.abspath(__file__))):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty_engine.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def handler(event, context):
    """
    Vercel serverless function handler for Django WSGI app.
    """
    # Get the origin from the request
    origin = event.get('headers', {}).get('origin', '*')

    # Handle OPTIONS preflight request explicitly
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': '',
            'isBase64Encoded': False,
        }

    environ = {
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': event.get('headers', {}).get('x-forwarded-proto', 'http'),
        'wsgi.input': BytesIO(event.get('body', b'')),
        'wsgi.errors': sys.stderr,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
        'wsgi.run_once': False,
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': json.dumps(event.get('queryStringParameters', {})),
        'SERVER_NAME': event.get('headers', {}).get('host', ''),
        'SERVER_PORT': event.get('headers', {}).get('x-forwarded-port', '80'),
        'CONTENT_LENGTH': event.get('headers', {}).get('content-length', ''),
        'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
        'HTTP_ACCESS_CONTROL_ALLOW_ORIGIN': '*',  # Add this header to allow CORS
        'HTTP_ACCESS_CONTROL_ALLOW_METHODS': 'GET, POST, OPTIONS, PUT, DELETE',
        'HTTP_ACCESS_CONTROL_ALLOW_HEADERS': 'Content-Type, Authorization',
    }

    # Add headers
    for header, value in event.get('headers', {}).items():
        key = 'HTTP_%s' % header.upper().replace('-', '_')
        environ[key] = value

    status = [None]
    headers_list = [None]
    body = []

    def start_response(status_code, response_headers):
        # Add CORS headers to the response
        cors_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
        ]
        response_headers.extend(cors_headers)
        status[0] = status_code
        headers_list[0] = dict(response_headers)
        return lambda x: None

    def write(data):
        body.append(data)

    application(environ, start_response)

    return {
        'statusCode': int(status[0].split()[0]) if status[0] else 200,
        'headers': headers_list[0] or {},
        'body': ''.join([b.decode('utf-8') for b in body]) if body else '',
        'isBase64Encoded': False
    }
