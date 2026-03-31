import Foundation
import Combine
#if canImport(AppKit)
import AppKit
#endif

class ProcessManager: ObservableObject {
    @Published var isRunning = false
    private var process: Process?
    private var outputPipe: Pipe?
    
    func startJarvis() {
        guard !isRunning else { return }
        
        // Recreate Pipe for new process
        outputPipe = Pipe()
        
        let fileManager = FileManager.default
        let projectRoot = "/Users/samsonganta/Desktop/jarvis-assistant"
        let pythonPath = "\(projectRoot)/.venv/bin/python3"
        let scriptPath = "\(projectRoot)/jarvis.py"
        
        // 1. Validate Paths
        if !fileManager.fileExists(atPath: pythonPath) {
            print("❌ Error: Python interpreter not found at: \(pythonPath)")
            return
        }
        if !fileManager.fileExists(atPath: scriptPath) {
            print("❌ Error: Script not found at: \(scriptPath)")
            return
        }
        
        print("🚀 Starting Jarvis Backend... (BUILD v4.0 - NUCLEAR)")
        print("📂 Root: \(projectRoot)")
        print("🐍 Python: \(pythonPath)")
        
        process = Process()
        // Use Python directly to ensure TCC permissions are inherited 
        process?.executableURL = URL(fileURLWithPath: pythonPath)
        
        // CRITICAL: Inject Environment for Finder launches
        var env = ProcessInfo.processInfo.environment
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        env["HOME"] = "/Users/samsonganta"
        env["LC_ALL"] = "en_US.UTF-8"
        env["LANG"] = "en_US.UTF-8"
        env["PYTHONUNBUFFERED"] = "1"

        // Load .env file so Python backend has ST_* credentials even when
        // the app is launched from Finder/Dock (no shell environment).
        let dotEnvPath = "\(projectRoot)/.env"
        if let lines = try? String(contentsOfFile: dotEnvPath, encoding: .utf8) {
            print("🔑 [ProcessManager] Loading .env from: \(dotEnvPath)")
            for line in lines.components(separatedBy: .newlines) {
                let t = line.trimmingCharacters(in: .whitespaces)
                guard !t.hasPrefix("#"), !t.isEmpty else { continue }
                let parts = t.split(separator: "=", maxSplits: 1).map(String.init)
                guard parts.count == 2 else { continue }
                let k = parts[0].trimmingCharacters(in: .whitespaces)
                var v = parts[1].trimmingCharacters(in: .whitespaces)
                if (v.hasPrefix("\"") && v.hasSuffix("\"")) || (v.hasPrefix("'") && v.hasSuffix("'")) {
                    v = String(v.dropFirst().dropLast())
                }
                // Process env wins — only set if not already present
                if env[k] == nil { env[k] = v }
            }
        } else {
            print("⚠️ [ProcessManager] .env not found at \(dotEnvPath) — ST_* vars may be missing.")
        }

        process?.environment = env
        
        // Run script directly
        process?.arguments = ["-u", scriptPath, "--api"]
        process?.currentDirectoryURL = URL(fileURLWithPath: projectRoot)
        
        process?.standardOutput = outputPipe
        process?.standardError = outputPipe
        
        outputPipe?.fileHandleForReading.readabilityHandler = { handle in
             let data = handle.availableData
             if !data.isEmpty, let str = String(data: data, encoding: .utf8) {
                 // Print directly to stdout for Terminal visibility
                 fputs("[PYTHON] \(str)", stdout)
                 fflush(stdout)
                 
                 // 💡 LOG-BASED SHUTDOWN TRIGGER (Robust Fallback)
                 if str.contains("[OFFLINE] Shutting Down") {
                     DispatchQueue.main.async {
                         print("🛑 Log Trigger: Terminating App...")
                         // C-Level Kill to bypass any Swift runtime cleanup hanging
                         kill(getpid(), SIGKILL)
                     }
                 }
             }
        }
        
        process?.terminationHandler = { [weak self] proc in
            DispatchQueue.main.async {
                self?.isRunning = false
                print("🛑 Backend Exited with status: \(proc.terminationStatus)")
                // ☢️ NUCLEAR OPTION: If backend exits cleanly, kill the app.
                if proc.terminationStatus == 0 {
                    print("🛑 Clean Exit Detected. Terminating App.")
                    kill(getpid(), SIGKILL)
                }
            }
        }
        
        do {
            try process?.run()
            isRunning = true
        } catch {
            print("❌ Failed to launch process: \(error)")
            isRunning = false
        }
    }
    
    func stopJarvis() {
        process?.terminate()
        process = nil
        isRunning = false
    }
}
