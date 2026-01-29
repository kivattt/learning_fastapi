## Running (non-Windows)
```
CHAT_ENVIRONMENT=dev uv run uvicorn "webserver.main:app" --reload
```

<details>
<summary>Running inside PyCharm (click to expand)</summary>
If you are using PyCharm, you can create a run configuration like this:

In the Run/Debug Configurations menu, click `+` and select FastAPI.\
Now set the fields so that they look something like this:

<img src="pycharm_run_configuration.png" width="80%"></img>
</details>

## Problems / TODO
- Make a frontend
- Our message timestamps are too fine-grained e.g. `"timestamp": "2026-01-29T23:08:17.372220"`
- We should include a self-reported sent-time timestamp from the client in messages
- No authentication
- Server data is kept in a .json file called `server.json`
- Might be missing global keyword for the chats mutex... Need to look into it
- Make a `routers/` folder, like FastAPI suggests [here](https://fastapi.tiangolo.com/tutorial/bigger-applications/). Currently, all routes are defined in `webserver/main.py`
