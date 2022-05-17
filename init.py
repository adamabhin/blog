#!/usr/bin/python3

import re
import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

FOLDER_ID = '1ntP1ADl9-d1bPlekw156lrjpt5KWwue5'


def main():
    creds = service_account.Credentials.from_service_account_file('auth.json')

    try:
        drive = build('drive', 'v3', credentials=creds)
        files = drive.files().list(q="'{}' in parents".format(FOLDER_ID)).execute().get('files', [])
 
        for file in files:
            if file.get('mimeType') != 'application/vnd.google-apps.document':
                continue

            DOCUMENT_ID = file.get('id')

            docs = build('docs', 'v1', credentials=creds)
            document = docs.documents().get(documentId=DOCUMENT_ID).execute()

            with open('content/blog/' + _slugify(document.get('title')) + '.md', 'w') as blog:
                blog.write('---\n'
                    + 'title: ' + str(document.get('title')) + '\n'
                    + '---\n\n')

            with open('content/blog/' + _slugify(document.get('title')) + '.md', 'a') as blog:
                for content in document.get('body').get('content'):
                    if 'paragraph' in content:
                        blog.write(str(content) + '\n\n')

                    # if (content.get('paragraph').get('paragraphStyle').get('namedStyleType') != 'NORMAL_TEXT'):
                    #     blog.write(str(content.get('paragraph').get('paragraphStyle').get('namedStyleType')) + '\n\n')

                    # if (content.get('paragraph').get('elements')[0].get('textRun').get('textStyle') != {}):
                    #     blog.write(str(content.get('paragraph').get('elements')[0].get('textRun').get('textStyle')) + '\n\n')

                    # if (content.get('paragraph').get('elements')[0].get('textRun').get('content') != '\n'):
                    #     blog.write(str(content.get('paragraph').get('elements')[0].get('textRun').get('content')) + '\n')

    except HttpError as err:
        print(err)


def _slugify(text):
    non_url_safe = ['"', '#', '$', '%', '&', '+',
                    ',', '/', ':', ';', '=', '?',
                    '@', '[', '\\', ']', '^', '`',
                    '{', '|', '}', '~', "'"]

    non_url_safe_regex = re.compile(
        r'[{}]'.format(''.join(re.escape(x) for x in non_url_safe)))
        
    text = non_url_safe_regex.sub('', text).strip()
    text = u'-'.join(re.split(r'\s+', text))
    text = str.lower(text)
    return text


if __name__ == '__main__':
    main()
