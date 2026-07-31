import Foundation

/// Service for running Gemma 4 on-device via MLX Swift
/// All inference is local. No data leaves the phone.
class GemmaService {
    private let tradingPrompt: String
    private let guardianPrompt: String
    
    init() {
        // System prompts for each mode
        tradingPrompt = """
        You are MAAT Trader, an expert in Easy E's ICT/SMC methodology.
        You analyze charts for Fair Value Gaps, 50-yard line, liquidity sweeps, and retests.
        You log trades, calculate position sizes, track sessions, and save trade ideas.
        All data stays on-device. Be concise and precise with price levels.
        """
        
        guardianPrompt = """
        You are MAAT Guardian, a constitutional safety assistant.
        You help users know their rights during police encounters.
        You provide de-escalation guidance and record keeping.
        You never give legal advice, only factual information about rights.
        All data stays on-device and encrypted.
        """
    }
    
    /// Load the Gemma 4 model (called once at app start)
    func loadModel() async {
        // MLX Swift will download and cache the model
        // This runs once, subsequent launches use cached version
        // model = try? await LLM.load("mlx-community/gemma-4-2b-it")
    }
    
    /// Process user input and return response
    func process(_ input: String, mode: AppState.AppMode) async -> String {
        let systemPrompt = mode == .trading ? tradingPrompt : guardianPrompt
        
        // For now, return a placeholder response
        // Once MLX Swift is integrated, this will run the actual model
        return processLocally(input, mode: mode)
    }
    
    /// Local processing for common commands (no model needed)
    private func processLocally(_ input: String, mode: AppState.AppMode) -> String {
        let lower = input.lowercased()
        
        if mode == .trading {
            if lower.contains("session") || lower.contains("london") || lower.contains("new york") {
                return getSessionInfo()
            }
            if lower.contains("help") {
                return """
                🎤 **MAAT Trader Commands**
                
                Say what you want:
                • "Analyze this chart" — uses camera
                • "FVG scan [candles]" — pattern detection
                • "Log trade: ES=F long, entry 7448, exit 7500, qty 2"
                • "What's my win rate?" — journal stats
                • "Position: $80k, 1% risk, long 7448, stop 7420"
                • "What sessions are active?"
                • "Save idea: ES=F bearish at 7450"
                """
            }
        } else {
            if lower.contains("rights") || lower.contains("know your rights") {
                return """
                🛡️ **Know Your Rights**
                
                1. **You have the right to remain silent.** Say: "I am exercising my right to remain silent."
                2. **You have the right to an attorney.** Say: "I want to speak to my lawyer."
                3. **You do not have to consent to a search.** Say: "I do not consent to searches."
                4. **If detained, ask:** "Am I free to leave?"
                
                Stay calm. Keep hands visible. Say nothing beyond these statements.
                This app is recording. Footage is encrypted on-device.
                """
            }
            if lower.contains("record") || lower.contains("start recording") {
                return "🔴 Recording started. Footage will be encrypted on-device. Tap again to stop."
            }
        }
        
        return "I heard: \"\(input)\". Processing with Gemma 4 on-device..."
    }
    
    private func getSessionInfo() -> String {
        let now = Date()
        let calendar = Calendar.current
        let hour = calendar.component(.hour, from: now)
        let min = calendar.component(.minute, from: now)
        let utc = Double(hour) + Double(min) / 60.0
        
        // Session definitions (UTC)
        struct Session { let name: String; let open: Double; let close: Double; let emoji: String }
        let sessions = [
            Session(name: "Sydney", open: 21, close: 6, emoji: "🇦🇺"),
            Session(name: "Tokyo/Asia", open: 23, close: 8, emoji: "🇯🇵"),
            Session(name: "London", open: 7, close: 16, emoji: "🇬🇧"),
            Session(name: "New York", open: 12, close: 21, emoji: "🇺🇸"),
        ]
        
        var result = "⏰ **Trading Sessions**\n"
        for s in sessions {
            let isActive = s.open <= s.close ? (utc >= s.open && utc < s.close) : (utc >= s.open || utc < s.close)
            let status = isActive ? "🟢 Active" : "⚫"
            result += "\(s.emoji) \(s.name): \(status)\n"
        }
        return result
    }
}
