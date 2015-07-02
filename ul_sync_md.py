# python3.3
# ul_sync_md.py

# version-1.0.1 - 2015-01-09 at 20:43 IST
# GNU (cl) 2015 @RoyRogers56, free to use and improve. Not for sale.
# Only tested with python 3.3 on OS X 10.10

# First checking for Changes in Markdown files (exported from Ulysses)
# and copying changed files to Markdorn_sync_Inbox (folder in External sources in Ulysses)
# Then checking for changes in Ulysses sheets and groups,
# and exporting Markdown from Ulysses if Changes.

import os
import fnmatch
import re
import datetime
import subprocess

HOME = os.getenv("HOME", "") + "/"

#markdown_path = HOME + "Archive_Ulysses/UL_Markdown"
markdown_path = HOME + "OneDrive/UL_Markdown"
sync_inbox_path = HOME + "OneDrive/md_sync_inbox"

ulysses_path = HOME + "Library/Mobile Documents/X5AZV975AG~com~soulmen~ulysses3/"\
    + "Documents/Library/"


def main():
    if check_for_md_updates(markdown_path, sync_inbox_path):
        notify("Files imported to 'md_sync_inbox'")
    if check_for_ulysses_updates(ulysses_path, markdown_path):
        import ul_snapshot
        ul_snapshot.make_markdown_export(ulysses_path, markdown_path)
        notify('Exported Markdown from Ulysses')


def read_file(file_name):
    f = open(file_name, "r", encoding='utf-8')
    file_content = f.read()
    f.close()
    return file_content


def write_file(filename, file_content, modified):
    f = open(filename, "w", encoding='utf-8')
    f.write(file_content)
    f.close()
    if modified > 0:
        os.utime(filename, (-1, modified))


def get_file_date(filename):
    try:
        t = os.path.getmtime(filename)
        return t
    except:
        return 0


def check_for_md_updates(md_path, sync_inbox):
    ts_file = os.path.join(md_path, ".sync-time.txt")
    files_found = False
    if not os.path.exists(ts_file):
        return False
    ts_last_export = os.path.getmtime(ts_file)
    for root, dirnames, filenames in os.walk(md_path):
        for filename in fnmatch.filter(filenames, '*.md'):
            md_file = os.path.join(root, filename)
            try:
                ts = os.path.getmtime(md_file)
            except:
                pass
            if ts > ts_last_export:
                files_found = True
                if not os.path.exists(sync_inbox):
                    os.makedirs(sync_inbox)
                from_group = "%% Synced from: " + root.replace(md_path, "") + "/\n"
                synced_file = os.path.join(sync_inbox, filename[5:])
                count = 2
                while os.path.exists(synced_file):
                    file_part = re.sub(r"(( - \d\d)?\.md)", r"", synced_file)
                    synced_file = file_part + " - " + str(count).zfill(2) + ".md"
                    count += 1
                md_text = read_file(md_file)
                pos = md_text.find("\n")
                if pos == -1:
                    md_text = md_text + "\n" + from_group
                else:
                    md_text = md_text[:pos+1] + from_group + md_text[pos+1:]
                ts = get_file_date(md_file)
                write_file(synced_file, md_text, ts)
                print("*** File to md_sync_inbox: " + synced_file)
    write_file(os.path.join(md_path, ".sync-time.txt"),
               "Checked for Markdown updates to sync at: " +
               datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"), 0)
    return files_found


def check_for_ulysses_updates(ul_path, md_ts_path):
    ts_file = os.path.join(md_ts_path, ".export-time.txt")
    if not os.path.exists(ts_file):
        return True
    ts_last_export = os.path.getmtime(ts_file)
    for root, dirnames, filenames in os.walk(ul_path):
        for dirname in fnmatch.filter(dirnames, '*.ulysses'):
            if root.endswith("Trash-ultrash"):
                continue
            ul_file = os.path.join(root, dirname)
            ts = os.path.getmtime(ul_file)
            if ts > ts_last_export:
                print("*** Sheet update:", dirname)
                return True
        for filename in fnmatch.filter(filenames, 'Info.ulgroup'):
            info_file = os.path.join(root, filename)
            ts = os.path.getmtime(info_file)
            if ts > ts_last_export:
                print("*** Group update:", root.replace(ul_path, ""))
                return True
    return False


def notify(message):
    title = "ul_sync_md.py"

    try:
        # Uses "terminal-notifier", download at:
        # https://github.com/downloads/alloy/terminal-notifier/terminal-notifier_1.4.2.zip
        # Only works with OS X 10.8+
        subprocess.call(['/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier',
                         '-message', message, "-title", title])
    except:
        print('* "terminal-notifier.app" is missing!')

        try:
            # Uses "growlnotify", download at:
            # http://growl.cachefly.net/GrowlNotify-2.1.zip
            # Depends on Growl 2
            subprocess.call(['/usr/local/bin/growlnotify', title,
                             '-m', message])
        except:
            print('* "growlnotify" is missing!')

    print("* Message:", str(message.encode("utf-8")))
    return


if __name__ == '__main__':
    main()
