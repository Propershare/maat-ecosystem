import Foundation
import Speech
import AVFoundation

/// Handles voice input (speech-to-text) and output (text-to-speech)
/// All processing is on-device. No data leaves the phone.
class SpeechService: NSObject {
    private let synthesizer = AVSpeechSynthesizer()
    private let audioEngine = AVAudioEngine()
    private var recognitionTask: SFSpeechRecognitionTask?
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    
    var onResult: ((String) -> Void)?
    
    override init() {
        super.init()
    }
    
    /// Start listening and return the transcribed text via callback
    func startListening(callback: @escaping (String) -> Void) {
        self.onResult = callback
        
        // Check permissions
        SFSpeechRecognizer.requestAuthorization { status in
            guard status == .authorized else {
                callback("Speech recognition not authorized")
                return
            }
        }
        
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            guard granted else {
                callback("Microphone not authorized")
                return
            }
        }
        
        guard let recognizer = recognizer, recognizer.isAvailable else {
            callback("Speech recognition not available")
            return
        }
        
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            callback("Audio session error")
            return
        }
        
        // Create a NEW request each time (can't reuse)
        let recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        recognitionRequest.shouldReportPartialResults = false
        
        let inputNode = audioEngine.inputNode
        
        recognitionTask = recognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            if let result = result, result.isFinal {
                callback(result.bestTranscription.formattedString)
                self?.stopListening()
            } else if error != nil {
                callback("")
                self?.stopListening()
            }
        }
        
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        audioEngine.prepare()
        do {
            try audioEngine.start()
        } catch {
            callback("Could not start audio engine")
        }
    }
    
    /// Stop listening
    func stopListening() {
        if audioEngine.isRunning {
            audioEngine.stop()
        }
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionTask?.cancel()
        recognitionTask = nil
    }
    
    /// Speak text through device speaker (or glasses)
    func speak(_ text: String) {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = 0.5
        utterance.pitchMultiplier = 1.0
        utterance.volume = 1.0
        synthesizer.speak(utterance)
    }
}
