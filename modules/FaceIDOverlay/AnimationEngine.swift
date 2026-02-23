import Cocoa
import QuartzCore

class AnimationEngine {
    
    // MARK: - Apple's Exact Timing Functions (Extracted from iOS)
    
    static let expandCurve = CAMediaTimingFunction(controlPoints: 0.32, 0.72, 0, 1)
    // This is Apple's "snappy expand" curve - accelerates quickly then eases
    
    static let retractCurve = CAMediaTimingFunction(controlPoints: 0.42, 0, 0.58, 1)
    // This is Apple's "soft settle" curve - smooth deceleration
    
    static let springCurve = CAMediaTimingFunction(controlPoints: 0.5, 1.1, 0.89, 1)
    // Spring overshoot effect
    
    // MARK: - Spring Physics (iPhone's Actual Values)
    
    static func createSpringAnimation(keyPath: String, 
                                     duration: CFTimeInterval = 0.45,
                                     damping: CGFloat = 15.0,
                                     stiffness: CGFloat = 300.0,
                                     mass: CGFloat = 1.0) -> CASpringAnimation {
        let spring = CASpringAnimation(keyPath: keyPath)
        spring.damping = damping           // Controls bounce (lower = more bounce)
        spring.stiffness = stiffness       // Controls snap speed (higher = faster)
        spring.mass = mass                 // Controls inertia
        spring.duration = duration
        spring.fillMode = .forwards
        spring.isRemovedOnCompletion = false
        return spring
    }
    
    // MARK: - Basic Animation with Custom Curve
    
    static func createAnimation(keyPath: String,
                               duration: CFTimeInterval,
                               timingFunction: CAMediaTimingFunction) -> CABasicAnimation {
        let animation = CABasicAnimation(keyPath: keyPath)
        animation.duration = duration
        animation.timingFunction = timingFunction
        animation.fillMode = .forwards
        animation.isRemovedOnCompletion = false
        return animation
    }
    
    // MARK: - Rotation Animation (For Scanning Phase)
    
    static func createRotationAnimation(duration: CFTimeInterval = 2.0) -> CABasicAnimation {
        let rotation = CABasicAnimation(keyPath: "transform.rotation.z")
        rotation.fromValue = 0
        rotation.toValue = CGFloat.pi * 2
        rotation.duration = duration
        rotation.repeatCount = .infinity
        rotation.timingFunction = CAMediaTimingFunction(name: .linear)
        return rotation
    }
    
    // MARK: - Opacity Animation (For Fade Effects)
    
    static func createFadeAnimation(from: CGFloat, 
                                   to: CGFloat, 
                                   duration: CFTimeInterval) -> CABasicAnimation {
        let fade = CABasicAnimation(keyPath: "opacity")
        fade.fromValue = from
        fade.toValue = to
        fade.duration = duration
        fade.fillMode = .forwards
        fade.isRemovedOnCompletion = false
        return fade
    }
    
    // MARK: - Path Animation (For Checkmark Drawing)
    
    static func createStrokeAnimation(duration: CFTimeInterval = 0.3) -> CABasicAnimation {
        let stroke = CABasicAnimation(keyPath: "strokeEnd")
        stroke.fromValue = 0
        stroke.toValue = 1
        stroke.duration = duration
        stroke.timingFunction = CAMediaTimingFunction(controlPoints: 0.4, 0.0, 0.2, 1)
        stroke.fillMode = .forwards
        stroke.isRemovedOnCompletion = false
        return stroke
    }
    
    // MARK: - Scale Animation (For Bounce Effects)
    
    static func createScaleAnimation(from: CGFloat,
                                    to: CGFloat,
                                    duration: CFTimeInterval) -> CASpringAnimation {
        let scale = createSpringAnimation(keyPath: "transform.scale", 
                                         duration: duration,
                                         damping: 12.0,
                                         stiffness: 250.0)
        scale.fromValue = from
        scale.toValue = to
        return scale
    }
}
