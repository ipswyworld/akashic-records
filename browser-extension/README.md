# Akasha Browser Extension

This extension allows you to stream your web activity directly into your Akasha "Akashic Records" and manually clip web pages for long-term storage and AI analysis.

## Features
- **Telemetry Streaming:** Automatically logs page visits to your local Akasha node.
- **Web Clipper:** One-click clipping of the current URL into your Library.
- **Customizable:** Configure your backend URL and User ID in the settings.

## Installation
1. Open Chrome or any Chromium-based browser (Edge, Brave, etc.).
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** (toggle in the top-right corner).
4. Click **Load unpacked**.
5. Select the `browser-extension` directory from this project.

## Development Notes
- **Background Script (`background.js`):** Handles the automatic telemetry pings.
- **Popup (`popup.html`/`popup.js`):** Provides the manual clipping interface and settings.
- **Content Script (`content.js`):** Currently a placeholder for future feature expansion (like DOM manipulation or local extraction).

## Icons
Please replace the placeholder files in `icons/` with valid PNG images (16x16, 48x48, 128x128) to avoid extension loading warnings.
