import Foundation
import Network
import Combine
#if canImport(AppKit)
import AppKit
#endif

struct JarvisMessage: Identifiable, Codable, Hashable {
    var id = UUID()
    let type: String
    let header: String?
    let detail: String?
    let data: String?
    
    var text: String {
        return data ?? detail ?? ""
    }
}

class SocketClient: ObservableObject {
    @Published var isConnected = false
    @Published var messages: [JarvisMessage] = []
    @Published var statusHeader: String = "IDLE"
    @Published var statusDetail: String = "Standing By"
    @Published var isFlashOverlayVisible: Bool = false
    
    private var connection: NWConnection?
    private let queue = DispatchQueue(label: "SocketQueue")
    private var lastFeedbackHeader: String = ""
    private var lastFeedbackAt: TimeInterval = 0
    
    func connect() {
        let params = NWParameters.tcp
        
        // Force IPv4
        if let ipOptions = params.defaultProtocolStack.internetProtocol as? NWProtocolIP.Options {
            ipOptions.version = .v4
        }
        
        connection = NWConnection(host: "127.0.0.1", port: 8492, using: params)
        
        print("🔄 Attempting to connect to 127.0.0.1:8492 (SOCKET v3.0)...")

        connection?.stateUpdateHandler = { [weak self] state in
            DispatchQueue.main.async {
                switch state {
                case .ready:
                    print("✅ Connected to Jarvis API")
                    self?.isConnected = true
                    self?.receive()
                case .failed(let error):
                    print("❌ Connection Failed: \(error)")
                    self?.isConnected = false
                    // Retry aggressively
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self?.connect() }
                case .waiting(let error):
                    print("⏳ Waiting... \(error) - Retrying...")
                    self?.connection?.cancel()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self?.connect() }
                default:
                    break
                }
            }
        }
        
        connection?.start(queue: queue)
    }
    
    func send(text: String, webSearch: Bool = false) {
        // 1. Optimistically append user message to UI
        let userMsg = JarvisMessage(type: "command", header: "USER", detail: nil, data: text)
        // Ensure UI update on main thread
        DispatchQueue.main.async { [weak self] in
            self?.messages.append(userMsg)
            if (self?.messages.count ?? 0) > 50 { self?.messages.removeFirst() }
        }

        // 2. Send to Server
        // Using Any to handle mixed types (String and Bool)
        let json: [String: Any] = ["type": "command", "data": text, "web_search": webSearch]
        guard let data = try? JSONSerialization.data(withJSONObject: json) else { return }
        let payload = data + "\n".data(using: .utf8)!
        
        connection?.send(content: payload, completion: .contentProcessed({ error in
            if let error = error {
                print("Send error: \(error)")
            }
        }))
    }
    
    // NEW: Handle Config Updates
    func sendConfigUpdate(key: String, value: Bool) {
        // We pack a collection of updates or single update
        // "data" field will contain the JSON for the config dict
        let configPayload: [String: Bool] = [key: value]
        guard let configJson = try? JSONEncoder().encode(configPayload),
              let configString = String(data: configJson, encoding: .utf8) else { return }
        
        let json: [String: String] = ["type": "config", "data": configString]
         guard let data = try? JSONEncoder().encode(json) else { return }
        let payload = data + "\n".data(using: .utf8)!
        
        connection?.send(content: payload, completion: .contentProcessed({ error in
             if let error = error { print("Send Error: \(error)") }
        }))
    }
    
    private func receive() {
        // Read line by line is hard with NWConnection, it gives chunks.
        // We will read a stream and look for newlines. 
        // For simplicity, we assume messages come in reasonably sized chunks.
        
        connection?.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] content, _, isComplete, error in
            if let data = content, !data.isEmpty {
                self?.decodeAndAppend(data)
            }
            if isComplete {
                self?.connect() // Reconnect
            } else if error == nil {
                self?.receive() // Loop
            }
        }
    }
    
    private var buffer = ""
    
    @Published var liveCaption: String = "" // NEW: Real-time text buffer
    
    private func decodeAndAppend(_ data: Data) {
        guard let string = String(data: data, encoding: .utf8) else { return }
        buffer += string
        
        while let range = buffer.range(of: "\n") {
            let line = String(buffer[..<range.lowerBound])
            buffer.removeSubrange(...range.lowerBound)
            
            if let jsonData = line.data(using: .utf8),
               let msg = try? JSONDecoder().decode(JarvisMsgRaw.self, from: jsonData) {
                DispatchQueue.main.async {
                    // 1. ADD SHUTDOWN LOGIC HERE
                    if let h = msg.header, h == "OFFLINE" {
                        print("🛑 Termination signal received. Shutting down App.")
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            #if os(macOS)
                            NSApplication.shared.terminate(nil)
                            #else
                            exit(0)
                            #endif
                        }
                    }
                    
                    // 2. LIVE CAPTIONS (PARTIAL)
                    if msg.type == "partial" {
                        self.statusHeader = "STREAMING"
                        self.statusDetail = "Responding..."
                        self.emitStatusFeedbackIfNeeded("STREAMING")
                        self.liveCaption = msg.data ?? ""
                        return // Don't add to chat history yet
                    }

                    // 2b. In-app low-light flash control
                    if let header = msg.header?.uppercased(), header == "FLASH" {
                        self.isFlashOverlayVisible = (msg.detail?.uppercased() == "ON")
                        return
                    }
                    
                    // 3. FINAL MESSAGE (Clear Caption)
                    self.liveCaption = "" 
                    if let header = msg.header, !header.isEmpty {
                        self.statusHeader = header
                        self.emitStatusFeedbackIfNeeded(header)
                    }
                    if let detail = msg.detail, !detail.isEmpty {
                        self.statusDetail = detail
                    }
                    
                    let fullMsg = JarvisMessage(type: msg.type, header: msg.header, detail: msg.detail, data: msg.data)
                    self.messages.append(fullMsg)
                    // Keep history last 50
                    if self.messages.count > 50 { self.messages.removeFirst() }
                }
            }
        }
    }

    private func emitStatusFeedbackIfNeeded(_ rawHeader: String) {
        let header = rawHeader.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        guard !header.isEmpty else { return }
        let now = Date().timeIntervalSince1970
        if header == lastFeedbackHeader { return }
        if now - lastFeedbackAt < 0.25 {
            lastFeedbackHeader = header
            return
        }
        lastFeedbackHeader = header
        lastFeedbackAt = now

        #if canImport(AppKit)
        let pattern: NSHapticFeedbackManager.FeedbackPattern
        if header.contains("ERROR") || header == "OFFLINE" || header == "ACCESS DENIED" {
            pattern = .alignment
        } else if header == "LISTENING" || header == "THINKING" || header == "PROCESSING" || header == "STREAMING" {
            pattern = .levelChange
        } else if header == "IDLE" {
            pattern = .generic
        } else {
            return
        }
        NSHapticFeedbackManager.defaultPerformer.perform(pattern, performanceTime: .default)
        #endif
    }
}

// Helper strict struct for decoding
struct JarvisMsgRaw: Decodable {
    let type: String
    let header: String?
    let detail: String?
    let data: String?
}
