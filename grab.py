#!/usr/bin/env python3
import os
import requests
import requests.cookies
import sys

"""
    Environment variables:

    CONFLUENCE_HOST=http://confluence.acme.com
    CONFLUENCE_DOMAIN=confluence.acme.com
    CONFLUENCE_PATH=/  # optional
    CONFLUENCE_JSESSIONID=GET_IT_FROM_WEBBROWSER
    
    Installation:
    pip install -r requirements.txt
    
    Usage:
    ./grab.py {start_page_id} {start_page_title} {output_path}
    
    Example:
    ./grab.py 1234567 Start_page ./output/Start_page
"""

confluence_url = os.getenv('CONFLUENCE_HOST')

jar = requests.cookies.RequestsCookieJar()
jar.set('JSESSIONID', os.getenv('CONFLUENCE_JSESSIONID'), domain=os.getenv('CONFLUENCE_DOMAIN'), path=os.getenv('CONFLUENCE_PATH', '/'))

def request_api(page_id):
    api_url = '{confluence_url}/rest/api/content/search?cql=parent={parent_id}&limit=500'

    url = api_url.format(confluence_url=confluence_url, parent_id=page_id)
    print('Requesting %s' % url)
    r = requests.get(url, cookies=jar)
    return r

def get_page(page_id, path, title):
    download_url = '{confluence_url}/spaces/flyingpdf/pdfpageexport.action?pageId={page_id}'

    title = title.replace('/', '_')

    file = requests.get(download_url.format(confluence_url=confluence_url, page_id=page_id), cookies=jar)

    if not os.path.exists(path):
        os.makedirs(path)

    with open('%s.pdf' % os.path.join(path, title), 'wb') as fd:
        for chunk in file.iter_content(chunk_size=128):
            fd.write(chunk)

    r = request_api(page_id)
    children = r.json().get('results')

    for page in children:
        if page.get('id') != page_id:
            print(page.get('id'), os.path.join(path, page.get('title')), page.get('title'))
            get_page(page.get('id'), os.path.join(path, page.get('title')), page.get('title'))

if __name__ == '__main__':

    try:
        parent_id = sys.argv[1]
        parent_title = sys.argv[2]
        output_dir = sys.argv[3]

    except Exception:
        print('Arguments: parent_id, parent_title, output_dir')
        exit(1)

    else:
        if not os.path.exists(output_dir):
            os.makedirs(os.path.join(os.getcwd(), output_dir))
        else:
            if not os.path.isdir(output_dir):
                print('Output dir have to be dir')
                exit(1)

        get_page(parent_id, output_dir, parent_title)
