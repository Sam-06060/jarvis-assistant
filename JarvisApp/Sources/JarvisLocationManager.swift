import Foundation
import CoreLocation
import Combine

class JarvisLocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    
    @Published var location: CLLocation?
    @Published var authorizationStatus: CLAuthorizationStatus
    
    override init() {
        self.authorizationStatus = manager.authorizationStatus
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 100 // Update whenever user moves 100 meters
    }
    
    func requestPermission() {
        #if os(macOS)
        manager.requestAlwaysAuthorization() // macOS uses Always (or authorized)
        #else
        manager.requestWhenInUseAuthorization()
        #endif
    }
    
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        DispatchQueue.main.async {
            self.authorizationStatus = manager.authorizationStatus
            #if os(macOS)
            if self.authorizationStatus == .authorizedAlways || self.authorizationStatus == .authorized {
                self.manager.startUpdatingLocation()
            }
            #else
            if self.authorizationStatus == .authorizedAlways || self.authorizationStatus == .authorizedWhenInUse {
                self.manager.startUpdatingLocation()
            }
            #endif
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let newLoc = locations.last else { return }
        DispatchQueue.main.async {
            self.location = newLoc
            // We purposefully do NOT stop updating; the distance filter handles power efficiency.
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("⚠️ CoreLocation Error: \(error.localizedDescription)")
    }
}
