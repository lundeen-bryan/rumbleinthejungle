<div align='center'>

# Rumble In The Jungle

*A Kodi 21 add-on for browsing and streaming videos from Rumble.*

</div>

---

## **Table of Contents**
- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Author Info](#author-info)

---

## **About**
**Rumble In The Jungle** is a Kodi 21 add-on that allows users to browse, search, and stream videos from **Rumble** directly within Kodi.

This add-on is built using **Python 3.11+** and is compatible with **Kodi 21 Omega**. It fetches videos from Rumble using their API (if available) or web scraping.

---

## **Installation**

### **Option 1: Install from ZIP**

1. Download the latest `plugin.video.rumbleinthejungle.zip` file from the [Releases](https://github.com/lundeen-bryan/rumbleinthejungle/releases) page.
2. Open Kodi and navigate to:
Add-ons > Install from ZIP file
3. Select the downloaded ZIP file to install the add-on.
4. After installation, find the add-on under:
Add-ons > Video Add-ons > Rumble In The Jungle

### **Option 2: Install via Kodi Source**

1. **Open Kodi** and navigate to: Settings > File Manager
2. **Add Source** and when prompted for the path, enter: https://lundeen-bryan.github.io/rumbleinthejungle/
3. Give the source a name (e.g., `RumbleInTheJungle`).
4. Return to Kodi's **Add-ons** menu and select: Install from zip file.
5. Choose the source you just added (e.g., `RumbleInTheJungle`), then select the ZIP file to install **Ruble In The Jungle**.
6. After installation, find the add-on under: Addons > Video Add-ons > Rumble In The Jungle

---

## **Usage**
Once installed:
1. **Launch the Add-on** from Kodi's "Video Add-ons" section.
2. **Browse Categories**: Select from trending, subscriptions, or search for videos.
3. **Play Videos**: Click on a video to stream it inside Kodi.

---

## **Features**

✅ Browse **Rumble** videos within Kodi
✅ Stream videos directly using Kodi's built-in player
✅ Simple UI with list and grid views
✅ Search functionality for finding specific videos
✅ Compatible with **Kodi 21 Omega**

---

## **Dependencies**

This add-on requires the following Python libraries:

- [`requests`](https://pypi.org/project/requests/) - Fetch video data from Rumble
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) - Web scraping (if API is unavailable)
- [`urllib3`](https://pypi.org/project/urllib3/) - Handling HTTP requests

### **Installing Dependencies (For Developers)**
If developing locally, install dependencies with:
```bash
pip install -r requirements.txt
```

## Development

### Project Structure

plugin.video.rumbleinthejungle
 ┣ lib
 ┣ resources
 ┃ ┗ settings.xml
 ┣ .gitignore
 ┣ addon.xml
 ┣ CHANGELOG.md
 ┣ fanart.png
 ┣ icon.png
 ┣ main.py
 ┗ README.md

## Running in Kodi

1. Zip the add-on for Kodi installation:
cd plugin.video.rumbleinthejungle
zip -r ../plugin.video.rumbleinthejungle.zip *

2. Install the add-on via Kodi's "Install from ZIP file" option.

## Contributing

Pull requests are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request (PR)
For major changes, open an issue first to discuss them.

## License

This add-on is licensed under the MIT License.

# Author Info

- Github - [lundeen-bryan](https://github.com/lundeen-bryan)
- LinkedIn - [BryanLundeen](https://www.linkedin.com/in/bryanlundeen/)
- Twitter – [@LundeenBryan](https://twitter.com/LundeenBryan)
- Facebook – [realbryanlundeen](https://www.facebook.com/realbryanlundeen)

[⭡ Back to top](#rumble-in-the-jungle)

