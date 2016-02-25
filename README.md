
# Ulysses Snapshot – ul_snapshot.py

* This Python script takes a snapshot of all Ulysses III Sheets, 
* to a readable folder structure, named with Group and Sheet titles. 
* Groups and Sheets are prefixed with sequence numbers. Original sheet's modified dates are also preserved. 
* Complete markdown files get also embedded in all .ulysses packages.
* Individual Sheets or Groups can be restored by dragging them to Ulysses via Finder. 
* Filters, glued sheets, and original modified time, will not be preserved when restoring from Arcive. (If complete library restoration is needed, rely on Ulysses own built-in backup instead. Filters, glued sheets, and original modified time, will then also be restored.)

## Also: 
* Convert all Ulysses Sheets to Markdown files, 
* with all special MarkdownXL tags and attachmets included in HTML tags and in HTML comment blocks: `<!-- Comment --\>`
* Original sheet's modified dates are also preserved.
* Embedded images are included in "/Media/" folder

# Look for changes and Sync – ul_sync_md.py

1. First checking for Changes in Markdown files (exported from Ulysses) 
2. copying any changed files to Markdorn_sync_Inbox (folder in External sources in Ulysses)
3. Then checking for changes in Ulysses sheets and groups,
4. and exporting Markdown from Ulysses if any changes.
5. Uses rsync for copying, so only markdown files of changed sheets will be updated.

