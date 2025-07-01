# serve.py
import http.server
import socketserver
import os
import sys

PORT = 8000
# Serve vanuit de map waar het script zich bevindt
# Dit maakt het makkelijker als het script niet vanuit de project root wordt aangeroepen
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = SCRIPT_DIR

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Optioneel: stil de logging naar console, of formatteer het anders.
        # super().log_message(format, *args)
        sys.stderr.write("[%s] %s\n" %
                         (self.log_date_time_string(),
                          format%args))


# Zorg ervoor dat de server correct wordt afgesloten bij Ctrl+C
class StoppableTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self._shutdown_request = False
        self.allow_reuse_address = True # Sta hergebruik van adres toe

    def serve_forever(self, poll_interval=0.5):
        try:
            super().serve_forever(poll_interval)
        except KeyboardInterrupt:
            # Geen print hier, wordt afgehandeld in de __main__ block
            pass
        finally:
            self.server_close() # Zorg ervoor dat de socket gesloten wordt.

    def verify_request(self, request, client_address):
        # Checkt of shutdown is aangevraagd voordat een request wordt afgehandeld
        if self._shutdown_request:
            return False
        return super().verify_request(request, client_address)

    def shutdown(self):
        self._shutdown_request = True
        # Forceer het sluiten van de server socket om de serve_forever loop te onderbreken
        # Dit is soms nodig op bepaalde platformen/Python versies.
        try:
            self.socket.close()
        except Exception:
            pass # Negeer fouten bij het sluiten van de socket
        super().shutdown()


if __name__ == "__main__":
    # Controleer of index.html bestaat in de serveermap
    index_path = os.path.join(DIRECTORY, "index.html")
    if not os.path.exists(index_path):
        print(f"FOUT: 'index.html' niet gevonden in de map '{os.path.abspath(DIRECTORY)}'.")
        print("Zorg ervoor dat 'serve.py' in dezelfde map staat als je 'index.html', 'style.css', en 'script.js'.")
        sys.exit(1) # Stop het script als index.html niet gevonden is

    httpd = None
    try:
        # Probeer de server te starten
        httpd = StoppableTCPServer(("", PORT), Handler)
        print(f"Server gestart op http://localhost:{PORT}")
        print(f"Serveert bestanden vanuit: {os.path.abspath(DIRECTORY)}")
        print("Druk op Ctrl+C om de server te stoppen.")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98: # Adres al in gebruik (Linux/Mac)
            print(f"FOUT: Poort {PORT} is al in gebruik. Probeer een andere poort of sluit het programma dat de poort gebruikt.")
        elif e.errno == 10048: # Adres al in gebruik (Windows)
             print(f"FOUT: Poort {PORT} is al in gebruik. Probeer een andere poort of sluit het programma dat de poort gebruikt.")
        else:
            print(f"FOUT bij het starten van de server: {e}")
    except Exception as e:
        print(f"Een onverwachte fout is opgetreden: {e}")
    finally:
        if httpd:
            print("\nServer wordt afgesloten...")
            httpd.shutdown() # Zorg ervoor dat de server netjes afsluit
        print("Server gestopt.")
