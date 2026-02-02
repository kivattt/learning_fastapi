import datetime
import logging
import os
import sys
from contextlib import asynccontextmanager
from http.client import SEE_OTHER
from logging import INFO

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from webserver.chat import Message, User
from webserver.server import load_server_from_file, write_server_file, Server


@asynccontextmanager
async def lifespan(_: FastAPI):
    startup()
    yield
    shutdown()


print(sys.path)

# prod or dev
ENVIRONMENT = os.getenv("CHAT_ENVIRONMENT", "prod")

# Attach file handler to uvicorn loggers
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_error = logging.getLogger("uvicorn.error")

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh = logging.FileHandler("chat.log")
fh.setFormatter(formatter)

uvicorn_access.addHandler(fh)
uvicorn_error.addHandler(fh)

app = FastAPI(
    lifespan=lifespan,
    title="Chat",
    version="r0",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/mit",
    }
)

# Mount our static .html/.css/.js files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

server_filename = "server.json"
server_global: Server


@app.get("/")
async def root():
    return RedirectResponse(status_code=SEE_OTHER, url="/static")


@app.post("/chat/create_new/{chat_title}")
async def create_new_chat(chat_title: str):
    chat_id = server_global.create_new_chat(chat_title)
    return RedirectResponse(status_code=SEE_OTHER, url="/chat/" + str(chat_id))


@app.post("/chat/{chat_id}/new_message/{author}/{text}")
async def new_message(chat_id: str, author: str, text: str):
    print("DEBUGGING:", chat_id, author, text)
    with server_global._chats_lock:
        if chat_id not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        new_message = Message(
            is_server_message=False,
            string=text,
            author=User(username=author),
            timestamp=datetime.datetime.now(),
        )
        server_global.chats[chat_id].add_message(new_message)
        return "Success"  # FIXME: Return a proper success message in JSON


@app.post("/chat/{chat_id}/messages")
async def messages(chat_id: str):
    with server_global._chats_lock:
        if chat_id not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        return jsonable_encoder(server_global.chats[chat_id].message_history)


@app.get("/chat/{chat_id}")
async def chat(chat_id: str):
    with server_global._chats_lock:
        if chat_id not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        return "hello world! :3"


'''
@app.get("/client")
async def client(chat_id: str): # URL query parameter
    return RedirectResponse(status_code=SEE_OTHER, url="/client")
'''

# Private endpoints we don't want to expose in production
if ENVIRONMENT == "dev":
    @app.post("/chats")
    async def chats_list():
        print("in chats_list: server_global = ", server_global)
        with server_global._chats_lock:
            list_of_chat_chat_ids: list[str] = []
            for chat_id in server_global.chats.keys():
                # list_of_chat_chat_ids.append(chat_id)

                title = server_global.chats[chat_id].title
                list_of_chat_chat_ids.append(str(chat_id) + " / " + title)

            return jsonable_encoder(list_of_chat_chat_ids)


def startup():
    logging.log(INFO, "Called startup()")
    # Read the server data from a file
    global server_global
    server_global = load_server_from_file(server_filename)
    if server_global is None:
        print("Failed to load server from file \"" + server_filename + "\"")
        server_global = Server(chats=dict())
    else:
        print("Loaded server data from file \"" + server_filename + "\"")

    print("CHAT_ENVIRONMENT = " + ENVIRONMENT)
    if ENVIRONMENT != "prod":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!        Not running in prod        !")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


def shutdown():
    logging.log(INFO, "Called shutdown()")
    # Write the whole server class to a file
    running = True
    while running:
        try:
            write_server_file(server_global, server_filename)
            print("Saved server to: \"" + server_filename + "\"")
            running = False
        except (TypeError, OSError) as e:
            print("Failed to save server with exception:", e)
            yes_or_no = input("Try again? [Y/n]: ")
            if yes_or_no.lower() == 'n':
                print("Quitting")
                running = False
