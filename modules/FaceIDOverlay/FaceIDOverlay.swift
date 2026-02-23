import Cocoa
import QuartzCore
import Foundation

class FaceIDWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

// MARK: - Spring Physics Engine
struct Spring {
    var value: CGFloat
    var target: CGFloat
    var velocity: CGFloat = 0
    
    // Physics Configuration
    let tension: CGFloat = 180
    let friction: CGFloat = 16
    
    mutating func update(dt: CGFloat) -> Bool {
        let displacement = value - target
        let force = -tension * displacement - friction * velocity
        velocity += force * dt
        value += velocity * dt
        return abs(displacement) < 0.1 && abs(velocity) < 0.1
    }
}

class FaceIDOverlayView: NSView {

    override var isFlipped: Bool { true }

    enum State { case expanding, scanning, success, verified }
    var state: State = .expanding

    let notchInfo = NotchDetector.detect()

    // MARK: Layers
    let islandLayer = CAShapeLayer()
    let contentLayer = CALayer()
    let glowLayer = CALayer()
    
    let outerRing = CAShapeLayer()      // Brackets -> Hidden on success
    let featuresLayer = CAShapeLayer()  // Face Glyph
    let circleClipLayer = CALayer()     // Holds the 2 Ring Clusters
    
    // Verified Layers
    let checkmarkLayer = CAShapeLayer()
    let progressCircleLayer = CAShapeLayer()

    // Animation / Physics
    var displayLink: CVDisplayLink?
    var lastTime: CFTimeInterval = 0
    
    lazy var wSpring = Spring(value: notchInfo.width, target: notchInfo.width + 60)
    lazy var hSpring = Spring(value: notchInfo.height, target: 220)
    lazy var rSpring = Spring(value: 16, target: 48)
    lazy var alphaSpring = Spring(value: 0, target: 1)

    // MARK: - COLORS (Neon Green)
    let black = NSColor.black.cgColor
    
    // Vibrant Neon Green
    let neonGreen = NSColor(displayP3Red: 0.7176, green: 0.9922, blue: 0.6824, alpha: 1.0).cgColor    
    // Constants
    let faceLineWidth: CGFloat = 3.8
    let heroRingWidth: CGFloat = 3.5
    let ghostRingWidth: CGFloat = 4.2
    
    override init(frame: NSRect) {
        super.init(frame: frame)
        wantsLayer = true
        layer?.backgroundColor = NSColor.clear.cgColor
        setup()
        start()
    }

    required init?(coder: NSCoder) { fatalError() }

    // MARK: Setup

    func setup() {
        islandLayer.fillColor = black
        islandLayer.shadowOpacity = 0
        islandLayer.shadowRadius = 30
        islandLayer.shadowOffset = CGSize(width: 0, height: 4)
        layer?.addSublayer(islandLayer)

        layer?.addSublayer(contentLayer)
        
        var p = CATransform3DIdentity
        p.m34 = -1 / 700
        contentLayer.sublayerTransform = p

        // Green Glow
        glowLayer.shadowColor = neonGreen
        glowLayer.shadowOpacity = 1
        glowLayer.shadowRadius = 36
        glowLayer.compositingFilter = "plusL"
        contentLayer.addSublayer(glowLayer)

        // Green Outer Ring (Brackets)
        outerRing.strokeColor = neonGreen
        outerRing.fillColor = NSColor.clear.cgColor
        outerRing.lineWidth = faceLineWidth
        outerRing.lineCap = .round
        outerRing.lineJoin = .round
        contentLayer.addSublayer(outerRing)

        // Green Features
        featuresLayer.strokeColor = neonGreen
        featuresLayer.fillColor = NSColor.clear.cgColor
        featuresLayer.lineWidth = faceLineWidth
        featuresLayer.lineCap = .round
        featuresLayer.lineJoin = .round
        contentLayer.addSublayer(featuresLayer)

        contentLayer.addSublayer(featuresLayer)

        // ⭐️ FIX: Apply Perspective to the CLIP layer so children look 3D inside it
        var perspective = CATransform3DIdentity
        perspective.m34 = -1.0 / 500.0 // Stronger perspective for "Physical" feel
        circleClipLayer.sublayerTransform = perspective
        
        circleClipLayer.masksToBounds = true
        contentLayer.addSublayer(circleClipLayer)

        // Verified Layer Setup
        checkmarkLayer.strokeColor = neonGreen
        checkmarkLayer.fillColor = NSColor.clear.cgColor
        checkmarkLayer.lineWidth = faceLineWidth
        checkmarkLayer.lineCap = .round
        checkmarkLayer.lineJoin = .round
        checkmarkLayer.strokeEnd = 0
        contentLayer.addSublayer(checkmarkLayer)
        
        progressCircleLayer.strokeColor = neonGreen
        progressCircleLayer.fillColor = NSColor.clear.cgColor
        progressCircleLayer.lineWidth = faceLineWidth
        progressCircleLayer.lineCap = .round
        progressCircleLayer.strokeEnd = 0
        // Rotate -90 degrees so it starts from top
        progressCircleLayer.transform = CATransform3DMakeRotation(-CGFloat.pi / 2, 0, 0, 1)
        contentLayer.addSublayer(progressCircleLayer)

        contentLayer.opacity = 0
        updateIslandGeometry()
    }

    // MARK: Physics Loop

    func start() {
        lastTime = CACurrentMediaTime()
        CVDisplayLinkCreateWithActiveCGDisplays(&displayLink)
        CVDisplayLinkSetOutputCallback(displayLink!, { _,_,_,_,_,ctx in
            let v = Unmanaged<FaceIDOverlayView>.fromOpaque(ctx!).takeUnretainedValue()
            DispatchQueue.main.async { v.tick() }
            return kCVReturnSuccess
        }, Unmanaged.passUnretained(self).toOpaque())
        CVDisplayLinkStart(displayLink!)
    }

    func tick() {
        let now = CACurrentMediaTime()
        let dt = CGFloat(min(now - lastTime, 0.05))
        lastTime = now

        if state == .expanding {
            let wDone = wSpring.update(dt: dt)
            let hDone = hSpring.update(dt: dt)
            let rDone = rSpring.update(dt: dt)
            let aDone = alphaSpring.update(dt: dt)
            
            updateIslandGeometry()
            
            islandLayer.shadowOpacity = Float(alphaSpring.value) * 0.5
            contentLayer.opacity = Float(alphaSpring.value)

            if wDone && hDone && rDone && aDone {
                state = .scanning
                // 🛑 STOP PHYSICS LOOP: We are now 100% Core Animation driven
                CVDisplayLinkStop(displayLink!) 
                startScan()
            }
        }
    }

    // MARK: Geometry Update

    func updateIslandGeometry() {
        let w = wSpring.value
        let h = hSpring.value
        let r = rSpring.value
        
        let cx = notchInfo.centerX
        let top: CGFloat = 0

        islandLayer.path = NSBezierPath(
            roundedRect: CGRect(
                x: cx - w / 2,
                y: top,
                width: w,
                height: h
            ),
            xRadius: r,
            yRadius: r
        ).cgPath

        CATransaction.begin()
        CATransaction.setDisableActions(true)
        contentLayer.bounds = CGRect(x: 0, y: 0, width: w, height: h)
        contentLayer.position = CGPoint(x: cx, y: h / 2)
        CATransaction.commit()
    }

    // MARK: Scanning Logic (Breathing Face)

    func startScan() {
        let size: CGFloat = 84
        let centerY = hSpring.value / 2
        
        buildFace(size: size, centerY: centerY)

        let scaleAnim = CABasicAnimation(keyPath: "transform.scale")
        scaleAnim.fromValue = 0.96
        scaleAnim.toValue = 1.04
        scaleAnim.duration = 1.3
        scaleAnim.autoreverses = true
        scaleAnim.repeatCount = .infinity
        scaleAnim.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        contentLayer.add(scaleAnim, forKey: "breathingScale")
        
        let glowAnim = CABasicAnimation(keyPath: "shadowRadius")
        glowAnim.fromValue = 20
        glowAnim.toValue = 50
        glowAnim.duration = 1.3
        glowAnim.autoreverses = true
        glowAnim.repeatCount = .infinity
        glowAnim.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        glowLayer.add(glowAnim, forKey: "breathingGlow")
        
        print("Ready. Type 'success' in terminal to unlock.")
    }

    func buildFace(size: CGFloat, centerY: CGFloat) {
        let cx = wSpring.value / 2
        featuresLayer.frame = contentLayer.bounds
        
        let frame = CGRect(
            x: cx - size / 2,
            y: centerY - size / 2,
            width: size,
            height: size
        )
        
        // 1. OUTER RING (Brackets)
        let bracketPath = NSBezierPath()
        let gap = size * 0.25
        let cornerR = size * 0.28
        let minX = frame.minX, maxX = frame.maxX
        let minY = frame.minY, maxY = frame.maxY
        
        // Top Left
        bracketPath.move(to: CGPoint(x: minX, y: frame.midY - gap))
        bracketPath.appendArc(from: CGPoint(x: minX, y: minY), to: CGPoint(x: frame.midX, y: minY), radius: cornerR)
        bracketPath.line(to: CGPoint(x: frame.midX - gap, y: minY))
        
        // Top Right
        bracketPath.move(to: CGPoint(x: frame.midX + gap, y: minY))
        bracketPath.appendArc(from: CGPoint(x: maxX, y: minY), to: CGPoint(x: maxX, y: frame.midY), radius: cornerR)
        bracketPath.line(to: CGPoint(x: maxX, y: frame.midY - gap))
        
        // Bottom Right
        bracketPath.move(to: CGPoint(x: maxX, y: frame.midY + gap))
        bracketPath.appendArc(from: CGPoint(x: maxX, y: maxY), to: CGPoint(x: frame.midX, y: maxY), radius: cornerR)
        bracketPath.line(to: CGPoint(x: frame.midX + gap, y: maxY))
        
        // Bottom Left
        bracketPath.move(to: CGPoint(x: frame.midX - gap, y: maxY))
        bracketPath.appendArc(from: CGPoint(x: minX, y: maxY), to: CGPoint(x: minX, y: frame.midY), radius: cornerR)
        bracketPath.line(to: CGPoint(x: minX, y: frame.midY + gap))
        
        outerRing.path = bracketPath.cgPath
        glowLayer.frame = frame
        circleClipLayer.frame = frame
        circleClipLayer.cornerRadius = cornerR

        // 2. FACE FEATURES
        let p = NSBezierPath()
        let eyeW = size * 0.105
        let eyeH = size * 0.16
        let eyeSpacing = size * 0.19
        
        let leftEyeRect = CGRect(x: cx - eyeSpacing - eyeW/2, y: centerY - eyeH * 0.55, width: eyeW, height: eyeH)
        let rightEyeRect = CGRect(x: cx + eyeSpacing - eyeW/2, y: centerY - eyeH * 0.55, width: eyeW, height: eyeH)
        
        p.append(NSBezierPath(roundedRect: leftEyeRect, xRadius: eyeW/2, yRadius: eyeW/2))
        p.append(NSBezierPath(roundedRect: rightEyeRect, xRadius: eyeW/2, yRadius: eyeW/2))

        let noseTop = CGPoint(x: cx, y: centerY - size * 0.08)
        let noseCorner = CGPoint(x: cx, y: centerY + size * 0.12)
        let noseEnd = CGPoint(x: cx - size * 0.11, y: centerY + size * 0.12)
        
        p.move(to: noseTop)
        p.line(to: noseCorner)
        p.curve(
            to: noseEnd,
            controlPoint1: CGPoint(x: cx, y: centerY + size * 0.17),
            controlPoint2: CGPoint(x: cx - size * 0.08, y: centerY + size * 0.17)
        )
        
        let mouthY = centerY + size * 0.24
        let mouthW = size * 0.21
        p.move(to: CGPoint(x: cx - mouthW, y: mouthY))
        p.curve(
            to: CGPoint(x: cx + mouthW, y: mouthY),
            controlPoint1: CGPoint(x: cx - mouthW * 0.5, y: mouthY + size * 0.14),
            controlPoint2: CGPoint(x: cx + mouthW * 0.5, y: mouthY + size * 0.14)
        )
        
        featuresLayer.path = p.cgPath
        startIdleAnimation()
    }
    
    func startIdleAnimation() {
        let lookX = CAKeyframeAnimation(keyPath: "transform.translation.x")
        lookX.values = [0, 2, -2, 0]
        lookX.keyTimes = [0, 0.3, 0.7, 1]
        lookX.duration = 5.0
        lookX.repeatCount = .infinity
        lookX.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        
        let lookY = CAKeyframeAnimation(keyPath: "transform.translation.y")
        lookY.values = [0, -1.5, 1, 0]
        lookY.keyTimes = [0, 0.2, 0.8, 1]
        lookY.duration = 6.5
        lookY.repeatCount = .infinity
        lookY.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        
        featuresLayer.add(lookX, forKey: "lookX")
        featuresLayer.add(lookY, forKey: "lookY")
    }

    // MARK: TRIGGER (Pop + Activate Double Rings)

    func advanceState() {
        switch state {
        case .scanning:
            triggerSuccessAnimation()
        case .success:
            triggerVerifiedAnimation()
        default:
            break
        }
    }

    func triggerSuccessAnimation() {
        guard state == .scanning else { return }
        state = .success

        let size: CGFloat = 84
        let centerY = hSpring.value / 2
        let cx = wSpring.value / 2
        let frame = CGRect(x: cx - size / 2, y: centerY - size / 2, width: size, height: size)

        contentLayer.removeAnimation(forKey: "breathingScale")
        glowLayer.removeAnimation(forKey: "breathingGlow")

        // 1. POP OUT (Shrink)
        let popOut = CABasicAnimation(keyPath: "transform.scale")
        popOut.fromValue = 1.0
        popOut.toValue = 0.01
        popOut.duration = 0.2
        popOut.timingFunction = CAMediaTimingFunction(controlPoints: 0.3, 0.0, 1.0, 1.0)
        popOut.fillMode = .forwards
        popOut.isRemovedOnCompletion = false
        contentLayer.add(popOut, forKey: "popOut")
        
        // 2. THE SWAP
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            
            self.featuresLayer.opacity = 0
            self.outerRing.opacity = 0 // Hide bracket layer, we use ring clusters now
            self.circleClipLayer.cornerRadius = size / 2
            
            // SPAWN INTERLEAVED CLUSTERS (Physics Fix)
            // Creates a single unified system of interlaced rings
            self.spawnInterleavedClusters(radius: size / 2)
            
            // POP IN (Spring)
            let spring = CASpringAnimation(keyPath: "transform.scale")
            spring.fromValue = 0.01
            spring.toValue = 1.0
            spring.mass = 0.6
            spring.stiffness = 240
            spring.damping = 14
            spring.initialVelocity = 10
            spring.duration = spring.settlingDuration
            spring.fillMode = .forwards
            spring.isRemovedOnCompletion = false
            
            self.contentLayer.add(spring, forKey: "popIn")
            
            // 3. AUTO-TRIGGER CHECKMARK (Chain Sequence)
            // Wait 0.8s (Balanced "Apple" Timing)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
                if self.state == .success {
                    self.triggerVerifiedAnimation()
                }
            }
        }
    }
    

    
    // MARK: - THE "AXIS SHIFT" ANIMATION LOGIC (CHOREOGRAPHED SEQUENCE)
    
    func getAxisShiftAnimation(clockwise: Bool, delayOffset: Double) -> CAAnimationGroup {
        
        // TOTAL SEQUENCE DURATION (Matches the 0.8s wait time)
        let totalDuration: Double = 0.8
        
        // ⭐️ APPLE PHYSICS EASING
        // "Heavy Start, Effortless Glide"
        // This is close to kCAMediaTimingFunctionEaseOut but sharper at the end.
        let appleEase = CAMediaTimingFunction(controlPoints: 0.33, 0, 0, 1)
        
        // 1. CONSTANT SPIN (With Inertia)
        let spin = CABasicAnimation(keyPath: "transform.rotation.z")
        spin.fromValue = 0
        // Slower Spin (User Request: "2x slow" -> Half Speed)
        // Was 0.019*pi, now 0.0095*pi (approx 1.7 degrees) in the same 2.0s.
        spin.toValue = clockwise ? CGFloat.pi * 0.0095 : -CGFloat.pi * 0.0095
        spin.duration = totalDuration
        spin.timingFunction = appleEase // Apply Inertia
        spin.fillMode = .forwards
        spin.isRemovedOnCompletion = false
        
        // 2. DEEP X-TUMBLE (Tuned 66 Degrees)
        let xRot = CAKeyframeAnimation(keyPath: "transform.rotation.x")
        // Start 0 -> Tilt Down -> Tilt Up -> Tilt Down -> CONVERGE
        xRot.values = [0, 1.15, -1.15, 1.15, 0, 0]
        xRot.keyTimes = [0, 0.25, 0.55, 0.85, 0.98, 1]
        xRot.duration = totalDuration
        xRot.timingFunction = appleEase // Sync Tumble with Spin Inertia
        xRot.fillMode = .forwards
        xRot.isRemovedOnCompletion = false

        // 3. DEEP Y-TUMBLE (Tuned 66 Degrees)
        let yRot = CAKeyframeAnimation(keyPath: "transform.rotation.y")
        // Start 0 -> Tilt Right -> Tilt Left -> Tilt Right -> CONVERGE
        yRot.values = [0, -1.15, 1.15, -1.15, 0, 0]
        yRot.keyTimes = [0, 0.20, 0.50, 0.80, 0.98, 1]
        yRot.duration = totalDuration
        yRot.timingFunction = appleEase // Sync Tumble with Spin Inertia
        yRot.fillMode = .forwards
        yRot.isRemovedOnCompletion = false
        
        let group = CAAnimationGroup()
        group.animations = [spin, xRot, yRot]
        group.duration = totalDuration
        group.repeatCount = 0
        group.isRemovedOnCompletion = false
        group.fillMode = .forwards
        
        // ⭐️ TIME OFFSET FOR TRAIL
        group.beginTime = CACurrentMediaTime() + delayOffset
        
        return group
    }

    // MARK: Ring Cluster Spawner (INTERLEAVED)

    func spawnInterleavedClusters(radius: CGFloat) {
        
        // ⭐️ APPLE ELEGANCE GEOMETRY
        // Count 8: Clean, legible, distinct structure.
        let count = 6 //make 8
        // Trail 0.25: Balanced tail, perfectly proportional to the 8 rings.
        let trailDuration: Double = 0.25 
        let lagPerRing = trailDuration / Double(count)

        // Create the Container for this Cluster
        let clusterLayer = CALayer()
        clusterLayer.frame = circleClipLayer.bounds
        circleClipLayer.addSublayer(clusterLayer)

        for i in 0..<count {
            
            // Loop twice per index: once for CW, once for CCW.
            // This ensures Layer 0=CW, Layer 1=CCW, Layer 2=CW... mixed depth!
            let directions = [true, false] 
            
            for clockwise in directions {
                
                let isHero = i == 0
                
                let axisLayer = CALayer()
                axisLayer.frame = clusterLayer.bounds

                let ring = CAShapeLayer()
                let path = NSBezierPath(ovalIn: axisLayer.bounds.insetBy(dx: 2, dy: 2)).cgPath
                ring.path = path
                
                if isHero {
                    // HERO RING: Sharp Core
                    ring.lineWidth = heroRingWidth
                    ring.strokeColor = neonGreen
                    ring.opacity = 1.0
                    ring.shadowColor = neonGreen
                    ring.shadowOpacity = 0.2 //0.8
                    ring.shadowRadius = 20 //8
                } else {
                    // ⭐️ APPLE "GLOW" GHOSTS
                    // Not a smear, but a "Glow".
                    // Radius 15 creates a soft, premium halo around the motion.
                    ring.lineWidth = ghostRingWidth
                    
                    ring.shadowColor = neonGreen
                    ring.shadowRadius = 15 //15 //5 //2(almost perfect)
                    ring.shadowOpacity = 0.5 //1.0
                    ring.shadowOffset = .zero

                    let progress = CGFloat(i) / CGFloat(count)
                    let fade = 1.0 - progress
                    
                    // Translucent Glow Stroke
                    ring.strokeColor = neonGreen
                    ring.opacity = Float(0.4 * fade)
                    
                    // Keep Rasterization OFF
                    ring.shouldRasterize = false
                }
                
                ring.fillColor = NSColor.clear.cgColor
                axisLayer.addSublayer(ring)
                clusterLayer.addSublayer(axisLayer)
                
                let lag = -Double(i) * lagPerRing
                let animGroup = getAxisShiftAnimation(clockwise: clockwise, delayOffset: lag)
                axisLayer.add(animGroup, forKey: "gymbal")
            }
        }
    }

    // MARK: - VERIFIED ANIMATION (Tick + Progress)

    func triggerVerifiedAnimation() {
        guard state == .success else { return }
        state = .verified
        
        // 0. STOP RINGS (Freeze in place)
        // Capture current state to avoid "snap" to default rotation
        let pausedTime = circleClipLayer.convertTime(CACurrentMediaTime(), from: nil)
        circleClipLayer.speed = 0.0
        circleClipLayer.timeOffset = pausedTime
        
        // 1. POP OUT (Shrink + Fade Out)
        let popOut = CABasicAnimation(keyPath: "transform.scale")
        popOut.fromValue = 1.0
        popOut.toValue = 0.01
        // Elegant Snap (User Request: 0.05 was too fast, 0.2 too slow -> Now 0.15 balanced)
        popOut.duration = 0.15 
        popOut.timingFunction = CAMediaTimingFunction(controlPoints: 0.3, 0.0, 1.0, 1.0)
        popOut.fillMode = .forwards
        popOut.isRemovedOnCompletion = false
        contentLayer.add(popOut, forKey: "popOutVerified")
        
        let fadeOut = CABasicAnimation(keyPath: "opacity")
        fadeOut.fromValue = 1.0
        fadeOut.toValue = 0.0
        fadeOut.duration = 0.15
        fadeOut.timingFunction = CAMediaTimingFunction(name: .easeIn)
        fadeOut.fillMode = .forwards
        fadeOut.isRemovedOnCompletion = false
        contentLayer.add(fadeOut, forKey: "fadeOutVerified")
        
        // 2. THE SWAP & POP IN
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            
            let size: CGFloat = 84
            let centerY = self.hSpring.value / 2
            let cx = self.wSpring.value / 2
            
            let bounds = CGRect(x: 0, y: 0, width: size, height: size)
            let centerPos = CGPoint(x: cx, y: centerY)

            // Disable implicit animations
            CATransaction.begin()
            CATransaction.setDisableActions(true)
            
            // 1. Hide Rings Instantly
            self.circleClipLayer.opacity = 0
            
            // 2. Prepare Verified Geometry
            self.checkmarkLayer.bounds = bounds
            self.checkmarkLayer.position = centerPos
            
            self.progressCircleLayer.bounds = bounds
            self.progressCircleLayer.position = centerPos
            CATransaction.commit()
            
            // Build Paths
            let checkPath = NSBezierPath()
            checkPath.move(to: CGPoint(x: size * 0.28, y: size * 0.5))
            checkPath.line(to: CGPoint(x: size * 0.45, y: size * 0.70))
            checkPath.line(to: CGPoint(x: size * 0.75, y: size * 0.30))
            self.checkmarkLayer.path = checkPath.cgPath
            
            let circlePath = NSBezierPath(ovalIn: CGRect(x: 0, y: 0, width: size, height: size))
            self.progressCircleLayer.path = circlePath.cgPath
            
            // 3. POP IN (Spring + Fade In)
            let spring = CASpringAnimation(keyPath: "transform.scale")
            spring.fromValue = 0.01
            spring.toValue = 1.0
            spring.mass = 0.6
            spring.stiffness = 240
            spring.damping = 14
            spring.initialVelocity = 10
            spring.duration = spring.settlingDuration
            spring.fillMode = .forwards
            spring.isRemovedOnCompletion = false
            self.contentLayer.add(spring, forKey: "popInVerified")
            
            let fadeIn = CABasicAnimation(keyPath: "opacity")
            fadeIn.fromValue = 0.0
            fadeIn.toValue = 1.0
            fadeIn.duration = 0.15
            fadeIn.timingFunction = CAMediaTimingFunction(name: .easeOut)
            fadeIn.fillMode = .forwards
            fadeIn.isRemovedOnCompletion = false
            self.contentLayer.add(fadeIn, forKey: "fadeInVerified")

            // 4. Animate Progress Circle (Sequenced AFTER Pop In)
            self.progressCircleLayer.strokeEnd = 0
            
            // Start when spring is mostly settled (0.3 factor for hyper speed)
            let drawStartTime = CACurrentMediaTime() + spring.settlingDuration * 0.3
            let circleDuration: TimeInterval = 0.15 // Blink speed
            
            let circleAnim = CABasicAnimation(keyPath: "strokeEnd")
            circleAnim.fromValue = 0
            circleAnim.toValue = 1
            circleAnim.duration = circleDuration
            circleAnim.beginTime = drawStartTime
            circleAnim.timingFunction = CAMediaTimingFunction(name: .easeOut)
            circleAnim.fillMode = .both
            circleAnim.isRemovedOnCompletion = false
            self.progressCircleLayer.add(circleAnim, forKey: "circleDraw")
            
            // 5. Animate Checkmark
            self.checkmarkLayer.strokeEnd = 0
            
            let checkAnim = CABasicAnimation(keyPath: "strokeEnd")
            checkAnim.fromValue = 0
            checkAnim.toValue = 1
            checkAnim.duration = 0.15 // Instant tick
            // Start AFTER circle completes + 0.05s delay
            checkAnim.beginTime = drawStartTime + circleDuration + 0.05
            checkAnim.timingFunction = CAMediaTimingFunction(controlPoints: 0.2, 0.9, 0.2, 1.0) // Bouncy/Snap tick
            checkAnim.fillMode = .both
            checkAnim.isRemovedOnCompletion = false
            self.checkmarkLayer.add(checkAnim, forKey: "checkDraw")
            
            print("Verified.")
        }
    }
}

// MARK: App

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: FaceIDWindow!
    var view: FaceIDOverlayView!

    func applicationDidFinishLaunching(_ n: Notification) {
        let s = NSScreen.main!
        window = FaceIDWindow(
            contentRect: s.frame,
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        window.level = .statusBar
        window.isOpaque = false
        window.backgroundColor = .clear
        window.ignoresMouseEvents = true
        
        view = FaceIDOverlayView(frame: s.frame)
        window.contentView = view
        window.makeKeyAndOrderFront(nil)
        
        setupTerminalListener()
    }
    
    func setupTerminalListener() {
        DispatchQueue.global(qos: .background).async {
            print("--- Listening for Input ---")
            while let line = readLine() {
                DispatchQueue.main.async {
                    print("Processing input: \(line)")
                    self.view.advanceState()
                }
            }
        }
    }
}

@main
struct FaceIDApp {
    static func main() {
        let app = NSApplication.shared
        let d = AppDelegate()
        app.delegate = d
        app.setActivationPolicy(.accessory)
        app.run()
    }
}
