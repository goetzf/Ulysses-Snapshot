
# Ulysses Markdown export – ul_snapshot.py

### Developed by [rovest](https://github.com/rovest/ulysses_snapshot).

* This Python script takes a snapshot of all Ulysses' sheets and groups, 
* to a readable folder structure, named with Group and Sheet titles. 
* Groups and Sheets are prefixed with sequence numbers. 
* Original sheet's modified dates are also preserved. 
* **Complete markdown file** is also embedded in all .ulysses packages (together with Ulysses' own xml file)
* Individual Sheets or Groups can be restored by dragging them to Ulysses' sidebar via Finder. 

Note: Filters, glued sheets, and creation time, will not be preserved when restoring from Arcive.    
If complete library restoration is needed, rely on Ulysses own built-in backup instead. Filters, glued sheets, and original creation time, will then also be restored.

## Complete markdown export: 
* Converts all Ulysses Sheets to Markdown files, in a similar named folder structure as above. 
* All special MarkdownXL tags and attachmets, not native to basic Markdown, are preserved by converting them to HTML `<span>`-tags and `<!-- HTML comment blocks -->`
* Original sheet's modified dates are also preserved.
* Embedded images are included in "/Media/" folder
* Conversion from Ulysses' xml sheet format to Markdown, is done by OSX xslt process. 

# Markdown export and sync – ul_sync_md.py

Runs functions from script above (ul_snapshot.py) by:

1. First checking for Changes in Markdown files (exported from Ulysses) 
2. copying any changed files to Markdorn_sync_Inbox (This folder can be added to External sources in Ulysses)
3. Then checking for changes in Ulysses sheets and groups,
4. and exporting Markdown from Ulysses if any changes.
5. Uses rsync for copying, so only markdown files of changed sheets will be updated.

Great for running the scripts whith a sheduler app or cron job, or just on demand. It's polling for changes, so should not use too much machine resources.

