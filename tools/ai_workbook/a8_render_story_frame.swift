#!/usr/bin/env swift
import AppKit
import Foundation

func die(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 6 else {
    die("usage: a8_render_story_frame.swift input_image output_png title subtitle watermark [scene_tag]")
}

let inputURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])
let title = args[3]
let subtitle = args[4]
let watermark = args[5]
let sceneTag = args.count >= 7 ? args[6] : ""

guard let sourceImage = NSImage(contentsOf: inputURL) else {
    die("cannot read image: \(inputURL.path)")
}

let canvasSize = NSSize(width: 1080, height: 1920)
let canvas = NSImage(size: canvasSize)

func font(_ names: [String], size: CGFloat, weight: NSFont.Weight) -> NSFont {
    for name in names {
        if let candidate = NSFont(name: name, size: size) {
            return candidate
        }
    }
    return NSFont.systemFont(ofSize: size, weight: weight)
}

func drawText(
    _ text: String,
    in rect: NSRect,
    font: NSFont,
    color: NSColor,
    alignment: NSTextAlignment = .left,
    lineSpacing: CGFloat = 6
) {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = alignment
    paragraph.lineBreakMode = .byWordWrapping
    paragraph.lineSpacing = lineSpacing
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: paragraph
    ]
    (text as NSString).draw(
        with: rect,
        options: [.usesLineFragmentOrigin, .usesFontLeading],
        attributes: attrs
    )
}

canvas.lockFocus()

NSColor(calibratedRed: 0.98, green: 0.97, blue: 0.94, alpha: 1.0).setFill()
NSBezierPath(rect: NSRect(origin: .zero, size: canvasSize)).fill()

let imageSize = sourceImage.size
let scale = max(canvasSize.width / imageSize.width, canvasSize.height / imageSize.height)
let sourceWidth = canvasSize.width / scale
let sourceHeight = canvasSize.height / scale
let sourceRect = NSRect(
    x: max(0, (imageSize.width - sourceWidth) / 2),
    y: max(0, (imageSize.height - sourceHeight) / 2),
    width: min(imageSize.width, sourceWidth),
    height: min(imageSize.height, sourceHeight)
)

sourceImage.draw(
    in: NSRect(origin: .zero, size: canvasSize),
    from: sourceRect,
    operation: .copy,
    fraction: 1.0,
    respectFlipped: true,
    hints: [.interpolation: NSImageInterpolation.high]
)

NSColor(calibratedWhite: 0.0, alpha: 0.34).setFill()
NSBezierPath(rect: NSRect(x: 0, y: canvasSize.height - 405, width: canvasSize.width, height: 405)).fill()

NSColor(calibratedWhite: 0.0, alpha: 0.28).setFill()
NSBezierPath(rect: NSRect(x: 0, y: 0, width: canvasSize.width, height: 250)).fill()

let titleFont = font(["PingFangTC-Semibold", "PingFang TC Semibold", "Heiti TC"], size: 66, weight: .semibold)
let subtitleFont = font(["PingFangTC-Regular", "PingFang TC", "Heiti TC"], size: 44, weight: .regular)
let smallFont = font(["PingFangTC-Medium", "PingFang TC", "Heiti TC"], size: 28, weight: .medium)
let watermarkFont = font(["AvenirNext-DemiBold", "HelveticaNeue-Medium"], size: 28, weight: .medium)

drawText(
    title,
    in: NSRect(x: 72, y: canvasSize.height - 160, width: 936, height: 95),
    font: titleFont,
    color: .white,
    lineSpacing: 4
)

drawText(
    subtitle,
    in: NSRect(x: 72, y: canvasSize.height - 285, width: 880, height: 130),
    font: subtitleFont,
    color: NSColor(calibratedWhite: 1.0, alpha: 0.94),
    lineSpacing: 8
)

if !sceneTag.isEmpty {
    drawText(
        sceneTag,
        in: NSRect(x: 72, y: 116, width: 680, height: 44),
        font: smallFont,
        color: NSColor(calibratedWhite: 1.0, alpha: 0.86)
    )
}

drawText(
    watermark,
    in: NSRect(x: 650, y: 74, width: 360, height: 46),
    font: watermarkFont,
    color: NSColor(calibratedWhite: 1.0, alpha: 0.84),
    alignment: .right
)

canvas.unlockFocus()

guard let tiff = canvas.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let png = rep.representation(using: .png, properties: [:]) else {
    die("cannot render output png")
}

do {
    try png.write(to: outputURL)
} catch {
    die("cannot write image: \(outputURL.path): \(error.localizedDescription)")
}
