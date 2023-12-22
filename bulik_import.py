import requests
import os
from typing import Dict
from cat.mad_hatter.decorators import tool, hook
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log


@hook(priority=10)
def agent_fast_reply(fast_reply, cat) -> Dict:
    return_direct = False
    # Get user message
    user_message = cat.working_memory["user_message_json"]["text"]

    if user_message.startswith("bulkimport url"):
        response = bulk_url_import(user_message.split(" ")[2], cat)
        return_direct = True

    if user_message.startswith("bulkimport docs"):
        response = bulk_docs_import(cat)
        return_direct = True

    # Manage response
    if return_direct:
        return {"output": response}

    return fast_reply


def bulk_url_import(url_list: str, cat):
    message = '<table><thead><tr><th class="text-neutral">URL</th><th class="text-neutral">Status</th></tr></thead><tbody>'
    for link in url_list.split(","):
        if not link.startswith(("http://", "https://")):
            message = (
                message
                + link
                + ": Invalid link format: must start with 'http://' or 'https://'\n"
            )
        else:
            try:
                parsed_link = requests.get(link).url
                log("Send " + parsed_link + " to rabbithole", "WARNING")
                cat.rabbit_hole.ingest_file(cat, parsed_link, 400, 100)
                log(parsed_link + " sent to rabbithole!", "WARNING")
                message = message + "<tr><td>" + link + "</td><td>&#x2705;</td></tr>"
            except requests.exceptions.RequestException as err:
                message = (
                    message
                    + "<tr><td>"
                    + link
                    + "</td><td>&#x274C; "
                    + str(err)
                    + "</td></tr>"
                )
    message = message + "</tbody></table>"
    return message


def bulk_docs_import(cat):
    message = '<table><thead><tr><th class="text-neutral">Document</th><th class="text-neutral">Status</th></tr></thead><tbody>'
    files = os.listdir("/app/cat/static/bulkimport")
    for file in files:
        if file.startswith("."):
            continue
        try:
            log("Send " + file + " to rabbithole", "WARNING")
            filepath = "/app/cat/static/bulkimport/" + file
            cat.rabbit_hole.ingest_file(cat, filepath, 400, 100)
            log(file + " sent to rabbithole!", "WARNING")
            message = message + "<tr><td>" + file + "</td><td>&#x2705;</td></tr>"
            os.remove(filepath)
        except requests.exceptions.RequestException as err:
            message = (
                message
                + "<tr><td>"
                + file
                + "</td><td>&#x274C; "
                + str(err)
                + "</td></tr>"
            )
    message = message + "</tbody></table>"
    return message
