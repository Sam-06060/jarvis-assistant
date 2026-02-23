import SwiftUI

struct ArcReactorView: View {
    var isConnected: Bool
    var isSpeaking: Bool
    
    // Animation States
    @State private var plasmaRotation1: Double = 0
    @State private var plasmaRotation2: Double = 0
    @State private var plasmaRotation3: Double = 0
    @State private var corePulse: CGFloat = 1.0
    @State private var turbulence: CGFloat = 0.0
    
    @State private var voiceTimer: Timer?
    @State private var voiceIntensity: CGFloat = 0.0
    
    // Design Constants
    let coreSize: CGFloat = 220
    
    var body: some View {
        ZStack {
            // === AMBIENT GLOW BACKDROP ===
            Circle()
                .fill(
                    RadialGradient(
                        gradient: Gradient(colors: [
                            Color.hologramBlue.opacity(0.3),
                            Color.hologramDeepBlue.opacity(0.2),
                            Color.clear
                        ]),
                        center: .center,
                        startRadius: 50,
                        endRadius: 250
                    )
                )
                .frame(width: 500, height: 500)
                .blur(radius: 40)
                .opacity(isConnected ? 1.0 : 0.3)
            
            // === FLUID PLASMA CORE ===
            // Multiple overlapping layers of angular gradients rotating at different speeds
            // create a "swirling liquid" effect when blurred.
            
            ZStack {
                // Layer 1: Deep Base (Slow)
                Circle()
                    .fill(
                        AngularGradient(
                            gradient: Gradient(colors: [
                                Color.hologramBlue, Color.hologramDeepBlue,
                                Color.hologramBlue, Color.clear
                            ]),
                            center: .center
                        )
                    )
                    .frame(width: coreSize, height: coreSize)
                    .rotationEffect(.degrees(plasmaRotation1))
                    .blur(radius: 20)
                
                // Layer 2: Bright Highlights (Medium)
                Circle()
                    .fill(
                        AngularGradient(
                            gradient: Gradient(colors: [
                                Color.clear, Color.hologramCyan,
                                Color.clear, Color.hologramCyan.opacity(0.5)
                            ]),
                            center: .center
                        )
                    )
                    .frame(width: coreSize - 20, height: coreSize - 20)
                    .rotationEffect(.degrees(plasmaRotation2))
                    .blur(radius: 15)
                    .blendMode(.screen) // Additive blending for light feel
                
                // Layer 3: White Hot Energy (Fast)
                Circle()
                    .fill(
                        AngularGradient(
                            gradient: Gradient(colors: [
                                Color.clear, Color.white.opacity(0.8),
                                Color.clear, Color.white.opacity(0.4)
                            ]),
                            center: .center
                        )
                    )
                    .frame(width: coreSize - 50, height: coreSize - 50)
                    .rotationEffect(.degrees(plasmaRotation3))
                    .blur(radius: 10)
                    .blendMode(.overlay)
                
                // === CONTAINMENT FIELD REMOVED ===
                // User requested pure plasma core.
                
                // Subtle HUD Markers REMOVED
            }
            .scaleEffect(corePulse)
            .shadow(color: .hologramCyan, radius: 20 + (voiceIntensity * 20)) // Bloom
            
            // Text Status
            VStack {
                 Spacer()
                    .frame(height: 280)
                // Text Status Removed - Managed by Parent View
            }
        }
        // Force the layout size to be smaller than the visual size (glow overflows)
        .frame(width: 300, height: 300)
        .onAppear {
            startIdleAnimations()
        }
        .onChange(of: isSpeaking) { speaking in
             if speaking {
                startVoiceActivity()
            } else {
                stopVoiceActivity()
            }
        }
    }
    
    // MARK: - Animations
    
    private func startIdleAnimations() {
        // Continuous Swirling
        withAnimation(.linear(duration: 10).repeatForever(autoreverses: false)) {
            plasmaRotation1 = 360
        }
        withAnimation(.linear(duration: 7).repeatForever(autoreverses: false)) {
            plasmaRotation2 = -360
        }
        withAnimation(.linear(duration: 5).repeatForever(autoreverses: false)) {
            plasmaRotation3 = 360
        }
        
        // Breathing
        withAnimation(.easeInOut(duration: 3).repeatForever(autoreverses: true)) {
            corePulse = 1.05
        }
    }
    
    private func startVoiceActivity() {
         voiceTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            withAnimation(.spring(response: 0.1, dampingFraction: 0.6)) {
                voiceIntensity = CGFloat.random(in: 0.3...1.0)
                // Turbulence effect: Randomize rotation offsets slightly or scale
                corePulse = 1.0 + (voiceIntensity * 0.15)
            }
        }
    }
    
    private func stopVoiceActivity() {
        voiceTimer?.invalidate()
        voiceTimer = nil
        withAnimation(.easeOut(duration: 0.5)) {
            voiceIntensity = 0.0
            corePulse = 1.0
        }
    }
}

struct ArcReactorView_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            ArcReactorView(isConnected: true, isSpeaking: true)
        }
    }
}
