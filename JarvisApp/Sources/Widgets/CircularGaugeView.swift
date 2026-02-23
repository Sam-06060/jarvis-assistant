import SwiftUI

struct CircularGaugeView: View {
    var value: Double // 0.0 to 1.0
    var label: String
    var color: Color = .ironManCyan
    
    var body: some View {
        VStack(spacing: 5) {
            ZStack {
                // Background Track
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 8)
                    .frame(width: 60, height: 60)
                
                // Value Arc
                Circle()
                    .trim(from: 0.0, to: CGFloat(min(self.value, 1.0)))
                    .stroke(color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .frame(width: 60, height: 60)
                    .rotationEffect(.degrees(-90))
                    .shadow(color: color.opacity(0.5), radius: 5)
                
                // Percentage Text
                Text("\(Int(value * 100))%")
                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                    .foregroundColor(color)
            }
            
            Text(label)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(color.opacity(0.8))
        }
    }
}
