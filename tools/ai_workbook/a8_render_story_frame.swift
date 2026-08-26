#!/usr/bin/env swift
import AppKit
import Foundation

func die(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 6 else {
    die("usage: a8_render_story_frame.swift input_image output_png title subtitle watermark [scene_tag] [mode] [width] [height]")
}

let inputURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])
let title = args[3]
let subtitle = args[4]
let watermark = args[5]
let sceneTag = args.count >= 7 ? args[6] : ""
let mode = args.count >= 8 ? args[7] : "scene"
let canvasWidth = args.count >= 9 ? CGFloat(Double(args[8]) ?? 1080) : 1080
let canvasHeight = args.count >= 10 ? CGFloat(Double(args[9]) ?? 1920) : 1920

let isClear = args[1] == "clear" || args[1] == "transparent"
let sourceImage: NSImage?
if isClear {
    sourceImage = nil
} else {
    guard let img = NSImage(contentsOf: inputURL) else {
        die("cannot read image: \(inputURL.path)")
    }
    sourceImage = img
}

let canvasSize = NSSize(width: canvasWidth, height: canvasHeight)
let isLandscape = canvasSize.width > canvasSize.height
let canvas = NSImage(size: canvasSize)

let cream = NSColor(calibratedRed: 0.98, green: 0.97, blue: 0.94, alpha: 1.0)
let warmCream = NSColor(calibratedRed: 0.98, green: 0.96, blue: 0.92, alpha: 1.0)
let darkBrown = NSColor(calibratedRed: 0.24, green: 0.17, blue: 0.12, alpha: 1.0)
let warmGold = NSColor(calibratedRed: 0.79, green: 0.66, blue: 0.43, alpha: 1.0)

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

if let img = sourceImage {
    cream.setFill()
    NSBezierPath(rect: NSRect(origin: .zero, size: canvasSize)).fill()

    let imageSize = img.size
    let scale = max(canvasSize.width / imageSize.width, canvasSize.height / imageSize.height)
    let sourceWidth = canvasSize.width / scale
    let sourceHeight = canvasSize.height / scale
    let sourceRect = NSRect(
        x: max(0, (imageSize.width - sourceWidth) / 2),
        y: max(0, (imageSize.height - sourceHeight) / 2),
        width: min(imageSize.width, sourceWidth),
        height: min(imageSize.height, sourceHeight)
    )

    img.draw(
        in: NSRect(origin: .zero, size: canvasSize),
        from: sourceRect,
        operation: .copy,
        fraction: 1.0,
        respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high]
    )
} else {
    NSColor.clear.setFill()
    NSBezierPath(rect: NSRect(origin: .zero, size: canvasSize)).fill()
}

let titleFont = font(["PingFangTC-Semibold", "PingFang TC Semibold", "Heiti TC"], size: isLandscape ? 52 : 54, weight: .semibold)
let subtitleFont = font(["PingFangTC-Regular", "PingFang TC", "Heiti TC"], size: isLandscape ? 34 : 36, weight: .regular)
let smallFont = font(["PingFangTC-Medium", "PingFang TC", "Heiti TC"], size: isLandscape ? 24 : 28, weight: .medium)
let brandFont = font(["AvenirNext-DemiBold", "HelveticaNeue-Medium"], size: isLandscape ? 28 : 32, weight: .medium)
let scriptFont = font(["AvenirNext-Regular", "HelveticaNeue"], size: isLandscape ? 22 : 25, weight: .regular)

func drawBrandRule(y: CGFloat, width: CGFloat = 220, x: CGFloat = 72) {
    warmGold.withAlphaComponent(0.92).setFill()
    NSBezierPath(rect: NSRect(x: x, y: y, width: width, height: 4)).fill()
}

func drawWatermark(color: NSColor = NSColor(calibratedWhite: 1.0, alpha: 0.82)) {
    drawText(
        watermark,
        in: isLandscape
            ? NSRect(x: canvasSize.width - 480, y: 48, width: 410, height: 42)
            : NSRect(x: 645, y: 68, width: 365, height: 46),
        font: brandFont,
        color: color,
        alignment: .right
    )
}

if mode == "intro" {
    warmCream.withAlphaComponent(0.80).setFill()
    NSBezierPath(rect: NSRect(origin: .zero, size: canvasSize)).fill()

    drawText(
        watermark,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 118, width: 560, height: 48)
            : NSRect(x: 72, y: canvasSize.height - 170, width: 500, height: 55),
        font: brandFont,
        color: darkBrown,
        lineSpacing: 3
    )
    drawBrandRule(y: canvasSize.height - (isLandscape ? 142 : 210), width: 180)
    drawText(
        title,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 320, width: canvasSize.width - 144, height: 108)
            : NSRect(x: 72, y: canvasSize.height - 430, width: 850, height: 130),
        font: font(["PingFangTC-Semibold", "PingFang TC Semibold", "Heiti TC"], size: isLandscape ? 58 : 62, weight: .semibold),
        color: darkBrown,
        lineSpacing: 8
    )
    drawText(
        subtitle,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 405, width: canvasSize.width - 220, height: 72)
            : NSRect(x: 72, y: canvasSize.height - 535, width: 800, height: 95),
        font: subtitleFont,
        color: darkBrown.withAlphaComponent(0.86),
        lineSpacing: 8
    )
    drawText(
        "SINCE 2016",
        in: NSRect(x: 72, y: isLandscape ? 48 : 88, width: 360, height: 44),
        font: smallFont,
        color: darkBrown.withAlphaComponent(0.72)
    )
} else if mode == "outro" {
    warmCream.withAlphaComponent(0.86).setFill()
    NSBezierPath(rect: NSRect(origin: .zero, size: canvasSize)).fill()

    let outroTitleFont = font(["PingFangTC-Semibold", "PingFang TC Semibold", "Heiti TC"], size: isLandscape ? 44 : 43, weight: .semibold)
    let outroSubtitleFont = font(["PingFangTC-Regular", "PingFang TC", "Heiti TC"], size: isLandscape ? 30 : 33, weight: .regular)

    drawText(
        title,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 330, width: canvasSize.width - 144, height: 160)
            : NSRect(x: 72, y: canvasSize.height - 455, width: 936, height: 190),
        font: outroTitleFont,
        color: darkBrown,
        lineSpacing: 12
    )
    drawBrandRule(y: canvasSize.height - (isLandscape ? 360 : 490), width: 230)
    drawText(
        subtitle,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 450, width: canvasSize.width - 220, height: 78)
            : NSRect(x: 72, y: canvasSize.height - 602, width: 820, height: 90),
        font: outroSubtitleFont,
        color: darkBrown.withAlphaComponent(0.84),
        lineSpacing: 8
    )
    drawText(
        watermark,
        in: NSRect(x: 72, y: isLandscape ? 48 : 88, width: 430, height: 48),
        font: brandFont,
        color: darkBrown.withAlphaComponent(0.80)
    )
} else {
    let topBandHeight: CGFloat = isLandscape ? 235 : 305
    let bottomBandHeight: CGFloat = isLandscape ? 130 : 178
    darkBrown.withAlphaComponent(0.18).setFill()
    NSBezierPath(rect: NSRect(x: 0, y: canvasSize.height - topBandHeight, width: canvasSize.width, height: topBandHeight)).fill()

    darkBrown.withAlphaComponent(0.13).setFill()
    NSBezierPath(rect: NSRect(x: 0, y: 0, width: canvasSize.width, height: bottomBandHeight)).fill()

    drawBrandRule(y: canvasSize.height - (isLandscape ? 82 : 112), width: 145)
    drawText(
        title,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 145, width: canvasSize.width - 144, height: 64)
            : NSRect(x: 72, y: canvasSize.height - 190, width: 870, height: 78),
        font: titleFont,
        color: .white,
        lineSpacing: 4
    )

    drawText(
        subtitle,
        in: isLandscape
            ? NSRect(x: 72, y: canvasSize.height - 210, width: canvasSize.width - 144, height: 64)
            : NSRect(x: 72, y: canvasSize.height - 266, width: 850, height: 82),
        font: subtitleFont,
        color: NSColor(calibratedWhite: 1.0, alpha: 0.92),
        lineSpacing: 7
    )

    if !sceneTag.isEmpty {
        drawText(
            sceneTag,
            in: NSRect(x: 72, y: isLandscape ? 58 : 92, width: 230, height: 44),
            font: smallFont,
            color: NSColor(calibratedWhite: 1.0, alpha: 0.70)
        )
    }
    drawWatermark()
    drawText(
        "Catering Design",
        in: NSRect(x: 72, y: isLandscape ? 36 : 70, width: 380, height: 40),
        font: scriptFont,
        color: NSColor(calibratedWhite: 1.0, alpha: 0.66)
    )
}

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
