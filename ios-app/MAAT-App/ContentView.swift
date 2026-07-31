import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        MainView()
    }
}

// MARK: - Main View

struct MainView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            // Mode selector
            Picker("Mode", selection: $appState.activeMode) {
                ForEach(AppState.AppMode.allCases, id: \.self) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .padding()
            
            Spacer()
            
            // Big Talk Button
            TalkButton()
                .environmentObject(appState)
            
            Spacer()
            
            // Response area
            if !appState.lastResponse.isEmpty {
                ScrollView {
                    Text(appState.lastResponse)
                        .font(.body)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                        .padding()
                }
                .frame(maxHeight: 200)
            }
            
            // Quick actions
            QuickActions()
                .environmentObject(appState)
                .padding(.bottom)
        }
    }
}

// MARK: - Big Talk Button

struct TalkButton: View {
    @EnvironmentObject var appState: AppState
    @State private var isPulsing = false
    
    var body: some View {
        Button(action: {
            appState.speech.startListening { text in
                appState.isProcessing = true
                Task {
                    let response = await appState.gemma.process(text, mode: appState.activeMode)
                    await MainActor.run {
                        appState.lastResponse = response
                        appState.isProcessing = false
                        appState.speech.speak(response)
                    }
                }
            }
        }) {
            ZStack {
                Circle()
                    .fill(appState.isProcessing ? Color.orange : Color.red)
                    .frame(width: 120, height: 120)
                    .scaleEffect(isPulsing ? 1.1 : 1.0)
                    .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: isPulsing)
                
                Image(systemName: appState.isProcessing ? "waveform" : "mic.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.white)
            }
        }
        .onAppear { isPulsing = true }
        .disabled(appState.isProcessing)
    }
}

// MARK: - Quick Actions

struct QuickActions: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack(spacing: 20) {
            if appState.activeMode == .trading {
                ActionButton(icon: "chart.bar.fill", label: "FVG Scan")
                ActionButton(icon: "book.fill", label: "Journal")
                ActionButton(icon: "ruler.fill", label: "Position")
                ActionButton(icon: "clock.fill", label: "Sessions")
            } else {
                ActionButton(icon: "shield.fill", label: "Know Rights")
                ActionButton(icon: "video.fill", label: "Record")
                ActionButton(icon: "person.fill", label: "Contact")
                ActionButton(icon: "book.fill", label: "Training")
            }
        }
        .padding(.horizontal)
    }
}

struct ActionButton: View {
    let icon: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.title2)
            Text(label)
                .font(.caption2)
        }
        .frame(width: 70, height: 60)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

// MARK: - Membership View

struct MembershipView: View {
    @EnvironmentObject var appState: AppState
    @State private var inviteCode = ""
    @State private var errorMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Image(systemName: "shield.checkered")
                .font(.system(size: 60))
                .foregroundColor(.blue)
            
            Text("MAAT")
                .font(.largeTitle).bold()
            
            Text("Members-only trading & guardian tools")
                .foregroundColor(.secondary)
            
            VStack(spacing: 12) {
                TextField("Enter invite code", text: $inviteCode)
                    .textFieldStyle(.roundedBorder)
                    .autocapitalization(.allCharacters)
                    .disableAutocorrection(true)
                
                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                Button(action: verifyCode) {
                    if isLoading {
                        ProgressView()
                    } else {
                        Text("Verify & Join")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(inviteCode.isEmpty || isLoading)
            }
            .padding(.horizontal, 40)
            
            Spacer()
            
            Text("All processing on-device. No cloud.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
    
    func verifyCode() {
        isLoading = true
        errorMessage = ""
        
        // Valid invite codes (offline verification)
        let validCodes = ["MAATF125", "MAATD7C4", "MAAT001", "MAAT002", "MAAT003"]
        let code = inviteCode.uppercased().trimmingCharacters(in: .whitespaces)
        
        if validCodes.contains(code) {
            appState.storage.saveMembership(code: code)
            appState.isMember = true
            isLoading = false
            return
        }
        
        // Fallback: try lab bridge
        Task {
            // Try local network first, then tunnel
            let urls = [
                "http://192.168.4.36:9876/verify",
                "https://6159cc5a74e059.lhr.life/verify"
            ]
            
            for urlString in urls {
                guard let url = URL(string: urlString) else { continue }
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                request.httpBody = try? JSONEncoder().encode(["code": code])
                request.timeoutInterval = 3
                
                if let (data, _) = try? await URLSession.shared.data(for: request),
                   let result = try? JSONDecoder().decode(VerifyResult.self, from: data),
                   result.valid {
                    await MainActor.run {
                        appState.storage.saveMembership(code: code)
                        appState.isMember = true
                    }
                    await MainActor.run { isLoading = false }
                    return
                }
            }
            
            await MainActor.run {
                errorMessage = "Invalid invite code"
                isLoading = false
            }
        }
    }
}

struct VerifyResult: Codable {
    let valid: Bool
    let member: String?
}
