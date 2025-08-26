import os
import json
import requests
import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(os.getenv("LOG_DIR", "bot.log"), when='midnight', interval=1, backupCount=14),
        logging.StreamHandler()
    ]
) 
    
import http.server
import socketserver
from agent import WorkingGraph

PORT = 8000  # Choose any available port number here (default: 8000).
DIRECTORY = '.'  # Serve files from the current directory.

class Handler(http.server.SimpleHTTPRequestHandler):
    # own_host = os.getenv("OWN_HOST")
    # context_path = os.getenv("CONTEXT_PATH")
    url = os.getenv("TELEGRAM_URL")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    agent = WorkingGraph()

    def log_request(self, code = "-", size = "-"):
        logging.info(
            f"{self.client_address[0]} - {self.command} {self.path} - HTTP {code}"
        )

    def log_error(self, format, *args):
        logging.error(
            f"{self.client_address[0]} - {self.command} {self.path} - ERROR: {format % args}"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        # set_hook = requests.get(self.url+self.token+'/setWebhook?url='+self.own_host+self.context_path)
        # if not set_hook: raise ValueError('Cannot setup webhook')

    def do_GET(self):
        self.log_request()
        self.send_response(200)

    def do_POST(self):
        """Handle POST requests"""
        self.log_request()
        
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        try:
            json_string=json.loads(post_data)
        except Exception as e:
            logging.error(f'Error parsing JSON request: {repr(e)}')
        
        chat_id = str(json_string['message']['chat']['id'])
        input_message = json_string['message']['text']

        logging.info(f"Got message from user_id = {chat_id}")

        # Send headers indicating success
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        self.handle_chat_message(chat_id, input_message)
        
    def handle_chat_message(self, chat_id: str, input_message: str):
        if input_message.lower() in ["/clear", "/clean"]:
            self.agent.clear_memory(chat_id)
            logging.info(f"Cleared memory for chat: {chat_id}")
        else:
            self.respod(chat_id, input_message)

    def respod(self, chat_id: str, input_message: str):
        # Invoke Agent
        response_txt = self.agent.invoke(chat_id, input_message)

        # Send response in Telegram
        send_message = requests.get(self.url+self.token+'/sendMessage?chat_id='+str(chat_id)+'&text='+str(response_txt))
        if not send_message: logging.error(f"Cannot sent respose to Telegram. Code: {send_message.status_code}")
        else: logging.info("Respose succesfully sent")


def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving at port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            httpd.shutdown()
            httpd.server_close()

if __name__ == "__main__":
    run_server()
