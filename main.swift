#!/usr/bin/env swift

import SwiftUI
import AppKit

// Simple version for quick testing
class SimpleDino: ObservableObject {
    @Published var emoji = "🦕"
    @Published var status = "Idle"
    
    func updateBasedOnApp() {
        if let frontApp = NSWorkspace.shared.frontmostApplication {
            let bundleId = frontApp.bundleIdentifier ?? ""
            let appName = frontApp.localizedName ?? ""
            
            switch bundleId.lowercased() {
            case let id where id.contains("slack"):
                emoji = "🦖💼"
                status = "Working hard on Slack!"
            case let id where id.contains("code") || id.contains("xcode") || id.contains("terminal"):
                emoji = "🦕💻"
                status = "Coding like a pro!"
            case let id where id.contains("chrome") || id.contains("safari"):
                emoji = "🦖😴"
                status = "Browsing the web..."
            default:
                emoji = "🦕"
                status = "Just chilling"
            }
        }
    }
}

class SimpleMenuBarApp: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var dino = SimpleDino()
    var timer: Timer?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        if let button = statusItem.button {
            button.title = dino.emoji
            button.action = #selector(statusItemClicked)
            button.target = self
        }
        
        // Update every 3 seconds
        timer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { [weak self] _ in
            self?.dino.updateBasedOnApp()
            DispatchQueue.main.async {
                self?.statusItem.button?.title = self?.dino.emoji ?? "🦕"
            }
        }
        
        print("🦕 Dino Tamagotchi is now running in your menu bar!")
        print("Your dino will change based on what apps you use:")
        print("🦖💼 Slack = Working")
        print("🦕💻 Code/Terminal = Coding")
        print("🦖😴 Browser = Browsing")
        print("🦕 Default = Idle")
    }
    
    @objc func statusItemClicked() {
        let alert = NSAlert()
        alert.messageText = "🦕 Your Dino"
        alert.informativeText = dino.status
        alert.addButton(withTitle: "Feed 🍖")
        alert.addButton(withTitle: "Pet 🫳")
        alert.addButton(withTitle: "OK")
        
        let response = alert.runModal()
        switch response {
        case .alertFirstButtonReturn:
            dino.emoji = "🦕🍖"
            statusItem.button?.title = dino.emoji
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.dino.emoji = "🦕"
                self.statusItem.button?.title = self.dino.emoji
            }
        case .alertSecondButtonReturn:
            dino.emoji = "🦖✨"
            statusItem.button?.title = dino.emoji
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.dino.emoji = "🦕"
                self.statusItem.button?.title = self.dino.emoji
            }
        default:
            break
        }
    }
}

let app = NSApplication.shared
let delegate = SimpleMenuBarApp()
app.delegate = delegate
app.setActivationPolicy(.accessory) // This makes it a menu bar only app
app.run()