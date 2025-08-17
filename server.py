import os   
import json
import requests
from agent import stream_graph_updates

# def MainProtokol(s,ts = 'Запись'):
#     dt=time.strftime('%d.%m.%Y %H:%M:')+'00'

#     f=open('log.txt','a')
#     f.write(dt+';'+str(ts)+';'+str(s)+'\n')
#     f.close        
    
import http.server
import socketserver

PORT = 8004  # Choose any available port number here (default: 8000).
DIRECTORY = '.'  # Serve files from the current directory.

class Handler(http.server.SimpleHTTPRequestHandler):
    # own_host = os.getenv("OWN_HOST").strip()
    # context_path = os.getenv("CONTEXT_PATH").strip()
    url = os.getenv("TELEGRAM_URL").strip()
    token = os.getenv("TELEGRAM_BOT_TOKEN").strip()

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
            print(repr(e))
            raise ValueError('Error parsing JSON request')
        
        chat_id = json_string['message']['chat']['id']
        input_message = json_string['message']['text']

        # print('Get from chat: '+str(chat_id)+', message:'+input_message)

        # Send headers indicating success
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        # Invoke Agent
        response_txt = stream_graph_updates(input_message)

        # Send response in Telegram
        send_message=requests.get(self.url+self.token+'/sendMessage?chat_id='+str(chat_id)+'&text='+str(response_txt))
        if not send_message: raise ValueError('Не удалось отправить текст в бот. status:'+str(send_message.status_code))


def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
