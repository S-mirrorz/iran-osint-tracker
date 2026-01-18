# 🔍 Iran OSINT Tracker v3.0 - Complete Edition

**Open Source Intelligence Platform for Iran Research & Accountability**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

A comprehensive, self-hosted OSINT (Open Source Intelligence) toolkit designed specifically for researchers, journalists, human rights organizations, and investigators documenting activities related to the Iranian regime. This tool helps track individuals, investigate financial connections, verify media authenticity, and monitor internet connectivity in Iran.

---

## 📋 Table of Contents

- [Why This Tool Exists](#-why-this-tool-exists)
- [Features Overview](#-features-overview)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Security & Safety](#-security--safety)
- [Feature Details](#-feature-details)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Legal Disclaimer](#-legal-disclaimer)
- [Resources](#-resources)
- [Acknowledgments](#-acknowledgments)
- [License](#-license)

---

## 🎯 Why This Tool Exists

The Iranian regime has been documented engaging in widespread human rights abuses, including the violent suppression of protests (such as the 2022 Mahsa Amini protests), execution of political prisoners, and transnational repression targeting diaspora communities. 

This tool was created to support:

- **Human Rights Organizations** documenting abuses and building cases for accountability
- **Investigative Journalists** researching regime-affiliated individuals and networks
- **Researchers** studying sanctions evasion, shell companies, and illicit finance
- **Legal Teams** preparing evidence for international tribunals and courts
- **Diaspora Communities** identifying regime agents operating abroad

All methods employed by this tool comply with platform Terms of Service and follow the [Berkeley Protocol on Digital Open Source Investigations](https://www.ohchr.org/en/publications/policy-and-methodological-publications/berkeley-protocol-digital-open-source).

---

## ✨ Features Overview

### 🔎 Core Investigation Tools
- **Subject Management** — Track investigation targets with status, risk levels, and notes
- **Search URL Generator** — Automatically generate OSINT search links across 20+ platforms
- **Findings Database** — Document and cite all discoveries with source attribution

### 💰 Follow the Money (NEW in v3.0)
- Financial investigation resources (ICIJ, FinCEN, FATF)
- Shell company research tools
- Trade and shipping tracking (vessels, flights, cargo)
- Property and asset search databases
- Reference list of IRGC-linked sanctioned entities

### 📷 Media Verification (NEW in v3.0)
- Reverse image search across multiple engines
- Geolocation tools for photos and videos
- Image forensics (metadata, manipulation detection)
- Video verification tools
- Step-by-step Berkeley Protocol methodology guide

### 🌐 Internet Status Monitoring (NEW in v3.0)
- Real-time Iran connectivity monitoring
- Censorship testing resources
- Circumvention tool links
- Historical shutdown tracking

### 📚 Comprehensive Database Links
- Sanctions databases (OFAC, OpenSanctions, UK, EU, UN)
- Corporate registries (OpenCorporates, ICIJ Offshore Leaks)
- Iran-specific resources (IranWatch, IHR, HRW)
- OSINT tools (Archive.org, Shodan, Maltego)

### 📡 Monitoring Dashboard
- Track up to 10 Twitter/X accounts
- Monitor up to 10 news sources
- Suggested sources for Iran coverage

### 📖 Security Guide
- VPN and connection security recommendations
- Identity protection best practices
- Browser security configurations
- Operational security (OpSec) guidance
- Emergency contacts for threatened researchers

---

## 📸 Screenshots

The web dashboard features a modern, dark-themed interface with intuitive navigation:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍 Iran OSINT Tracker                                               │
│ Open Source Intelligence Platform v3.0                              │
├─────────────────────────────────────────────────────────────────────┤
│ [Investigate] [Subjects] [Databases] [Follow Money] [Verify Media]  │
│ [Internet Status] [How To] [Monitor] [References] [Contacts]        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ ➕ Add       │  │ 🔎 Generate  │  │ 📊 Statistics │              │
│  │ Subject      │  │ Search URLs  │  │              │              │
│  │              │  │              │  │ Total: 12    │              │
│  │ Name (EN):   │  │ Name:        │  │ New: 5       │              │
│  │ [________]   │  │ [________]   │  │ Active: 4    │              │
│  │              │  │              │  │ Verified: 3  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Installation

### Prerequisites

- **Python 3.8 or higher** (Python 3.10+ recommended)
- No external dependencies required — uses only Python standard library
- Works on Windows, macOS, and Linux

### Option 1: Direct Download

```bash
# Download the script
curl -O https://raw.githubusercontent.com/your-repo/iran-osint-tracker/main/iran_osint_v3_complete.py

# Make executable (Linux/macOS)
chmod +x iran_osint_v3_complete.py
```

### Option 2: Clone Repository

```bash
git clone https://github.com/your-repo/iran-osint-tracker.git
cd iran-osint-tracker
```

### Verify Installation

```bash
python iran_osint_v3_complete.py --help
```

You should see:

```
usage: iran_osint_v3_complete.py [-h] [--dashboard] [--port PORT] 
                                  [--search NAME] [--add NAME] 
                                  [--list] [--stats]

🔍 Iran OSINT Tracker v3.0 - Complete Edition
```

---

## 🚀 Quick Start

### Launch Web Dashboard (Recommended)

```bash
python iran_osint_v3_complete.py --dashboard
```

This will:
1. Create a local SQLite database at `~/iran_osint/database.db`
2. Start a web server on `http://localhost:8000`
3. Automatically open the dashboard in your default browser

### Command Line Interface

```bash
# Add a new investigation subject
python iran_osint_v3_complete.py --add "Subject Name"

# List all subjects
python iran_osint_v3_complete.py --list

# Generate search URLs for a name
python iran_osint_v3_complete.py --search "Subject Name"

# View statistics
python iran_osint_v3_complete.py --stats

# Use custom port
python iran_osint_v3_complete.py --dashboard --port 9000
```

---

## 📖 Usage Guide

### Adding Investigation Subjects

1. Navigate to the **Investigate** tab
2. Fill in the subject information:
   - **Name (English)** — Required
   - **Name (Farsi)** — Helps with Persian-language searches
   - **Location Spotted** — Where the individual was identified
   - **Event/Context** — How they came to your attention
   - **Notes** — Any additional information
3. Click **Add Subject**

### Generating Search URLs

1. Enter the name you want to research
2. Optionally add the Persian spelling
3. Click **Generate URLs**
4. The tool generates links for:
   - LinkedIn (direct + Google indexed)
   - Sanctions databases (OFAC, OpenSanctions, UK, EU)
   - Corporate registries
   - Social media platforms
   - General web search
   - Persian-language searches (if name provided)

### Managing Subjects

In the **Subjects** tab:
- View all investigation subjects in a table
- Filter by status (New, Investigating, Verified)
- Click **View** to see details and update:
  - Status (New → Investigating → Verified)
  - Risk Level (Unknown, Low, Medium, High, Critical)
  - Notes
- Delete subjects when no longer needed

### Documenting Findings

In the **References** tab:
1. Record each discovery with:
   - Title
   - Type (LinkedIn, Corporate, Sanctions, Financial, Photo/Video, etc.)
   - Source URL and name
   - Importance level
   - Description
   - Tags for organization
2. All findings are stored locally for your records

### Following the Money

The **Follow Money** tab provides direct links to:
- Financial crime databases
- Shell company research tools
- Trade and shipping trackers
- Property registries
- A reference list of known IRGC-linked entities

### Verifying Photos and Videos

The **Verify Media** tab includes:
- Reverse image search engines (Google, Yandex, TinEye)
- Geolocation tools (Google Earth, SunCalc)
- Forensic analysis tools (FotoForensics, metadata viewers)
- Video verification resources
- A step-by-step methodology guide based on the Berkeley Protocol

### Monitoring Internet Status

The **Internet Status** tab provides:
- Real-time connectivity monitoring for Iran
- Censorship testing resources
- Links to circumvention tools
- Historical shutdown data

---

## 🔒 Security & Safety

### ⚠️ IMPORTANT: Read Before Using

Investigating regime-affiliated individuals carries real risks. The Iranian government actively monitors diaspora activities and has a documented history of transnational repression.

### Recommended Security Practices

#### Always Use a VPN
- **Mullvad** — No email required, accepts cash/crypto
- **ProtonVPN** — Swiss-based, strong privacy policy
- **IVPN** — Privacy-focused, multi-hop available

Choose servers in privacy-friendly jurisdictions: Switzerland, Iceland, Sweden, or the Netherlands.

#### Consider Using Tor
For highly sensitive research:
- Download Tor Browser from [torproject.org](https://www.torproject.org)
- Use bridges in censored regions
- Never use Tor for accounts linked to your real identity

#### Create Research Personas
- Dedicated email accounts (ProtonMail, Tutanota)
- Separate browser profiles
- Consider a dedicated device
- Never mix research and personal accounts

#### Browser Security
- Use Firefox with privacy extensions or Brave
- Essential extensions:
  - uBlock Origin (ad/tracker blocking)
  - Privacy Badger (intelligent blocking)
  - Container tabs (session isolation)

#### Data Security
- Encrypt sensitive data with VeraCrypt
- Use secure communication (Signal)
- Regular backups to encrypted storage
- Document everything with timestamps

### Emergency Contacts

If you face threats or digital attacks:

| Organization | Contact | Description |
|--------------|---------|-------------|
| **Access Now Helpline** | help@accessnow.org | 24/7 digital security assistance |
| **Committee to Protect Journalists** | info@cpj.org | Journalist safety resources |
| **EFF** | info@eff.org | Digital rights legal advocacy |
| **Citizen Lab** | citizenlab.ca | Research on targeted threats |

---

## 📚 Feature Details

### Database Storage

All data is stored locally in a SQLite database at:
```
~/iran_osint/database.db
```

Tables include:
- `subjects` — Investigation targets
- `twitter_accounts` — Monitored Twitter accounts
- `news_sources` — Monitored news websites
- `findings` — Documented discoveries
- `user_contacts` — Custom contact directory

### Search URL Categories

The search generator creates links for:

| Category | Platforms |
|----------|-----------|
| LinkedIn | Direct search, Google indexed profiles, Iran connection search |
| Sanctions | OFAC, OpenSanctions, UK Sanctions, EU Sanctions |
| Corporate | OpenCorporates, UK Companies House, ICIJ Offshore Leaks |
| Social Media | Twitter/X, Instagram (via Google), Facebook (via Google) |
| Web Search | Google, Google News, DuckDuckGo |
| Persian | Google (Farsi), LinkedIn (Farsi), Twitter (Farsi) |

### Known IRGC-Linked Entities

The tool includes a reference list of commonly sanctioned entities:

**Banks:** Bank Melli, Bank Mellat, Bank Saderat, Bank Sepah, Parsian Bank

**Airlines:** Mahan Air, Iran Air, Qeshm Air, SAHA Airlines, Pouya Air

**Conglomerates:** Khatam al-Anbiya, Bonyad Mostazafan, MAPNA Group, Iran Electronics Industries

**Shipping:** IRISL, NITC, NIOC

---

## 🔌 API Reference

The web dashboard exposes a REST API for programmatic access:

### Subjects

```bash
# Get all subjects
GET /api/subjects

# Get subjects filtered by status
GET /api/subjects?status=Investigating

# Get single subject
GET /api/subjects/{id}

# Add subject
POST /api/subjects
Content-Type: application/json
{"name_en": "Name", "name_fa": "نام", "location": "City", "notes": "..."}

# Update subject
PUT /api/subjects/{id}
Content-Type: application/json
{"status": "Verified", "risk_level": "High"}

# Delete subject
DELETE /api/subjects/{id}
```

### Search

```bash
# Generate search URLs
GET /api/search?name=Subject%20Name&name_fa=نام
```

### Statistics

```bash
# Get statistics
GET /api/stats
```

### Monitor

```bash
# Twitter accounts
GET /api/monitor/twitter
POST /api/monitor/twitter {"username": "account", "description": "..."}
DELETE /api/monitor/twitter/{id}

# News sources
GET /api/monitor/news
POST /api/monitor/news {"name": "Source", "url": "https://...", "description": "..."}
DELETE /api/monitor/news/{id}
```

### Findings

```bash
GET /api/findings
GET /api/findings?finding_type=Sanctions
POST /api/findings {"title": "...", "finding_type": "...", "source_url": "..."}
DELETE /api/findings/{id}
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Use GitHub Issues to report bugs
- Include your Python version and operating system
- Provide steps to reproduce the issue

### Suggesting Features

- Open a GitHub Issue with the "enhancement" label
- Describe the use case and proposed solution

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution

- Additional database integrations
- Improved search algorithms
- Localization (Farsi, Arabic, Turkish translations)
- Automated data collection (respecting ToS)
- Enhanced reporting/export features
- Mobile-responsive UI improvements

---

## ⚖️ Legal Disclaimer

### Terms of Use

This tool is provided for **legitimate research purposes only**, including:
- Journalism and investigative reporting
- Human rights documentation
- Academic research
- Legal investigations
- Policy analysis

### Prohibited Uses

This tool must **NOT** be used for:
- Harassment or stalking of individuals
- Doxxing or publishing private information maliciously
- Violating platform Terms of Service
- Any illegal activities in your jurisdiction
- Targeting individuals based on protected characteristics

### Compliance

- All search methods use publicly accessible information
- The tool generates links to legitimate, legal databases
- Users are responsible for compliance with local laws
- No automated scraping or ToS violations

### No Warranty

This software is provided "as is" without warranty of any kind. The authors are not responsible for how the tool is used or any consequences arising from its use.

---

## 📚 Resources

### OSINT Methodology

- [Berkeley Protocol on Digital Open Source Investigations](https://www.ohchr.org/en/publications/policy-and-methodological-publications/berkeley-protocol-digital-open-source)
- [Bellingcat's Online Investigation Toolkit](https://docs.google.com/spreadsheets/d/18rtqh8EG2q1xBo2cLNyhIDuK9jrPGwYr9DI2UncoqJQ/)
- [OSINT Framework](https://osintframework.com/)

### Iran-Specific Resources

- [Iran Human Rights (IHR)](https://iranhr.net/en/)
- [Center for Human Rights in Iran](https://iranhumanrights.org/)
- [IranWatch Entity Database](https://www.iranwatch.org/iranian-entities)
- [United Against Nuclear Iran (UANI)](https://www.unitedagainstnucleariran.com/)

### Digital Security

- [EFF Surveillance Self-Defense](https://ssd.eff.org/)
- [Access Now Digital Security Helpline](https://www.accessnow.org/help/)
- [CPJ Digital Safety Kit](https://cpj.org/2019/07/digital-safety-kit-journalists/)
- [Security in a Box](https://securityinabox.org/)

### Sanctions Information

- [OFAC Sanctions Programs](https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/iran-sanctions)
- [OpenSanctions](https://www.opensanctions.org/)
- [EU Sanctions Map](https://www.sanctionsmap.eu/)

---

## 🙏 Acknowledgments

This tool was built with gratitude for the brave work of:

- **Iranian human rights defenders** documenting abuses at great personal risk
- **Investigative journalists** exposing regime networks globally
- **The Bellingcat community** for pioneering open source investigation methods
- **Digital security experts** protecting researchers and activists


---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact & Support

- **Issues:** GitHub Issues
- **Security vulnerabilities:** Please report privately
- **General inquiries:** Open a GitHub Discussion

---



<p align="center">
  Built with ❤️ for human rights and accountability
</p>
