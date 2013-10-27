#!/usr/bin/python
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python fileencoding=utf-8

import sqlite3
import datetime
import re

def indent4(m):
    return '\n        ' + m.group(1).replace('\n', '\n        ')

def convert(text):
    text = re.sub('\r\n', '\n', text)
    text = re.sub(r'{{{(.*?)}}}', r'`\1`', text)
    text = re.sub(r'(?sm){{{\n(.*?)\n}}}', indent4, text)
    text = re.sub(r'(?m)^====\s+(.*?)\s+====$', r'#### \1', text)
    text = re.sub(r'(?m)^===\s+(.*?)\s+===$', r'### \1', text)
    text = re.sub(r'(?m)^==\s+(.*?)\s+==$', r'## \1', text)
    text = re.sub(r'(?m)^=\s+(.*?)\s+=$', r'# \1', text)
    text = re.sub(r'^             * ', r'****', text)
    text = re.sub(r'^         * ', r'***', text)
    text = re.sub(r'^     * ', r'**', text)
    text = re.sub(r'^ * ', r'*', text)
    text = re.sub(r'^ \d+. ', r'1.', text)

    a = []
    for line in text.split('\n'):
        if not line.startswith('        '):
            line = re.sub(r'\[(https?://[^\s\[\]]+)\s([^\[\]]+)\]', r'[\2](\1)', line)
            line = re.sub(r'\[(wiki:[^\s\[\]]+)\s([^\[\]]+)\]', r'[\2](/\1/)', line)
            line = re.sub(r'\!(([A-Z][a-z0-9]+){2,})', r'\1', line)
            line = re.sub(r'\'\'\'(.*?)\'\'\'', r'*\1*', line)
            line = re.sub(r'\'\'(.*?)\'\'', r'_\1_', line)
        a.append(line)
    text = '\n'.join(a)
    return text

def save_file(text, name, version, date, author):
    fp = file('%s.md' % name, 'w')
    print >>fp, '<!-- Name: %s -->' % name
    print >>fp, '<!-- Version: %d -->' % version
    print >>fp, '<!-- Last-Modified: %s -->' % date
    print >>fp, '<!-- Author: %s -->' % author
    fp.write(text.encode('utf-8'))
    fp.close()

if __name__ == "__main__":
    SQL = '''
    select
            name, version, time, author, text
        from
            wiki w
        where
            version = (select max(version) from wiki where name = w.name)
'''

    conn = sqlite3.connect('../trac.db')
    result = conn.execute(SQL)
    for row in result:
        name = row[0]
        version = row[1]
        time = row[2]
        author = row[3]
        text = row[4]
        text = convert(text)
        time=''
        try:
            time= datetime.datetime.fromtimestamp(time).strftime('%Y/%m/%d %H:%M:%S')
        except ValueError:
            time= datetime.datetime.fromtimestamp(time/1000000).strftime('%Y/%m/%d %H:%M:%S')
        save_file(text, name, version, time, author)


