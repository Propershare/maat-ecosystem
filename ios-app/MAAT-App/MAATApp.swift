import SwiftUI

@main
struct MAATApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var isMember = false
    @Published var isProcessing = false
    @Published var lastResponse = ""
    @Published var activeMode: AppMode = .trading
    
    let gemma = GemmaService()
    let speech = SpeechService()
    let storage = EncryptedStorage()
    
    enum AppMode: String, CaseIterable {
        case trading = "📊 Trader"
        case guardian = "🛡️ Guardian"
    }
    
    init() {
        // Check if already registered
        isMember = storage.hasMembership()
    }
}
