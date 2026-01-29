import datetime
import logging
import os
import sys
from contextlib import asynccontextmanager
from http.client import SEE_OTHER
from logging import INFO
from uuid import UUID

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import RedirectResponse

from chat import Message, User
from server import load_server_from_file, write_server_file, Server


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

server_filename = "server.json"
server_global: Server


@app.post("/chat/create_new/{chat_title}")
async def create_new_chat(chat_title: str):
    uuid = server_global.create_new_chat(chat_title)
    return RedirectResponse(status_code=SEE_OTHER, url="/chat/" + str(uuid))


@app.post("/chat/{uuid}/new_message/{author}/{text}")
async def new_message(uuid: UUID, author: str, text: str):
    with server_global._chats_lock:
        if uuid not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        new_message = Message(
            is_server_message=False,
            string=text,
            author=User(username=author),
            timestamp=datetime.datetime.now(),
        )
        server_global.chats[uuid].add_message(new_message)
        return "Success"  # FIXME: Return a proper success message in JSON


@app.post("/chat/{uuid}/messages")
async def messages(uuid: UUID):
    with server_global._chats_lock:
        print("UUID:", uuid)
        if uuid not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        return jsonable_encoder(server_global.chats[uuid].message_history)


@app.get("/chat/{uuid}")
async def chat(uuid: UUID):
    with server_global._chats_lock:
        print("UUID:", uuid)
        if uuid not in server_global.chats:
            return "This chat does not exist"  # FIXME: Return a proper error message in JSON

        return "hello world! :3"


if ENVIRONMENT == "dev":
    @app.post("/chats")
    async def chats_list():
        print("in chats_list: server_global = ", server_global)
        with server_global._chats_lock:
            list_of_chat_uuids: list[str] = []
            for uuid in server_global.chats.keys():
                # list_of_chat_uuids.append(uuid)

                title = server_global.chats[uuid].title
                list_of_chat_uuids.append(str(uuid) + " / " + title)

            return jsonable_encoder(list_of_chat_uuids)


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
