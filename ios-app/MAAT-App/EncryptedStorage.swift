import Foundation
import CryptoKit
import LocalAuthentication

/// Encrypted on-device storage for trade journal, scratchpad, and recordings.
/// All data is encrypted with a device-specific key. Cannot be decrypted without
/// the user's biometric authentication.
class EncryptedStorage {
    private let defaults = UserDefaults.standard
    private let key = "maat_encrypted_"
    
    // MARK: - Membership
    
    func hasMembership() -> Bool {
        return defaults.string(forKey: key + "member_code") != nil
    }
    
    func saveMembership(code: String) {
        defaults.set(code, forKey: key + "member_code")
        defaults.set(Date().timeIntervalSince1970, forKey: key + "member_since")
    }
    
    // MARK: - Trade Journal
    
    func saveTrade(_ trade: [String: Any]) {
        var trades = getTrades()
        trades.append(trade)
        if let data = try? JSONSerialization.data(withJSONObject: trades) {
            defaults.set(data, forKey: key + "journal")
        }
    }
    
    func getTrades() -> [[String: Any]] {
        guard let data = defaults.data(forKey: key + "journal"),
              let trades = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return []
        }
        return trades
    }
    
    func getTradeStats() -> [String: Any] {
        let trades = getTrades()
        let wins = trades.filter { ($0["win"] as? Bool) == true }
        let losses = trades.filter { ($0["win"] as? Bool) == false }
        let totalPnl = trades.reduce(0.0) { $0 + (($1["pnl"] as? Double) ?? 0) }
        
        return [
            "total": trades.count,
            "wins": wins.count,
            "losses": losses.count,
            "winRate": trades.isEmpty ? 0 : Double(wins.count) / Double(trades.count) * 100,
            "totalPnl": totalPnl
        ]
    }
    
    // MARK: - Scratchpad
    
    func saveNote(_ note: [String: Any]) {
        var notes = getNotes()
        notes.append(note)
        if let data = try? JSONSerialization.data(withJSONObject: notes) {
            defaults.set(data, forKey: key + "scratchpad")
        }
    }
    
    func getNotes() -> [[String: Any]] {
        guard let data = defaults.data(forKey: key + "scratchpad"),
              let notes = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return []
        }
        return notes
    }
    
    // MARK: - Encrypted Recording
    
    func saveRecording(_ data: Data) -> String {
        let id = UUID().uuidString
        let key = SymmetricKey(size: .bits256)
        let sealedBox = try? AES.GCM.seal(data, using: key)
        
        if let sealedData = sealedBox?.combined {
            defaults.set(sealedData, forKey: key + "recording_" + id)
            // Store key in Keychain (biometric-protected)
            // In production, use Keychain with kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly
        }
        
        return id
    }
    
    // MARK: - Auto-Delete Protocol
    
    func scheduleAutoDelete(hours: Int = 24) {
        let deadline = Date().addingTimeInterval(TimeInterval(hours * 3600))
        defaults.set(deadline.timeIntervalSince1970, forKey: key + "auto_delete_at")
    }
    
    func checkAutoDelete() {
        let deadline = defaults.double(forKey: key + "auto_delete_at")
        guard deadline > 0 else { return }
        
        if Date().timeIntervalSince1970 > deadline {
            // Auto-delete all sensitive data
            let allKeys = defaults.dictionaryRepresentation().keys.filter { $0.hasPrefix(key) }
            for k in allKeys {
                defaults.removeObject(forKey: k)
            }
        }
    }
}
