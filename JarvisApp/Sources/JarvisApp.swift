import SwiftUI
import Speech
import AVFoundation

@main
struct JarvisApp: App {
    @StateObject var processManager = ProcessManager()
    @StateObject var socketClient = SocketClient()
    @StateObject var acController = JarvisACController()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(processManager)
                .environmentObject(socketClient)
                .environmentObject(acController)
                .onAppear {
                    // Request Permissions explicitly to trigger macOS Prompt
                    requestPermissions()

                    // Wire AC hardware bridge into the socket client
                    socketClient.acController = acController

                    // Start Jarvis when app launches
                    processManager.startJarvis()

                    // Connect to Socket after short delay
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                        socketClient.connect()
                    }
                }
                .onDisappear {
                    processManager.stopJarvis()
                }
        }
    }
    
    func requestPermissions() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            switch authStatus {
            case .authorized:
                print("✅ Speech Recognition: Authorized")
            case .denied:
                print("❌ Speech Recognition: Denied")
            case .restricted:
                print("⚠️ Speech Recognition: Restricted")
            case .notDetermined:
                print("❓ Speech Recognition: Not Determined")
            @unknown default:
                print("❓ Speech Recognition: Unknown")
            }
        }
        
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            if granted {
                print("✅ Microphone: Authorized")
            } else {
                print("❌ Microphone: Denied")
            }
        }
    }
}
