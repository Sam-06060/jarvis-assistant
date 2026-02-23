import Cocoa
import Foundation

class NotchDetector {
    struct NotchInfo {
        let centerX: CGFloat
        let centerY: CGFloat  // This will be from TOP of screen
        let width: CGFloat
        let height: CGFloat
        let hasNotch: Bool
    }
    
    static func detect() -> NotchInfo {
        guard let screen = NSScreen.main else {
            // Fallback for no screen detected
            return NotchInfo(centerX: 0, centerY: 0, width: 0, height: 0, hasNotch: false)
        }
        
        let frame = screen.frame
        let visibleFrame = screen.visibleFrame
        
        // Calculate top inset (notch height)
        // macOS coordinate system: origin is bottom-left
        // visibleFrame.maxY is where the visible area ends (below menu bar/notch)
        // frame.maxY is the actual top of the screen
        let topInset = frame.maxY - visibleFrame.maxY
        
        // MacBook notch dimensions (Apple's standard)
        let hasNotch = topInset > 30  // If there's significant top inset, there's a notch
        
        // Notch dimensions (Apple's exact specs)
        let notchWidth: CGFloat = 126.0
        let notchHeight: CGFloat = hasNotch ? topInset : 37.0
        
        // CRITICAL FIX: Calculate from TOP of screen
        // In macOS coordinates, screen.frame.maxY is the TOP
        // We want the notch to be just below the very top edge
        
        let centerX = frame.width / 2
        let centerY = notchHeight / 2  // Distance from TOP edge (in layer coordinates)
        
        print("🔍 Screen Debug:")
        print("   Screen Height: \(frame.height)")
        print("   Notch Center Y (from top): \(centerY)")
        print("   Notch Width: \(notchWidth)")
        print("   Notch Height: \(notchHeight)")
        print("   Has Notch: \(hasNotch)")
        
        return NotchInfo(
            centerX: centerX,
            centerY: centerY,
            width: notchWidth,
            height: notchHeight,
            hasNotch: hasNotch
        )
    }
}
