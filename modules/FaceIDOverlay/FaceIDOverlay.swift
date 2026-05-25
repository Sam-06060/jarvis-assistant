import Cocoa
import QuartzCore
import CoreImage
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
    
    // Critically-damped: ζ = friction / (2 * √tension) ≈ 1.0
    let tension: CGFloat = 200
    let friction: CGFloat = 28
    
    mutating func update(dt: CGFloat) -> Bool {
        let displacement = value - target
        let force = -tension * displacement - friction * velocity
        velocity += force * dt
        value += velocity * dt
        return abs(displacement) < 0.1 && abs(velocity) < 0.1
    }
}

// MARK: - FaceIDOverlayView

class FaceIDOverlayView: NSView {

    override var isFlipped: Bool { true }

    // ┌─────────────────────────────────────────────────────┐
    // │  STATE MACHINE                                      │
    // │  expanding → scanning → success → verified → retract│
    // └─────────────────────────────────────────────────────┘
    enum State { case expanding, scanning, success, verified, retracting }
    var state: State = .expanding

    let notchInfo = NotchDetector.detect()

    // ┌─────────────────────────────────────────────────────┐
    // │  LAYER HIERARCHY                                    │
    // │                                                     │
    // │  root (clear)                                       │
    // │  ├── islandLayer      (black rounded-rect island)   │
    // │  └── contentLayer     (all visual content)          │
    // │      ├── glowLayer        (green glow halo)         │
    // │      ├── bracketLayer     (broken squircle brackets)│
    // │      ├── featuresLayer    (face glyph)              │
    // │      ├── spinContainer    (3D perspective host)     │
    // │      │   └── ringLayer    (squircle → circle morph) │
    // │      └── checkmarkLayer   (green checkmark)         │
    // └─────────────────────────────────────────────────────┘
    let islandLayer = CAShapeLayer()
    let contentLayer = CALayer()
    let glowLayer = CALayer()

    let bracketLayer = CAShapeLayer()
    let featuresLayer = CAShapeLayer()

    let spinContainer = CALayer()
    let ringLayer = CAShapeLayer()
    var ghostRings: [CAShapeLayer] = []   // Motion-trail afterimages
    let ghostCount = 4                     // Clean trail without excess

    let checkmarkLayer = CAShapeLayer()

    var faceFrame: CGRect = .zero  // Stored for bracket animation

    // MARK: Physics
    var displayLink: CVDisplayLink?
    var lastTime: CFTimeInterval = 0

    lazy var wSpring = Spring(value: notchInfo.width, target: notchInfo.width + 46)
    lazy var hSpring = Spring(value: notchInfo.height, target: 175)
    lazy var rSpring = Spring(value: 16, target: 44)
    lazy var alphaSpring = Spring(value: 0, target: 1)

    // MARK: Colors & Constants
    let black = NSColor.black.cgColor
    let neonGreen = NSColor(displayP3Red: 0.7176, green: 0.9922, blue: 0.6824, alpha: 1.0).cgColor
    let faceLineWidth: CGFloat = 3.8
    let ringLineWidth: CGFloat = 5.5

    // MARK: - Init

    override init(frame: NSRect) {
        super.init(frame: frame)
        wantsLayer = true
        layer?.backgroundColor = NSColor.clear.cgColor
        setup()
        start()
    }

    required init?(coder: NSCoder) { fatalError() }

    // MARK: - Layer Setup

    func setup() {
        // ── Island (black background shape) ──────────────────────────
        islandLayer.fillColor = black
        islandLayer.shadowOpacity = 0
        islandLayer.shadowRadius = 30
        islandLayer.shadowOffset = CGSize(width: 0, height: 4)
        layer?.addSublayer(islandLayer)

        // ── Content container ────────────────────────────────────────
        layer?.addSublayer(contentLayer)

        // ── Green glow halo ──────────────────────────────────────────
        glowLayer.shadowColor = neonGreen
        glowLayer.shadowOpacity = 1
        glowLayer.shadowRadius = 36
        glowLayer.compositingFilter = "plusL"
        contentLayer.addSublayer(glowLayer)

        // ── Broken squircle brackets (scanning phase) ────────────────
        bracketLayer.strokeColor = neonGreen
        bracketLayer.fillColor = NSColor.clear.cgColor
        bracketLayer.lineWidth = ringLineWidth
        bracketLayer.lineCap = .round
        bracketLayer.lineJoin = .round
        contentLayer.addSublayer(bracketLayer)

        // ── Face glyph (scanning phase) ──────────────────────────────
        featuresLayer.strokeColor = neonGreen
        featuresLayer.fillColor = NSColor.clear.cgColor
        featuresLayer.lineWidth = faceLineWidth
        featuresLayer.lineCap = .round
        featuresLayer.lineJoin = .round
        contentLayer.addSublayer(featuresLayer)

        // ── Spin container with 3D perspective (spin phase) ──────────
        // Only layers INSIDE this container get 3D depth.
        // Checkmark stays outside = always flat.
        var perspective = CATransform3DIdentity
        perspective.m34 = -1.0 / 400.0
        spinContainer.sublayerTransform = perspective
        spinContainer.opacity = 0  // Hidden until morph
        contentLayer.addSublayer(spinContainer)

        // ── Continuous ring (morphs squircle → circle) ───────────────
        ringLayer.strokeColor = neonGreen
        ringLayer.fillColor = NSColor.clear.cgColor
        ringLayer.lineWidth = ringLineWidth
        ringLayer.lineCap = .round
        ringLayer.lineJoin = .round
        spinContainer.addSublayer(ringLayer)

        // ── Checkmark (verified phase) ───────────────────────────────
        checkmarkLayer.strokeColor = neonGreen
        checkmarkLayer.fillColor = NSColor.clear.cgColor
        checkmarkLayer.lineWidth = ringLineWidth
        checkmarkLayer.lineCap = .round
        checkmarkLayer.lineJoin = .round
        checkmarkLayer.strokeEnd = 0
        checkmarkLayer.opacity = 0  // Hidden until verified
        contentLayer.addSublayer(checkmarkLayer)

        contentLayer.opacity = 0
        updateIslandGeometry()
    }

    // MARK: - Expanding Phase (Spring Physics)

    func start() {
        lastTime = CACurrentMediaTime()
        CVDisplayLinkCreateWithActiveCGDisplays(&displayLink)
        CVDisplayLinkSetOutputCallback(displayLink!, { _, _, _, _, _, ctx in
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

        guard state == .expanding else { return }

        let wDone = wSpring.update(dt: dt)
        let hDone = hSpring.update(dt: dt)
        let rDone = rSpring.update(dt: dt)
        let aDone = alphaSpring.update(dt: dt)

        updateIslandGeometry()

        islandLayer.shadowOpacity = Float(alphaSpring.value) * 0.5
        contentLayer.opacity = Float(alphaSpring.value)

        if wDone && hDone && rDone && aDone {
            state = .scanning
            CVDisplayLinkStop(displayLink!)
            startScan()
        }
    }

    func updateIslandGeometry() {
        let w = wSpring.value
        let h = hSpring.value
        let r = rSpring.value
        let cx = notchInfo.centerX

        islandLayer.path = NSBezierPath(
            roundedRect: CGRect(x: cx - w / 2, y: 0, width: w, height: h),
            xRadius: r, yRadius: r
        ).cgPath

        CATransaction.begin()
        CATransaction.setDisableActions(true)
        contentLayer.bounds = CGRect(x: 0, y: 0, width: w, height: h)
        contentLayer.position = CGPoint(x: cx, y: h / 2)
        CATransaction.commit()
    }

    // MARK: - Scanning Phase (Face Glyph + Brackets + Breathing)

    func startScan() {
        let size: CGFloat = 84
        let centerY = hSpring.value / 2
        let cx = wSpring.value / 2
        let frame = CGRect(x: cx - size / 2, y: centerY - size / 2, width: size, height: size)
        faceFrame = frame

        buildBrackets(frame: frame)
        buildFace(size: size, cx: cx, centerY: centerY)
        prepareRingAndCheckmark(frame: frame)

        // Breathing scale
        let breathe = CABasicAnimation(keyPath: "transform.scale")
        breathe.fromValue = 0.96
        breathe.toValue = 1.04
        breathe.duration = 1.3
        breathe.autoreverses = true
        breathe.repeatCount = .infinity
        breathe.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        contentLayer.add(breathe, forKey: "breathingScale")

        // Glow pulse
        let glow = CABasicAnimation(keyPath: "shadowRadius")
        glow.fromValue = 20
        glow.toValue = 50
        glow.duration = 1.3
        glow.autoreverses = true
        glow.repeatCount = .infinity
        glow.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        glowLayer.add(glow, forKey: "breathingGlow")

        print("Ready. Type 'success' in terminal to unlock.")
    }

    func buildBrackets(frame: CGRect) {
        bracketLayer.path = makeBracketPath(frame: frame, gapFraction: 0.25)
        glowLayer.frame = frame
    }

    /// Builds a bracket path with configurable gap size.
    /// gapFraction 0.25 = short brackets (scanning), 0.03 = nearly closed.
    func makeBracketPath(frame: CGRect, gapFraction: CGFloat, cornerRFraction: CGFloat = 0.28) -> CGPath {
        let size = frame.width
        let gap = size * gapFraction
        let cornerR = size * cornerRFraction
        let minX = frame.minX, maxX = frame.maxX
        let minY = frame.minY, maxY = frame.maxY

        let path = NSBezierPath()

        // Top-left bracket
        path.move(to: CGPoint(x: minX, y: frame.midY - gap))
        path.appendArc(from: CGPoint(x: minX, y: minY),
                       to: CGPoint(x: frame.midX, y: minY), radius: cornerR)
        path.line(to: CGPoint(x: frame.midX - gap, y: minY))

        // Top-right bracket
        path.move(to: CGPoint(x: frame.midX + gap, y: minY))
        path.appendArc(from: CGPoint(x: maxX, y: minY),
                       to: CGPoint(x: maxX, y: frame.midY), radius: cornerR)
        path.line(to: CGPoint(x: maxX, y: frame.midY - gap))

        // Bottom-right bracket
        path.move(to: CGPoint(x: maxX, y: frame.midY + gap))
        path.appendArc(from: CGPoint(x: maxX, y: maxY),
                       to: CGPoint(x: frame.midX, y: maxY), radius: cornerR)
        path.line(to: CGPoint(x: frame.midX + gap, y: maxY))

        // Bottom-left bracket
        path.move(to: CGPoint(x: frame.midX - gap, y: maxY))
        path.appendArc(from: CGPoint(x: minX, y: maxY),
                       to: CGPoint(x: minX, y: frame.midY), radius: cornerR)
        path.line(to: CGPoint(x: minX, y: frame.midY + gap))

        return path.cgPath
    }

    /// Builds 4 arc segments of a TRUE CIRCLE with tiny gaps.
    /// Used as the morph TARGET so brackets smoothly transform into circle arcs.
    /// CRITICAL: Must have IDENTICAL path structure to makeBracketPath
    /// (same number of move/arc/line elements) for Core Animation to interpolate.
    func makeCircleArcBracketPath(frame: CGRect, inset: CGFloat, gapAngle: CGFloat) -> CGPath {
        // The ring lives at frame inset by the ring stroke width
        let r = (frame.width - inset * 2) / 2
        let cx = frame.midX
        let cy = frame.midY

        // Each bracket covers ~90° of the circle minus the gap.
        // Angles in the macOS coordinate system (Y flipped): 0=right, π/2=down
        // Gap angle in radians — small = nearly closed circle
        let halfGap = gapAngle / 2

        let path = NSBezierPath()

        // Top-left arc (from ~180° down to ~270°, i.e. left+top quadrant)
        let tlStart = CGFloat.pi + halfGap          // just past 180° (left)
        let tlEnd   = CGFloat.pi * 1.5 - halfGap   // just before 270° (top)
        path.move(to: CGPoint(x: cx + r * cos(tlStart), y: cy + r * sin(tlStart)))
        path.appendArc(withCenter: CGPoint(x: cx, y: cy), radius: r,
                       startAngle: tlStart * 180 / .pi,
                       endAngle:   tlEnd   * 180 / .pi,
                       clockwise: false)
        // "line" to end (zero length — keeps path element count the same)
        path.line(to: CGPoint(x: cx + r * cos(tlEnd), y: cy + r * sin(tlEnd)))

        // Top-right arc (from ~270° to ~360°)
        let trStart = CGFloat.pi * 1.5 + halfGap
        let trEnd   = CGFloat.pi * 2.0 - halfGap
        path.move(to: CGPoint(x: cx + r * cos(trStart), y: cy + r * sin(trStart)))
        path.appendArc(withCenter: CGPoint(x: cx, y: cy), radius: r,
                       startAngle: trStart * 180 / .pi,
                       endAngle:   trEnd   * 180 / .pi,
                       clockwise: false)
        path.line(to: CGPoint(x: cx + r * cos(trEnd), y: cy + r * sin(trEnd)))

        // Bottom-right arc (from ~0° to ~90°)
        let brStart = halfGap
        let brEnd   = CGFloat.pi * 0.5 - halfGap
        path.move(to: CGPoint(x: cx + r * cos(brStart), y: cy + r * sin(brStart)))
        path.appendArc(withCenter: CGPoint(x: cx, y: cy), radius: r,
                       startAngle: brStart * 180 / .pi,
                       endAngle:   brEnd   * 180 / .pi,
                       clockwise: false)
        path.line(to: CGPoint(x: cx + r * cos(brEnd), y: cy + r * sin(brEnd)))

        // Bottom-left arc (from ~90° to ~180°)
        let blStart = CGFloat.pi * 0.5 + halfGap
        let blEnd   = CGFloat.pi - halfGap
        path.move(to: CGPoint(x: cx + r * cos(blStart), y: cy + r * sin(blStart)))
        path.appendArc(withCenter: CGPoint(x: cx, y: cy), radius: r,
                       startAngle: blStart * 180 / .pi,
                       endAngle:   blEnd   * 180 / .pi,
                       clockwise: false)
        path.line(to: CGPoint(x: cx + r * cos(blEnd), y: cy + r * sin(blEnd)))

        return path.cgPath
    }

    func buildFace(size: CGFloat, cx: CGFloat, centerY: CGFloat) {
        featuresLayer.frame = contentLayer.bounds

        let p = NSBezierPath()

        // Eyes
        let eyeW = size * 0.105
        let eyeH = size * 0.16
        let eyeSpacing = size * 0.19

        p.append(NSBezierPath(roundedRect: CGRect(
            x: cx - eyeSpacing - eyeW / 2, y: centerY - eyeH * 0.55,
            width: eyeW, height: eyeH), xRadius: eyeW / 2, yRadius: eyeW / 2))
        p.append(NSBezierPath(roundedRect: CGRect(
            x: cx + eyeSpacing - eyeW / 2, y: centerY - eyeH * 0.55,
            width: eyeW, height: eyeH), xRadius: eyeW / 2, yRadius: eyeW / 2))

        // Nose
        let noseTop = CGPoint(x: cx, y: centerY - size * 0.08)
        let noseCorner = CGPoint(x: cx, y: centerY + size * 0.12)
        let noseEnd = CGPoint(x: cx - size * 0.11, y: centerY + size * 0.12)
        p.move(to: noseTop)
        p.line(to: noseCorner)
        p.curve(to: noseEnd,
                controlPoint1: CGPoint(x: cx, y: centerY + size * 0.17),
                controlPoint2: CGPoint(x: cx - size * 0.08, y: centerY + size * 0.17))

        // Mouth
        let mouthY = centerY + size * 0.24
        let mouthW = size * 0.21
        p.move(to: CGPoint(x: cx - mouthW, y: mouthY))
        p.curve(to: CGPoint(x: cx + mouthW, y: mouthY),
                controlPoint1: CGPoint(x: cx - mouthW * 0.5, y: mouthY + size * 0.14),
                controlPoint2: CGPoint(x: cx + mouthW * 0.5, y: mouthY + size * 0.14))

        featuresLayer.path = p.cgPath

        // Subtle idle eye movement
        let lookX = CAKeyframeAnimation(keyPath: "transform.translation.x")
        lookX.values = [0, 2, -2, 0]
        lookX.keyTimes = [0, 0.3, 0.7, 1]
        lookX.duration = 5.0
        lookX.repeatCount = .infinity

        let lookY = CAKeyframeAnimation(keyPath: "transform.translation.y")
        lookY.values = [0, -1.5, 1, 0]
        lookY.keyTimes = [0, 0.2, 0.8, 1]
        lookY.duration = 6.5
        lookY.repeatCount = .infinity

        featuresLayer.add(lookX, forKey: "lookX")
        featuresLayer.add(lookY, forKey: "lookY")
    }

    /// Pre-build ring, ghost trails, and checkmark geometry (invisible until success trigger)
    func prepareRingAndCheckmark(frame: CGRect) {
        let size = frame.width
        let inset = ringLineWidth / 2
        let localRect = CGRect(x: inset, y: inset,
                               width: size - inset * 2, height: size - inset * 2)
        let squircleR = size * 0.28
        let squirclePath = NSBezierPath(
            roundedRect: localRect,
            xRadius: squircleR, yRadius: squircleR
        ).cgPath

        CATransaction.begin()
        CATransaction.setDisableActions(true)

        // Position spin container at face area
        spinContainer.frame = frame
        spinContainer.opacity = 0

        // ── Ghost trail rings ("drunk blur" afterimages) ─────────────
        // Added BEFORE the hero ring so they render behind it.
        // Each ghost is a translucent, slightly glowy copy that will
        // run the same spin animation with a staggered time offset.
        ghostRings.forEach { $0.removeFromSuperlayer() }
        ghostRings.removeAll()

        for i in 0..<ghostCount {
            let ghost = CAShapeLayer()
            ghost.frame = spinContainer.bounds
            ghost.path = squirclePath
            ghost.strokeColor = neonGreen
            ghost.fillColor = NSColor.clear.cgColor
            ghost.lineWidth = i < 1 ? ringLineWidth : ringLineWidth + CGFloat(i) * 2.0
            ghost.lineCap = .round
            ghost.lineJoin = .round

            // Start invisible — ghosts only appear when spin begins
            // (prevents artifacts during brackets→ring cross-fade)
            let progress = CGFloat(i + 1) / CGFloat(ghostCount + 1)
            ghost.opacity = 0

            // ⭐️ SHADOW GLOW = THE BLUR
            // Each ghost’s shadow acts as its soft blur halo.
            // Progressive radius makes distant ghosts softer/wider.
            ghost.shadowColor = neonGreen
            ghost.shadowRadius = 7 + CGFloat(i) * 4  // 7, 11, 15, 19
            ghost.shadowOpacity = Float(0.65 * (1.0 - progress))
            ghost.shadowOffset = .zero

            spinContainer.addSublayer(ghost)
            ghostRings.append(ghost)
        }

        // ── Hero ring (on top of ghosts) ─────────────────────────────
        ringLayer.frame = spinContainer.bounds
        ringLayer.path = squirclePath
        // Shadow starts off — revealed when spin begins
        // (prevents glow artifacts during brackets→ring cross-fade)
        ringLayer.shadowColor = neonGreen
        ringLayer.shadowRadius = 7
        ringLayer.shadowOpacity = 0
        ringLayer.shadowOffset = .zero
        // Re-add to ensure it's on top of the ghost stack
        ringLayer.removeFromSuperlayer()
        spinContainer.addSublayer(ringLayer)

        // ── Checkmark geometry (centered in face area) ───────────────
        checkmarkLayer.bounds = CGRect(x: 0, y: 0, width: size, height: size)
        checkmarkLayer.position = CGPoint(x: frame.midX, y: frame.midY)
        checkmarkLayer.opacity = 0
        checkmarkLayer.strokeEnd = 0

        let check = NSBezierPath()
        check.move(to: CGPoint(x: size * 0.28, y: size * 0.50))
        check.line(to: CGPoint(x: size * 0.44, y: size * 0.68))
        check.line(to: CGPoint(x: size * 0.74, y: size * 0.32))
        checkmarkLayer.path = check.cgPath

        CATransaction.commit()
    }

    // MARK: - State Machine

    func advanceState() {
        switch state {
        case .scanning:
            triggerSuccessAnimation()
        default:
            break
        }
    }

    // MARK: - ⭐️ THE APPLE FACE ID SEQUENCE ⭐️
    //
    // Timeline (from success trigger):
    //
    //  T+0.00   Face features fade out
    //  T+0.05   Brackets ↔ Ring cross-fade (ring starts as squircle)
    //  T+0.12   Ring path morphs: squircle → perfect circle
    //  T+0.15   3D spin + X/Y tumble begins (face topography scan)
    //  T+0.60   Ring snaps flat (3D → 2D), spin stops
    //  T+0.75   Green checkmark draws in (strokeEnd 0 → 1)
    //  T+1.05   Brief dwell
    //  T+1.27   Island retracts into notch
    //  T+1.55   Process exits

    func triggerSuccessAnimation() {
        guard state == .scanning else { return }
        state = .success

        let size: CGFloat = 84
        let inset = ringLineWidth / 2
        let localRect = CGRect(x: inset, y: inset,
                               width: size - inset * 2, height: size - inset * 2)

        // Stop breathing
        contentLayer.removeAnimation(forKey: "breathingScale")
        glowLayer.removeAnimation(forKey: "breathingGlow")

        // ═══════════════════════════════════════════════════════════════
        // STEP 1: Face features fade out (T+0.00, 0.15s)
        // The face glyph dissolves smoothly before the ring appears.
        // ═══════════════════════════════════════════════════════════════
        let faceFade = CABasicAnimation(keyPath: "opacity")
        faceFade.toValue = 0.0
        faceFade.duration = 0.15
        faceFade.timingFunction = CAMediaTimingFunction(name: .easeIn)
        faceFade.fillMode = .forwards
        faceFade.isRemovedOnCompletion = false
        featuresLayer.add(faceFade, forKey: "faceFade")

        // ═══════════════════════════════════════════════════════════════
        // STEP 1.5: Brackets MORPH INTO CIRCLE ARCS (T+0.00, 0.18s)
        // The brackets path-morph from squircle-corner arcs → 4 arc
        // segments of the final circle, while shrinking to match the
        // ring’s inset rect. Looks like the corners round off and
        // contract into a circle shape before the ring cross-fades in.
        // ═══════════════════════════════════════════════════════════════
        // Morph target: nearly closed brackets with 85%-rounded corners
        // cornerRFraction 0.42 = between squircle (0.28) and circle (0.50)
        // — still has squircle character, not a perfect circle arc.
        let circleArcTarget = makeBracketPath(
            frame: faceFrame,
            gapFraction: 0.03,
            cornerRFraction: 0.42
        )
        let morph = CABasicAnimation(keyPath: "path")
        morph.toValue = circleArcTarget
        morph.duration = 0.18
        morph.timingFunction = CAMediaTimingFunction(controlPoints: 0.4, 0.0, 0.2, 1.0)
        morph.fillMode = .forwards
        morph.isRemovedOnCompletion = false
        bracketLayer.add(morph, forKey: "extendBrackets")

        // ═══════════════════════════════════════════════════════════════
        // STEP 2: Brackets ↔ Ring cross-fade (T+0.10, 0.10s)
        // Pushed later so brackets are nearly closed before ring appears.
        // ═══════════════════════════════════════════════════════════════
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.16) {
            // Brackets fade out
            let bracketsOut = CABasicAnimation(keyPath: "opacity")
            bracketsOut.toValue = 0.0
            bracketsOut.duration = 0.10
            bracketsOut.timingFunction = CAMediaTimingFunction(name: .easeIn)
            bracketsOut.fillMode = .forwards
            bracketsOut.isRemovedOnCompletion = false
            self.bracketLayer.add(bracketsOut, forKey: "bracketsFade")

            // Continuous ring fades in (same squircle shape — seamless)
            let ringIn = CABasicAnimation(keyPath: "opacity")
            ringIn.fromValue = 0.0
            ringIn.toValue = 1.0
            ringIn.duration = 0.10
            ringIn.timingFunction = CAMediaTimingFunction(name: .easeOut)
            ringIn.fillMode = .forwards
            ringIn.isRemovedOnCompletion = false
            self.spinContainer.add(ringIn, forKey: "ringFadeIn")
        }

        // ═══════════════════════════════════════════════════════════════
        // STEP 3: Path morph — squircle → circle (T+0.12, 0.25s)
        // Both paths built with NSBezierPath(roundedRect:) so they
        // have identical segment counts → smooth Core Animation lerp.
        // Morph applies to hero ring AND all ghost trails.
        // ═══════════════════════════════════════════════════════════════
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.12) {
            let circlePath = NSBezierPath(
                roundedRect: localRect,
                xRadius: localRect.width / 2,
                yRadius: localRect.height / 2
            ).cgPath

            let morph = CABasicAnimation(keyPath: "path")
            morph.toValue = circlePath
            morph.duration = 0.25
            morph.timingFunction = CAMediaTimingFunction(controlPoints: 0.32, 0.72, 0, 1)
            morph.fillMode = .forwards
            morph.isRemovedOnCompletion = false
            self.ringLayer.add(morph, forKey: "morphToCircle")

            // Morph ghost trails too
            for ghost in self.ghostRings {
                let ghostMorph = morph.copy() as! CABasicAnimation
                ghost.add(ghostMorph, forKey: "morphToCircle")
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // STEP 4: 3D spin + X/Y tumble (T+0.15)
        // The ring spins and tilts through X/Y axes, simulating
        // the ring wrapping around a 3D face topography.
        // ═══════════════════════════════════════════════════════════════
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            self.startSpinAnimation()
        }

        // ═══════════════════════════════════════════════════════════════
        // STEP 5: Auto-trigger verified (T+0.60)
        // After the spin completes, snap flat and draw checkmark.
        // ═══════════════════════════════════════════════════════════════
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.60) {
            self.triggerVerifiedAnimation()
        }
    }

    // MARK: - 3D Spin (Face Topography Scan Effect)

    func startSpinAnimation() {
        // Duration matches the gap between spin start (T+0.15) and flatten (T+0.60)
        let dur: CFTimeInterval = 0.45

        // Time lag between each ghost — tight spacing for dense, smooth trail.
        // 6 ghosts × 0.02s = 120ms total trail span (~7 frames at 60fps).
        let lagPerGhost: CFTimeInterval = 0.02

        // Z rotation — 1 full turn, decelerating
        let spin = CABasicAnimation(keyPath: "transform.rotation.z")
        spin.fromValue = 0
        spin.toValue = CGFloat.pi * 2
        spin.duration = dur
        spin.timingFunction = CAMediaTimingFunction(controlPoints: 0.33, 0, 0, 1)
        spin.fillMode = .forwards
        spin.isRemovedOnCompletion = false

        // X tumble — "scanning face depth" (tilts forward/back)
        let xTilt = CAKeyframeAnimation(keyPath: "transform.rotation.x")
        xTilt.values = [0, 0.85, -0.85, 0.45, 0]
        xTilt.keyTimes = [0, 0.25, 0.55, 0.82, 1.0]
        xTilt.duration = dur
        xTilt.calculationMode = .cubic
        xTilt.fillMode = .forwards
        xTilt.isRemovedOnCompletion = false

        // Y tumble — "scanning face width" (tilts left/right)
        let yTilt = CAKeyframeAnimation(keyPath: "transform.rotation.y")
        yTilt.values = [0, -0.75, 0.90, -0.35, 0]
        yTilt.keyTimes = [0, 0.20, 0.50, 0.82, 1.0]
        yTilt.duration = dur
        yTilt.calculationMode = .cubic
        yTilt.fillMode = .forwards
        yTilt.isRemovedOnCompletion = false

        // Apply to hero ring
        ringLayer.add(spin, forKey: "spin")
        ringLayer.add(xTilt, forKey: "xTilt")
        ringLayer.add(yTilt, forKey: "yTilt")

        // Reveal hero shadow now that spin is starting
        let shadowReveal = CABasicAnimation(keyPath: "shadowOpacity")
        shadowReveal.fromValue = 0
        shadowReveal.toValue = 0.55
        shadowReveal.duration = 0.12
        shadowReveal.fillMode = .forwards
        shadowReveal.isRemovedOnCompletion = false
        ringLayer.add(shadowReveal, forKey: "shadowReveal")

        // Reveal ghost trails with a quick fade-in
        for (i, ghost) in ghostRings.enumerated() {
            let progress = CGFloat(i + 1) / CGFloat(ghostCount + 1)
            let targetOpacity = Float(0.45 * (1.0 - progress))

            let fadeIn = CABasicAnimation(keyPath: "opacity")
            fadeIn.fromValue = 0
            fadeIn.toValue = targetOpacity
            fadeIn.duration = 0.10
            fadeIn.fillMode = .forwards
            fadeIn.isRemovedOnCompletion = false
            ghost.add(fadeIn, forKey: "ghostReveal")
        }

        // ── Apply to ghost trails with staggered time offsets ────────
        // Each ghost gets the same animations but beginTime is delayed,
        // so it trails behind the hero ring by a few frames.
        let now = CACurrentMediaTime()
        for (i, ghost) in ghostRings.enumerated() {
            let lag = CFTimeInterval(i + 1) * lagPerGhost

            let gSpin = spin.copy() as! CABasicAnimation
            gSpin.beginTime = now + lag
            gSpin.fillMode = .both

            let gX = xTilt.copy() as! CAKeyframeAnimation
            gX.beginTime = now + lag
            gX.fillMode = .both

            let gY = yTilt.copy() as! CAKeyframeAnimation
            gY.beginTime = now + lag
            gY.fillMode = .both

            ghost.add(gSpin, forKey: "spin")
            ghost.add(gX, forKey: "xTilt")
            ghost.add(gY, forKey: "yTilt")
        }
    }

    // MARK: - Verified Animation (Snap Flat + Draw Checkmark)
    //
    // The spinning 3D ring instantly stops and snaps flat,
    // becoming a crisp 2D green circle outline.
    // Then a green checkmark is drawn inside it.

    func triggerVerifiedAnimation() {
        guard state == .success else { return }
        state = .verified

        // ═══════════════════════════════════════════════════════════════
        // STEP 1: Snap ring flat — 3D → 2D
        // Capture the current visual transform (all active rotations),
        // remove the animations, set the model layer to the captured
        // state, then spring-animate to identity.
        // ═══════════════════════════════════════════════════════════════
        let current = ringLayer.presentation()?.transform ?? CATransform3DIdentity

        // Remove 3D rotation animations from hero ring
        ringLayer.removeAnimation(forKey: "spin")
        ringLayer.removeAnimation(forKey: "xTilt")
        ringLayer.removeAnimation(forKey: "yTilt")

        // Set model layer to captured visual state (prevents snap-back)
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        ringLayer.transform = current
        CATransaction.commit()

        // Spring-animate to flat (identity transform)
        let flatten = CABasicAnimation(keyPath: "transform")
        flatten.fromValue = current
        flatten.toValue = CATransform3DIdentity
        flatten.duration = 0.20
        flatten.timingFunction = CAMediaTimingFunction(controlPoints: 0.2, 0.9, 0.2, 1.0)
        flatten.fillMode = .forwards
        flatten.isRemovedOnCompletion = false
        ringLayer.add(flatten, forKey: "flatten")

        // ── Fade out ghost trails (they dissolve as ring snaps flat) ─
        for ghost in ghostRings {
            ghost.removeAnimation(forKey: "spin")
            ghost.removeAnimation(forKey: "xTilt")
            ghost.removeAnimation(forKey: "yTilt")

            let ghostFade = CABasicAnimation(keyPath: "opacity")
            ghostFade.toValue = 0.0
            ghostFade.duration = 0.15
            ghostFade.timingFunction = CAMediaTimingFunction(name: .easeIn)
            ghostFade.fillMode = .forwards
            ghostFade.isRemovedOnCompletion = false
            ghost.add(ghostFade, forKey: "ghostFadeOut")
        }

        // ═══════════════════════════════════════════════════════════════
        // STEP 2: Draw green checkmark (T+0.15, 0.30s)
        // Gentle strokeEnd animation — the checkmark "writes in"
        // from the start of its path to the end.
        // ═══════════════════════════════════════════════════════════════
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            // Show checkmark layer
            CATransaction.begin()
            CATransaction.setDisableActions(true)
            self.checkmarkLayer.opacity = 1
            self.checkmarkLayer.strokeEnd = 0
            CATransaction.commit()

            // Animate stroke drawing
            let draw = CABasicAnimation(keyPath: "strokeEnd")
            draw.fromValue = 0
            draw.toValue = 1
            draw.duration = 0.30
            // Smooth ease — gentle start, clean finish
            draw.timingFunction = CAMediaTimingFunction(controlPoints: 0.25, 0.1, 0.25, 1.0)
            draw.fillMode = .forwards
            draw.isRemovedOnCompletion = false
            self.checkmarkLayer.add(draw, forKey: "drawCheck")

            // ═══════════════════════════════════════════════════════════
            // STEP 3: Chain retract after brief dwell (0.22s)
            // ═══════════════════════════════════════════════════════════
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.30 + 0.22) {
                self.triggerRetractAnimation()
            }

            print("Verified.")
        }
    }

    // MARK: - Retract Animation (Island → Notch)

    func triggerRetractAnimation() {
        guard state == .verified else { return }
        state = .retracting

        let notch = notchInfo

        // Content fades out
        let fade = CABasicAnimation(keyPath: "opacity")
        fade.toValue = 0.0
        fade.duration = 0.13
        fade.timingFunction = CAMediaTimingFunction(name: .easeIn)
        fade.fillMode = .forwards
        fade.isRemovedOnCompletion = false
        contentLayer.add(fade, forKey: "retractContentFade")

        // Island collapses back to notch shape
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) {
            let targetW = notch.width
            let targetH = notch.height
            let targetR: CGFloat = 16
            let dur: CFTimeInterval = 0.28
            // Apple "soft-settle" curve — smooth deceleration, no bounce
            let curve = CAMediaTimingFunction(controlPoints: 0.42, 0, 0.58, 1)

            CATransaction.begin()
            CATransaction.setAnimationDuration(dur)
            CATransaction.setAnimationTimingFunction(curve)
            CATransaction.setCompletionBlock {
                // Clean exit after animation settles
                NSApplication.shared.terminate(nil)
            }

            // Path animation: island → notch
            let targetPath = NSBezierPath(
                roundedRect: CGRect(
                    x: notch.centerX - targetW / 2, y: 0,
                    width: targetW, height: targetH
                ),
                xRadius: targetR, yRadius: targetR
            ).cgPath

            let pathAnim = CABasicAnimation(keyPath: "path")
            pathAnim.toValue = targetPath
            pathAnim.duration = dur
            pathAnim.timingFunction = curve
            pathAnim.fillMode = .forwards
            pathAnim.isRemovedOnCompletion = false
            self.islandLayer.add(pathAnim, forKey: "retractPath")

            // Shrink content bounds to match
            let shrink = CABasicAnimation(keyPath: "bounds.size")
            shrink.toValue = CGSize(width: targetW, height: targetH)
            shrink.duration = dur
            shrink.timingFunction = curve
            shrink.fillMode = .forwards
            shrink.isRemovedOnCompletion = false
            self.contentLayer.add(shrink, forKey: "retractBounds")

            // Island fades out at 30% through retract
            let islandFade = CABasicAnimation(keyPath: "opacity")
            islandFade.toValue = 0.0
            islandFade.duration = dur
            islandFade.beginTime = CACurrentMediaTime() + dur * 0.30
            islandFade.timingFunction = CAMediaTimingFunction(name: .easeIn)
            islandFade.fillMode = .both
            islandFade.isRemovedOnCompletion = false
            self.islandLayer.add(islandFade, forKey: "islandFade")

            self.islandLayer.shadowOpacity = 0

            CATransaction.commit()
        }
    }

} // End FaceIDOverlayView

// MARK: - App

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
