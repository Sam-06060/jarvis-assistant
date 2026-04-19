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

                # 🚀 PROACTIVE SYNC: Broadcast current agent state to NEW client
                try:
                    import config
                    status = "ON" if getattr(config, "ENABLE_AGENTIC_MODE", False) else "OFF"
                    # We use a short delay to ensure the client is ready to receive
                    def sync_broadcast():
                        time.sleep(0.5)
                        self.broadcast("SYSTEM", f"Agentic Mode: {status}")
                    threading.Thread(target=sync_broadcast, daemon=True).start()
                except: pass
            except Exception as e:
                if self.running:
                    print(f"Socket Accept Error: {e}")

    def _handle_client(self, client_sock):
        """Reads data from a client and puts it into input_queue"""
        from utils.logger import get_logger
        logger = get_logger()
        buffer = ""
        decoder = json.JSONDecoder()
        try:
            while self.running:
                # Increased buffer to handle large pastes (16KB chunks)
                data = client_sock.recv(16384)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
                # Use raw_decode to extract JSON objects sequentially.
                # This ensures internal newlines in command data don't break the parser.
                while buffer.strip():
                    try:
                        # Attempt to decode a JSON object from the start of the buffer
                        message, index = decoder.raw_decode(buffer.lstrip())
                        # Successfully decoded an object, remove it from buffer
                        buffer = buffer.lstrip()[index:].lstrip()
                        
                        if message.get("type") == "command" and self.input_queue:
                            data = message.get("data", "")
                            web_search = message.get("web_search", False)
                            
                            current_time = time.time()
                            
                            # 1. Block Partial Results (Native Speech)
                            if data.startswith("__PARTIAL__"):
                                self.last_partial_time = current_time
                                continue
                                
                            # 2. Block Final Native Speech (Heuristic)
                            if hasattr(self, 'last_partial_time') and (current_time - self.last_partial_time < 1.0):
                                logger.debug(f"🔇 Ignoring Native Speech Final: '{data[:50]}...'")
                                self.last_partial_time = 0 
                                continue

                            logger.info(f"📥 Received CMD: {data[:100]}... [Web: {web_search}]")
                            
                            # PHASE 13.3: TYPE SAFETY
                            from core.schemas import JarvisCommand
                            try:
                                command_obj = JarvisCommand(
                                    text=data,
                                    web_search=web_search,
                                    source="socket_api"
                                )
                                
                                # ====== INSTANT HARDWARE ROUTING ======
                                # Instead of queueing and waiting for Jarvis to IDLE, process Audio Routing instantly on receiving thread.
                                if data.startswith("__UPDATE_CONFIG__"):
                                    try:
                                        json_str = data.replace("__UPDATE_CONFIG__:", "").strip()
                                        payload_data = json.loads(json_str)
                                        if payload_data.get("key") == "FORCE_MAC_BUILTIN_AUDIO":
                                            val = payload_data.get("value")
                                            import config
                                            setattr(config, "FORCE_MAC_BUILTIN_AUDIO", val)
                                            # Write to disk asynchronously if needed, but in-memory applies immediately.
                                            from core.registry import ServiceRegistry
                                            sp = ServiceRegistry.get("speech")
                                            if sp:
                                                logger.info(f"⚡️ Hot-Swapping Audio Engine to {'Mac Built-in' if val else 'System Default'}...")
                                                if hasattr(sp, 'recorder'):
                                                    # Use a safe flag to reload PyAudio exactly between read frames on the main thread
                                                    sp.recorder.needs_reinit = True
                                                if hasattr(sp, 'tts'):
                                                    # Flag TTS to hop output audio devices mid-sentence synchronously
                                                    sp.tts.needs_hotswap = True
                                                
                                            # If it's just audio update, we don't even need to queue it. 
                                            # Let Jarvis handle the disk update when it reaches idle, but route is applied NOW.
                                            self.input_queue.put(command_obj.dict())
                                            continue
                                    except Exception as e:
                                        logger.error(f"Failed to apply instant audio swap: {e}")
                                        
                                # Queue the validated object for normal processing (Agentic toggle, etc)
                                self.input_queue.put(command_obj.dict())
                                
                            except Exception as e:
                                logger.error(f"❌ Invalid Command Data: {e}")
                                continue


                        elif message.get("type") == "config":
                            if self.input_queue:
                                self.input_queue.put(f"__UPDATE_CONFIG__ {json.dumps(message.get('data'))}")

                        elif message.get("type") == "approval_response":
                            req_id = message.get("id")
                            approved = message.get("approved", False)
                            
                            if not hasattr(self, 'approval_results'):
                                self.approval_results = {}
                            self.approval_results[req_id] = approved
                            
                            if hasattr(self, 'approval_events') and req_id in self.approval_events:
                                self.approval_events[req_id].set()

                        elif message.get("type") == "plan_approval":
                            # Plan Mode: user tapped Proceed or Reject in the inline plan view
                            task_id = message.get("task_id", "")
                            approved = message.get("approved", False)
                            try:
                                from core.registry import ServiceRegistry
                                plan_mode = ServiceRegistry.get("plan_mode")
                                if plan_mode and task_id:
                                    plan_mode.receive_approval(task_id, approved)
                            except Exception as _pe:
                                logger.error(f"❌ plan_approval handler error: {_pe}")
                                
                    except json.JSONDecodeError:
                        # Not enough data yet to form a full JSON object, wait for more packets
                        break
                        
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
        
        try:
            msg = json.dumps({
                "type": msg_type,
                "header": str(header),
                "detail": str(detail)
            }) + "\n"
            
            with self.lock:
                disconnected = []
                for client in self.clients:
                    try:
                        client.sendall(msg.encode('utf-8'))
                    except:
                        disconnected.append(client)
                
                for disc in disconnected:
                    if disc in self.clients:
                        self.clients.remove(disc)
        except Exception as e:
            print(f"Broadcast Error: {e}")

    def broadcast_signal(self, signal: str):
        """
        Send an __AC_*__ hardware command signal to all connected Swift clients.
        The Swift SocketClient intercepts messages whose 'data' field starts with '__AC_'
        and dispatches them to JarvisACController.

        Protocol examples:
            broadcast_signal("__AC_ON__")
            broadcast_signal("__AC_OFF__")
            broadcast_signal("__AC_TEMP_22__")
            broadcast_signal("__AC_MODE_cool__")
        """
        try:
            msg = json.dumps({
                "type": "command",
                "header": "AC_SIGNAL",
                "detail": signal,
                "data": signal
            }) + "\n"

            with self.lock:
                disconnected = []
                for client in self.clients:
                    try:
                        client.sendall(msg.encode('utf-8'))
                    except:
                        disconnected.append(client)

                for disc in disconnected:
                    if disc in self.clients:
                        self.clients.remove(disc)

            print(f"📡 [SocketServer] AC signal broadcasted: {signal}")
        except Exception as e:
            print(f"Signal Broadcast Error: {e}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
