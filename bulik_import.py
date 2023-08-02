import requests
import os

from cat.mad_hatter.decorators import tool, hook
from cat.log import log


@tool(return_direct=True)
def bulk_url_import(url_list: str, cat):
    """Replies to "bulkimport url". Input is the comma separated list of urls."""
    message = "<table><thead><tr><th class=\"text-neutral\">URL</th><th class=\"text-neutral\">Status</th></tr></thead><tbody>"
    for link in url_list.split(","):
        if not link.startswith(('http://', 'https://')):
            message = message + link + ": Invalid link format: must start with 'http://' or 'https://'\n"
        else:
            try:
                parsed_link = requests.get(link).url
                log("Send " + parsed_link + " to rabbithole", "WARNING")
                cat.rabbit_hole.ingest_file(parsed_link, 400, 100)
                log(parsed_link + " sent to rabbithole!", "WARNING")
                message = message + "<tr><td>" + link + "</td><td>&#x2705;</td></tr>"
            except requests.exceptions.RequestException as err:
                message = message + "<tr><td>" + link + \
                    "</td><td>&#x274C; " + str(err) + "</td></tr>"
    message = message + "</tbody></table>"
    return message


@tool(return_direct=True)
def bulk_docs_import(tool_input,cat):
    """Replies to "bulkimport docs". Input is always none"""

    message = "<table><thead><tr><th class=\"text-neutral\">Document</th><th class=\"text-neutral\">Status</th></tr></thead><tbody>"
    files = os.listdir("/app/cat/static/bulkimport")
    for file in files:
       if file.startswith('.'):
           continue
       try:
            log("Send " + file + " to rabbithole", "WARNING")
            filepath = "/app/cat/static/bulkimport/" + file
            cat.rabbit_hole.ingest_file(filepath, 400, 100)
            log(file + " sent to rabbithole!", "WARNING")
            message = message + "<tr><td>" + file + "</td><td>&#x2705;</td></tr>"
            os.remove(filepath)
       except requests.exceptions.RequestException as err:
            message = message + "<tr><td>" + file + \
                "</td><td>&#x274C; " + str(err) + "</td></tr>"
    message = message + "</tbody></table>"
    return message