import SwiftUI

extension Color {
    // Apple Native / Glass Colors
    static let glassPanel = Color.black.opacity(0.4) // Dark Mode Glass
    static let glassBorder = Color.white.opacity(0.1)
    static let glassTextPrimary = Color.white.opacity(0.9)
    static let glassTextSecondary = Color.white.opacity(0.6)
    
    // Accent Colors (Subtle/iOS style)
    static let appleBlue = Color(red: 0.0, green: 122.0/255.0, blue: 1.0)
    static let appleCyan = Color(red: 50.0/255.0, green: 173.0/255.0, blue: 230.0/255.0)
    static let appleMint = Color(red: 0.0, green: 199.0/255.0, blue: 190.0/255.0)
    
    // Legacy mapping (for compatibility, mapped to new colors)
    static let ironManCyan = appleCyan
    static let ironManBlue = appleBlue
    static let ironManGold = Color.orange
    static let ironManRed = Color.red
    static let hudBlack = Color.black
    
    // New Reactor Colors (Holographic FUI)
    static let hologramCyan = Color(red: 0.2, green: 1.0, blue: 1.0)
    static let hologramBlue = Color(red: 0.0, green: 0.6, blue: 1.0)
    static let hologramDeepBlue = Color(red: 0.0, green: 0.1, blue: 0.3)
    // Pure light colors
    static let coreWhite = Color(white: 1.0)
}

struct GlassModifier: ViewModifier {
    var cornerRadius: CGFloat = 20
    
    func body(content: Content) -> some View {
        content
            .background(.thinMaterial) // SwiftUI Native Glass Material
            .cornerRadius(cornerRadius)
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .stroke(Color.white.opacity(0.2), lineWidth: 0.5)
            )
            .shadow(color: Color.black.opacity(0.2), radius: 10, x: 0, y: 5)
    }
}

extension View {
    func glass(cornerRadius: CGFloat = 20) -> some View {
        self.modifier(GlassModifier(cornerRadius: cornerRadius))
    }
    
    func glow(color: Color = .appleCyan, radius: CGFloat = 5) -> some View {
        self.shadow(color: color.opacity(0.5), radius: radius, x: 0, y: 0)
    }
}
