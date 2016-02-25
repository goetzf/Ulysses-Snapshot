
# Ulysses Snapshot – ul_snapshot.py

* This Python script takes a snapshot of all Ulysses III Sheets, 
* to a readable folder structure, named with Group and Sheet titles. 
* Groups and Sheets are prefixed with sequence numbers. 
* Original sheet's modified dates are also preserved. 
* Complete markdown files get also embedded in all .ulysses packages.
* Individual Sheets or Groups can be restored by dragging them to Ulysses' sidebar via Finder. 

Note: Filters, glued sheets, and original creation time, will not be preserved when restoring from Arcive.    
If complete library restoration is needed, rely on Ulysses own built-in backup instead. Filters, glued sheets, and original creation time, will then also be restored.

## Also: 
* Convert all Ulysses Sheets to Markdown files. 
* All special MarkdownXL tags and attachmets are included in HTML `<span>`-tags and `<!-- HTML comment blocks -->`
* Original sheet's modified dates are also preserved.
* Embedded images are included in "/Media/" folder
* Conversion from Ulysses' xml sheet format to Markdown, is done by OSX xslt process. 

# Look for changes and Sync – ul_sync_md.py

1. First checking for Changes in Markdown files (exported from Ulysses) 
2. copying any changed files to Markdorn_sync_Inbox (This folder can be added to External sources in Ulysses)
3. Then checking for changes in Ulysses sheets and groups,
4. and exporting Markdown from Ulysses if any changes.
5. Uses rsync for copying, so only markdown files of changed sheets will be updated.

