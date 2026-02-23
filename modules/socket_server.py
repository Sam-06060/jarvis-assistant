import socket
import threading
import json
import time

class JarvisSocketServer:
    def __init__(self, port=8492, input_queue=None, hud_queue=None):
        self.port = port
        self.input_queue = input_queue
        # hud_queue is NOT used for input here, but we will attach a separate thread 
        # to READ from hud_queue and broadcast to clients.
        self.clients = []
        self.server_socket = None
        self.running = False
        self.lock = threading.Lock()
        self.last_partial_time = 0 # For filtering native speech

    def start(self):
        """Start the socket server in a background thread"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(('0.0.0.0', self.port))
            print(f"✅ Socket bound to 0.0.0.0:{self.port}")
        except OSError:
            print(f"⚠️ Port {self.port} in use. Waiting 2 seconds...")
            time.sleep(2)
            try:
                self.server_socket.bind(('0.0.0.0', self.port))
            except Exception as e:
                print(f"❌ Failed to bind port {self.port}: {e}")
                return
        self.server_socket.listen(5)
        
        print(f"🔌 API Server listening on port {self.port}")
        
        # Thread for accepting connections
        self.accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
        self.accept_thread.start()

    def _accept_clients(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(client_sock)
                # handle client in a separate thread
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"Socket Accept Error: {e}")

    def _handle_client(self, client_sock):
        """Reads data from a client and puts it into input_queue"""
        from utils.logger import get_logger
        logger = get_logger()
        buffer = ""
        try:
            while self.running:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
                # Split by newline (assuming JSON-lines or newline delimited headers)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line: continue
                    
                    try:
                        message = json.loads(line)
                        # Expected format: {"type": "command", "data": "hello"}
                        if message.get("type") == "command" and self.input_queue:
                            # Extract data and web_search flag
                            data = message.get("data", "")
                            web_search = message.get("web_search", False)
                            
                            # --- NATIVE SPEECH FILTER ---
                            current_time = time.time()
                            
                            # 1. Block Partial Results
                            if data.startswith("__PARTIAL__"):
                                self.last_partial_time = current_time
                                continue
                                
                            # 2. Block Final Native Speech (Heuristic)
                            if hasattr(self, 'last_partial_time') and (current_time - self.last_partial_time < 1.0):
                                logger.debug(f"🔇 Ignoring Native Speech Final: '{data}'")
                                self.last_partial_time = 0 
                                continue
                            # ----------------------------

                            logger.info(f"📥 Received CMD: {data} [Web: {web_search}]")
                            
                            # PHASE 13.3: TYPE SAFETY
                            from core.schemas import JarvisCommand
                            try:
                                command_obj = JarvisCommand(
                                    text=data,
                                    web_search=web_search,
                                    source="socket_api"
                                )
                                # Queue the validated object (or dict for backward compat)
                                self.input_queue.put(command_obj.dict())
                            except Exception as e:
                                logger.error(f"❌ Invalid Command Data: {e}")
                                continue

                        elif message.get("type") == "config":
                            if self.input_queue:
                                self.input_queue.put(f"__UPDATE_CONFIG__ {json.dumps(message.get('data'))}")
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Invalid JSON: {line}")
                        
        except Exception as e:
            logger.error(f"❌ Socket Client Error: {e}")
        finally:
            with self.lock:
                if client_sock in self.clients:
                    self.clients.remove(client_sock)
            client_sock.close()

    def broadcast(self, header, detail):
        """Send a HUD update to all connected clients"""
        msg_type = "hud_update"
        data_field = None
        
        # New: Handle Partial Transcripts for Live Captions
        if header == "PARTIAL":
            msg_type = "partial"
            data_field = detail # Send text as 'data'
        
        message = json.dumps({
            "type": msg_type,
            "header": header,
            "detail": detail,
            "data": data_field
        }) + "\n"
        
        with self.lock:
            for client in self.clients[:]:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    self.clients.remove(client)

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except: pass
