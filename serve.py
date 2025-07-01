# serve.py
import http.server
import socketserver
import os
import sys

PORT = 8000
# Serve vanuit de map waar het script zich bevindt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = SCRIPT_DIR

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" %
                         (self.log_date_time_string(),
                          format%args))

class StoppableTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self._shutdown_request = False
        self.allow_reuse_address = True

    def serve_forever(self, poll_interval=0.5):
        try:
            super().serve_forever(poll_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()

    def verify_request(self, request, client_address):
        if self._shutdown_request:
            return False
        return super().verify_request(request, client_address)

    def shutdown(self):
        self._shutdown_request = True
        try:
            self.socket.close()
        except Exception:
            pass
        super().shutdown()

if __name__ == "__main__":
    index_path = os.path.join(DIRECTORY, "index.html")
    if not os.path.exists(index_path):
        print(f"FOUT: 'index.html' niet gevonden in de map '{os.path.abspath(DIRECTORY)}'.")
        print("Zorg ervoor dat 'serve.py' in dezelfde map staat als je 'index.html', 'style.css', en 'script.js'.")
        sys.exit(1)

    httpd = None
    try:
        httpd = StoppableTCPServer(("", PORT), Handler)
        print(f"Server gestart op http://localhost:{PORT}")
        print(f"Serveert bestanden vanuit: {os.path.abspath(DIRECTORY)}")
        print("Druk op Ctrl+C om de server te stoppen.")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:
            print(f"FOUT: Poort {PORT} is al in gebruik. Probeer een andere poort of sluit het programma dat de poort gebruikt.")
        elif e.errno == 10048:
             print(f"FOUT: Poort {PORT} is al in gebruik. Probeer een andere poort of sluit het programma dat de poort gebruikt.")
        else:
            print(f"FOUT bij het starten van de server: {e}")
    except Exception as e:
        print(f"Een onverwachte fout is opgetreden: {e}")
    finally:
        if httpd:
            print("\nServer wordt afgesloten...")
            httpd.shutdown()
        print("Server gestopt.")
