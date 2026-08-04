import AppKit
import Foundation

// usage: swift ce_cards.swift <input.json> <base_dir>
let args = CommandLine.arguments
let inputJson = args[1]
let baseDir = args[2]
let previewDir = baseDir + "/preview"
let outDir = baseDir + "/spec_cards"
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let data = try! Data(contentsOf: URL(fileURLWithPath: inputJson))
let cards = try! JSONSerialization.jsonObject(with: data) as! [[String: Any]]

let W: CGFloat = 720, H: CGFloat = 1280
func font(_ s: CGFloat) -> NSFont { NSFont(name: "PingFangTC-Semibold", size: s) ?? NSFont.boldSystemFont(ofSize: s) }

for c in cards {
    let id = c["id"] as! Int
    let tone = c["tone"] as! String
    let hook = c["hook_disp"] as! String
    let frame = c["frame"] as! String
    guard let base = NSImage(contentsOfFile: previewDir + "/" + frame) else { print("skip \(id) no frame"); continue }
    let img = NSImage(size: NSSize(width: W, height: H))
    img.lockFocus()
    let bs = base.size
    let scale = max(W / bs.width, H / bs.height)
    let dw = bs.width * scale, dh = bs.height * scale
    base.draw(in: NSRect(x: (W - dw) / 2, y: (H - dh) / 2, width: dw, height: dh))
    NSColor(white: 0, alpha: 0.45).setFill(); NSRect(x: 0, y: H - 150, width: W, height: 150).fill()
    NSColor(white: 0, alpha: 0.42).setFill(); NSRect(x: 0, y: 0, width: W, height: 380).fill()
    let top = "#\(String(format: "%02d", id))  \(tone)"
    (top as NSString).draw(at: NSPoint(x: 30, y: H - 100),
        withAttributes: [.font: font(40), .foregroundColor: NSColor.white])
    let para = NSMutableParagraphStyle(); para.lineSpacing = 10
    (hook as NSString).draw(in: NSRect(x: 40, y: 70, width: W - 80, height: 290),
        withAttributes: [.font: font(56), .foregroundColor: NSColor.white, .paragraphStyle: para])
    img.unlockFocus()
    guard let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
          let jpg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85]) else { continue }
    try? jpg.write(to: URL(fileURLWithPath: outDir + "/card_" + String(format: "%02d", id) + ".jpg"))
    print("card \(id) ok")
}
