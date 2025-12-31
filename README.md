# RedAmon

**Unmask the hidden before the world does.**

An automated OSINT reconnaissance and vulnerability scanning framework combining multiple security tools for comprehensive target assessment.

---

## 🎯 Quick Start

```bash
# 1. Install requirements
pip install -r requirements.txt
sudo apt install tor proxychains4  # Optional: for anonymous scanning

# 2. Configure target in params.py
TARGET_DOMAIN = "example.com"

# 3. Run the scan
python recon/main.py
```

---

## 🔄 Scanning Pipeline Overview

RedAmon executes scans in a modular pipeline. Each module adds data to a single JSON output file.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RedAmon Scanning Pipeline                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │ initial_recon│───►│     nmap     │───►│    nuclei    │───►│  github   │  │
│  │              │    │              │    │              │    │           │  │
│  │  • WHOIS     │    │  • Ports     │    │  • Web vulns │    │  • Secrets│  │
│  │  • DNS       │    │  • Services  │    │  • CVEs      │    │  • Leaks  │  │
│  │  • Subdomains│    │  • OS detect │    │  • XSS/SQLi  │    │  • Keys   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘  │
│         │                   │                   │                   │       │
│         └───────────────────┴───────────────────┴───────────────────┘       │
│                                     │                                       │
│                                     ▼                                       │
│                    📄 recon/output/recon_<domain>.json                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Scan Modules Explained

### Configure Which Modules to Run

Edit `params.py`:

```python
# Run all modules (recommended for full assessment)
SCAN_MODULES = ["initial_recon", "nmap", "nuclei", "github"]

# Quick recon only (no vulnerability scanning)
SCAN_MODULES = ["initial_recon"]

# Port scan + web vulnerabilities (skip domain discovery)
SCAN_MODULES = ["nmap", "nuclei"]

# Update existing scan with just Nuclei
SCAN_MODULES = ["nuclei"]
```

---

### Module 1: `initial_recon` - Domain Intelligence

**Purpose:** Gather information about the target domain and discover attack surface.

| What It Does | Output |
|--------------|--------|
| **WHOIS lookup** | Registrar, creation date, owner info |
| **Subdomain discovery** | Finds subdomains via passive sources |
| **DNS enumeration** | A, AAAA, MX, NS, TXT, CNAME records |
| **IP resolution** | Maps all discovered hostnames to IPs |

**Key Parameters:**
```python
TARGET_DOMAIN = "example.com"           # Your target
USE_TOR_FOR_RECON = False               # Use Tor for anonymity
USE_BRUTEFORCE_FOR_SUBDOMAINS = False   # Brute force subdomain discovery
```

---

### Module 2: `nmap` - Network & Infrastructure Scanning

**Purpose:** Discover open ports, running services, OS fingerprinting, and network-level vulnerabilities.

| What It Finds | Examples |
|---------------|----------|
| **Open ports** | 22/SSH, 80/HTTP, 443/HTTPS, 3306/MySQL |
| **Service versions** | Apache 2.4.41, OpenSSH 8.2 |
| **OS detection** | Ubuntu 20.04, Windows Server 2019 |
| **Network vulns** | EternalBlue (MS17-010), Heartbleed, SSL issues |
| **CVEs** | Matches service versions against CVE database |

**Execution:** Runs via Docker (`instrumentisto/nmap:latest`) - no local installation needed.

**Key Parameters:**
```python
NMAP_USE_DOCKER = True                  # Use Docker (recommended)
NMAP_SCAN_TYPE = "thorough"             # fast | thorough | stealth
NMAP_TOP_PORTS = 1000                   # Number of ports to scan
NMAP_VULN_SCAN = True                   # Enable vulnerability scripts
NMAP_VULN_INTENSITY = "standard"        # light | standard | aggressive
```

📖 **Detailed documentation:** [readmes/README.NMAP.md](readmes/README.NMAP.md)

---

### Module 3: `nuclei` - Web Application Vulnerability Scanning

**Purpose:** Deep web application security testing with thousands of vulnerability templates.

| What It Finds | Examples |
|---------------|----------|
| **Web CVEs** | Log4Shell, Spring4Shell, Drupalgeddon |
| **Injection flaws** | SQL injection, XSS, Command injection |
| **Misconfigurations** | Exposed admin panels, debug endpoints |
| **Information leaks** | .git exposure, backup files, API keys |
| **Default credentials** | Admin:admin, test accounts |
| **Technology detection** | WordPress, Nginx, PHP version |

**Execution:** Runs via Docker (`projectdiscovery/nuclei:latest`) with Katana crawler for DAST.

**Key Parameters:**
```python
NUCLEI_SEVERITY = ["critical", "high", "medium", "low"]  # What to report
NUCLEI_DAST_MODE = True                  # Active fuzzing (XSS, SQLi testing)
NUCLEI_RATE_LIMIT = 100                  # Requests per second
NUCLEI_AUTO_UPDATE_TEMPLATES = True      # Update 9000+ templates
```

📖 **Detailed documentation:** [readmes/README.NUCLEI.md](readmes/README.NUCLEI.md)

---

### Module 4: `github` - Secret Hunting

**Purpose:** Find leaked credentials, API keys, and secrets in GitHub repositories.

| What It Finds | Examples |
|---------------|----------|
| **API keys** | AWS, Google Cloud, Stripe, Twilio |
| **Credentials** | Passwords, tokens, private keys |
| **Database strings** | Connection strings with passwords |
| **Private keys** | SSH keys, SSL certificates |

**Key Parameters:**
```python
GITHUB_ACCESS_TOKEN = "ghp_xxxxx"        # Required - set in .env file
GITHUB_TARGET_ORG = "company-name"       # Organization or username
GITHUB_SCAN_COMMITS = True               # Search git history
GITHUB_MAX_COMMITS = 100                 # Commits per repo
```

---

## 🆚 Deep Comparison: Nmap vs Nuclei vs GVM

Understanding the differences between these scanners is crucial for effective vulnerability assessment.

### Overview Comparison

| Aspect | Nmap | Nuclei | GVM/OpenVAS |
|--------|------|--------|-------------|
| **Primary Focus** | Network infrastructure | Web applications | Full vulnerability management |
| **OSI Layer** | Layer 3-4 (Network/Transport) | Layer 7 (Application) | Layer 3-7 (Full stack) |
| **Speed** | ⚡ Fast (minutes) | 🔄 Medium (minutes-hours) | 🐢 Slow (hours-days) |
| **CVE Database** | ~600 NSE vuln scripts | ~9,000+ templates | ~80,000+ NVTs |
| **Setup Complexity** | 🟢 Easy (single binary) | 🟢 Easy (single binary) | 🔴 Complex (Docker stack) |
| **Resource Usage** | Low (~100MB RAM) | Medium (~500MB RAM) | High (~8GB+ RAM) |

### Vulnerability Detection Capabilities

| Vulnerability Type | Nmap | Nuclei | GVM |
|--------------------|------|--------|-----|
| **Open Ports** | ✅ Primary function | ❌ Relies on input | ✅ Yes |
| **Service Versions** | ✅ Excellent (-sV) | ⚠️ Limited | ✅ Yes |
| **OS Fingerprinting** | ✅ Excellent (-O) | ❌ No | ✅ Yes |
| **SSL/TLS Issues** | ✅ Good (NSE scripts) | ✅ Good | ✅ Excellent |
| **SQL Injection** | ⚠️ Basic detection | ✅ Excellent (DAST) | ✅ Good |
| **XSS (Cross-Site Scripting)** | ⚠️ Basic detection | ✅ Excellent (DAST) | ✅ Good |
| **Command Injection** | ⚠️ Limited | ✅ Excellent (DAST) | ✅ Good |
| **CSRF** | ❌ No | ✅ Yes | ⚠️ Limited |
| **File Inclusion (LFI/RFI)** | ⚠️ Limited | ✅ Excellent | ✅ Good |
| **Directory Traversal** | ⚠️ Limited | ✅ Excellent | ✅ Good |
| **Information Disclosure** | ✅ Good | ✅ Excellent | ✅ Excellent |
| **Default Credentials** | ✅ Good (brute scripts) | ✅ Good | ✅ Excellent |
| **SMB Vulnerabilities** | ✅ Excellent (EternalBlue, etc.) | ⚠️ Limited | ✅ Excellent |
| **SSH Vulnerabilities** | ✅ Good | ⚠️ Limited | ✅ Excellent |
| **Database Vulns** | ✅ Good (MySQL, MSSQL) | ⚠️ Limited | ✅ Excellent |
| **Web Server Misconfig** | ✅ Good | ✅ Excellent | ✅ Excellent |
| **CMS Vulnerabilities** | ⚠️ Limited | ✅ Excellent (WP, Joomla, Drupal) | ✅ Good |
| **API Security** | ❌ No | ✅ Good | ⚠️ Limited |
| **Cloud Misconfigurations** | ❌ No | ✅ Good (AWS, Azure, GCP) | ⚠️ Limited |

**Legend:** ✅ Excellent/Primary | ⚠️ Limited/Basic | ❌ Not supported

### Detection Methods

| Method | Nmap | Nuclei | GVM |
|--------|------|--------|-----|
| **Banner Grabbing** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Version Fingerprinting** | ✅ Excellent | ⚠️ Basic | ✅ Excellent |
| **Active Fuzzing (DAST)** | ⚠️ Limited | ✅ Excellent | ✅ Good |
| **Passive Detection** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Authenticated Scanning** | ⚠️ Limited (SSH, SMB) | ⚠️ HTTP headers only | ✅ Excellent |
| **Template/Signature Based** | ✅ NSE scripts | ✅ YAML templates | ✅ NVTs |
| **Exploit Verification** | ⚠️ Some scripts | ✅ Yes (safe) | ✅ Yes |
| **Out-of-Band (OOB)** | ❌ No | ✅ Interactsh | ⚠️ Limited |

### CVE Coverage by Category

| CVE Category | Nmap | Nuclei | GVM |
|--------------|------|--------|-----|
| **Network Services** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Web Applications** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Operating Systems** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **CMS/Frameworks** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **IoT/Embedded** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cloud Services** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Databases** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### Scan Performance

| Metric | Nmap | Nuclei | GVM |
|--------|------|--------|-----|
| **100 ports scan** | ~30 seconds | N/A | ~5 minutes |
| **1000 ports + services** | ~5 minutes | N/A | ~30 minutes |
| **Full web app scan** | ~10 minutes (scripts) | ~15-30 minutes | ~2-4 hours |
| **Full vuln assessment** | ~30 minutes | ~1-2 hours | ~4-8 hours |
| **Parallel targets** | ✅ Excellent | ✅ Good | ⚠️ Limited |
| **Rate limiting** | ✅ Configurable (-T0 to -T5) | ✅ Fine-grained | ⚠️ Basic |

### Output & Reporting

| Feature | Nmap | Nuclei | GVM |
|---------|------|--------|-----|
| **JSON Output** | ✅ Yes (-oJ) | ✅ Yes (-json) | ✅ Yes (API) |
| **XML Output** | ✅ Yes (-oX) | ❌ No | ✅ Yes |
| **HTML Reports** | ⚠️ Via XSLT | ⚠️ Via tools | ✅ Built-in |
| **PDF Reports** | ❌ No | ❌ No | ✅ Built-in |
| **CVSS Scores** | ✅ Via vulners | ✅ Yes | ✅ Yes |
| **Remediation Guidance** | ⚠️ Limited | ✅ Good | ✅ Excellent |
| **Compliance Reports** | ❌ No | ❌ No | ✅ PCI-DSS, HIPAA |
| **Trend Analysis** | ❌ No | ❌ No | ✅ Yes |

### Practical Use Cases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHICH SCANNER FOR WHICH TASK?                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔍 "What ports are open?"                    ──► NMAP                     │
│  🔍 "What services are running?"              ──► NMAP                     │
│  🔍 "What OS is this server?"                 ──► NMAP                     │
│                                                                             │
│  🌐 "Is this website vulnerable to XSS?"      ──► NUCLEI (DAST mode)       │
│  🌐 "Does this app have SQL injection?"       ──► NUCLEI (DAST mode)       │
│  🌐 "Is WordPress outdated?"                  ──► NUCLEI                   │
│  🌐 "Are there exposed admin panels?"         ──► NUCLEI                   │
│                                                                             │
│  🏢 "Full CVE audit for compliance"           ──► GVM                      │
│  🏢 "Enterprise vulnerability management"     ──► GVM                      │
│  🏢 "Authenticated internal scan"             ──► GVM                      │
│  🏢 "PCI-DSS compliance report"               ──► GVM                      │
│                                                                             │
│  ⚡ "Quick external assessment"               ──► NMAP + NUCLEI            │
│  ⚡ "Bug bounty hunting"                      ──► NUCLEI (primary)         │
│  ⚡ "Pentest infrastructure"                  ──► NMAP (primary) + GVM     │
│  ⚡ "Pentest web application"                 ──► NUCLEI (primary)         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Recommended Scan Strategy

For **comprehensive assessment**, use all three in this order:

```
1. NMAP (Infrastructure Discovery)
   └─► Discover ports, services, OS
   └─► Find network-level vulns (SMB, SSL, SSH)
   └─► Output: IP list, service map, initial CVEs
   
2. NUCLEI (Web Application Testing)  
   └─► Deep web vulnerability scanning
   └─► DAST fuzzing for XSS, SQLi, etc.
   └─► Technology-specific CVE checks
   └─► Output: Web vulns, misconfigs, exposures

3. GVM (Enterprise Validation) - Optional
   └─► Comprehensive CVE validation
   └─► Authenticated scanning
   └─► Compliance reporting
   └─► Output: Full audit report
```

### Quick Decision Matrix

| Your Situation | Recommended Scanner |
|----------------|---------------------|
| Bug bounty on web app | **Nuclei** (DAST mode) |
| Quick external recon | **Nmap** → **Nuclei** |
| Internal network audit | **Nmap** → **GVM** |
| Web app pentest | **Nuclei** (primary) |
| Infrastructure pentest | **Nmap** (primary) |
| Compliance audit (PCI/HIPAA) | **GVM** (required) |
| CTF/Learning | **Nmap** + **Nuclei** |
| Red team engagement | All three |

### Limitations Summary

| Scanner | Main Limitations |
|---------|------------------|
| **Nmap** | Limited web app testing, no DAST fuzzing, basic XSS/SQLi detection |
| **Nuclei** | No port scanning, limited auth scanning, requires URLs as input |
| **GVM** | Very slow, high resource usage, complex setup, overkill for quick scans |

---

## ⚙️ Key Configuration Parameters

### `params.py` - Essential Settings

```python
# ═══════════════════════════════════════════════════════════════════
# TARGET & MODULES
# ═══════════════════════════════════════════════════════════════════
TARGET_DOMAIN = "example.com"
SCAN_MODULES = ["initial_recon", "nmap", "nuclei"]

# ═══════════════════════════════════════════════════════════════════
# ANONYMITY (Optional)
# ═══════════════════════════════════════════════════════════════════
USE_TOR_FOR_RECON = False       # Route traffic through Tor

# ═══════════════════════════════════════════════════════════════════
# NMAP - Network Scanning
# ═══════════════════════════════════════════════════════════════════
NMAP_USE_DOCKER = True          # Use Docker container
NMAP_SCAN_TYPE = "thorough"     # fast | thorough | stealth
NMAP_VULN_SCAN = True           # Enable vulnerability scripts
NMAP_VULN_INTENSITY = "standard"# light | standard | aggressive

# ═══════════════════════════════════════════════════════════════════
# NUCLEI - Web Application Scanning
# ═══════════════════════════════════════════════════════════════════
NUCLEI_DAST_MODE = True         # Active fuzzing for XSS, SQLi
NUCLEI_SEVERITY = ["critical", "high", "medium", "low"]
NUCLEI_RATE_LIMIT = 100         # Requests per second
NUCLEI_AUTO_UPDATE_TEMPLATES = True  # Get latest templates

# ═══════════════════════════════════════════════════════════════════
# GITHUB - Secret Hunting
# ═══════════════════════════════════════════════════════════════════
GITHUB_ACCESS_TOKEN = ""        # Set in .env file!
GITHUB_TARGET_ORG = "company"   # Organization/username to scan
```

---

## 🔧 Prerequisites

### Required
- **Python 3.8+**
- **Docker** (for Nmap, Nuclei, and optionally GVM)

### Optional
```bash
# For anonymous scanning
sudo apt install tor proxychains4
sudo systemctl start tor
```

### Docker Images (auto-pulled on first run)
```bash
# Nmap scanner
docker pull instrumentisto/nmap:latest

# Nuclei scanner + Katana crawler
docker pull projectdiscovery/nuclei:latest
docker pull projectdiscovery/katana:latest
```

---

## 📁 Project Structure

```
RedAmon/
├── params.py              # 🎛️  Global configuration (edit this!)
├── requirements.txt       # Python dependencies
├── .env                   # Secrets (GITHUB_TOKEN, GVM_PASSWORD)
│
├── recon/                 # Reconnaissance & scanning modules
│   ├── main.py            # 🚀 Entry point - run this!
│   ├── domain_recon.py    # Subdomain discovery
│   ├── whois_recon.py     # WHOIS lookup
│   ├── nmap_scan.py       # Port & vulnerability scanning
│   ├── nuclei_scan.py     # Web application scanning
│   ├── github_hunter.py   # GitHub secret hunting
│   └── output/            # 📄 Scan results (JSON)
│
├── gvm_scan/              # GVM/OpenVAS integration
│   ├── main.py            # GVM scan entry point
│   └── output/            # GVM results
│
├── readmes/               # 📖 Detailed documentation
│   ├── README.NMAP.md     # Nmap configuration guide
│   ├── README.NUCLEI.md   # Nuclei configuration guide
│   └── README.GVM.md      # GVM/OpenVAS setup guide
│
└── docker-compose.yml     # GVM container orchestration
```

---

## 📊 Output Format

All modules write to a single JSON file: `recon/output/recon_<domain>.json`

```json
{
  "metadata": {
    "target": "example.com",
    "scan_timestamp": "2024-01-15T10:30:00"
  },
  "whois": {
    "registrar": "GoDaddy",
    "creation_date": "2010-01-01"
  },
  "subdomains": ["www.example.com", "api.example.com", "admin.example.com"],
  "dns": {
    "A": ["93.184.216.34"],
    "MX": ["mail.example.com"]
  },
  "nmap": {
    "scan_metadata": { "execution_mode": "docker" },
    "by_target": {
      "93.184.216.34": {
        "ports": [
          {"port": 443, "service": "https", "version": "nginx 1.18"}
        ],
        "vulnerabilities": { "total": 3, "critical": 0, "high": 1 }
      }
    }
  },
  "nuclei": {
    "scan_metadata": { "dast_mode": true },
    "discovered_urls": {
      "dast_urls_with_params": ["https://example.com/search?q=test"]
    },
    "vulnerabilities": {
      "critical": [],
      "high": [{"template": "cve-2021-44228", "name": "Log4Shell"}]
    }
  }
}
```

---

## 🛡️ GVM/OpenVAS - Enterprise Vulnerability Scanning

**GVM (Greenbone Vulnerability Management)** is an open-source vulnerability scanner for comprehensive enterprise security assessment.

### What GVM Does

| Capability | Description |
|------------|-------------|
| **80,000+ vulnerability tests** | Comprehensive CVE database coverage |
| **Misconfiguration detection** | Finds insecure settings and hardening issues |
| **Compliance checking** | PCI-DSS, HIPAA, CIS benchmarks |
| **Credential scanning** | Authenticated scans for deeper analysis |
| **Detailed reporting** | Severity ratings (Critical/High/Medium/Low) |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                            │
│                                                              │
│  Python Scanner ──► GVMD (API) ──► OpenVAS-D ──► Redis      │
│                        │                                     │
│                   PostgreSQL                                 │
│                                                              │
│  + Data containers: NVTs, SCAP, CERT (vulnerability DB)     │
└─────────────────────────────────────────────────────────────┘
```

| Component | Purpose |
|-----------|---------|
| **GVMD** | Management daemon - exposes API for Python |
| **OpenVAS-D** | Scanner daemon - executes vulnerability tests |
| **PostgreSQL** | Stores configs, results, scan history |
| **Redis** | Inter-process communication |
| **Data containers** | Download 80K+ vulnerability tests on first run |

### Quick Start

#### 1. Start GVM containers (first time takes 10-15 min)

```bash
# Pull all required images (first time only)
docker pull registry.community.greenbone.net/community/redis-server
docker pull registry.community.greenbone.net/community/pg-gvm:stable
docker pull registry.community.greenbone.net/community/gvmd:stable
docker pull registry.community.greenbone.net/community/ospd-openvas:stable
docker pull registry.community.greenbone.net/community/vulnerability-tests
docker pull registry.community.greenbone.net/community/notus-data
docker pull registry.community.greenbone.net/community/scap-data
docker pull registry.community.greenbone.net/community/cert-bund-data
docker pull registry.community.greenbone.net/community/dfn-cert-data
docker pull registry.community.greenbone.net/community/data-objects
docker pull registry.community.greenbone.net/community/report-formats
docker pull registry.community.greenbone.net/community/gpg-data

# Start containers
docker compose up -d
```

#### 2. Watch logs until ready

```bash
docker compose logs -f gvmd
# Wait for: "Starting GVMd" or similar ready message

# More detailed logs
docker compose logs -f gvmd ospd-openvas python-scanner
```

#### 3. Create admin user (first time only)

```bash
docker compose exec -u gvmd gvmd gvmd --create-user=admin --password=admin
```

#### 4. Run vulnerability scan

```bash
# Make sure recon was run first for your target domain
docker compose --profile scanner up python-scanner

# If scanner code changed, rebuild first
docker compose build python-scanner && docker compose --profile scanner up python-scanner
```

**Output:** `gvm_scan/output/vuln_<domain>.json`

#### 5. Update GVM vulnerability feeds (recommended weekly)

GVM uses **data containers** that download vulnerability feeds on first startup. To get the latest CVEs and vulnerability tests, you need to re-pull and re-run these containers:

```bash
# Pull latest feed images (downloads new vulnerability data)
docker compose pull vulnerability-tests notus-data scap-data cert-bund-data dfn-cert-data data-objects report-formats

# Re-run data containers to update volumes
docker compose up vulnerability-tests notus-data scap-data cert-bund-data dfn-cert-data data-objects report-formats

# Restart gvmd to reload the updated feeds
docker compose restart gvmd

# Wait for gvmd to sync (check logs)
docker compose logs -f gvmd
# Look for: "Updating VTs in database ... done"
```

**What gets updated:**

| Feed | Contents | Why Update |
|------|----------|------------|
| `vulnerability-tests` | 170,000+ NVT scripts (.nasl) | New vulnerability checks |
| `scap-data` | CVE definitions, CVSS scores from NIST | New CVE entries |
| `cert-bund-data` | German CERT security advisories | New security bulletins |
| `dfn-cert-data` | DFN-CERT advisories | Research network alerts |
| `notus-data` | Package vulnerability data | OS package CVE mappings |
| `data-objects` | Scan configs, policies | Updated scan profiles |
| `report-formats` | Report templates | Output format updates |

**Update frequency:** Greenbone updates feeds **daily**. Recommended to update weekly or before important scans.

### Docker Commands Reference

```bash
# Start GVM
docker compose up -d

# Stop GVM  
docker compose down

# View logs
docker compose logs -f gvmd

# Check status
docker compose ps

# Run Python scanner
docker compose --profile scanner up python-scanner

# Reset everything (delete all data)
docker compose down -v
```

### GVM Configuration (`params.py`)

```python
# Use targets from recon scan
USE_RECON_FOR_TARGET = True

# Or specify targets manually
GVM_IP_LIST = ["192.168.1.1", "192.168.1.2"]
GVM_HOSTNAME_LIST = ["example.com"]

# Scan configuration preset
GVM_SCAN_CONFIG = "Full and fast"  # Options:
# - "Full and fast"           - Comprehensive, good performance (recommended)
# - "Full and fast ultimate"  - Most thorough, slower
# - "Discovery"               - Network discovery only

# Scan targets strategy
GVM_SCAN_TARGETS = "both"  # both | ips_only | hostnames_only

# Task timeout (GVM scans can take hours)
GVM_TASK_TIMEOUT = 14400  # 4 hours
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Failed to connect to GVM" | Wait for gvmd to finish starting (check logs) |
| "OpenVAS scanner not found" | Data sync still in progress, wait 10-15 min |
| Scan takes too long | Reduce targets or use "Discovery" scan config |
| Out of disk space | GVM needs ~20GB for vulnerability data |

📖 **Detailed documentation:** [readmes/README.GVM.md](readmes/README.GVM.md)

---

## 🧪 Test Targets

Safe, **legal** targets specifically designed for security testing. No authorization needed.

### Acunetix Vulnweb (Recommended)

Acunetix provides intentionally vulnerable web applications at **vulnweb.com**:

| Target | Technology | Vulnerabilities |
|--------|------------|-----------------|
| `testphp.vulnweb.com` | PHP + MySQL | SQL Injection, XSS, File Upload, LFI, CSRF |
| `testhtml5.vulnweb.com` | HTML5 + JavaScript | DOM XSS, Client-side attacks, HTML5 security |
| `testasp.vulnweb.com` | ASP.NET + SQL Server | SQL Injection, XSS, Authentication flaws |

**🎯 Best for testing:** These sites have real vulnerabilities that Nuclei DAST mode and Nmap vuln scripts will detect.

```python
# Example: Test with vulnweb
TARGET_DOMAIN = "testphp.vulnweb.com"
SCAN_MODULES = ["initial_recon", "nmap", "nuclei"]
NUCLEI_DAST_MODE = True  # Will find XSS, SQLi
```

### Other Legal Test Targets

| Target | Description |
|--------|-------------|
| `scanme.nmap.org` | Nmap's official test target (port scanning only) |
| `demo.testfire.net` | IBM AppScan demo banking app (Altoro Mutual) |
| `juice-shop.herokuapp.com` | OWASP Juice Shop - modern vulnerable app |
| `hack-yourself-first.com` | Troy Hunt's vulnerable ASP.NET site |

### OWASP WebGoat (Local)

For offline testing, run OWASP WebGoat locally:

```bash
docker run -p 8080:8080 webgoat/webgoat
# Then scan: TARGET_DOMAIN = "localhost:8080"
```

---

## ⚠️ Legal Disclaimer

**Only scan systems you own or have explicit written permission to test.**

Unauthorized scanning is illegal in most jurisdictions. RedAmon is intended for:
- Penetration testers with proper authorization
- Security researchers on approved targets
- Bug bounty hunters within program scope
- System administrators testing their own infrastructure

---

## 📖 Detailed Documentation

| Module | Documentation |
|--------|---------------|
| Nmap | [readmes/README.NMAP.md](readmes/README.NMAP.md) |
| Nuclei | [readmes/README.NUCLEI.md](readmes/README.NUCLEI.md) |
| GVM/OpenVAS | [readmes/README.GVM.md](readmes/README.GVM.md) |
