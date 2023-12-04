from flask import Flask
import threading
from sonic_engine.core.engine import Engine


def run_server(manager: Engine):
    def thread_server():
        nonlocal manager
        app = Flask(__name__)

        @app.route("/")
        def home():
            return "TODO: help text"

        app.run(debug=True, use_reloader=False, port=8011)

    t_webApp = threading.Thread(name='Atlas API', target=thread_server)
    t_webApp.setDaemon(True)
    t_webApp.start()
