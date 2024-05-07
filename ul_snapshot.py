# python3.3
# ul_snapshot.py
# version-1.3.3 2016-05-24 at 09:04 -  EST

# GNU (cl) 2016 @rovest, free to use and improve. Not for sale.
# Only tested with python 3.3 on OS X 10.10

# Update 2016-05-22: process_ul_sheets_and_groups(): Fixed over-simplification from 2016-02-27
#                                                    (sheets got wrong sequence numbering)
# Update 2016-02-27: process_ul_sheets_and_groups(): Fixed and simplified processing sheets
# Update 2016-02-21: make_ul_archive():
#                    Hard-coded access to Groups-ulgroup and Unfiled-ulgroup (Inbox) only.
#                    Inbox and all top level groups will now be on same level.
# Update 2015-07-03: 1. Added workaround for bug in Ulysses 2.1 restore backup function.
#                    2. Removed backup sections (Ulysses 2.1 now has native backup solution).
#                    3. Reorganized order of functions to make the script easier to read.
# Update 2015-01-23: Tweaked XSLT for image attachments.
# Update 2015-01-16: Fixed: regex for image matching in markdown files.
#                    Fixed: bug where old Markdown files and folder where not deleted.
#                    Now, markdown is made to fresh Temp folder, then rsynced to final destination.
# Update 2015-01-15: Replacement of Unicode LF to Markdown 2 x spaces + LF, now done in XSLT

# This Python script takes a snapshot of all Ulysses III Sheets,
# to a readable folder structure, named with Group and Sheet titles.
# Groups and Sheets are prefixed with sequence numbers.
# Original sheet's modified dates are also preserved.

# Individual Sheets or Groups can be restored by dragging them to Ulysses via Finder.
# Filters, glued sheets, and original modified time,
# will not be preserved when restoring from Arcive.

# If complete library restoration is needed, rely on the complete library backup (below) instead.
# Filters, glued sheets, and original modified time, will then also be restored.
# DO NOT drag in the backup file! But replace the UL Library Document folder with the backup.

# Optional: convert all Ulysses Sheets to Markdown files,
# with all special MarkdownXL tags and attachmets included in HTML tags and comment blocks.
# Original sheet's modified dates are also preserved.
# Embedded images are included in "/Media/" folder

import os
import datetime
import subprocess
import fnmatch
import xml.etree.ElementTree as ET
import plistlib
import re
import shutil

do_markdown_archive = True
do_embed_markdown = True

HOME = os.getenv("HOME", "") + "/"
time_stamp = "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

# Note!!! DO NOT LEAVE ANY OF THE PATH NAMES BELOW EMPTY OR TO ROOT OF EXISTING FOLDERS!!!
# Note!!! YOU MAY THEN DELETE ALL YOUR USER FILES !!!

# Path for Ulysses Archive (Snapshots):
archive_ul_path = HOME + "Archive_Ulysses/UL_Archive" + time_stamp
# Path for Ulysses Markdown Archive:
archive_markdown_path = HOME + "Archive_Ulysses/UL_Markdown"  # + time_stamp

archive_ul_temp = HOME + "Archive_Ulysses/Temp_UL_Archive"

# Note!!! Do not change last part of folder name: "Temp_UL_Markdown"!!!
markdown_ul_temp = HOME + "Archive_Ulysses/Temp_UL_Markdown"


def main():
    # Plain backup of Ulysses Library
    print("===============================================")
    print("*** Ulysses Snapshot/Archive script started ***")
    print("===============================================")

    ulysses_path_lib = os.path.join(HOME,
                                    "Library/Mobile Documents/X5AZV975AG~com~soulmen~ulysses3",
                                    "Documents/Library") + "/"

    print("*** Making UL Archive from:", ulysses_path_lib)
    make_ul_archive(ulysses_path_lib, archive_ul_temp)
    subprocess.call(['rsync', '-t', '-r', '--delete',
                    archive_ul_temp + "/", archive_ul_path])
    print("*** Ul Archive written to:", archive_ul_path)
    print()

    if do_markdown_archive:
        print("*** Making Markdown Archive from:", archive_ul_temp)
        make_markdown(archive_ul_temp, archive_markdown_path)
        print("*** Ul Markdown written to:", archive_markdown_path)
        print()

    if do_embed_markdown:
        print("*** Embedding Markdown in .ulysses packages:", archive_ul_path)
        embed_markdown(archive_ul_path)
        print('*** Markdown added to all packages as "Content.md" in:', archive_ul_path)
        print()

    print("=============================")
    print("*** Archive Job Completed ***")
    print("=============================")
# end_main


def make_ul_archive(ul_library_path, archive_path):
    # Copy library:
    sub_paths = (('Groups-ulgroup', ''), ('Unfiled-ulgroup', '00 - Inbox'))
    for from_sub, to_sub in sub_paths:
        from_path = os.path.join(ul_library_path, from_sub) + '/'
        to_path = os.path.join(archive_path, to_sub)
        if not os.path.exists(to_path):
            os.makedirs(to_path)
        subprocess.call(['rsync', '-t', '-r', '--delete',
                        from_path, to_path])
    # Rename Sheets and Groups:
    process_ul_sheets_and_groups(archive_path)
    include_make_markdown_script(archive_path)


def process_ul_sheets_and_groups(path):
    for root, dirnames, filenames in os.walk(path, topdown=False):
        # Processing Sheets
        # num = 1
        # for dirname in fnmatch.filter(dirnames, '*.ulysses'):
        #     new_title = rename_sheet(root, dirname, num)
        #     if new_title != "":
        #         num += 1

        # Processing Groups
        for filename in fnmatch.filter(filenames, 'Info.ulgroup'):
            info_file = os.path.join(root, filename)
            with open(info_file, 'rb') as infile:
                pl = plistlib.load(infile)
            # pl_res_data = pl["resolutionData"]
            if "sheetClusters" in pl:
                num = 1
                for pl_entry0 in pl["sheetClusters"]:
                    for pl_entry in pl_entry0:
                            if str(pl_entry).endswith(".ulysses"):
                                new_title = rename_sheet(root, pl_entry, num)
                                if new_title != "":
                                    num += 1
                    # continue
            if "childOrder" in pl:
                num = 1
                for pl_entry in pl["childOrder"]:
                    if str(pl_entry).endswith("-ulgroup"):
                        group_title = rename_group(root, pl_entry, num)
                        if group_title != "":
                            num += 1


def rename_sheet(root, ul_name, num):
    xml_file = os.path.join(root, ul_name, "Content.xml")
    ul_file = os.path.join(root, ul_name)
    if not os.path.exists(ul_file):
        # print("*** File Missing:", ul_file)
        return ""

    try:
        xml_doc = ET.parse(xml_file)
        p = xml_doc.find(".//p")
        if p is not None:
            title = ET.tostring(p, "unicode", "text")
        else:
            title = "Untitled"
        new_title = str(num).zfill(2) + " - " + clean_title(title) + ".ulysses"
        new_file = os.path.join(root, new_title)
        os.rename(ul_file, new_file)
        # print(ul_name)
        # print(new_title)
        # print()

        return new_title.strip()
    except:
        print("*** File Missing or Corrupt XML", xml_file)
        return "*** Corrupt XML"


def rename_group(root, group, num):
    info_file = os.path.join(root, group, "Info.ulgroup")
    group_path = os.path.join(root, group)
    if not os.path.exists(info_file):
        # print("*** Group Missing:", info_file)
        return ""
    
    with open(info_file, 'rb') as infile:
        pl = plistlib.load(infile)

    if "displayName" in pl:
        group_title = pl["displayName"]
    else:
        group_title = "Untitled"
    
    group_title = re.sub(r'[\/\?\*]', '-', group_title)
    
    if group_path.endswith("-ulgroup"):
        group_title = str(num).zfill(2) + " - " + group_title
        os.rename(group_path, group_path[:-40] + group_title)
    return group_title


def read_file(file_name):
    f = open(file_name, "r", encoding='utf-8')
    file_content = f.read()
    f.close()
    return file_content


def write_file(filename, file_content):
    f = open(filename, "w", encoding='utf-8')
    f.write(file_content)
    f.close()


def clean_title(title):
    # Clean MD titel to make safe cross-platform filenames:
    title = re.sub(r"[/\\—|.&<>:—–]", r"-", title)
    title = re.sub(r"[\*]", r"_", title)

    # Strip all special chars:
    # title = re.sub(r"[^_0-9a-zA-Z \-]", r"", title)  # ASCII Only
    title = re.sub(r"[#?*^!$+=%§'\[\]\{\}\"\t\n\r\f\v“”‘’´`¨]", r"", title)
    title = title.replace(u"\u2028", "-")
    title = title.strip()
    if title == "":
        title = "Untitled"
    return title[:64]


def include_make_markdown_script(archive_path):
    xslt_file = os.path.join(archive_path, "ulysses2md.xslt")
    write_file(xslt_file, ulysse2markdown_xslt)
    sh_file = os.path.join(archive_path, "ul2md.sh")
    write_file(sh_file, shell_script_ul2md)
    subprocess.call(['chmod', '777', sh_file])


def process_md_time_stamp(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.md'):
            md_file = os.path.join(root, filename)
            # Update .md-files modified with .ulysses' timestamp
            try:
                ulysses_file = md_file[:-3] + ".ulysses"
                ts = os.path.getmtime(ulysses_file)
                os.utime(md_file, (-1, ts))
            except:
                pass


def replace_media_link(md_file, media_list):
    md_text = read_file(md_file)
    regex = r"!\[.*?\]\(Media/([\dabcdef]+?) "
    result = re.findall(regex, md_text)
    is_dirty = False
    for media_uuid in result:
        new_media_ref = media_list[media_uuid].replace(" ", "%20")
        md_text = md_text.replace(media_uuid, new_media_ref)
        is_dirty = True
    if is_dirty:
        ts = os.path.getmtime(md_file)
        write_file(md_file, md_text)
        os.utime(md_file, (-1, ts))


def copy_and_link_media(ul_archive_path, md_path):
    media_list = {}
    all_md_with_media = []
    # Find all sheets with images and copy image-files to Media folder in Markdown archive:
    for root, dirnames, filenames in os.walk(ul_archive_path):
        for dirname in fnmatch.filter(dirnames, 'Media'):
            media_path = os.path.join(root, dirname)
            md_file_with_media = md_path + root.replace(ul_archive_path, "")[:-8] + ".md"
            all_md_with_media.append(md_file_with_media)
            pos = md_file_with_media.rfind("/")
            md_media_root = md_file_with_media[0:pos] + "/Media"
            if not os.path.exists(md_media_root):
                os.makedirs(md_media_root)
            for file in os.listdir(media_path):
                media_file = os.path.join(media_path, file)
                shutil.copy2(media_file, md_media_root)
                media_file_uuid = file.split(".")[-2]
                media_list[media_file_uuid] = file
    # Replace media uuid in .md-file with complete filename:
    for md_file in all_md_with_media:
        replace_media_link(md_file, media_list)


def make_markdown(ul_archive_path, md_path):
    # Make Markdown files:
    # Traverse through all .ulysses packages and run XSLT script on each Content.xml
    # Result will be written in parent folder:

    temp_xslt = "ul2md_tmp.xslt"
    write_file(temp_xslt, ulysse2markdown_xslt)
    subprocess.call(['find', ul_archive_path, '-iname', "*.ulysses", '-exec', 'sh', '-c',
                     'xsltproc ul2md_tmp.xslt "$0/Content.xml" > "$0.md"',
                     '{}', ';'])
    os.remove(temp_xslt)

    # Rename all *.ulysses.md files to *.md:
    subprocess.call(['find', ul_archive_path, '-iname', "*.ulysses.md",
                    '-exec', 'bash', '-c', 'mv "$0" "${0%\.ulysses.md}.md"', '{}', ';'])

    process_md_time_stamp(ul_archive_path)

    # Move all markdown files to temp folder using rsync:
    if os.path.exists(markdown_ul_temp) and "Temp_UL_Markdown" in markdown_ul_temp:
        # *** NOTE! Double checking that markdown_ul_temp folder contains "Temp_UL_Markdown"
        # *** Otherwise if accidentally empty or root,
        # *** shutil.rmtree() may delete all user files or your complete Hard Drive!!
        shutil.rmtree(markdown_ul_temp)
        # *** NOTE: USE rmtree() WITH EXTREME CAUTION!

    os.makedirs(markdown_ul_temp)
    subprocess.call(['rsync', '-r', '-t', '--include=*.md', '--exclude=*.ulysses', '--exclude=*.ulgroup',
                     '--exclude=*-ulfilter/', '--exclude=.DS_Store' '--remove-source-files',
                     ul_archive_path + "/", markdown_ul_temp])

    # Copy all mediafiles and change UUID-link in .md-file to full filename:
    copy_and_link_media(ul_archive_path, markdown_ul_temp)

    # Finally write to time-stamp.txt file (used by external sync-script)
    write_file(os.path.join(markdown_ul_temp, ".export-time.txt"),
               "Markdown from Ulysses written at: " +
               datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"))
    write_file(os.path.join(markdown_ul_temp, ".sync-time.txt"),
               "Markdown from Ulysses written at: " +
               datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"))

    # Move all markdown files to new folder using rsync:
    if not os.path.exists(md_path):
        os.makedirs(md_path)
    subprocess.call(['rsync', '-r', '-t', '--delete',
                     markdown_ul_temp + "/", md_path])


def link_media(md_file, media_path):
    media_list = {}
    for file in os.listdir(media_path):
        media_file_uuid = file.split(".")[-2]
        media_list[media_file_uuid] = file
    # Replace media uuid in .md-file with complete filename:
    replace_media_link(md_file, media_list)


def keep_orig_modified(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, 'Content.md'):
            md_file = os.path.join(root, filename)
            media_path = os.path.join(root, "Media")
            if os.path.exists(media_path):
                link_media(md_file, media_path)
            # Update Content.md and .ulysses package with timestamp from Content.xml:
            xml_file = os.path.join(root, "Content.xml")
            try:
                ts = os.path.getmtime(xml_file)
                os.utime(md_file, (-1, ts))
                os.utime(root, (-1, ts))
            except:
                pass


def embed_markdown(ul_archive_path):
    # Make Markdown files inside .ulysses packages:
    # Traverse through all .ulysses packages and run XSLT script on each Content.xml
    # Result will be written inside .ulysses packages as Content.md:

    temp_xslt = "ul2md_tmp.xslt"
    write_file(temp_xslt, ulysse2markdown_xslt)
    subprocess.call(['find', ul_archive_path, '-iname', "*.ulysses", '-exec', 'sh', '-c',
                     'xsltproc ul2md_tmp.xslt "$0/Content.xml" > "$0/Content.md"',
                     '{}', ';'])
    os.remove(temp_xslt)
    keep_orig_modified(ul_archive_path)


def make_markdown_export(ulysses_path, md_path):
    print("*** Making Markdown Archive from:", ulysses_path)
    make_ul_archive(ulysses_path, archive_ul_temp)
    make_markdown(archive_ul_temp, md_path)
    print("*** Ul Markdown written to:", md_path)
    print()


# This is the XSLT style sheet embedded, to make this a one-file-only-script:
ulysse2markdown_xslt = """<?xml version='1.0'?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8" omit-xml-declaration="yes"
    indent="no" standalone="yes"/>

<!--
    XSLT Style sheet for transforming Ulysses Content.xml to Multimarkdown
    (c) MIT 2014, RoyRogers56
    Not for commercial use, but free for personal use, on your own risk.
    Version 1.1, 2015-01-13 at 21:44 IST
    Added "search-and-replace" template, for unicode-LF (&#x2028;) -> "2 x space + LF"
    Feel free to use and improve.
-->

<xsl:template match="/">
    <xsl:apply-templates select="sheet/string/p"/>
    <xsl:apply-templates select="//element[@kind='footnote']/attribute/string"/>
    <xsl:apply-templates select="sheet/attachment"/>
</xsl:template>

<xsl:template match="p">
    <xsl:apply-templates />
    <xsl:text>&#10;</xsl:text>
</xsl:template>

<xsl:template match="p[tags/tag[@kind='comment']]">
    <xsl:text>&lt;!--</xsl:text>
        <xsl:apply-templates />
    <xsl:text>--&gt;&#10;</xsl:text>
</xsl:template>

<xsl:template match="p[tags/tag[@kind='nativeblock']]">
    <xsl:text></xsl:text><xsl:value-of select="text()"/>
    <xsl:text>&#10;</xsl:text>
</xsl:template>

<xsl:template match="p[tags/tag[@kind='divider']]">
    <xsl:text>&#10;* * *&#10;&#10;</xsl:text>
</xsl:template>

<xsl:template match="p[tags/tag[@kind='codeblock']]">
    <xsl:text>&#9;</xsl:text><xsl:value-of select="text()"/>
    <xsl:text>&#10;</xsl:text>
</xsl:template>

<xsl:template match="element[@startTag]">
    <xsl:value-of select="@startTag"/><xsl:apply-templates /><xsl:value-of select="@startTag"/>
</xsl:template>

<xsl:template match="element">
    <xsl:value-of select="@startTag"/><xsl:apply-templates /><xsl:value-of select="@startTag"/>
</xsl:template>

<xsl:template match="element[@kind='inlineNative']">
    <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="element[@kind='inlineComment' or @kind='delete']">
    <xsl:text>&lt;!--</xsl:text>
    <xsl:value-of select="@startTag"/>
    <xsl:value-of select="."/>
    <xsl:value-of select="@startTag"/>
    <xsl:text>--&gt;</xsl:text>
</xsl:template>

<xsl:template match="element[@kind='mark']">
    <xsl:text>&lt;mark&gt;</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>&lt;/mark&gt;</xsl:text>
</xsl:template>

<!-- Inline Footnotes (NOT supported by many markdown editors/parsers) -->
<!--
<xsl:template match="element[@kind='footnote']">
     <xsl:text>[^</xsl:text>
     <xsl:apply-templates select="attribute/string/p"/>
     <xsl:text>]</xsl:text>
</xsl:template>
-->

<xsl:template match="element[@kind='footnote']">
<!-- Inline footnote reference number -->
    <xsl:text>[^</xsl:text>
    <xsl:value-of select="count(preceding::element[@kind='footnote']) + 1"/>
    <xsl:text>]</xsl:text>
</xsl:template>

<xsl:template match="element[@kind='footnote']/attribute/string">
<!-- Footnote itself, written at bottom of Markdown file (called in the first xsl:template) -->
    <xsl:text>[^</xsl:text>
    <xsl:value-of select="count(preceding::element[@kind='footnote']) + 1"/>
    <xsl:text>]: </xsl:text>
    <xsl:apply-templates select="p"/>
    <xsl:text>&#10;</xsl:text>
</xsl:template>

<xsl:template match="element[@kind='annotation']">
    <xsl:value-of select="text()"/>
    <xsl:text>&lt;!--</xsl:text>
    <xsl:apply-templates select="attribute/string/p"/>
    <xsl:text>--&gt;</xsl:text>
</xsl:template>

<xsl:template match="element[@kind='link']">
    <xsl:text>[</xsl:text><xsl:value-of select="text()"/><xsl:text>]</xsl:text>
    <xsl:text>(</xsl:text>
    <xsl:value-of select="attribute[@identifier='URL']"/>
    <xsl:text> "</xsl:text>
    <xsl:value-of select="attribute[@identifier='title']"/>
    <xsl:text>")</xsl:text>
</xsl:template>

<xsl:template match="element[@kind='image']">
    <xsl:text>![</xsl:text>
    <xsl:value-of select="attribute[@identifier='description']"/>
    <xsl:text>]</xsl:text>
    <xsl:choose>
        <xsl:when test="attribute[@identifier='URL'] != ''">
            <xsl:text>(</xsl:text><xsl:value-of select="attribute[@identifier='URL']"/>
        </xsl:when>
        <xsl:otherwise>
            <!-- When embedded image, only partial image filename (UUID only) is saved,
                 also with no filetype.
                 This makes it extremely difficult to reference the image file directly in XSLT.
                 Postprocesseing Content.md with Phyton to extract complete image-filenames
                 is neccessary :( -->
            <xsl:text>(Media/</xsl:text>
            <xsl:value-of select="attribute[@identifier='image']"/>
            <!--<xsl:text>.jpeg or .tif or .gif or .png or .???</xsl:text>-->
        </xsl:otherwise>
    </xsl:choose>
    <xsl:text> "</xsl:text>
    <xsl:value-of select="attribute[@identifier='title']"/>
    <xsl:text>")</xsl:text>
</xsl:template>

<xsl:template match="*">
    <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="text()">
    <!-- Replace Ulysses' unicode new line char with markdown equivalent: "2 x space + lf" -->
    <xsl:call-template name="search-and-replace">
        <xsl:with-param name="input" select="."/>
        <xsl:with-param name="search-string"><xsl:text>&#x2028;</xsl:text></xsl:with-param>
        <xsl:with-param name="replace-string"><xsl:text>  &#10;</xsl:text></xsl:with-param>
    </xsl:call-template>
</xsl:template>

<xsl:template match="escape">
    <xsl:value-of select="."/>
</xsl:template>

<!--
<xsl:template match="@startTag">
</xsl:template>

<xsl:template match="@kind">
</xsl:template>
-->

<xsl:template match="attachment">
<!--Ulysses attachmets included as plain text in HTLM comments tags-->
        <xsl:text>&#10;&lt;!--Attachment: </xsl:text>
        <xsl:choose>
            <xsl:when test="@type='file'">
                <xsl:text>![Image](Media/</xsl:text>
                <xsl:value-of select="."/>
                <xsl:text> "")</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@type"/>
                <xsl:text>: </xsl:text>
                <xsl:value-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>--&gt;&#10;</xsl:text>
</xsl:template>

<xsl:template name="search-and-replace">
    <xsl:param name="input"/>
    <xsl:param name="search-string"/>
    <xsl:param name="replace-string"/>
    <xsl:choose>
        <!-- See if the input contains the search string -->
        <xsl:when test="$search-string and contains($input,$search-string)">
            <!-- If so, then concatenate the substring before the search
                 string to the replacement string and to the result of
                 recursively applying this template to the remaining substring.
            -->
            <xsl:value-of select="substring-before($input,$search-string)"/>
            <xsl:value-of select="$replace-string"/>
            <xsl:call-template name="search-and-replace">
                <xsl:with-param name="input" select="substring-after($input,$search-string)"/>
                <xsl:with-param name="search-string" select="$search-string"/>
                <xsl:with-param name="replace-string" select="$replace-string"/>
            </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
            <!-- There are no more occurrences of the search string so
                 just return the current input string -->
            <xsl:value-of select="$input"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

</xsl:stylesheet>"""


# Shell script to be included in Snapshot Archive.
# In case of emergency and you need to extract
# markdown later, on a machine without Ulysses.
# But it's not used by this python script!

shell_script_ul2md = r"""#!/bin/bash
# This script will traverse through all .ulysses packages in all folders
# transforming all Content.xml to Markdown using XSLT,
# and then moving all .md-files to a pure Markdown folder.
# Embedded image files will not be included :(
# (c) (MIT) 2014, RoyRogers56, 2014-12-31 at 19:07 IST

# cd "%~dp0"

# First remove old Markdown folder:
rm -r "Markdown from Ulysses XML"

# Traverse through all .ulysses packages and run XSLT script on each Content.xml
# Result will be written in parent folder:
find . -iname "*.ulysses" -exec sh -c 'xsltproc ulysses2md.xslt "$0/Content.xml" > "$0.md"' {} \;

# Move all markdown files to new folder in current folder using rsync:
rsync -r -t -v --include '*.ulysses.md' --exclude '*.*' --remove-source-files "." "Markdown from Ulysses XML"

# Rename all *.ulysses.md files to *.md:
find . -iname "*.ulysses.md" -exec bash -c 'mv "$0" "${0%\.ulysses.md}.md"' {} \;

echo ===============================================================================================
echo  All Ulysses sheets are now converted to Markdown in folder: '"Markdown from Ulysses XML"'
echo ===============================================================================================
"""


if __name__ == '__main__':
    main()
