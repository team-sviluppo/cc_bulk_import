import os
import requests
from typing import Dict
from cat.mad_hatter.decorators import tool, hook, plugin
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log
from threading import Thread
from multiprocessing import cpu_count
from enum import Enum
from pydantic import BaseModel
import concurrent.futures
import time

class BatchSize(Enum):
    auto: str = "Auto"
    one: int = 1
    two: int = 2
    three: int = 3
    four: int = 4
    

class BulkImportSettings(BaseModel):
    # Select
    files_to_ingest_simultaneously: BatchSize = BatchSize.one

# Give your settings model to the Cat.
@plugin
def settings_model():
    return BulkImportSettings


@hook(priority=10)
def agent_fast_reply(fast_reply, cat) -> Dict:
    return_direct = False
    # Get user message
    user_message = cat.working_memory["user_message_json"]["text"]

    if user_message.startswith("bulkimport url"):
        response = bulk_url_import(user_message.split(" ")[2], cat)
        return_direct = True

    if user_message.startswith("bulkimport docs"):
        # Use threading for bulk_docs_import
        thread = Thread(target=bulk_docs_import_thread, args=(cat,))
        thread.start()
        return_direct = True
        response = "Bulk document import process started."

    # Manage response
    if return_direct:
        return {"output": response}

    return fast_reply

# Define bulk_docs_import_thread to run bulk_docs_import in a separate thread
def bulk_docs_import_thread(cat):
    response = bulk_docs_import(cat)
    cat.send_ws_message(content=response, msg_type='chat')

    # Save the response to ingested_files.html
    with open('/app/cat/static/bulkimport/ingested_files.html', 'w', encoding='utf-8') as file:
        file.write(response)

def ingest_doc(doc_name, cat, doc_number=None):
    try:
        start_time = time.time() # get current time (in seconds since epoch)
        print(f"{doc_number} - Ingesting {doc_name}")
        cat.rabbit_hole.ingest_file(cat, doc_name, 400, 100)
        end_time = time.time() # get current time again
        total_time = end_time - start_time # calculate difference between times
        
        # convert total time from seconds to minutes and seconds
        mins, secs = divmod(total_time, 60)
        print(f"Ingestion took {int(mins)} minute(s) and {int(secs)} second(s).")

        print(f"{doc_number} - Ingested {doc_name}")

    except Exception as e:
        print(f"Error while ingesting '{doc_name}' ({e})")


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
                # Use threading
                tr = Thread(target=cat.rabbit_hole.ingest_file, args=(cat, parsed_link, 400, 100))
                tr.start()
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
    settings = cat.mad_hatter.get_plugin().load_settings()
    get_batch_size = settings.get("files_to_ingest_simultaneously")

    if get_batch_size == "Auto":
        batch_size = max(1, cpu_count() // 2)
    elif get_batch_size is None:
        get_batch_size = 1
    else:
        batch_size = int(get_batch_size)

    message = '<table><thead><tr><th class="text-neutral">Document</th><th class="text-neutral">Status</th></tr></thead><tbody>'
    files = os.listdir("/app/cat/static/bulkimport")

    cat.send_ws_message(content=f"Importing the documents from /app/cat/static/bulkimport folder.", msg_type='chat')
    cat.send_ws_message(content=f"I will ingest {len(files)} documents, {batch_size} documents at a time ...", msg_type='chat')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:

        futures = []
        for idx, file in enumerate(files, 1):
            if file.startswith("."):
                continue

            try:
                log("Send " + file + " to rabbithole", "WARNING")
                filepath = "/app/cat/static/bulkimport/" + file

                # Submit a new thread to the executor
                #future = executor.submit(cat.rabbit_hole.ingest_file, cat, filepath, 400, 100)
                future = executor.submit(ingest_doc, filepath, cat, idx)
                futures.append(future)

                log(file + " sent to rabbithole!", "WARNING")
                message += "<tr><td>" + file + "</td><td>&#x2705;</td></tr>"

                # Send progress message
                #progress_message = f"{idx}. <b>{file}</b> successfully sent to rabbithole."
                #cat.send_ws_message(content=progress_message, msg_type='chat')

            except requests.exceptions.RequestException as err:
                message += "<tr><td>" + file + "</td><td>&#x274C; " + str(err) + "</td></tr>"

                # Send error message
                error_message = f"Error sending {file} to rabbithole: {str(err)}"
                cat.send_ws_message(content=error_message, msg_type='chat')

        # Use as_completed to wait for any future to complete
        #for future in concurrent.futures.as_completed(futures):
            # Handle any results or exceptions here

    message += "</tbody></table>"
    return message
