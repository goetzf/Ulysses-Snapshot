# python3.3
# make_marked.py

import os
import fnmatch

# import subprocess
# import datetime
# import xml.etree.ElementTree as ET
# import plistlib
# import re


HOME = os.getenv("HOME", "") + "/"
archive_markdown_path = HOME + "Archive_Ulysses/UL_Markdown"


def make_marked(path):
    marked_text = []
    for root, dirnames, filenames in os.walk(path, topdown=True):
        print()
        print(root)
        # for dirname in dirnames:
        #     print(dirname)
        print("-----------------------------------------")
        for filename in fnmatch.filter(filenames, '*.md'):
            # md_file = os.path.join(root, filename)
            line = "<<[" + filename + "]"
            marked_text.append(line)
            # print(str(line.encode("utf-8"))[2:-1].replace("\\n", ""))

        print("=========================================")
        if len(marked_text) > 1:
            head, tail = os.path.split(root)
            marked_file = os.path.join(root, "00" + tail[2:] + ".marked")
            # marked_file = os.path.join(root, "00 - group.marked")
            write_file(marked_file, '\n'.join(marked_text))
            print(marked_file)
        marked_text = []


def write_file(filename, file_content):
    f = open(filename, "w", encoding='utf-8')
    f.write(file_content)
    f.close()


make_marked(archive_markdown_path)
