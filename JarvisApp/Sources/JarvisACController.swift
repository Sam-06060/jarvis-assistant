//
//  JarvisACController.swift
//  JarvisApp
//
//  Native macOS OAuth2 hardware bridge for Samsung SmartThings AC control.
//  Credentials are read from the process environment — never hard-coded.
//
//  Required environment variables (set in your shell before launching the app):
//    ST_CLIENT_ID      — SmartThings OAuth client ID
//    ST_CLIENT_SECRET  — SmartThings OAuth client secret
//    ST_DEVICE_ID      — SmartThings device UUID
//    ST_ACCESS_TOKEN   — Initial access token (only needed on first run)
//    ST_REFRESH_TOKEN  — Initial refresh token (only needed on first run)
//
//  After the first run, tokens are persisted in UserDefaults and auto-refreshed.
//  TODO: KEYCHAIN — migrate token storage to the macOS Keychain for production.
//

import Foundation

// MARK: - JarvisACController

@MainActor
final class JarvisACController: ObservableObject {

    // MARK: - Configuration (sourced from process environment)

    private let clientId: String
    private let clientSecret: String
    private let deviceId: String

    // MARK: - Token Storage (UserDefaults, seeded from env on first launch)
    // TODO: KEYCHAIN — replace UserDefaults with SecItemAdd / SecItemCopyMatching
    // for encrypted, secure storage in the macOS Keychain.

    private var accessToken: String {
        get {
            if let stored = UserDefaults.standard.string(forKey: "ST_AccessToken"),
               !stored.isEmpty {
                return stored
            }
            // First-run seed from environment variable
            return ProcessInfo.processInfo.environment["ST_ACCESS_TOKEN"] ?? ""
        }
        set {
            UserDefaults.standard.set(newValue, forKey: "ST_AccessToken")
        }
    }

    private var refreshToken: String {
        get {
            if let stored = UserDefaults.standard.string(forKey: "ST_RefreshToken"),
               !stored.isEmpty {
                return stored
            }
            // First-run seed from environment variable
            return ProcessInfo.processInfo.environment["ST_REFRESH_TOKEN"] ?? ""
        }
        set {
            UserDefaults.standard.set(newValue, forKey: "ST_RefreshToken")
        }
    }

    // MARK: - Initialiser

    init() {
        // Merge process env with .env file so the app works when launched
        // directly (Dock, Spotlight, double-click) without a shell sourcing .env.
        let merged = JarvisACController.mergedEnvironment()

        self.clientId  = merged["ST_CLIENT_ID"]     ?? ""
        self.clientSecret = merged["ST_CLIENT_SECRET"] ?? ""
        self.deviceId  = merged["ST_DEVICE_ID"]     ?? "ee2f1cab-7be3-3d30-895e-69af725c7291"

        // Seed tokens into UserDefaults on first launch (env wins over any stale cached value)
        if let tok = merged["ST_ACCESS_TOKEN"],  !tok.isEmpty {
            UserDefaults.standard.set(tok, forKey: "ST_AccessToken")
        }
        if let tok = merged["ST_REFRESH_TOKEN"], !tok.isEmpty {
            UserDefaults.standard.set(tok, forKey: "ST_RefreshToken")
        }

        if clientId.isEmpty     { print("⚠️ [JarvisAC] ST_CLIENT_ID not found in env or .env file.") }
        if clientSecret.isEmpty { print("⚠️ [JarvisAC] ST_CLIENT_SECRET not found in env or .env file.") }
        if accessToken.isEmpty  { print("⚠️ [JarvisAC] No access token found. Add ST_ACCESS_TOKEN to .env") }
        if refreshToken.isEmpty { print("⚠️ [JarvisAC] No refresh token found. Add ST_REFRESH_TOKEN to .env") }

        print("✅ [JarvisAC] Controller initialised. Device: \(String(deviceId.prefix(8)))...")
    }

    // MARK: - .env Loader

    /// Reads the project's `.env` file and merges it with the process environment.
    /// Process environment always wins (shell-exported vars take precedence).
    /// Looks for `.env` relative to the running binary's location.
    private static func mergedEnvironment() -> [String: String] {
        var env = ProcessInfo.processInfo.environment

        // Candidate paths for the .env file, from most to least likely
        let candidates: [String] = [
            // Primary: hardcoded project root (works in .app bundles and swift run)
            "/Users/samsonganta/Desktop/jarvis-assistant/.env",
            // Fallback: tilde expansion
            NSString("~/Desktop/jarvis-assistant/.env").expandingTildeInPath,
        ]

        for path in candidates {
            guard FileManager.default.fileExists(atPath: path),
                  let content = try? String(contentsOfFile: path, encoding: .utf8) else { continue }

            print("🔑 [JarvisAC] Loading credentials from: \(path)")
            for line in content.components(separatedBy: .newlines) {
                let trimmed = line.trimmingCharacters(in: .whitespaces)
                guard !trimmed.hasPrefix("#"), !trimmed.isEmpty else { continue }
                let parts = trimmed.split(separator: "=", maxSplits: 1).map(String.init)
                guard parts.count == 2 else { continue }
                let key   = parts[0].trimmingCharacters(in: .whitespaces)
                var value = parts[1].trimmingCharacters(in: .whitespaces)
                // Strip optional surrounding quotes
                if (value.hasPrefix("\"") && value.hasSuffix("\"")) ||
                   (value.hasPrefix("'")  && value.hasSuffix("'")) {
                    value = String(value.dropFirst().dropLast())
                }
                // Process env always wins
                if env[key] == nil { env[key] = value }
            }
            break // Stop after the first found .env
        }

        return env
    }


    // MARK: - Public Interface

    /// Power the AC unit on.
    func turnOn() async {
        let ok = await sendCommand(capability: "switch", command: "on")
        print(ok ? "✅ [JarvisAC] AC turned ON." : "❌ [JarvisAC] Failed to turn AC on.")
    }

    /// Power the AC unit off.
    func turnOff() async {
        let ok = await sendCommand(capability: "switch", command: "off")
        print(ok ? "✅ [JarvisAC] AC turned OFF." : "❌ [JarvisAC] Failed to turn AC off.")
    }

    /// Set the cooling setpoint. Valid range: 16 – 30 °C.
    func setTemperature(to celsius: Int) async {
        guard (16...30).contains(celsius) else {
            print("⚠️ [JarvisAC] Temperature \(celsius)°C is out of range [16, 30]. Clamping rejected.")
            return
        }
        let ok = await sendCommand(
            capability: "thermostatCoolingSetpoint",
            command:    "setCoolingSetpoint",
            arguments:  [celsius]
        )
        print(ok ? "✅ [JarvisAC] Temperature set to \(celsius)°C." : "❌ [JarvisAC] Failed to set temperature.")
    }

    /// Adjust the cooling setpoint by a relative delta (e.g. +1 or -1).
    func adjustTemperature(by delta: Int) async {
        // Fetch the current setpoint from SmartThings first
        guard let current = await fetchCoolingSetpoint() else {
            print("⚠️ [JarvisAC] Could not read current setpoint to adjust temperature.")
            return
        }
        let newTemp = current + delta
        await setTemperature(to: newTemp)
    }

    /// Log basic device status (switch state + temp) to console.
    func logStatus() async {
        guard !deviceId.isEmpty else {
            print("⚠️ [JarvisAC] No device ID configured.")
            return
        }
        let urlString = "https://api.smartthings.com/v1/devices/\(deviceId)/components/main/status"
        guard let url = URL(string: urlString) else { return }
        var request = URLRequest(url: url)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                print("❌ [JarvisAC] Could not parse status response.")
                return
            }
            let sw    = (json["switch"] as? [String: Any])?["switch"] as? [String: Any]
            let tm    = (json["temperatureMeasurement"] as? [String: Any])?["temperature"] as? [String: Any]
            let sp    = (json["thermostatCoolingSetpoint"] as? [String: Any])?["coolingSetpoint"] as? [String: Any]
            let mode  = ((json["airConditionerMode"] as? [String: Any])?["airConditionerMode"] as? [String: Any])?["value"] as? String ?? "?"
            let fan   = ((json["airConditionerFanMode"] as? [String: Any])?["fanMode"] as? [String: Any])?["value"] as? String ?? "?"
            let power = sw?["value"] as? String ?? "?"
            let temp  = tm?["value"] as? Double
            let setpt = sp?["value"] as? Double
            var summary = "📊 [JarvisAC] AC=\(power) | mode=\(mode) | fan=\(fan)"
            if let t = temp  { summary += " | room=\(Int(t))°C" }
            if let s = setpt { summary += " | setpoint=\(Int(s))°C" }
            print(summary)
        } catch {
            print("❌ [JarvisAC] Status fetch error: \(error.localizedDescription)")
        }
    }

    /// Set the operating mode. Valid values: "cool", "heat", "auto", "dry", "wind", "fanOnly".
    func setMode(_ mode: String) async {
        let valid = ["cool", "heat", "auto", "dry", "wind", "fanonly"]
        guard valid.contains(mode.lowercased()) else {
            print("⚠️ [JarvisAC] '\(mode)' is not a valid AC mode. Valid: \(valid.joined(separator: ", "))")
            return
        }
        let ok = await sendCommand(
            capability: "airConditionerMode",
            command:    "setAirConditionerMode",
            arguments:  [mode.lowercased()]
        )
        print(ok ? "✅ [JarvisAC] Mode set to '\(mode)'." : "❌ [JarvisAC] Failed to set mode.")
    }

    // MARK: - Core Execution Engine

    /// Send a command, automatically refreshing the OAuth token once if the first attempt returns 401.
    private func sendCommand(capability: String, command: String, arguments: [Any] = []) async -> Bool {
        let firstAttempt = await executeNetworkRequest(capability: capability, command: command, arguments: arguments)
        if firstAttempt { return true }

        print("⚠️ [JarvisAC] Access token may be expired. Refreshing credentials...")
        let refreshed = await refreshOAuthTokens()
        guard refreshed else {
            print("❌ [JarvisAC] FATAL: Refresh token failed. Manual re-authentication required.")
            return false
        }
        print("✅ [JarvisAC] Credentials refreshed. Retrying command...")
        return await executeNetworkRequest(capability: capability, command: command, arguments: arguments)
    }

    /// Execute a single HTTP POST to the SmartThings device commands endpoint.
    /// Returns `true` on HTTP 2xx, `false` on 401 (so `sendCommand` can retry), or on any other error.
    private func executeNetworkRequest(capability: String, command: String, arguments: [Any]) async -> Bool {
        guard !deviceId.isEmpty else {
            print("❌ [JarvisAC] Device ID is not configured.")
            return false
        }

        let urlString = "https://api.smartthings.com/v1/devices/\(deviceId)/commands"
        guard let url = URL(string: urlString) else {
            print("❌ [JarvisAC] Invalid URL: \(urlString)")
            return false
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 10

        let payload: [String: Any] = [
            "commands": [[
                "component":  "main",
                "capability": capability,
                "command":    command,
                "arguments":  arguments
            ] as [String: Any]]
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            print("🔌 [JarvisAC] Sending → capability=\(capability) command=\(command) token=\(String(accessToken.prefix(8)))...")
            let (data, response) = try await URLSession.shared.data(for: request)

            guard let http = response as? HTTPURLResponse else { return false }

            let body = String(data: data, encoding: .utf8) ?? "<no body>"
            print("📡 [JarvisAC] HTTP \(http.statusCode) ← \(body.prefix(200))")

            if http.statusCode == 401 {
                print("⚠️ [JarvisAC] 401 Unauthorized — token needs refresh.")
                return false  // Signal caller to attempt refresh
            }
            if (200...299).contains(http.statusCode) {
                return true
            }
            print("⚠️ [JarvisAC] Unexpected HTTP \(http.statusCode) from SmartThings.")
        } catch {
            print("❌ [JarvisAC] Network error: \(error.localizedDescription)")
        }
        return false
    }

    // MARK: - Status Helpers

    /// Fetch the current cooling setpoint integer from SmartThings.
    private func fetchCoolingSetpoint() async -> Int? {
        guard !deviceId.isEmpty else { return nil }
        let urlString = "https://api.smartthings.com/v1/devices/\(deviceId)/components/main/capabilities/thermostatCoolingSetpoint/status"
        guard let url = URL(string: urlString) else { return nil }
        var request = URLRequest(url: url)
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 8
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let sp = json["coolingSetpoint"] as? [String: Any],
               let val = sp["value"] as? Double {
                return Int(val)
            }
        } catch {
            print("❌ [JarvisAC] fetchCoolingSetpoint error: \(error.localizedDescription)")
        }
        return nil
    }

    // MARK: - OAuth Token Regeneration

    /// POST to the SmartThings OAuth token endpoint with the current refresh token.
    /// On success, updates `accessToken` and `refreshToken` in UserDefaults.
    private func refreshOAuthTokens() async -> Bool {
        guard let url = URL(string: "https://api.smartthings.com/oauth/token") else { return false }
        guard !clientId.isEmpty, !clientSecret.isEmpty else {
            print("❌ [JarvisAC] Cannot refresh — ST_CLIENT_ID or ST_CLIENT_SECRET is not set.")
            return false
        }
        guard !refreshToken.isEmpty else {
            print("❌ [JarvisAC] Cannot refresh — no refresh token available.")
            return false
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 10

        // Basic Auth: Base64-encode "clientId:clientSecret"
        let credentials = "\(clientId):\(clientSecret)"
        let base64Creds = Data(credentials.utf8).base64EncodedString()
        request.setValue("Basic \(base64Creds)", forHTTPHeaderField: "Authorization")
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let body = "grant_type=refresh_token&refresh_token=\(refreshToken)&client_id=\(clientId)&client_secret=\(clientSecret)"
        request.httpBody = Data(body.utf8)

        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse,
                  (200...299).contains(http.statusCode) else {
                if let http = response as? HTTPURLResponse {
                    print("❌ [JarvisAC] Token refresh failed with HTTP \(http.statusCode).")
                }
                return false
            }

            guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let newAccess  = json["access_token"]  as? String,
                  let newRefresh = json["refresh_token"] as? String else {
                print("❌ [JarvisAC] Token refresh response missing expected fields.")
                return false
            }

            // Persist new tokens — they'll be used for all subsequent requests
            self.accessToken  = newAccess
            self.refreshToken = newRefresh
            print("✅ [JarvisAC] Tokens refreshed and saved.")
            return true

        } catch {
            print("❌ [JarvisAC] Token refresh network error: \(error.localizedDescription)")
        }
        return false
    }
}
