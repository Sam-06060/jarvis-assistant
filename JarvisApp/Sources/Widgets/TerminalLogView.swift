import SwiftUI

struct TerminalLogView: View {
    @EnvironmentObject var socketClient: SocketClient
    @Namespace var bottomID

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 4) {
                    ForEach(socketClient.messages) { msg in
                        if isChatMessage(msg) {
                            HStack(alignment: .top, spacing: 8) {
                                Text(msg.header == "USER" ? ">>" : "<<")
                                    .font(.system(size: 12, design: .monospaced))
                                    .foregroundColor(msg.header == "USER" ? .ironManGold : .ironManCyan)
                                
                                Text(msg.detail ?? "")
                                    .font(.system(size: 14, design: .monospaced))
                                    .foregroundColor(msg.header == "USER" ? .white : .ironManCyan)
                                    .shadow(color: (msg.header == "JARVIS" ? Color.ironManCyan : Color.clear).opacity(0.5), radius: 2)
                            }
                            .padding(.vertical, 2)
                        }
                    }
                    
                    // Live Typing Indicator
                    if !socketClient.liveCaption.isEmpty {
                        Text("> " + socketClient.liveCaption + " ▮")
                            .font(.system(size: 14, design: .monospaced))
                            .foregroundColor(.ironManGold)
                            .padding(.top, 5)
                            .id("live_typing")
                    }
                    
                    Color.clear.frame(height: 1).id(bottomID)
                }
                .padding()
            }
            .onChange(of: socketClient.messages.count) { _ in
                 withAnimation { proxy.scrollTo(bottomID) }
            }
            .onChange(of: socketClient.liveCaption) { _ in
                 withAnimation { proxy.scrollTo("live_typing") }
            }
        }
        .background(Color.black.opacity(0.5))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.ironManCyan.opacity(0.3), lineWidth: 1)
        )
    }
    
    func isChatMessage(_ msg: JarvisMessage) -> Bool {
        let h = msg.header ?? ""
        return h == "USER" || h == "JARVIS"
    }
}
