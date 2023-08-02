# What is this?

This is a plugin (tool) for the [Cheshire Cat Project](https://github.com/pieroit/cheshire-cat), which allows you to bulk import URLS and Documents into the Rabbit Hole.

# Install

Download the **cc_bulk_import** folder into the **cheshire-cat/core/cat/plugins** one.
Create a folder "bulkimport" into the **/core/cat/static** one.

# Usage

**IMPORT URLS**
Ask the cat """bulkimport url **LIST OF URLS COMMA SEPARATED**"
Example: bulkimport url https://cheshirecat.ai/code-of-ethics/,https://cheshirecat.ai/

**IMPORT DOCUMENTS**
Put a **COPY** (after import files wil be deleted, so put a copy not the original one) of files you want to import into **/core/cat/static/bulkimport** folder and then ask the cat """bulkimport docs"

# Output

The cat will give a feedback after the import process is completed, so if you have multiple urls on multiple document you need to wait for having a response from the cat.

The cat responde with a table containing the status (OK or KO) for any single url/document setn to the rabbit hole.
