import SwiftUI
import Foundation
#if canImport(AppKit)
import AppKit
#endif

struct ContentView: View {
    @EnvironmentObject var processManager: ProcessManager
    @EnvironmentObject var socketClient: SocketClient

    @State private var inputText = ""
    @State private var isWebSearchEnabled = false
    @State private var showChat = false
    
    // UI states for Audio toggle
    @AppStorage("FORCE_MAC_BUILTIN_AUDIO") private var forceBuiltInAudio = true
    @State private var showSettingsSidebar = false

    private var chatMessages: [JarvisMessage] {
        socketClient.messages.filter {
            let header = ($0.header ?? "").uppercased()
            guard header == "USER" || header == "JARVIS" else { return false }
            return !isEphemeralThinkingMessage($0)
        }
    }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            HStack(spacing: 0) {
                SidebarView()

                NavigationStack {
                    HomeScreen(
                        inputText: $inputText,
                        isWebSearchEnabled: $isWebSearchEnabled,
                        sendMessage: sendMessage
                    )
                    
                    .navigationDestination(isPresented: $showChat) {
                        ActiveChatScreen(
                            inputText: $inputText,
                            isWebSearchEnabled: $isWebSearchEnabled,
                            sendMessage: sendMessage
                        )
                        .environmentObject(socketClient)
                        
                    }
                }
                .background(Color.black)
            }
            .overlay(alignment: .topTrailing) {
                 Button(action: {
                     withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                         showSettingsSidebar.toggle()
                     }
                 }) {
                     Image(systemName: "gearshape.fill")
                         .font(.system(size: 18))
                         .foregroundColor(.white.opacity(0.6))
                         .padding(16)
                         .contentShape(Rectangle())
                 }
                 .buttonStyle(.plain)
                 .padding(.top, 14)
                 .padding(.trailing, 18)
            }
            .overlay(alignment: .trailing) {
                 if showSettingsSidebar {
                     SettingsSidebar(forceBuiltInAudio: $forceBuiltInAudio, showSettingsSidebar: $showSettingsSidebar)
                         .environmentObject(socketClient)
                         .transition(.move(edge: .trailing))
                         .zIndex(100)
                 }
            }

            if socketClient.isFlashOverlayVisible {
                Color.white
                    .ignoresSafeArea()
                    .transition(.opacity)
                    .zIndex(20)
            }
        }
        .animation(.easeInOut(duration: 0.15), value: socketClient.isFlashOverlayVisible)
        .onChange(of: chatMessages.count) { _ in
            if !chatMessages.isEmpty {
                showChat = true
            }
        }
    }

    private func sendMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }

        socketClient.send(text: text, webSearch: isWebSearchEnabled)
        inputText = ""

        if !showChat {
            showChat = true
        }
    }
}

private struct SidebarView: View {
    var body: some View {
        VStack(spacing: 0) { Spacer() }
        .frame(width: 66)
        .background(Color.black)
        .overlay(alignment: .trailing) {
            Rectangle().fill(Color.white.opacity(0.1)).frame(width: 1)
        }
    }
}

private struct HomeScreen: View {
    @Binding var inputText: String
    @Binding var isWebSearchEnabled: Bool
    let sendMessage: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            VStack(spacing: 28) {
                Text("Where should we begin?")
                    .font(.system(size: 45, weight: .bold, design: .serif))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)

                ChatInputBar(
                    placeholder: "Ask anything",
                    inputText: $inputText,
                    isWebSearchEnabled: $isWebSearchEnabled,
                    sendMessage: sendMessage
                )
            }
            .frame(maxWidth: 800)
            .padding(.horizontal, 18)

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

private struct ActiveChatScreen: View {
    @EnvironmentObject var socketClient: SocketClient

    @Binding var inputText: String
    @Binding var isWebSearchEnabled: Bool
    let sendMessage: () -> Void

    @State private var newestAssistantID: UUID?
    @State private var animatedAssistantIDs: Set<UUID> = []
    @State private var showScrollToBottomButton = false
    @State private var forceScrollToken = 0

    private var chatMessages: [JarvisMessage] {
        socketClient.messages.filter {
            if $0.type == "approval_request" {
                return true
            }
            let header = ($0.header ?? "").uppercased()
            guard header == "USER" || header == "JARVIS" else { return false }
            return !isEphemeralThinkingMessage($0)
        }
    }

    private var jarvisState: JarvisUIState {
        JarvisUIState.resolve(
            statusHeader: socketClient.statusHeader,
            statusDetail: socketClient.statusDetail,
            liveCaption: socketClient.liveCaption
        )
    }

    private var chatStateLabel: String? {
        let header = socketClient.statusHeader.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        let detail = socketClient.statusDetail.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        if header == "FETCHING SUBTITLES" || detail.contains("FETCHING SUBTITLES") { return "Preparing..." }
        if header == "ANALYZING VIDEO" || detail.contains("ANALYZING VIDEO") { return "Analyzing..." }
        if header == "WRITING NOTES" || detail.contains("WRITING NOTES") { return "Writing notes..." }
        if jarvisState == .thinking { return "Thinking" }
        if jarvisState == .listening { return "Listening" }
        return nil
    }

    var body: some View {
        VStack(spacing: 0) {
            topBar

            Divider().background(Color.white.opacity(0.08))

            VStack(spacing: 0) {
                ChatStreamView(
                    messages: chatMessages,
                    liveCaption: socketClient.liveCaption,
                    newestAssistantID: newestAssistantID,
                    jarvisState: jarvisState,
                    chatStateLabel: chatStateLabel,
                    heartbeatSteps: socketClient.heartbeatSteps,
                    showScrollToBottomButton: $showScrollToBottomButton,
                    forceScrollToken: $forceScrollToken
                )
                .frame(maxWidth: .infinity)

                // Inline Plan Card — shown when Python sends a plan_render message
                if let plan = socketClient.pendingPlan {
                    InlinePlanCard(plan: plan, onApprove: {
                        socketClient.sendPlanApproval(taskId: plan.task_id, approved: true)
                    }, onReject: {
                        socketClient.sendPlanApproval(taskId: plan.task_id, approved: false)
                    })
                    .transition(.move(edge: .bottom).combined(with: .opacity))
                    .animation(.spring(response: 0.35, dampingFraction: 0.85), value: socketClient.pendingPlan != nil)
                    .padding(.horizontal, 8)
                    .padding(.bottom, 6)
                }

                VStack(spacing: 0) {
                    Text("J.A.R.V.I.S can make mistakes. Check important info.")
                        .font(.system(size: 14, weight: .regular))
                        .foregroundColor(.white.opacity(0.45))
                        .padding(.top, 2)

                    ChatInputBar(
                        placeholder: "Ask anything",
                        inputText: $inputText,
                        isWebSearchEnabled: $isWebSearchEnabled,
                        sendMessage: sendMessage
                    )
                    .padding(.top, 10)
                    .padding(.bottom, 24)
                }
                .overlay(alignment: .top) {
                    if showScrollToBottomButton {
                        Button(action: {
                            forceScrollToken += 1
                        }) {
                            Image(systemName: "arrow.down")
                                .font(.system(size: 19, weight: .semibold))
                                .foregroundColor(.white.opacity(0.98))
                                .frame(width: 42, height: 42)
                                .background(
                                    Circle()
                                        .fill(.ultraThinMaterial)
                                )
                                .overlay(
                                    Circle().stroke(Color.white.opacity(0.36), lineWidth: 1)
                                )
                                .shadow(color: Color.white.opacity(0.22), radius: 6, x: 0, y: 0)
                                .shadow(color: Color.black.opacity(0.45), radius: 10, x: 0, y: 6)
                        }
                        .buttonStyle(.plain)
                        .offset(y: -48)
                        .transition(.opacity.combined(with: .scale(scale: 0.88)))
                    }
                }
                .animation(.spring(response: 0.22, dampingFraction: 0.9), value: showScrollToBottomButton)
                .frame(maxWidth: 800)
                .frame(maxWidth: .infinity)
            }
        }
        .background(Color.black)
        .onChange(of: chatMessages.last?.id) { _ in
            guard let last = chatMessages.last else { return }
            let lastHeader = (last.header ?? "").uppercased()

            // Animate only when the newly appended chat item is an assistant message.
            guard lastHeader == "JARVIS" else { return }
            guard !animatedAssistantIDs.contains(last.id) else { return }

            newestAssistantID = last.id
            animatedAssistantIDs.insert(last.id)
        }
        .onAppear {
            // Do not replay animation for historical messages on view appear.
            newestAssistantID = nil
        }
        .onChange(of: newestAssistantID) { id in
            guard let id else { return }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
                if newestAssistantID == id {
                    newestAssistantID = nil
                }
            }
        }
    }

    private var topBar: some View {
        HStack(spacing: 8) {
            Button(action: {}) {
                HStack(spacing: 8) {
                    Text("J.A.R.V.I.S")
                        .font(.system(size: 16, weight: .semibold))

                    StatusBadgeView(state: jarvisState)

                    Image(systemName: "chevron.down")
                        .font(.system(size: 11, weight: .semibold))
                }
                .foregroundColor(.white)
            }
            .buttonStyle(.plain)

            Spacer()

            // Keep original top-bar balance after removing action icons.
            Color.clear
                .frame(width: 56, height: 1)
        }
        .frame(maxWidth: .infinity, minHeight: 52, alignment: .center)
        .background(Color.black)
        .padding(.horizontal, 18)
        .padding(.vertical, 14)
    }
}

private func isEphemeralThinkingMessage(_ message: JarvisMessage) -> Bool {
    let header = (message.header ?? "").uppercased()
    guard header == "JARVIS" else { return false }

    let normalized = message.text
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .lowercased()
        .trimmingCharacters(in: CharacterSet(charactersIn: ".!?…"))

    if normalized == "thinking" { return true }
    if normalized == "preparing content assassin" { return true }
    if normalized.hasPrefix("analyzing ") { return true }
    return false
}

private enum JarvisUIState: Equatable {
    case idle
    case listening
    case thinking
    case responding
    case speaking
    case error
    case security
    case offline
    case booting
    case unknown(String)

    static func resolve(statusHeader: String, statusDetail: String, liveCaption: String) -> JarvisUIState {
        let header = statusHeader.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        let detail = statusDetail.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()

        if !liveCaption.isEmpty || header == "STREAMING" { return .responding }
        if header == "LISTENING" { return .listening }
        if header == "SPEAKING" { return .speaking }
        if header == "IDLE" { return .idle }
        if header == "SECURITY" { return .security }
        if header == "OFFLINE" { return .offline }
        if header == "BOOTING" { return .booting }
        if header.contains("ERROR") { return .error }
        if header == "FETCHING SUBTITLES" || detail.contains("FETCHING SUBTITLES") { return .thinking }
        if header == "ANALYZING VIDEO" || detail.contains("ANALYZING VIDEO") { return .thinking }
        if header == "WRITING NOTES" || detail.contains("WRITING NOTES") { return .thinking }
        if header == "THINKING" || detail.contains("THINKING") || header == "PROCESSING" { return .thinking }

        return .unknown(header.isEmpty ? "IDLE" : header)
    }

    var title: String {
        switch self {
        case .idle: return "IDLE"
        case .listening: return "LISTENING"
        case .thinking: return "THINKING"
        case .responding: return "RESPONDING"
        case .speaking: return "SPEAKING"
        case .error: return "ERROR"
        case .security: return "SECURITY"
        case .offline: return "OFFLINE"
        case .booting: return "BOOTING"
        case .unknown(let state): return state
        }
    }

    var tint: Color {
        switch self {
        case .error: return Color.red.opacity(0.95)
        case .listening: return Color.cyan.opacity(0.95)
        case .thinking: return Color.white.opacity(0.95)
        case .responding: return Color.green.opacity(0.95)
        case .speaking: return Color.orange.opacity(0.95)
        case .security: return Color.yellow.opacity(0.95)
        case .offline: return Color.gray.opacity(0.9)
        case .booting: return Color.blue.opacity(0.95)
        case .idle, .unknown: return Color.white.opacity(0.85)
        }
    }

    var shimmering: Bool {
        switch self {
        case .listening, .thinking, .responding, .booting:
            return true
        default:
            return false
        }
    }
}

private struct StatusBadgeView: View {
    let state: JarvisUIState

    var body: some View {
        ZStack {
            Capsule()
                .fill(Color.white.opacity(0.08))

            Capsule()
                .stroke(state.tint.opacity(0.35), lineWidth: 1)

            ShimmerText(text: state.title, color: state.tint, shimmering: state.shimmering)
                .font(.system(size: 11, weight: .bold, design: .rounded))
                .padding(.horizontal, 9)
        }
        .frame(height: 22)
        .fixedSize(horizontal: true, vertical: true)
    }
}

private struct ChatStreamView: View {
    let messages: [JarvisMessage]
    let liveCaption: String
    let newestAssistantID: UUID?
    let jarvisState: JarvisUIState
    let chatStateLabel: String?
    let heartbeatSteps: [HeartbeatStep]
    @Binding var showScrollToBottomButton: Bool
    @Binding var forceScrollToken: Int

    @State private var viewportMaxY: CGFloat = 0
    @State private var bottomAnchorMaxY: CGFloat = 0
    @State private var shouldAutoFollow = true

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 14) {
                    ForEach(Array(messages.enumerated()), id: \.element.id) { index, message in
                        let isUser = (message.header ?? "").uppercased() == "USER"
                        let previousIsUser: Bool = {
                            guard index > 0 else { return false }
                            return (messages[index - 1].header ?? "").uppercased() == "USER"
                        }()
                        
                        if message.type == "approval_request" {
                            CommandApprovalBubble(message: message)
                                .id(message.id)
                        } else if isUser {
                            UserBubble(text: message.text)
                                .id(message.id)
                        } else {
                            AssistantMessageView(
                                text: message.text,
                                shouldAnimate: message.id == newestAssistantID
                            )
                            .padding(.top, previousIsUser ? 14 : 0)
                            .id(message.id)
                        }
                    }

                    if !liveCaption.isEmpty {
                        ButterStreamText(text: liveCaption)
                            .font(.system(size: 19))
                            .foregroundColor(.white.opacity(0.92))
                            .id("live_caption")
                    }

                    if let indicatorLabel = chatStateLabel {
                        StateShimmerIndicatorView(label: indicatorLabel)
                            .padding(.top, 2)
                            .id("state_indicator_\(indicatorLabel)")
                    }

                    // Heartbeat progress stack (live agentic step indicators)
                    if !heartbeatSteps.isEmpty {
                        HeartbeatStackView(steps: heartbeatSteps)
                            .padding(.top, 6)
                            .id("heartbeat_stack")
                    }

                    Color.clear
                        .frame(height: 1)
                        .id("bottom_anchor")
                        .background(
                            GeometryReader { geo in
                                Color.clear.preference(
                                    key: ChatBottomAnchorYPreferenceKey.self,
                                    value: geo.frame(in: .global).maxY
                                )
                            }
                        )
                }
                .frame(maxWidth: 800)
                .frame(maxWidth: .infinity)
                .padding(.horizontal, 26)
                .padding(.top, 20)
                .padding(.bottom, 8)
            }
            .background(
                GeometryReader { geo in
                    Color.clear.preference(
                        key: ChatViewportMaxYPreferenceKey.self,
                        value: geo.frame(in: .global).maxY
                    )
                }
            )
            .onPreferenceChange(ChatViewportMaxYPreferenceKey.self) { value in
                viewportMaxY = value
                refreshScrollButtonVisibility()
            }
            .onPreferenceChange(ChatBottomAnchorYPreferenceKey.self) { value in
                bottomAnchorMaxY = value
                refreshScrollButtonVisibility()
            }
            .simultaneousGesture(
                DragGesture(minimumDistance: 2)
                    .onChanged { _ in
                        // User is intentionally navigating history; stop auto-follow until they reattach.
                        shouldAutoFollow = false
                    }
            )
            .onChange(of: messages.count) { _ in
                guard shouldAutoFollow else { return }
                proxy.scrollTo("bottom_anchor", anchor: .bottom)
            }
            .onChange(of: liveCaption) { _ in
                guard shouldAutoFollow else {
                    refreshScrollButtonVisibility()
                    return
                }
                // Streaming updates are high-frequency; avoid animated scroll jitter.
                proxy.scrollTo("bottom_anchor", anchor: .bottom)
                refreshScrollButtonVisibility()
            }
            .onChange(of: newestAssistantID) { _ in
                refreshScrollButtonVisibility()
            }
            .onChange(of: jarvisState) { _ in
                refreshScrollButtonVisibility()
            }
            .onChange(of: forceScrollToken) { _ in
                shouldAutoFollow = true
                withAnimation(.easeInOut(duration: 0.32)) {
                    proxy.scrollTo("bottom_anchor", anchor: .bottom)
                }
                withAnimation(.easeOut(duration: 0.12)) {
                    showScrollToBottomButton = false
                }
            }
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(Color.black.opacity(0.14))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            .shadow(color: Color.black.opacity(0.3), radius: 10, x: 0, y: 4)
        }
    }

    private func refreshScrollButtonVisibility() {
        // Keep logic explicit: button appears iff we are NOT at bottom.
        // In global coordinates, bottom is reached when content-bottom is at or above viewport-bottom.
        let atBottomThreshold: CGFloat = 18
        let isAtBottom = bottomAnchorMaxY <= (viewportMaxY + atBottomThreshold)

        shouldAutoFollow = isAtBottom
        let shouldShow = !isAtBottom
        if shouldShow != showScrollToBottomButton {
            withAnimation(.spring(response: 0.22, dampingFraction: 0.9)) {
                showScrollToBottomButton = shouldShow
            }
        }
    }
}

private struct ChatBottomAnchorYPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

private struct ChatViewportMaxYPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

private struct UserBubble: View {
    let text: String

    var body: some View {
        HStack {
            Spacer(minLength: 32)
            Text(text)
                .font(.system(size: 19))
                .foregroundColor(.white.opacity(0.97))
                .lineSpacing(2)
                .padding(.horizontal, 15)
                .padding(.vertical, 11)
                .background(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(Color(hex: 0x222327))
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(Color.white.opacity(0.10), lineWidth: 1)
                )
                .frame(maxWidth: 520, alignment: .trailing)
        }
    }
}

private struct CommandApprovalBubble: View {
    @EnvironmentObject var socketClient: SocketClient
    let message: JarvisMessage
    
    @State private var isExpanded = false
    @State private var status: String = "pending" // "approved" or "rejected"
    
    var parsedPayload: (command: String, description: String, risk: String) {
        let defaultReturn = ("Unknown Command", "No description provided.", "Unknown")
        guard let dataStr = message.data, 
              let data = dataStr.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return defaultReturn
        }
        return (
            json["command"] as? String ?? defaultReturn.0,
            json["description"] as? String ?? defaultReturn.1,
            json["risk"] as? String ?? defaultReturn.2
        )
    }
    
    var riskColor: Color {
        let r = parsedPayload.risk.lowercased()
        if r.contains("critical") || r.contains("high") || r.contains("danger") || r.contains("extreme") || r.contains("severe") { 
            return .red 
        }
        if r.contains("low") || r.contains("safe") || r.contains("minimal") { 
            return .green 
        }
        return .yellow
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 0) {
                // Header
                HStack {
                    Image(systemName: "terminal.fill")
                        .foregroundColor(.white.opacity(0.8))
                    Text("SYSTEM REQUEST")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white.opacity(0.9))
                    Spacer()
                    Text(parsedPayload.risk.uppercased())
                        .font(.system(size: 10, weight: .bold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(riskColor.opacity(0.15))
                        .foregroundColor(riskColor)
                        .cornerRadius(4)
                        .overlay(RoundedRectangle(cornerRadius: 4).stroke(riskColor.opacity(0.3), lineWidth: 1))
                }
                .padding(12)
                .background(Color(hex: 0x222222))
                
                // Body
                VStack(alignment: .leading, spacing: 12) {
                    Text(parsedPayload.command)
                        .font(.system(.subheadline, design: .monospaced))
                        .foregroundColor(.green)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.black.opacity(0.4))
                        .cornerRadius(6)
                    
                    if isExpanded {
                        Text(parsedPayload.description)
                            .font(.system(size: 14))
                            .foregroundColor(.white.opacity(0.75))
                            .transition(.opacity.combined(with: .move(edge: .top)))
                    }
                    
                    Button(action: { withAnimation { isExpanded.toggle() } }) {
                        Text(isExpanded ? "Show Less" : "Show More")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.gray)
                    }
                    .buttonStyle(.plain)
                    
                    if status == "pending" {
                        HStack(spacing: 12) {
                            Button(action: { handleDecision(false) }) {
                                Text("Reject")
                                    .font(.system(size: 14, weight: .bold))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                                    .background(Color.red.opacity(0.12))
                                    .foregroundColor(.red)
                                    .cornerRadius(6)
                                    .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.red.opacity(0.25), lineWidth: 1))
                            }
                            .buttonStyle(.plain)
                            
                            Button(action: { handleDecision(true) }) {
                                Text("Approve & Run")
                                    .font(.system(size: 14, weight: .bold))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                                    .background(Color.green.opacity(0.12))
                                    .foregroundColor(.green)
                                    .cornerRadius(6)
                                    .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.green.opacity(0.25), lineWidth: 1))
                            }
                            .buttonStyle(.plain)
                        }
                        .padding(.top, 4)
                    } else {
                        HStack {
                            Spacer()
                            Text(status == "approved" ? "✅ Execution Approved" : "❌ Execution Rejected")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundColor(status == "approved" ? .green : .red)
                            Spacer()
                        }
                        .padding(.top, 4)
                    }
                }
                .padding(14)
            }
            .background(Color(hex: 0x1A1A1A))
            .cornerRadius(12)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.white.opacity(0.08), lineWidth: 1))
            .frame(maxWidth: 550, alignment: .leading)
            .shadow(color: Color.black.opacity(0.2), radius: 8, x: 0, y: 4)
            
            Spacer(minLength: 36)
        }
        .padding(.top, 8)
    }
    
    private func handleDecision(_ approved: Bool) {
        guard status == "pending" else { return }
        status = approved ? "approved" : "rejected"
        socketClient.sendApprovalResponse(id: message.header ?? "", approved: approved)
    }
}

private struct AssistantMessageView: View {
    let text: String
    let shouldAnimate: Bool

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 10) {
                if shouldAnimate {
                    StreamingRichAssistantMessage(text: text)
                } else {
                    RichAssistantMessage(text: text)
                }
            }
            .padding(.horizontal, 15)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(Color(hex: 0x121316))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            .frame(maxWidth: 660, alignment: .leading)
            Spacer(minLength: 36)
        }
    }
}

private struct StreamingRichAssistantMessage: View {
    let text: String

    @State private var visibleTokenCount = 0
    @State private var streamTask: Task<Void, Never>?

    var body: some View {
        let tokens = StreamTokenizer.tokens(from: text)
        let visibleText = tokens.prefix(visibleTokenCount).joined()

        RichAssistantMessage(text: visibleText)
            .onAppear {
                streamTokens(total: tokens.count)
            }
            .onChange(of: text) { _ in
                streamTokens(total: tokens.count)
            }
            .onDisappear {
                streamTask?.cancel()
                streamTask = nil
            }
    }

    private func streamTokens(total: Int) {
        guard total > 0 else { return }
        streamTask?.cancel()
        visibleTokenCount = 0

        streamTask = Task {
            var index = 0
            while index < total, !Task.isCancelled {
                index = min(total, index + streamingBatchSize(total: total, current: index))
                await MainActor.run {
                    visibleTokenCount = index
                }
                try? await Task.sleep(nanoseconds: 12_000_000)
            }
        }
    }

    private func streamingBatchSize(total: Int, current: Int) -> Int {
        if total <= 120 { return 1 }
        let progress = Double(current) / Double(max(total, 1))
        if total > 500 { return progress > 0.65 ? 5 : 4 }
        if total > 260 { return progress > 0.65 ? 4 : 3 }
        return progress > 0.65 ? 3 : 2
    }
}

private struct ButterStreamText: View {
    let text: String
    var completion: (() -> Void)? = nil

    @State private var visibleTokenCount = 0
    @State private var didStart = false
    @State private var streamTask: Task<Void, Never>?

    var body: some View {
        let tokens = StreamTokenizer.tokens(from: text)

        Text(tokens.prefix(visibleTokenCount).joined())
            .opacity(visibleTokenCount == 0 ? 0 : 1)
            .offset(x: visibleTokenCount == 0 ? -4 : 0)
            .animation(.easeOut(duration: 0.12), value: visibleTokenCount)
            .frame(maxWidth: .infinity, alignment: .leading)
            .onAppear {
                guard !didStart else { return }
                didStart = true
                streamTokens(total: tokens.count)
            }
            .onChange(of: text) { _ in
                if didStart {
                    visibleTokenCount = 0
                    streamTokens(total: tokens.count)
                }
            }
            .onDisappear {
                streamTask?.cancel()
                streamTask = nil
            }
    }

    private func streamTokens(total: Int) {
        guard total > 0 else {
            completion?()
            return
        }

        streamTask?.cancel()
        streamTask = Task {
            var index = 0
            while index < total, !Task.isCancelled {
                let batch = streamingBatchSize(total: total, current: index)
                index = min(total, index + batch)
                await MainActor.run {
                    visibleTokenCount = index
                }
                try? await Task.sleep(nanoseconds: 12_000_000)
            }
            await MainActor.run {
                completion?()
            }
        }
    }

    private func streamingBatchSize(total: Int, current: Int) -> Int {
        if total <= 120 { return 1 }
        let progress = Double(current) / Double(max(total, 1))
        if total > 500 {
            return progress > 0.65 ? 5 : 4
        }
        if total > 260 {
            return progress > 0.65 ? 4 : 3
        }
        return progress > 0.65 ? 3 : 2
    }
}

private struct StateShimmerIndicatorView: View {
    let label: String
    @State private var pulse = false

    var body: some View {
        HStack {
            HStack(spacing: 8) {
                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.95))
                        .frame(width: 9, height: 9)
                        .scaleEffect(pulse ? 1.0 : 0.8)

                    Circle()
                        .stroke(Color.white.opacity(0.35), lineWidth: 1)
                        .frame(width: 9, height: 9)
                        .scaleEffect(pulse ? 2.0 : 1.0)
                        .opacity(pulse ? 0.0 : 0.75)
                }
                .animation(.easeInOut(duration: 1.18).repeatForever(autoreverses: true), value: pulse)

                ShimmerText(text: label, color: .white.opacity(0.9), shimmering: true)
                    .font(.system(size: 15, weight: .regular))
            }
            Spacer()
        }
        .onAppear {
            pulse = true
        }
    }
}

// MARK: - Heartbeat Progress Stack (Agentic Real-Time Activity)

private struct HeartbeatStackView: View {
    let steps: [HeartbeatStep]

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            ForEach(steps) { step in
                HeartbeatStepRow(step: step)
            }
        }
        .padding(.vertical, 4)
        .animation(.easeInOut(duration: 0.2), value: steps.count)
    }
}

private struct HeartbeatStepRow: View {
    let step: HeartbeatStep
    @State private var pulse = false

    private var icon: String {
        switch step.status {
        case .active, .thinking:
            return "circle.fill"
        case .success:
            return "checkmark.circle.fill"
        case .failed:
            return "xmark.circle.fill"
        case .clear:
            return "circle"
        }
    }

    private var iconColor: Color {
        switch step.status {
        case .active:
            return .cyan.opacity(0.95)
        case .thinking:
            return .white.opacity(0.5)
        case .success:
            return .green.opacity(0.9)
        case .failed:
            return .red.opacity(0.9)
        case .clear:
            return .gray.opacity(0.4)
        }
    }

    var body: some View {
        HStack(spacing: 8) {
            ZStack {
                Image(systemName: icon)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(iconColor)
                    .scaleEffect(step.status == .active && pulse ? 1.15 : 1.0)

                if step.status == .active {
                    Circle()
                        .stroke(iconColor.opacity(0.4), lineWidth: 1)
                        .frame(width: 16, height: 16)
                        .scaleEffect(pulse ? 1.8 : 1.0)
                        .opacity(pulse ? 0.0 : 0.6)
                }
            }
            .frame(width: 16, height: 16)
            .animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: pulse)

            if step.status == .active || step.status == .thinking {
                ShimmerText(
                    text: step.label,
                    color: step.status == .thinking ? .white.opacity(0.5) : .white.opacity(0.85),
                    shimmering: step.status == .active
                )
                .font(.system(size: 13, weight: .regular))
            } else {
                Text(step.label)
                    .font(.system(size: 13, weight: .regular))
                    .foregroundColor(step.status == .success ? .white.opacity(0.6) : .red.opacity(0.75))
                    .strikethrough(step.status == .failed, color: .red.opacity(0.4))
            }

            Spacer()

            if step.totalSteps > 0 {
                Text("\(step.stepIndex + 1)/\(step.totalSteps)")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.3))
            }
        }
        .padding(.horizontal, 4)
        .onAppear {
            if step.status == .active {
                pulse = true
            }
        }
    }
}

// MARK: - Inline Plan Card (Plan Mode UI)

private struct InlinePlanCard: View {
    let plan: PlanPayload
    let onApprove: () -> Void
    let onReject: () -> Void

    @State private var expanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack(spacing: 10) {
                Image(systemName: "doc.text.magnifyingglass")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.cyan)

                VStack(alignment: .leading, spacing: 2) {
                    Text("Implementation Plan")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                    Text(plan.goal)
                        .font(.system(size: 11, weight: .regular))
                        .foregroundColor(.white.opacity(0.55))
                        .lineLimit(1)
                }

                Spacer()

                Text("\(plan.steps.count) steps")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(.cyan.opacity(0.7))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Color.cyan.opacity(0.1))
                    .clipShape(Capsule())

                Button(action: { withAnimation(.easeInOut(duration: 0.2)) { expanded.toggle() } }) {
                    Image(systemName: expanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.4))
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 12)

            // Steps list (collapsible)
            if expanded {
                Divider().background(Color.white.opacity(0.08))

                VStack(alignment: .leading, spacing: 0) {
                    ForEach(plan.steps) { step in
                        HStack(alignment: .top, spacing: 10) {
                            // Step number circle
                            ZStack {
                                Circle()
                                    .fill(Color.cyan.opacity(0.15))
                                    .frame(width: 22, height: 22)
                                Text("\(step.number)")
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                    .foregroundColor(.cyan)
                            }

                            VStack(alignment: .leading, spacing: 3) {
                                Text(step.title)
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.white.opacity(0.9))

                                HStack(spacing: 6) {
                                    Label(step.tool, systemImage: "wrench.adjustable")
                                        .font(.system(size: 10, weight: .regular))
                                        .foregroundColor(.white.opacity(0.4))
                                }
                            }

                            Spacer()
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)

                        if step.number < plan.steps.count {
                            Divider().background(Color.white.opacity(0.05)).padding(.leading, 48)
                        }
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }

            Divider().background(Color.white.opacity(0.08))

            // Approve / Reject buttons
            HStack(spacing: 8) {
                Button(action: onReject) {
                    HStack(spacing: 5) {
                        Image(systemName: "xmark")
                            .font(.system(size: 11, weight: .semibold))
                        Text("Reject")
                            .font(.system(size: 12, weight: .medium))
                    }
                    .foregroundColor(.red.opacity(0.85))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 9)
                    .background(Color.red.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.red.opacity(0.2), lineWidth: 1))
                }
                .buttonStyle(.plain)

                Button(action: onApprove) {
                    HStack(spacing: 5) {
                        Image(systemName: "checkmark")
                            .font(.system(size: 11, weight: .semibold))
                        Text("Approve & Run")
                            .font(.system(size: 12, weight: .medium))
                    }
                    .foregroundColor(.green.opacity(0.95))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 9)
                    .background(Color.green.opacity(0.1))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.green.opacity(0.25), lineWidth: 1))
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
        }
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(
                            LinearGradient(
                                colors: [Color.cyan.opacity(0.35), Color.white.opacity(0.08)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            ),
                            lineWidth: 1
                        )
                )
        )
        .shadow(color: Color.cyan.opacity(0.12), radius: 16, x: 0, y: 4)
        .shadow(color: Color.black.opacity(0.4), radius: 10, x: 0, y: 6)
        .onAppear {
            // Auto-expand if ≤ 5 steps so user can see the plan immediately
            if plan.steps.count <= 5 { expanded = true }
        }
    }
}

private struct ShimmerText: View {
    let text: String
    let color: Color
    let shimmering: Bool

    @State private var shimmerOffset: CGFloat = -1.0

    var body: some View {
        Text(text)
            .foregroundColor(color.opacity(shimmering ? 0.78 : 1.0))
            .overlay {
                if shimmering {
                    GeometryReader { geometry in
                        let width = max(geometry.size.width, 1)
                        LinearGradient(
                            colors: [
                                color.opacity(0.0),
                                color.opacity(0.25),
                                color.opacity(1.0),
                                color.opacity(0.25),
                                color.opacity(0.0)
                            ],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                        .frame(width: width * 0.9)
                        .offset(x: shimmerOffset * width * 1.8)
                        .blendMode(.screen)
                        .onAppear {
                            shimmerOffset = -1.0
                            withAnimation(.linear(duration: 1.85).repeatForever(autoreverses: false)) {
                                shimmerOffset = 1.0
                            }
                        }
                    }
                    .mask(Text(text))
                }
            }
    }
}

private struct RichAssistantMessage: View {
    let text: String

    var body: some View {
        let segments = AssistantContentParser.parse(text)

        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(segments.enumerated()), id: \.offset) { _, segment in
                switch segment {
                case .markdown(let markdown):
                    MarkdownText(markdown: markdown)
                case .code(let block):
                    CodeBlockView(block: block)
                }
            }
        }
        .frame(maxWidth: 650, alignment: .leading)
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct MarkdownText: View {
    let markdown: String

    var body: some View {
        let blocks = MarkdownLayoutParser.parse(markdown)
        VStack(alignment: .leading, spacing: 11) {
            ForEach(Array(blocks.enumerated()), id: \.offset) { _, block in
                switch block {
                case .spacer:
                    Spacer().frame(height: 8)
                case .divider:
                    Rectangle()
                        .fill(Color.white.opacity(0.14))
                        .frame(height: 1)
                        .padding(.vertical, 8)
                case .heading(let level, let text):
                    InlineMarkdownText(
                        text: text,
                        font: .system(size: headingSize(for: level), weight: .bold),
                        color: .white.opacity(0.98),
                        autoStyle: false
                    )
                    .padding(.top, level <= 2 ? 6 : 2)
                case .paragraph(let text):
                    InlineMarkdownText(
                        text: text,
                        font: .system(size: 19, weight: .regular),
                        color: .white.opacity(0.95),
                        autoStyle: true
                    )
                    .padding(.bottom, 3)
                case .leadParagraph(let text):
                    InlineMarkdownText(
                        text: text,
                        font: .system(size: 21, weight: .regular),
                        color: .white.opacity(0.98),
                        autoStyle: true
                    )
                    .padding(.bottom, 8)
                case .bullet(let depth, let text):
                    HStack(alignment: .top, spacing: 8) {
                        Text("•")
                            .font(.system(size: 19, weight: .semibold))
                            .foregroundColor(.white.opacity(0.95))
                            .padding(.top, 1)
                        InlineMarkdownText(
                            text: text,
                            font: .system(size: 19, weight: .regular),
                            color: .white.opacity(0.95),
                            autoStyle: true
                        )
                    }
                    .padding(.leading, CGFloat(depth) * 18)
                case .numbered(let depth, let number, let text):
                    HStack(alignment: .top, spacing: 8) {
                        Text("\(number).")
                            .font(.system(size: 19, weight: .semibold))
                            .foregroundColor(.white.opacity(0.95))
                            .padding(.top, 1)
                        InlineMarkdownText(
                            text: text,
                            font: .system(size: 19, weight: .regular),
                            color: .white.opacity(0.95),
                            autoStyle: true
                        )
                    }
                    .padding(.leading, CGFloat(depth) * 18)
                case .keyValue(let label, let value):
                    HStack(alignment: .firstTextBaseline, spacing: 6) {
                        InlineMarkdownText(
                            text: "\(label):",
                            font: .system(size: 20, weight: .bold),
                            color: .white.opacity(0.98),
                            autoStyle: false
                        )
                        InlineMarkdownText(
                            text: value,
                            font: .system(size: 20, weight: .regular),
                            color: .white.opacity(0.95),
                            autoStyle: true
                        )
                    }
                case .table(let rows):
                    MarkdownTableView(rows: rows)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func headingSize(for level: Int) -> CGFloat {
        switch level {
        case 1: return 31
        case 2: return 26
        case 3: return 22
        default: return 19
        }
    }
}

private struct InlineMarkdownText: View {
    let text: String
    let font: Font
    let color: Color
    let autoStyle: Bool

    var body: some View {
        let rendered = autoStyle ? SmartMarkdownEnhancer.enhanceIfPlain(text) : text

        if let attributed = try? AttributedString(
            markdown: rendered,
            options: AttributedString.MarkdownParsingOptions(interpretedSyntax: .inlineOnlyPreservingWhitespace)
        ) {
            Text(attributed)
                .font(font)
                .foregroundColor(color)
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity, alignment: .leading)
        } else {
            Text(rendered)
                .font(font)
                .foregroundColor(color)
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct MarkdownTableView: View {
    let rows: [String]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            VStack(alignment: .leading, spacing: 0) {
                let parsedRows = rows.map { parseRow($0) }
                ForEach(Array(parsedRows.enumerated()), id: \.offset) { index, columns in
                    let isHeader = index == 0
                    let isDivider = isDividerRow(columns)
                    
                    if isDivider {
                        Rectangle()
                            .fill(Color.white.opacity(0.14))
                            .frame(height: 1)
                    } else {
                        HStack(spacing: 24) {
                            ForEach(Array(columns.enumerated()), id: \.offset) { colIndex, text in
                                Text(text)
                                    .font(.system(size: 15, weight: isHeader ? .bold : .regular, design: .monospaced))
                                    .foregroundColor(.white.opacity(isHeader ? 0.98 : 0.85))
                                    .frame(minWidth: 80, alignment: .leading)
                            }
                        }
                        .padding(.vertical, 10)
                        .padding(.horizontal, 16)
                        .background(
                            isHeader ? Color.white.opacity(0.08) : (index % 2 == 0 ? Color.clear : Color.white.opacity(0.03))
                        )
                    }
                }
            }
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .padding(.vertical, 8)
    }

    private func parseRow(_ row: String) -> [String] {
        let trimmed = row.trimmingCharacters(in: .whitespaces)
        var cols = trimmed.components(separatedBy: "|").map { $0.trimmingCharacters(in: .whitespaces) }
        if cols.first == "" { cols.removeFirst() }
        if cols.last == "" && !cols.isEmpty { cols.removeLast() }
        return cols
    }

    private func isDividerRow(_ cols: [String]) -> Bool {
        return cols.contains { $0.contains("---") }
    }
}

private enum SmartMarkdownEnhancer {
    static func enhanceIfPlain(_ text: String) -> String {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return text }
        if containsMarkdown(trimmed) { return text }
        if containsProtectedContent(trimmed) { return text }
        if trimmed.count > 120 { return text }
        if sentenceCount(in: trimmed) > 1 { return text }

        let mutable = NSMutableString(string: text)

        // Temporal context only. Keep auto-bold very conservative.
        applyBold(pattern: #"(?i)\bAs of\s+\d{4}\b"#, in: mutable)
        applyBold(pattern: #"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b"#, in: mutable)
        applyBold(pattern: #"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b"#, in: mutable)

        return mutable as String
    }

    private static func containsMarkdown(_ text: String) -> Bool {
        let markers = ["**", "__", "`", "](", "http://", "https://", "###", "## ", "# ", "- ", "* ", "1. "]
        return markers.contains { text.contains($0) }
    }

    private static func containsProtectedContent(_ text: String) -> Bool {
        // Skip auto-enhancement in content that is sensitive to symbol placement.
        text.contains("°") || text.contains("%") || text.contains("://")
    }

    private static func sentenceCount(in text: String) -> Int {
        text.split(whereSeparator: { ".!?".contains($0) }).filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }.count
    }

    private static func applyBold(pattern: String, in text: NSMutableString) {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else { return }
        let fullRange = NSRange(location: 0, length: text.length)
        let matches = regex.matches(in: text as String, options: [], range: fullRange)

        for match in matches.reversed() {
            let range = match.range
            guard range.location != NSNotFound, range.length > 0 else { continue }
            guard !isAlreadyBoldWrapped(text, range: range) else { continue }
            text.insert("**", at: range.location + range.length)
            text.insert("**", at: range.location)
        }
    }

    private static func isAlreadyBoldWrapped(_ text: NSString, range: NSRange) -> Bool {
        let hasPrefix = range.location >= 2 && text.substring(with: NSRange(location: range.location - 2, length: 2)) == "**"
        let suffixIndex = range.location + range.length
        let hasSuffix = suffixIndex + 2 <= text.length && text.substring(with: NSRange(location: suffixIndex, length: 2)) == "**"
        return hasPrefix && hasSuffix
    }
}

private enum MarkdownBlock: Equatable {
    case heading(Int, String)
    case leadParagraph(String)
    case bullet(Int, String)
    case numbered(Int, Int, String)
    case keyValue(String, String)
    case paragraph(String)
    case divider
    case spacer
    case table([String])
}

private enum MarkdownLayoutParser {
    static func parse(_ markdown: String) -> [MarkdownBlock] {
        let normalized = normalize(markdown)
        let lines = normalized.replacingOccurrences(of: "\r\n", with: "\n").components(separatedBy: "\n")
        var blocks: [MarkdownBlock] = []
        var emittedTextBlockCount = 0
        var paragraphBuffer: [String] = []
        var tableBuffer: [String] = []

        func flushTable() {
            if !tableBuffer.isEmpty {
                blocks.append(.table(tableBuffer))
                tableBuffer.removeAll(keepingCapacity: true)
            }
        }

        func flushParagraph() {
            let merged = paragraphBuffer.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
            if !merged.isEmpty {
                if emittedTextBlockCount == 0 && sentenceCount(in: merged) <= 2 && merged.count > 60 {
                    blocks.append(.leadParagraph(merged))
                } else {
                    blocks.append(.paragraph(merged))
                }
                emittedTextBlockCount += 1
            }
            paragraphBuffer.removeAll(keepingCapacity: true)
        }

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty {
                flushParagraph()
                flushTable()
                if blocks.last != .spacer {
                    blocks.append(.spacer)
                }
                continue
            }

            if isTableRow(trimmed) {
                flushParagraph()
                tableBuffer.append(trimmed)
                continue
            } else {
                flushTable()
            }

            if let heading = parseHeading(trimmed) {
                flushParagraph()
                blocks.append(.heading(heading.level, heading.text))
                continue
            }

            if isDisplayHeading(trimmed) {
                flushParagraph()
                blocks.append(.heading(3, trimmed))
                emittedTextBlockCount += 1
                continue
            }

            if let keyValue = parseKeyValue(trimmed) {
                flushParagraph()
                blocks.append(.keyValue(keyValue.label, keyValue.value))
                emittedTextBlockCount += 1
                continue
            }

            if isDivider(trimmed) {
                flushParagraph()
                if blocks.last != .divider {
                    blocks.append(.divider)
                }
                continue
            }

            if let bullet = parseBullet(line) {
                flushParagraph()
                blocks.append(.bullet(bullet.depth, bullet.text))
                continue
            }

            if let numbered = parseNumbered(line) {
                flushParagraph()
                blocks.append(.numbered(numbered.depth, numbered.number, numbered.text))
                continue
            }

            paragraphBuffer.append(trimmed)
        }

        flushParagraph()
        flushTable()
        while blocks.last == .spacer {
            blocks.removeLast()
        }
        return blocks
    }

    private static func parseHeading(_ line: String) -> (level: Int, text: String)? {
        let candidate = line.trimmingCharacters(in: .whitespaces)
        var level = 0
        for char in candidate {
            if char == "#" { level += 1 } else { break }
        }
        guard level > 0, level <= 6 else { return nil }
        let text = candidate.dropFirst(level).trimmingCharacters(in: .whitespaces)
        return text.isEmpty ? nil : (level, text)
    }

    private static func parseBullet(_ line: String) -> (depth: Int, text: String)? {
        let leadingSpaces = line.prefix { $0 == " " }.count
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        let prefixes = ["- ", "* ", "• "]
        guard let prefix = prefixes.first(where: { trimmed.hasPrefix($0) }) else { return nil }
        let text = String(trimmed.dropFirst(prefix.count)).trimmingCharacters(in: .whitespaces)
        return text.isEmpty ? nil : (leadingSpaces / 2, text)
    }

    private static func parseNumbered(_ line: String) -> (depth: Int, number: Int, text: String)? {
        let leadingSpaces = line.prefix { $0 == " " }.count
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        let pattern = #"^([0-9]+)[\.\)]\s+(.+)$"#
        guard let regex = try? NSRegularExpression(pattern: pattern),
              let match = regex.firstMatch(in: trimmed, range: NSRange(location: 0, length: (trimmed as NSString).length)),
              match.numberOfRanges == 3 else { return nil }

        let ns = trimmed as NSString
        let numText = ns.substring(with: match.range(at: 1))
        let bodyText = ns.substring(with: match.range(at: 2)).trimmingCharacters(in: .whitespaces)
        guard let number = Int(numText), !bodyText.isEmpty else { return nil }
        guard number > 0 && number <= 50 else { return nil }

        // Avoid false list parsing for weather/measurement/value lines like "2. 24°C" or "2. and ..."
        guard let first = bodyText.first else { return nil }
        let validListStart = first.isUppercase || first == "[" || first == "(" || first == "`" || first == "*"
        guard validListStart else { return nil }

        return (leadingSpaces / 2, number, bodyText)
    }

    private static func normalize(_ markdown: String) -> String {
        markdown
            .replacingOccurrences(of: "\\r\\n", with: "\n")
            .replacingOccurrences(of: "\\n", with: "\n")
            .replacingOccurrences(of: "\\t", with: "\t")
    }

    private static func isTableRow(_ line: String) -> Bool {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        return trimmed.hasPrefix("|") && trimmed.contains("|") && trimmed.count > 3
    }

    private static func isDivider(_ line: String) -> Bool {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        guard trimmed.count >= 3 else { return false }
        return Set(trimmed).isSubset(of: ["-", "*", "_"])
    }

    private static func isDisplayHeading(_ line: String) -> Bool {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        if trimmed.count < 8 || trimmed.count > 90 { return false }
        if trimmed.hasSuffix(".") { return false }
        if parseBullet(trimmed) != nil || parseNumbered(trimmed) != nil { return false }

        let startsWithEmojiOrIcon = trimmed.unicodeScalars.first.map { scalar in
            scalar.properties.isEmojiPresentation || scalar.properties.generalCategory == .otherSymbol
        } ?? false

        let titleCaseWords = trimmed.split(separator: " ").filter { !$0.isEmpty }
        let likelyTitle = titleCaseWords.count <= 10

        return startsWithEmojiOrIcon && likelyTitle
    }

    private static func parseKeyValue(_ line: String) -> (label: String, value: String)? {
        let pattern = #"^([A-Za-z][A-Za-z0-9 /\-\(\)]{1,32}):\s+(.+)$"#
        guard let regex = try? NSRegularExpression(pattern: pattern),
              let match = regex.firstMatch(in: line, range: NSRange(location: 0, length: (line as NSString).length)),
              match.numberOfRanges == 3 else { return nil }
        let ns = line as NSString
        let label = ns.substring(with: match.range(at: 1)).trimmingCharacters(in: .whitespaces)
        let value = ns.substring(with: match.range(at: 2)).trimmingCharacters(in: .whitespaces)
        if value.hasPrefix("//") || value.hasPrefix("http") { return nil }
        return (label, value.isEmpty ? line : value)
    }

    private static func sentenceCount(in text: String) -> Int {
        text.split(whereSeparator: { ".!?".contains($0) }).filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }.count
    }

    // Removed plain-text auto paragraphizer because it introduced incorrect hard line breaks
    // for abbreviations and name-like sequences in normal responses.
}

private struct CodeBlockView: View {
    let block: AssistantCodeBlock

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let filename = block.filename, !filename.isEmpty {
                Text("✅ \(filename)")
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("<> \(block.languageDisplay)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.gray)

                    Spacer()

                    Button(action: { copyToClipboard(block.code) }) {
                        Image(systemName: "doc.on.doc")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.gray)
                    }
                    .buttonStyle(.plain)
                }

                ScrollView(.horizontal, showsIndicators: false) {
                    SyntaxHighlightText(code: block.code)
                        .font(.system(.body, design: .monospaced))
                        .padding(.bottom, 2)
                }
            }
            .padding(12)
            .background(Color(hex: 0x1A1A1A))
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
    }

    private func copyToClipboard(_ text: String) {
        #if canImport(AppKit)
        let board = NSPasteboard.general
        board.clearContents()
        board.setString(text, forType: .string)
        #elseif canImport(UIKit)
        UIPasteboard.general.string = text
        #endif
    }
}

private struct SyntaxHighlightText: View {
    let code: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            ForEach(Array(code.split(separator: "\n", omittingEmptySubsequences: false).enumerated()), id: \.offset) { _, line in
                HStack(spacing: 0) {
                    let tokens = CodeSyntaxTokenizer.tokenize(String(line))
                    ForEach(Array(tokens.enumerated()), id: \.offset) { _, token in
                        Text(token.text)
                            .foregroundColor(token.color)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .textSelection(.enabled)
    }
}

private struct ChatInputBar: View {
    @EnvironmentObject var socketClient: SocketClient
    let placeholder: String
    @Binding var inputText: String
    @Binding var isWebSearchEnabled: Bool
    let sendMessage: () -> Void

    @State private var pulse = false

    var body: some View {
        HStack(spacing: 10) {
            MiniJarvisCore()
                .frame(width: 28, height: 28)

            PlainInputField(
                text: $inputText,
                placeholder: placeholder,
                onSubmit: sendMessage
            )
            .frame(maxWidth: .infinity)

            Button(action: { isWebSearchEnabled.toggle() }) {
                Image(systemName: isWebSearchEnabled ? "globe" : "mic")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(isWebSearchEnabled ? .cyan : .white.opacity(0.85))
                    .frame(width: 30, height: 30)
            }
            .buttonStyle(.plain)

            Button(action: { socketClient.toggleAgenticMode() }) {
                Image(systemName: "cpu")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(socketClient.isAgenticModeEnabled ? .orange : .white.opacity(0.85))
                    .frame(width: 30, height: 30)
                    .shadow(color: socketClient.isAgenticModeEnabled ? .orange.opacity(0.5) : .clear, radius: 4)
                    .opacity(socketClient.isConnected ? (socketClient.isAgenticModeTransitionPending ? 0.6 : 1.0) : 0.4)
            }
            .buttonStyle(.plain)
            .disabled(!socketClient.isConnected || socketClient.isAgenticModeTransitionPending)

            // Plan Mode button — sends __PLAN_MODE__ prefix to trigger plan generation
            Button(action: {
                let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !text.isEmpty else { return }
                socketClient.send(text: "__PLAN_MODE__ \(text)", webSearch: false)
                inputText = ""
            }) {
                Image(systemName: "doc.text.magnifyingglass")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                        ? .white.opacity(0.3) : .cyan.opacity(0.9))
                    .frame(width: 30, height: 30)
            }
            .buttonStyle(.plain)
            .disabled(!socketClient.isConnected || inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            .help("Generate a Plan before executing")

            Button(action: sendMessage) {
                ZStack {
                    Circle()
                        .fill(Color.white)
                        .frame(width: 34, height: 34)
                        .scaleEffect(pulse ? 1.0 : 0.92)
                        .animation(.easeInOut(duration: 0.85).repeatForever(autoreverses: true), value: pulse)

                    Image(systemName: inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "waveform" : "arrow.up")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.black)
                }
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color(hex: 0x1E1E1E))
        .clipShape(Capsule())
        .overlay(
            Capsule()
                .stroke(Color.white.opacity(0.10), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.35), radius: 8, x: 0, y: 4)
        .onAppear {
            pulse = true
        }
    }
}

private struct PlainInputField: View {
    @Binding var text: String
    let placeholder: String
    let onSubmit: () -> Void

    var body: some View {
        #if canImport(AppKit)
        NoFocusRingTextField(text: $text, placeholder: placeholder, onSubmit: onSubmit)
            .frame(height: 24)
        #else
        TextField("", text: $text, prompt: Text(placeholder).foregroundColor(.gray.opacity(0.8)))
            .textFieldStyle(.plain)
            .font(.system(size: 19))
            .foregroundColor(.white)
            .onSubmit { onSubmit() }
        #endif
    }
}

#if canImport(AppKit)
private struct NoFocusRingTextField: NSViewRepresentable {
    @Binding var text: String
    let placeholder: String
    let onSubmit: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(text: $text, onSubmit: onSubmit)
    }

    func makeNSView(context: Context) -> NSTextField {
        let field = NSTextField(string: text)
        field.delegate = context.coordinator
        field.isBordered = false
        field.isBezeled = false
        field.drawsBackground = false
        field.focusRingType = .none
        field.textColor = .white
        field.placeholderString = placeholder
        field.font = .systemFont(ofSize: 19, weight: .regular)
        field.lineBreakMode = .byTruncatingTail
        field.usesSingleLineMode = true
        return field
    }

    func updateNSView(_ nsView: NSTextField, context: Context) {
        if nsView.stringValue != text {
            nsView.stringValue = text
        }
        nsView.placeholderString = placeholder
    }

    final class Coordinator: NSObject, NSTextFieldDelegate {
        @Binding var text: String
        let onSubmit: () -> Void

        init(text: Binding<String>, onSubmit: @escaping () -> Void) {
            _text = text
            self.onSubmit = onSubmit
        }

        func controlTextDidChange(_ obj: Notification) {
            guard let field = obj.object as? NSTextField else { return }
            text = field.stringValue
        }

        func control(_ control: NSControl, textView: NSTextView, doCommandBy commandSelector: Selector) -> Bool {
            if commandSelector == #selector(NSResponder.insertNewline(_:)) {
                onSubmit()
                return true
            }
            return false
        }
    }
}
#endif

private struct MiniJarvisCore: View {
    @State private var rot1: Double = 0
    @State private var rot2: Double = 0
    @State private var pulse: CGFloat = 1.0

    var body: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            Color.hologramCyan.opacity(0.45),
                            Color.hologramBlue.opacity(0.28),
                            .clear
                        ],
                        center: .center,
                        startRadius: 1,
                        endRadius: 22
                    )
                )
                .blur(radius: 3)

            Circle()
                .fill(
                    AngularGradient(
                        colors: [
                            Color.hologramBlue,
                            Color.hologramCyan,
                            Color.hologramDeepBlue,
                            Color.hologramBlue
                        ],
                        center: .center
                    )
                )
                .rotationEffect(.degrees(rot1))
                .blur(radius: 1.8)

            Circle()
                .fill(
                    AngularGradient(
                        colors: [
                            .clear,
                            Color.white.opacity(0.75),
                            .clear,
                            Color.hologramCyan.opacity(0.4)
                        ],
                        center: .center
                    )
                )
                .rotationEffect(.degrees(rot2))
                .blendMode(.screen)
                .blur(radius: 1.3)
                .scaleEffect(0.78)
        }
        .scaleEffect(pulse)
        .shadow(color: .hologramCyan.opacity(0.55), radius: 8)
        .onAppear {
            withAnimation(.linear(duration: 4.2).repeatForever(autoreverses: false)) {
                rot1 = 360
            }
            withAnimation(.linear(duration: 2.8).repeatForever(autoreverses: false)) {
                rot2 = -360
            }
            withAnimation(.easeInOut(duration: 1.8).repeatForever(autoreverses: true)) {
                pulse = 1.07
            }
        }
    }
}

private enum AssistantSegment: Equatable {
    case markdown(String)
    case code(AssistantCodeBlock)
}

private struct AssistantCodeBlock: Equatable {
    let languageDisplay: String
    let code: String
    let filename: String?
}

private enum AssistantContentParser {
    static func parse(_ text: String) -> [AssistantSegment] {
        if !text.contains("```") {
            return [.markdown(text)]
        }

        let chunks = text.components(separatedBy: "```")
        var segments: [AssistantSegment] = []
        var pendingFilename: String?

        for index in chunks.indices {
            let chunk = chunks[index]

            if index % 2 == 0 {
                var markdown = chunk
                if index + 1 < chunks.count {
                    let extracted = extractTrailingFilename(from: markdown)
                    markdown = extracted.cleanedMarkdown
                    if let filename = extracted.filename {
                        pendingFilename = filename
                    }
                }

                if !markdown.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    segments.append(.markdown(markdown))
                }
            } else {
                let lines = chunk.split(separator: "\n", omittingEmptySubsequences: false)
                var language = "Code"
                var bodyStart = 0

                if let first = lines.first,
                   String(first).range(of: "^[A-Za-z0-9_+#.-]+$", options: .regularExpression) != nil {
                    language = String(first).capitalized
                    bodyStart = 1
                }

                let code = lines.dropFirst(bodyStart).joined(separator: "\n")
                    .trimmingCharacters(in: .newlines)

                segments.append(
                    .code(
                        AssistantCodeBlock(
                            languageDisplay: language,
                            code: code,
                            filename: pendingFilename
                        )
                    )
                )
                pendingFilename = nil
            }
        }

        return segments
    }

    private static func extractTrailingFilename(from markdown: String) -> (cleanedMarkdown: String, filename: String?) {
        let lines = markdown.components(separatedBy: "\n")
        guard let lastIndex = lines.lastIndex(where: { !$0.trimmingCharacters(in: .whitespaces).isEmpty }) else {
            return (markdown, nil)
        }

        let lastLine = lines[lastIndex].trimmingCharacters(in: .whitespaces)
        guard lastLine.hasPrefix("✅") else {
            return (markdown, nil)
        }

        let filename = lastLine.replacingOccurrences(of: "✅", with: "")
            .trimmingCharacters(in: .whitespaces)

        var mutable = lines
        mutable.remove(at: lastIndex)

        return (mutable.joined(separator: "\n"), filename.isEmpty ? nil : filename)
    }
}

private struct SyntaxToken {
    let text: String
    let color: Color
}

private enum CodeSyntaxTokenizer {
    private static let keywords: Set<String> = [
        "class", "struct", "func", "var", "let", "if", "else", "for", "while", "return",
        "import", "private", "public", "internal", "enum", "switch", "case", "break", "continue",
        "guard", "in", "try", "catch", "throw", "async", "await", "true", "false", "nil"
    ]

    static func tokenize(_ line: String) -> [SyntaxToken] {
        let ns = line as NSString
        let regex = try? NSRegularExpression(pattern: "\\\"(?:\\\\.|[^\\\"])*\\\"|\\b[A-Za-z_][A-Za-z0-9_]*\\b|\\s+|.", options: [])
        let matches = regex?.matches(in: line, options: [], range: NSRange(location: 0, length: ns.length)) ?? []

        return matches.map { match in
            let token = ns.substring(with: match.range)
            return SyntaxToken(text: token, color: color(for: token))
        }
    }

    private static func color(for token: String) -> Color {
        if token.first == "\"" && token.last == "\"" {
            return Color(hex: 0xFF9E64)
        }

        if keywords.contains(token) {
            return Color(hex: 0xD36BFF)
        }

        if token.first?.isUppercase == true {
            return Color(hex: 0x4EC9B0)
        }

        return .white.opacity(0.92)
    }
}

private enum StreamTokenizer {
    static func tokens(from text: String) -> [String] {
        let ns = text as NSString
        let pattern = "\\s+|[\\p{L}\\p{N}_]+|[^\\s\\p{L}\\p{N}_]"
        let regex = try? NSRegularExpression(pattern: pattern, options: [])
        let matches = regex?.matches(in: text, options: [], range: NSRange(location: 0, length: ns.length)) ?? []

        if matches.isEmpty {
            return text.isEmpty ? [] : [text]
        }
        return matches.map { ns.substring(with: $0.range) }
    }
}

private extension Color {
    init(hex: UInt32, alpha: Double = 1.0) {
        self.init(
            .sRGB,
            red: Double((hex >> 16) & 0xFF) / 255.0,
            green: Double((hex >> 8) & 0xFF) / 255.0,
            blue: Double(hex & 0xFF) / 255.0,
            opacity: alpha
        )
    }
}

// MARK: - Settings Sidebar
struct SettingsSidebar: View {
    @Binding var forceBuiltInAudio: Bool
    @Binding var showSettingsSidebar: Bool
    @EnvironmentObject var socketClient: SocketClient

    var body: some View {
        ZStack(alignment: .trailing) {
            Color.black.opacity(0.4)
                .ignoresSafeArea()
                .onTapGesture {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                        showSettingsSidebar = false
                    }
                }

            HStack(spacing: 0) {
                Spacer()

                VStack(alignment: .leading, spacing: 24) {
                    HStack {
                        Text("Settings")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.white)
                        Spacer()
                        Button(action: {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                                showSettingsSidebar = false
                            }
                        }) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(size: 20))
                                .foregroundColor(.white.opacity(0.6))
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.top, 24)
                    .padding(.horizontal, 24)

                    Divider().background(Color.white.opacity(0.1))

                    VStack(alignment: .leading, spacing: 12) {
                        Toggle("Force Mac Built-in Audio", isOn: $forceBuiltInAudio)
                            .toggleStyle(SwitchToggleStyle(tint: .blue))
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                            .onChange(of: forceBuiltInAudio) { newValue in
                                socketClient.setForceAudioStrategy(newValue)
                            }
                        
                        Text("When enabled, Jarvis bypasses your Bluetooth default and forces the physical Mac microphone and speakers. Prevents call interruptions!")
                            .font(.system(size: 13))
                            .foregroundColor(.white.opacity(0.5))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(.horizontal, 24)

                    Spacer()
                }
                .frame(width: 320)
                .background(Color(hex: 0x1A1A1E).ignoresSafeArea())
                .shadow(color: .black.opacity(0.5), radius: 20, x: -10, y: 0)
            }
        }
    }
}
