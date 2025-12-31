# RedAmon - Nmap Port & Vulnerability Scanner

## Complete Technical Documentation

> **Module:** `recon/nmap_scan.py`  
> **Purpose:** Comprehensive port scanning, service detection, and vulnerability assessment using Nmap NSE scripts  
> **Author:** RedAmon Security Suite

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Configuration Parameters](#configuration-parameters)
4. [Architecture & Flow](#architecture--flow)
5. [Function Reference](#function-reference)
6. [Nmap Arguments Explained](#nmap-arguments-explained)
7. [NSE Vulnerability Scripts](#nse-vulnerability-scripts)
8. [Vulnerability Detection Logic](#vulnerability-detection-logic)
9. [Output Data Structure](#output-data-structure)
10. [Tor/Proxychains Integration](#torproxychains-integration)
11. [Usage Examples](#usage-examples)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The `nmap_scan.py` module is a comprehensive wrapper around the Nmap security scanner that integrates with RedAmon's reconnaissance pipeline. It extracts all IPs and hostnames discovered during domain reconnaissance and performs:

- **Port Scanning**: TCP and UDP port discovery
- **Service Detection**: Identification of running services and versions
- **OS Fingerprinting**: Operating system detection
- **Vulnerability Scanning**: CVE detection using 100+ NSE scripts
- **Banner Grabbing**: Service banner extraction
- **Anonymous Scanning**: Optional Tor/proxychains integration

### How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Recon Data     │────▶│   nmap_scan.py   │────▶│  Enriched JSON  │
│  (domain, IPs,  │     │                  │     │  with ports,    │
│   subdomains)   │     │  1. Extract IPs  │     │  services,      │
└─────────────────┘     │  2. Build args   │     │  vulnerabilities│
                        │  3. Run scans    │     └─────────────────┘
                        │  4. Parse results│
                        │  5. Classify vulns│
                        └──────────────────┘
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Target Scanning** | Scans both IPs and hostnames from recon data |
| **Vulnerability Detection** | 150+ NSE scripts for CVE detection |
| **CVE Extraction** | Automatic CVE ID and CVSS score extraction |
| **Incremental Saving** | Results saved after each target scan |
| **Tor Integration** | Anonymous scanning via proxychains |
| **Smart Script Selection** | Filters scripts based on system availability |
| **Severity Classification** | Critical/High/Medium/Low/Info categorization |

---

## Configuration Parameters

All parameters are defined in `params.py`. Here's a detailed breakdown:

### Basic Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `NMAP_ENABLED` | `bool` | `True` | Master switch to enable/disable nmap scanning |
| `NMAP_TIMEOUT` | `int` | `300` | Maximum time (seconds) to wait for host scan. `0` = no timeout |
| `NMAP_SCAN_HOSTNAMES` | `bool` | `True` | Scan hostnames in addition to IPs (important for virtual hosts) |

### Scan Type Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `NMAP_SCAN_TYPE` | `str` | `"thorough"` | Scan timing and aggressiveness profile |

**Scan Type Values:**

| Value | Nmap Args | Description |
|-------|-----------|-------------|
| `"fast"` | `-T4` | Aggressive timing, quick results, may miss slow services |
| `"thorough"` | `-T3 -A` | Comprehensive scan with OS/version detection (recommended) |
| `"stealth"` | `-T2 -sS` | Slow, stealthy SYN scan, evades some IDS |
| `"default"` | `-T3` | Balanced timing, standard scan |

### Port Selection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `NMAP_TOP_PORTS` | `int` | `1000` | Scan top N most common ports (nmap's ranked list) |
| `NMAP_CUSTOM_PORTS` | `str` | `""` | Custom port specification (overrides TOP_PORTS) |
| `NMAP_SCAN_UDP` | `bool` | `True` | Enable UDP port scanning (slower but thorough) |

**Port Specification Examples:**
```python
NMAP_CUSTOM_PORTS = "22,80,443"           # Specific ports
NMAP_CUSTOM_PORTS = "1-1000"              # Port range
NMAP_CUSTOM_PORTS = "22,80,443,8000-8100" # Mixed
NMAP_CUSTOM_PORTS = ""                    # Use TOP_PORTS instead
```

### Detection Features

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `NMAP_SERVICE_DETECTION` | `bool` | `True` | Enable service/version detection (`-sV`) |
| `NMAP_OS_DETECTION` | `bool` | `True` | Enable OS fingerprinting (`-O`) - requires root |
| `NMAP_SCRIPT_SCAN` | `bool` | `True` | Enable safe default scripts (banner, http-title, ssl-cert) |

### Vulnerability Scanning

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `NMAP_VULN_SCAN` | `bool` | `True` | Enable NSE vulnerability scanning |
| `NMAP_VULN_INTENSITY` | `str` | `"standard"` | Vulnerability scan depth level |
| `NMAP_VULN_CATEGORIES` | `list` | `[]` | Specific categories to scan (empty = auto) |
| `NMAP_CUSTOM_SCRIPTS` | `list` | `[]` | Additional custom NSE scripts |
| `NMAP_BRUTE_SCAN` | `bool` | `True` | Enable brute force scripts (⚠️ may lock accounts) |
| `NMAP_SCRIPT_TIMEOUT` | `int` | `300` | Max time per script execution (seconds) |

**Vulnerability Intensity Levels:**

| Level | Scripts | Use Case |
|-------|---------|----------|
| `"light"` | ~25 scripts | Quick, non-intrusive checks. SSL/TLS, headers, banners |
| `"standard"` | ~80 scripts | Common CVEs, safe exploits. **Recommended for most scans** |
| `"aggressive"` | ~110 scripts | All vuln scripts including intrusive ones. **May crash services!** |

**Vulnerability Categories:**

| Category | Scripts Included |
|----------|-----------------|
| `"ssl"` | SSL/TLS vulnerabilities (heartbleed, poodle, weak ciphers) |
| `"http"` | Web vulnerabilities (SQLi, XSS, shellshock, misconfigs) |
| `"smb"` | SMB/Windows vulnerabilities (EternalBlue, MS08-067) |
| `"ftp"` | FTP vulnerabilities (anonymous access, backdoors) |
| `"ssh"` | SSH vulnerabilities (weak algos, auth methods) |
| `"dns"` | DNS vulnerabilities (zone transfer, cache poisoning) |
| `"smtp"` | SMTP vulnerabilities (open relay, CVEs) |
| `"auth"` | Authentication issues (default creds, anonymous access) |
| `"dos"` | DoS vulnerabilities (⚠️ use with caution!) |

### Anonymous Scanning

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `USE_TOR_FOR_RECON` | `bool` | `False` | Route scans through Tor network |

---

## Architecture & Flow

### Execution Flow

```
1. INITIALIZATION
   └── Load configuration from params.py
   └── Check Tor/proxychains availability
   └── Initialize nmap.PortScanner instance

2. TARGET EXTRACTION
   └── Parse recon_data JSON
   └── Extract unique IPs from DNS records
   └── Extract unique hostnames (domain + subdomains)
   └── Build IP-to-hostname mapping

3. ARGUMENT BUILDING
   └── Select scripts based on VULN_INTENSITY
   └── Filter unavailable scripts
   └── Build nmap argument string
   └── Adjust for Tor compatibility

4. PHASE 1: IP SCANNING
   └── For each IP:
       └── Run nmap scan (direct or via proxychains)
       └── Parse XML results
       └── Classify vulnerabilities
       └── Extract CVEs
       └── Save incremental results

5. PHASE 2: HOSTNAME SCANNING (if enabled)
   └── Same process for each hostname
   └── Important for virtual hosts

6. PHASE 3: UDP SCANNING (if enabled)
   └── Separate UDP scan pass
   └── Top 100 UDP ports

7. RESULT COMPILATION
   └── Aggregate all findings
   └── Sort CVEs by CVSS score
   └── Generate summary statistics
   └── Save final enriched JSON
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              params.py                                    │
│  NMAP_ENABLED, NMAP_SCAN_TYPE, NMAP_VULN_SCAN, NMAP_VULN_INTENSITY...   │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           nmap_scan.py                                    │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │ extract_targets │───▶│ build_nmap_args │───▶│ get_vuln_scripts    │  │
│  │ _from_recon()   │    │ ()              │    │ ()                  │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
│           │                     │                        │               │
│           ▼                     ▼                        ▼               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      scan_target()                               │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │    │
│  │  │ nmap.scan()   │─▶│ parse_nmap    │─▶│ classify          │   │    │
│  │  │ or proxychains│  │ _result()     │  │ _vulnerability()  │   │    │
│  │  └───────────────┘  └───────────────┘  └───────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                       │
│                                  ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    run_nmap_scan()                               │    │
│  │   Orchestrates phases, aggregates results, saves JSON           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   recon_<domain>.json    │
                    │   with "nmap" section    │
                    └──────────────────────────┘
```

---

## Function Reference

### `get_available_nmap_scripts() -> Set[str]`

**Purpose:** Discovers NSE scripts installed on the system.

**Mechanism:**
1. Checks `/usr/share/nmap/scripts` (standard location)
2. Falls back to `/usr/local/share/nmap/scripts`
3. Lists all `*.nse` files
4. Returns set of script names (without `.nse` extension)

**Returns:** Set of available script names

**Why needed:** Prevents errors from requesting non-existent scripts on different nmap versions.

---

### `get_vuln_scripts() -> List[str]`

**Purpose:** Builds the list of vulnerability scripts to run based on configuration.

**Logic Flow:**
```python
1. Select base scripts based on NMAP_VULN_INTENSITY
   - "light"      → VULN_SCRIPTS_LIGHT (~25 scripts)
   - "standard"   → VULN_SCRIPTS_STANDARD (~80 scripts)
   - "aggressive" → VULN_SCRIPTS_AGGRESSIVE (~110 scripts)

2. Add category-specific scripts from NMAP_VULN_CATEGORIES

3. Add NMAP_CUSTOM_SCRIPTS

4. Add BRUTE_SCRIPTS if NMAP_BRUTE_SCAN enabled

5. Remove duplicates (preserving order)

6. Filter out scripts not installed on system
   - Keeps wildcard patterns (e.g., "http-vuln-*") as-is
   - Only includes scripts found in get_available_nmap_scripts()
```

**Returns:** Filtered, deduplicated list of NSE script names

---

### `get_proxychains_cmd() -> Optional[str]`

**Purpose:** Finds the proxychains command on the system.

**Checks for:**
1. `proxychains4` (preferred, modern version)
2. `proxychains` (legacy)

**Returns:** Command name string or `None` if not found

---

### `is_root() -> bool`

**Purpose:** Checks if script is running with root privileges.

**Why needed:** OS detection (`-O`) and SYN scans (`-sS`) require root.

**Mechanism:** Uses `os.geteuid() == 0`

---

### `is_tor_running() -> bool`

**Purpose:** Verifies Tor SOCKS proxy is accessible.

**Mechanism:**
1. Creates TCP socket
2. Attempts connection to `127.0.0.1:9050` (default Tor SOCKS port)
3. Returns `True` if connection succeeds

---

### `extract_targets_from_recon(recon_data: dict) -> Tuple[Set[str], Set[str], Dict[str, List[str]]]`

**Purpose:** Extracts all scannable targets from reconnaissance data.

**Input:** Recon data dictionary with DNS structure

**Output Tuple:**
1. `unique_ips`: Set of all IPv4 and IPv6 addresses
2. `unique_hostnames`: Set of domain and subdomains with DNS records
3. `ip_to_hostnames`: Mapping of each IP to hostnames pointing to it

**Extraction Sources:**
- Root domain A/AAAA records (`dns.domain.ips.ipv4/ipv6`)
- Subdomain A/AAAA records (`dns.subdomains.*.ips.ipv4/ipv6`)

**Example:**
```python
# Input recon_data structure:
{
    "domain": "example.com",
    "dns": {
        "domain": {"ips": {"ipv4": ["93.184.216.34"], "ipv6": []}},
        "subdomains": {
            "www.example.com": {"has_records": True, "ips": {"ipv4": ["93.184.216.34"], "ipv6": []}},
            "mail.example.com": {"has_records": True, "ips": {"ipv4": ["93.184.216.35"], "ipv6": []}}
        }
    }
}

# Output:
ips = {"93.184.216.34", "93.184.216.35"}
hostnames = {"example.com", "www.example.com", "mail.example.com"}
ip_to_hostnames = {
    "93.184.216.34": ["example.com", "www.example.com"],
    "93.184.216.35": ["mail.example.com"]
}
```

---

### `build_nmap_arguments(for_hostname: bool = False, use_tor: bool = False) -> Tuple[str, List[str]]`

**Purpose:** Constructs the nmap command-line arguments string.

**Parameters:**
- `for_hostname`: If `True`, skips OS detection (less reliable for hostnames)
- `use_tor`: If `True`, forces connect scan and disables features incompatible with proxies

**Returns:**
1. Arguments string (e.g., `-T3 -sV --top-ports 1000 --script=...`)
2. List of vulnerability scripts being used

**Argument Construction Logic:**

```python
# 1. Tor adjustments
if use_tor:
    args.append("-sT")  # Connect scan (only type that works through proxy)

# 2. Timing based on SCAN_TYPE
if NMAP_SCAN_TYPE == "fast":
    args.append("-T4")      # Aggressive timing
elif NMAP_SCAN_TYPE == "thorough":
    args.append("-T3")      # Normal timing
    if not for_hostname and not use_tor:
        args.append("-A")   # OS + version + scripts + traceroute
elif NMAP_SCAN_TYPE == "stealth":
    if use_tor:
        args.append("-T3")  # Can't be stealthy through proxy
    else:
        args.append("-T2")  # Polite timing
        args.append("-sS")  # SYN scan (half-open)

# 3. Port specification
if NMAP_CUSTOM_PORTS:
    args.append(f"-p {NMAP_CUSTOM_PORTS}")
elif NMAP_TOP_PORTS > 0:
    args.append(f"--top-ports {NMAP_TOP_PORTS}")

# 4. Service detection (always if vuln scanning)
if NMAP_SERVICE_DETECTION or NMAP_VULN_SCAN:
    args.append("-sV")
    args.append("--version-intensity 7")  # Max version probe depth

# 5. OS detection (requires root, not through proxy)
if NMAP_OS_DETECTION and not for_hostname and not use_tor and is_root():
    args.append("-O")
    args.append("--osscan-guess")

# 6. Script selection
scripts = []
if NMAP_SCRIPT_SCAN:
    scripts.extend(["default", "banner", "http-title", "ssl-cert", "ssh-hostkey"])
if NMAP_VULN_SCAN:
    scripts.extend(get_vuln_scripts())

if scripts:
    args.append(f"--script={','.join(scripts)}")
    args.append(f"--script-timeout {NMAP_SCRIPT_TIMEOUT}s")
    args.append("--script-args=http.useragent=Mozilla/5.0,vulners.mincvss=0.0")

# 7. Always included
args.append("-Pn")      # Skip host discovery (assume online)
args.append("--open")   # Only show open ports
```

---

### `extract_cves_from_script(script_id: str, script_output: str) -> List[Dict]`

**Purpose:** Parses NSE script output to extract CVE identifiers and CVSS scores.

**Patterns Matched:**

1. **Vulners format:** `CVE-YYYY-NNNNN  SCORE  URL`
   ```
   CVE-2017-5638    10.0  https://vulners.com/cve/CVE-2017-5638
   ```

2. **Generic CVE pattern:** `CVE-YYYY-NNNNN`
   ```
   Vulnerable to CVE-2014-3566 (POODLE)
   ```

**Returns:** List of CVE dictionaries:
```python
[
    {
        "id": "CVE-2017-5638",
        "cvss": 10.0,
        "url": "https://vulners.com/cve/CVE-2017-5638",
        "source": "vulners"
    },
    {
        "id": "CVE-2014-3566",
        "cvss": None,
        "url": "https://nvd.nist.gov/vuln/detail/CVE-2014-3566",
        "source": "ssl-poodle"
    }
]
```

---

### `classify_vulnerability(script_id: str, script_output: str) -> Dict`

**Purpose:** Analyzes script output to determine if a vulnerability exists and classify its severity.

**Vulnerability Detection Logic:**

A vulnerability is marked as **confirmed** only if:

1. **CVEs are found** in the output, OR
2. **Nmap standard format** `State: VULNERABLE` is present, OR
3. **Explicit vulnerability phrases** are detected

**Detection Categories:**

```python
# Scripts that only produce output when they find something
vuln_detection_scripts = [
    "http-sql-injection", "http-stored-xss", "ssl-heartbleed",
    "ftp-anon", "dns-zone-transfer", "smb-vuln-ms17-010", ...
]

# Negative phrases (NOT vulnerable)
negative_phrases = [
    "couldn't find any", "not vulnerable", "no vulnerabilities",
    "does not appear", "appears to be safe", ...
]

# Positive vulnerability indicators
explicit_vuln_patterns = [
    "state: vulnerable",           # Nmap standard
    "is vulnerable",               # General
    "anonymous ftp login allowed", # FTP
    "allows zone transfer",        # DNS
    "sql injection",               # Web
    "xss vulnerability",           # Web
    "heartbleed",                  # SSL
    "backdoor",                    # Critical
    ...
]
```

**Severity Classification:**

| Severity | Trigger |
|----------|---------|
| **Critical** | EternalBlue, Heartbleed, Shellshock, RCE backdoors, CVSS ≥ 9.0 |
| **High** | POODLE, SMB vulns, SQL injection, CVSS ≥ 7.0 |
| **Medium** | XSS, CSRF, zone transfer, open relay, CVSS ≥ 4.0 |
| **Low** | Other confirmed vulnerabilities |
| **Info** | Not confirmed as vulnerable |

**Category Classification:**

| Script Prefix | Category |
|--------------|----------|
| `ssl-*` | `ssl_tls` |
| `http-*` | `web` |
| `smb-*` | `smb` |
| `ssh-*` | `ssh` |
| `ftp-*` | `ftp` |
| `dns-*` | `dns` |
| `smtp-*` | `smtp` |
| `*brute*` | `authentication` |
| `*vuln*` | `vulnerability` |

**Returns:**
```python
{
    "script_id": "ssl-heartbleed",
    "output": "...",
    "severity": "critical",
    "category": "ssl_tls",
    "is_vulnerable": True,
    "cves": [{"id": "CVE-2014-0160", ...}],
    "description": "VULNERABLE - Memory disclosure"
}
```

---

### `parse_nmap_result(nm: nmap.PortScanner, target: str, is_hostname: bool = False) -> Dict`

**Purpose:** Converts raw nmap scanner results into a structured dictionary.

**Extracts:**
- Host status (up/down)
- Resolved IPs (for hostname scans)
- Hostnames discovered
- OS detection matches (top 5)
- All TCP/UDP port information
- Service details (name, version, product, CPE)
- All script outputs
- Vulnerability classifications
- CVE aggregation

**Special Features:**

1. **Dual Script Tracking:**
   - `vulnerabilities.findings`: Only confirmed vulnerabilities
   - `all_script_results`: ALL scripts run (vulnerable + not vulnerable)

2. **Complete Audit Trail:**
   ```python
   "all_script_results": {
       "total_scripts_run": 45,
       "vulnerable": [...],      # Scripts that found issues
       "not_vulnerable": [...]   # Scripts that ran clean
   }
   ```

---

### `scan_with_proxychains(target: str, arguments: str, proxychains_cmd: str) -> Optional[str]`

**Purpose:** Executes nmap through proxychains for anonymous scanning.

**Command Construction:**
```bash
proxychains4 -q nmap -oX - [arguments] [target]
```

**Flags Used:**
- `-q`: Quiet mode (suppress proxychains messages)
- `-oX -`: Output XML to stdout (captured by subprocess)

**Returns:** XML output string or `None` on timeout/error

---

### `scan_target(nm: nmap.PortScanner, target: str, arguments: str, is_hostname: bool, label: str, proxychains_cmd: Optional[str]) -> Dict`

**Purpose:** Scans a single target and returns parsed results.

**Flow:**
1. Display scan initiation message
2. If `proxychains_cmd` provided:
   - Call `scan_with_proxychains()`
   - Parse XML with `nm.analyse_nmap_xml_scan()`
3. Else:
   - Direct scan with `nm.scan()`
4. Parse results with `parse_nmap_result()`
5. Print summary (ports found, vulnerabilities)
6. Return result dictionary

**Error Handling:** Returns error structure if scan fails

---

### `run_nmap_scan(recon_data: dict, output_file: Path = None) -> dict`

**Purpose:** Main orchestrator function that runs the complete nmap scanning pipeline.

**Phases:**

1. **Initialization:**
   - Check NMAP_ENABLED
   - Detect Tor/proxychains
   - Initialize PortScanner

2. **Target Extraction:**
   - Call `extract_targets_from_recon()`

3. **Argument Building:**
   - Call `build_nmap_arguments()`

4. **Phase 1 - IP Scanning:**
   - Scan each unique IP
   - Save incrementally after each

5. **Phase 2 - Hostname Scanning:**
   - If `NMAP_SCAN_HOSTNAMES` enabled
   - Scan each hostname separately

6. **Phase 3 - UDP Scanning:**
   - If `NMAP_SCAN_UDP` enabled and not using Tor
   - Separate UDP pass on IPs

7. **Result Compilation:**
   - Aggregate vulnerability counts
   - Sort CVEs by CVSS
   - Generate summary
   - Add to recon_data

**Returns:** Enriched `recon_data` with `nmap` section

---

### `enrich_recon_file(recon_file: Path) -> dict`

**Purpose:** Standalone function to enrich an existing recon JSON file.

**Usage:**
```python
from nmap_scan import enrich_recon_file
enriched = enrich_recon_file(Path("output/recon_example.com.json"))
```

---

## Nmap Arguments Explained

### Timing Templates (`-T<0-5>`)

| Flag | Name | Description |
|------|------|-------------|
| `-T0` | Paranoid | Extremely slow, IDS evasion |
| `-T1` | Sneaky | Slow, IDS evasion |
| `-T2` | Polite | Slowed down, less bandwidth/resources |
| `-T3` | Normal | Default timing |
| `-T4` | Aggressive | Fast, assumes fast network |
| `-T5` | Insane | Very fast, may miss results |

### Scan Types

| Flag | Name | Description | Root Required |
|------|------|-------------|---------------|
| `-sS` | SYN Scan | Half-open scan, stealthy | Yes |
| `-sT` | Connect Scan | Full TCP connect, works through proxy | No |
| `-sU` | UDP Scan | UDP port discovery | Yes |
| `-sA` | ACK Scan | Map firewall rules | Yes |

### Host Discovery

| Flag | Description |
|------|-------------|
| `-Pn` | Skip host discovery, treat all as online |
| `-PS<ports>` | TCP SYN ping |
| `-PA<ports>` | TCP ACK ping |

### Port Specification

| Flag | Example | Description |
|------|---------|-------------|
| `-p <ports>` | `-p 22,80,443` | Specific ports |
| `-p <range>` | `-p 1-1000` | Port range |
| `--top-ports <n>` | `--top-ports 1000` | N most common ports |

### Service/Version Detection

| Flag | Description |
|------|-------------|
| `-sV` | Probe open ports for service/version |
| `--version-intensity <0-9>` | How hard to try (7 is high) |
| `--version-all` | Try every single probe |

### OS Detection

| Flag | Description | Root Required |
|------|-------------|---------------|
| `-O` | Enable OS detection | Yes |
| `--osscan-guess` | Guess OS if uncertain | Yes |
| `-A` | Aggressive: OS + version + scripts + traceroute | Yes |

### Script Scanning

| Flag | Description |
|------|-------------|
| `--script=<scripts>` | Comma-separated list of scripts |
| `--script-args=<args>` | Arguments passed to scripts |
| `--script-timeout <time>` | Max time per script |

### Output Control

| Flag | Description |
|------|-------------|
| `-oX <file>` | XML output (used by python-nmap) |
| `-oN <file>` | Normal output |
| `-oG <file>` | Grepable output |
| `--open` | Only show open ports |

---

## NSE Vulnerability Scripts

### Light Intensity Scripts (~25)

**SSL/TLS Information:**
```
ssl-cert          - Certificate details
ssl-enum-ciphers  - Supported cipher suites  
ssl-known-key     - Known weak keys
ssl-date          - Server time from TLS
```

**HTTP Information:**
```
http-headers           - Response headers
http-server-header     - Server identification
http-security-headers  - Missing security headers
http-cookie-flags      - Cookie security flags
http-cors              - CORS configuration
http-methods           - Allowed HTTP methods
```

**General:**
```
banner         - Service banners
unusual-port   - Services on non-standard ports
ssh-hostkey    - SSH host key fingerprint
ssh2-enum-algos- SSH algorithms supported
dns-nsid       - DNS server ID
dns-recursion  - DNS recursion enabled
```

### Standard Intensity Scripts (~80)

**All light scripts plus:**

**SSL/TLS Vulnerabilities:**
```
ssl-heartbleed     - CVE-2014-0160 (Heartbleed)
ssl-poodle         - CVE-2014-3566 (POODLE)
ssl-ccs-injection  - CVE-2014-0224
ssl-dh-params      - Weak DH parameters
sslv2              - SSLv2 support (insecure)
sslv2-drown        - DROWN attack
```

**HTTP Vulnerabilities:**
```
http-vuln-cve2017-5638  - Apache Struts RCE
http-vuln-cve2014-3704  - Drupalgeddon
http-shellshock         - CVE-2014-6271
http-sql-injection      - SQL injection detection
http-stored-xss         - Stored XSS
http-dombased-xss       - DOM-based XSS
http-csrf               - CSRF tokens
http-enum               - Common paths/files
http-git                - Exposed .git directory
http-robots.txt         - robots.txt contents
http-config-backup      - Backup files
http-passwd             - /etc/passwd exposure
```

**SMB Vulnerabilities:**
```
smb-vuln-ms17-010  - EternalBlue
smb-vuln-ms08-067  - Conficker vector
smb-vuln-cve-2017-7494 - SambaCry
smb-double-pulsar-backdoor
smb-security-mode
smb-os-discovery
```

**FTP Vulnerabilities:**
```
ftp-anon              - Anonymous login
ftp-bounce            - FTP bounce attack
ftp-vsftpd-backdoor   - vsftpd 2.3.4 backdoor
ftp-proftpd-backdoor  - ProFTPD backdoor
```

**Other Services:**
```
dns-zone-transfer       - AXFR allowed
smtp-open-relay         - Open mail relay
mysql-vuln-cve2012-2122 - MySQL auth bypass
rdp-vuln-ms12-020       - RDP DoS/RCE
vulners                 - Version-based CVE lookup
```

### Aggressive Intensity Scripts (~110)

**All standard scripts plus:**

**Additional HTTP CVEs:**
```
http-vuln-cve2006-3392  - Webmin file disclosure
http-vuln-cve2010-0738  - JBoss
http-vuln-cve2010-2861  - Adobe ColdFusion
http-vuln-cve2012-1823  - PHP CGI
http-vuln-cve2015-1427  - Elasticsearch RCE
http-slowloris-check    - DoS vulnerability
http-dlink-backdoor     - D-Link router backdoor
```

**Additional SMB:**
```
smb-vuln-ms06-025
smb-vuln-ms07-029
smb-vuln-regsvc-dos
smb-vuln-webexec
smb2-vuln-uptime
```

### Brute Force Scripts (Optional)

```
ssh-brute     - SSH password brute force
ftp-brute     - FTP password brute force
http-brute    - HTTP Basic/Digest brute force
mysql-brute   - MySQL password brute force
smb-brute     - SMB password brute force
vnc-brute     - VNC password brute force
```

⚠️ **Warning:** Brute force scripts may trigger account lockouts!

---

## Vulnerability Detection Logic

### Classification Decision Tree

```
                     ┌─────────────────────┐
                     │   Script Output     │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │   Contains CVE?     │
                     └──────────┬──────────┘
                          ╱     │     ╲
                        Yes     │      No
                         │      │       │
           ┌─────────────▼──┐   │   ┌───▼───────────────────┐
           │ VULNERABLE     │   │   │ Contains negative     │
           │ Extract CVEs   │   │   │ phrase?               │
           │ Set severity   │   │   │ ("not vulnerable")    │
           └────────────────┘   │   └───────────┬───────────┘
                                │         ╱     │     ╲
                                │       Yes     │      No
                                │        │      │       │
                                │   ┌────▼────┐ │   ┌───▼───────────────┐
                                │   │ NOT     │ │   │ Is vuln-detection │
                                │   │ VULN    │ │   │ script with       │
                                │   │ (info)  │ │   │ findings?         │
                                │   └─────────┘ │   └───────────┬───────┘
                                │               │         ╱     │     ╲
                                │               │       Yes     │      No
                                │               │        │      │       │
                                │               │   ┌────▼────┐ │   ┌───▼───────────┐
                                │               │   │ VULN    │ │   │ Contains      │
                                │               │   │         │ │   │ explicit      │
                                │               │   └─────────┘ │   │ vuln phrase?  │
                                │               │               │   └───────┬───────┘
                                │               │               │     ╱     │     ╲
                                │               │               │   Yes     │      No
                                │               │               │    │      │       │
                                │               │               │┌───▼───┐  │  ┌────▼────┐
                                │               │               ││ VULN  │  │  │ NOT VULN│
                                │               │               │└───────┘  │  │ (info)  │
                                │               │               │           │  └─────────┘
```

### Severity Assignment

```python
# After classifying as vulnerable, assign severity:

CRITICAL if:
  - Script in [smb-vuln-ms17-010, ssl-heartbleed, http-shellshock, ...]
  - OR CVE with CVSS >= 9.0

HIGH if:
  - Script in [ssl-poodle, http-sql-injection, smb-vuln-*, ...]
  - OR CVE with CVSS >= 7.0

MEDIUM if:
  - Script in [http-stored-xss, dns-zone-transfer, smtp-open-relay, ...]
  - OR CVE with CVSS >= 4.0

LOW:
  - Other confirmed vulnerabilities

INFO:
  - Not classified as vulnerable
```

---

## Output Data Structure

### Complete JSON Schema

```json
{
  "nmap": {
    "scan_metadata": {
      "scan_timestamp": "2024-01-15T10:30:00.000000",
      "scanner_version": "(7, 94)",
      "scan_type": "thorough",
      "vuln_scan_enabled": true,
      "vuln_intensity": "standard",
      "scripts_loaded": 85,
      "anonymous_mode": false,
      "proxychains_cmd": null,
      "ip_arguments": "-T3 -sV --version-intensity 7 -O ...",
      "hostname_arguments": "-T3 -sV --version-intensity 7 ...",
      "total_ips": 2,
      "total_hostnames": 5
    },
    
    "by_ip": {
      "93.184.216.34": {
        "target": "93.184.216.34",
        "target_type": "ip",
        "scan_timestamp": "2024-01-15T10:30:15.000000",
        "status": "up",
        "resolved_ips": [],
        "hostnames": [
          {"name": "example.com", "type": "PTR"}
        ],
        "os_detection": [
          {
            "name": "Linux 4.15",
            "accuracy": "95",
            "os_family": "Linux",
            "os_gen": "4.X",
            "vendor": "Linux",
            "cpe": ["cpe:/o:linux:linux_kernel:4.15"]
          }
        ],
        "ports_scripts": {
          "tcp": [
            {
              "port": 80,
              "state": "open",
              "reason": "syn-ack",
              "service": "http",
              "product": "nginx",
              "version": "1.18.0",
              "extrainfo": "Ubuntu",
              "conf": "10",
              "cpe": ["cpe:/a:nginx:nginx:1.18.0"],
              "scripts": {
                "http-title": "Welcome to nginx!",
                "http-server-header": "nginx/1.18.0",
                "http-security-headers": "Missing: X-Frame-Options, ..."
              },
              "vulnerabilities": [
                {
                  "script_id": "http-sql-injection",
                  "output": "Possible SQL injection in /search.php?q=",
                  "severity": "high",
                  "category": "web",
                  "is_vulnerable": true,
                  "cves": [],
                  "description": "Possible SQL injection..."
                }
              ]
            },
            {
              "port": 443,
              "state": "open",
              "service": "https",
              "product": "nginx",
              "version": "1.18.0",
              "scripts": {
                "ssl-cert": "Subject: CN=example.com...",
                "ssl-enum-ciphers": "TLSv1.2: ...",
                "ssl-heartbleed": "NOT VULNERABLE"
              },
              "vulnerabilities": []
            }
          ],
          "udp": []
        },
        "host_scripts": {},
        "vulnerabilities": {
          "total": 1,
          "critical": 0,
          "high": 1,
          "medium": 0,
          "low": 0,
          "info": 0,
          "findings": [...],
          "cves": [],
          "by_category": {
            "web": [...]
          }
        },
        "all_script_results": {
          "total_scripts_run": 45,
          "vulnerable": [
            {
              "script_id": "http-sql-injection",
              "port": 80,
              "protocol": "tcp",
              "service": "http",
              "is_vulnerable": true,
              "severity": "high",
              "category": "web",
              "cves": [],
              "output": "...",
              "description": "..."
            }
          ],
          "not_vulnerable": [
            {
              "script_id": "ssl-heartbleed",
              "port": 443,
              "protocol": "tcp",
              "service": "https",
              "is_vulnerable": false,
              "severity": "info",
              "category": "ssl_tls",
              "cves": [],
              "output": "NOT VULNERABLE",
              "description": "NOT VULNERABLE"
            }
          ]
        }
      }
    },
    
    "by_hostname": {
      "www.example.com": { ... }
    },
    
    "ip_to_hostnames": {
      "93.184.216.34": ["example.com", "www.example.com"]
    },
    
    "summary": {
      "ips_scanned": 2,
      "ips_up": 2,
      "hostnames_scanned": 5,
      "hostnames_up": 5,
      "total_tcp_ports": 10,
      "total_udp_ports": 2
    },
    
    "vulnerabilities": {
      "total": 5,
      "critical": 1,
      "high": 2,
      "medium": 1,
      "low": 1,
      "info": 0,
      "all_cves": [
        {
          "id": "CVE-2017-5638",
          "cvss": 10.0,
          "url": "https://nvd.nist.gov/vuln/detail/CVE-2017-5638",
          "source": "vulners"
        }
      ],
      "by_severity": {
        "critical": [
          {
            "target": "93.184.216.34",
            "port": 8080,
            "service": "http-proxy",
            "script": "http-vuln-cve2017-5638",
            "description": "Apache Struts RCE",
            "cves": ["CVE-2017-5638"]
          }
        ],
        "high": [...],
        "medium": [...],
        "low": [...],
        "info": [...]
      }
    },
    
    "all_script_results_summary": {
      "total_scripts_run": 450,
      "total_vulnerable": 5,
      "total_not_vulnerable": 445
    }
  }
}
```

---

## Updating Vulnerability Data

Understanding how Nmap gets and updates CVE/CVSS information is important for effective vulnerability scanning.

### How Nmap Gets CVE/CVSS Data

Nmap does **NOT calculate CVSS scores** - it queries external databases in real-time:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NMAP CVE/CVSS DATA FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   NMAP SCAN                         VULNERS.COM API                     │
│   ┌─────────────────┐               ┌─────────────────┐                │
│   │  Service/Version│               │  250GB+ CVE     │                │
│   │  Detection      │               │  Database       │                │
│   │                 │               │                 │                │
│   │  nginx 1.18.0   │   HTTP API    │  Returns:       │                │
│   │  OpenSSH 8.2    │ ────────────▶ │  - CVE IDs      │                │
│   │  Apache 2.4.41  │               │  - CVSS Scores  │                │
│   │                 │ ◀──────────── │  - URLs         │                │
│   └─────────────────┘               └─────────────────┘                │
│          │                                   │                          │
│          │                                   │                          │
│          ▼                                   │                          │
│   ┌─────────────────┐                        │                          │
│   │  vulners NSE    │  Real-time lookup      │                          │
│   │  Script Output  │  (requires internet)   │                          │
│   │                 │                        │                          │
│   │  CVE-2021-44228 │                        │                          │
│   │  CVSS: 10.0     │ ◀──────────────────────┘                          │
│   │  https://...    │                                                   │
│   └─────────────────┘                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Point: No Local Database Updates Needed

Unlike GVM and Nuclei, **Nmap doesn't store vulnerability data locally**. The `vulners` NSE script queries vulners.com API during each scan:

| Aspect | Nmap/Vulners | GVM | Nuclei |
|--------|--------------|-----|--------|
| **Data Location** | Remote (vulners.com) | Local (Docker volumes) | Local (Docker volume) |
| **Update Required** | NO | YES (weekly) | YES (auto or manual) |
| **Internet Required** | YES (during scan) | NO (after sync) | NO (after sync) |
| **Database Size** | 250GB+ (remote) | ~3GB (local) | ~100MB (local) |
| **Freshness** | Real-time | As of last sync | As of last update |

### What You DO Need to Update

While CVE data is fetched live, the NSE scripts themselves may need updates:

```bash
# Update nmap NSE script database (only if you add/modify local scripts)
nmap --script-updatedb

# Update nmap itself for new built-in scripts
sudo apt update && sudo apt upgrade nmap

# If using Docker, pull latest image
docker pull instrumentisto/nmap:latest
```

### How vulners NSE Script Works

1. **Scan detects service version** (e.g., `nginx/1.18.0`)
2. **Script sends CPE to vulners.com API**
3. **API returns matching CVEs with CVSS scores**
4. **Script formats output**:
   ```
   vulners:
     CVE-2021-23017  7.5  https://vulners.com/cve/CVE-2021-23017
     CVE-2019-20372  5.3  https://vulners.com/cve/CVE-2019-20372
   ```

### CVSS Score Source

In RedAmon's nmap output, CVSS scores come from vulners.com (which aggregates from NVD):

```python
# In nmap_scan.py - CVE extraction from vulners output
# Pattern: CVE-YYYY-NNNNN  SCORE  URL
vulners_pattern = r'(CVE-\d{4}-\d+)\s+(\d+\.?\d*)\s+(https?://\S+)?'

# Example match:
# CVE-2021-44228  10.0  https://vulners.com/cve/CVE-2021-44228
```

**Severity Classification:**
```
CVSS 9.0-10.0  →  Critical
CVSS 7.0-8.9   →  High
CVSS 4.0-6.9   →  Medium
CVSS 0.1-3.9   →  Low
CVSS 0.0/None  →  Info
```

### Requirements for CVE Detection

1. **Internet connection** during scan (for vulners API)
2. **Service detection enabled** (`-sV` flag)
3. **vulners script included** (`--script=vulners`)

```python
# In params.py - ensure these are enabled
NMAP_SERVICE_DETECTION = True  # Required for version-based CVE lookup
NMAP_VULN_SCAN = True          # Enables vulners and other vuln scripts
```

### Offline Alternative: vulscan

For air-gapped environments, you can use `vulscan` with local CSV databases:

```bash
# Install vulscan (not included by default)
git clone https://github.com/scipag/vulscan /usr/share/nmap/scripts/vulscan

# Download offline CVE databases
cd /usr/share/nmap/scripts/vulscan
./update.sh

# Use in scan
nmap --script=vulscan/vulscan.nse <target>
```

**Note:** Offline databases require manual updates and may be less current than vulners.

### Troubleshooting CVE Detection

| Issue | Cause | Solution |
|-------|-------|----------|
| No CVEs found | Version not detected | Enable `-sV`, increase `--version-intensity` |
| No CVEs found | vulners script not loaded | Check script inclusion, verify internet |
| Outdated CVEs | Using offline vulscan | Update vulscan databases |
| "vulners: ERROR" | API rate limited | Reduce scan rate, wait and retry |
| Missing CVSS scores | CVE too new | vulners.com updates within hours of NVD |

---

## Tor/Proxychains Integration

### Requirements

1. **Tor service running:**
   ```bash
   sudo apt install tor
   sudo systemctl start tor
   sudo systemctl enable tor  # Optional: start on boot
   ```

2. **Proxychains4 installed:**
   ```bash
   sudo apt install proxychains4
   ```

3. **Configuration** (`/etc/proxychains4.conf`):
   ```
   # Default Tor configuration
   [ProxyList]
   socks5 127.0.0.1 9050
   ```

### Limitations When Using Tor

| Feature | Direct Scan | Through Tor |
|---------|-------------|-------------|
| SYN Scan (`-sS`) | ✅ | ❌ (uses `-sT`) |
| OS Detection (`-O`) | ✅ | ❌ (disabled) |
| UDP Scan (`-sU`) | ✅ | ❌ (skipped) |
| Stealth Timing | ✅ | ❌ (uses `-T3`) |
| Speed | Fast | Slower |

### How It Works

```
┌──────────┐     ┌─────────────┐     ┌─────────┐     ┌────────┐
│ nmap_scan│────▶│ proxychains4│────▶│   Tor   │────▶│ Target │
│   .py    │     │  -q nmap    │     │ Network │     │        │
└──────────┘     └─────────────┘     └─────────┘     └────────┘
                       │
                       │ -oX - (XML to stdout)
                       ▼
              ┌─────────────────┐
              │ XML captured by │
              │ subprocess      │
              │ parsed by       │
              │ python-nmap     │
              └─────────────────┘
```

### Command Executed

```bash
proxychains4 -q nmap -oX - -sT -T3 -Pn --open -sV --version-intensity 7 \
  --top-ports 1000 --script=ssl-cert,http-headers,vulners,... \
  --script-timeout 300s --script-args=http.useragent=Mozilla/5.0,vulners.mincvss=0.0 \
  --host-timeout 300s <target>
```

---

## Usage Examples

### Basic Usage (from main.py)

```python
from nmap_scan import run_nmap_scan

# recon_data comes from domain_recon module
enriched_data = run_nmap_scan(recon_data)
```

### Standalone File Enrichment

```python
from pathlib import Path
from nmap_scan import enrich_recon_file

enriched = enrich_recon_file(Path("output/recon_example.com.json"))
```

### Custom Configuration

```python
# In params.py:

# Quick scan of web ports only
NMAP_SCAN_TYPE = "fast"
NMAP_CUSTOM_PORTS = "80,443,8080,8443"
NMAP_VULN_SCAN = True
NMAP_VULN_INTENSITY = "light"
NMAP_VULN_CATEGORIES = ["http", "ssl"]

# Or comprehensive internal network scan
NMAP_SCAN_TYPE = "thorough"
NMAP_TOP_PORTS = 65535  # All ports
NMAP_VULN_INTENSITY = "aggressive"
NMAP_SCAN_UDP = True
NMAP_BRUTE_SCAN = False  # Disable for internal
```

### Anonymous Scan

```bash
# Start Tor
sudo systemctl start tor

# Verify Tor is running
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
```

```python
# In params.py:
USE_TOR_FOR_RECON = True
NMAP_SCAN_TYPE = "default"  # Can't use stealth through Tor
```

---

## Troubleshooting

### Common Issues

#### "Nmap not found"
```bash
# Install nmap
sudo apt install nmap

# Verify
nmap --version
```

#### "OS detection requires root"
```bash
# Run with sudo
sudo python3 recon/main.py

# Or disable OS detection in params.py
NMAP_OS_DETECTION = False
```

#### "Script not found" warnings
```bash
# Update nmap scripts database
sudo nmap --script-updatedb

# Check available scripts
ls /usr/share/nmap/scripts/ | grep <script-name>
```

#### "Proxychains: command not found"
```bash
sudo apt install proxychains4
```

#### Tor connection refused
```bash
# Check Tor status
sudo systemctl status tor

# Start if not running
sudo systemctl start tor

# Test SOCKS proxy
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
```

#### Scan taking too long
```python
# Reduce scope in params.py:
NMAP_TOP_PORTS = 100           # Fewer ports
NMAP_VULN_INTENSITY = "light"  # Fewer scripts
NMAP_SCAN_UDP = False          # Skip UDP
NMAP_TIMEOUT = 120             # Shorter timeout
NMAP_SCRIPT_TIMEOUT = 60       # Shorter script timeout
```

#### No vulnerabilities found (expected some)
```python
# Ensure vulnerability scanning is enabled
NMAP_VULN_SCAN = True
NMAP_SERVICE_DETECTION = True  # Required for version-based CVE lookup

# Try higher intensity
NMAP_VULN_INTENSITY = "aggressive"
```

### Debug Mode

Add to script output to see exact nmap command:
```python
# In scan_target(), after nm.scan():
print(f"[DEBUG] Command: {nm.command_line()}")
```

---

## Security Considerations

⚠️ **Legal Warning:** Only scan systems you have explicit permission to test.

| Risk | Mitigation |
|------|------------|
| Account lockouts | Disable `NMAP_BRUTE_SCAN` |
| Service crashes | Use `"light"` or `"standard"` intensity |
| IDS/IPS alerts | Use `"stealth"` scan type or Tor |
| Bandwidth saturation | Reduce `NMAP_TOP_PORTS`, use `-T2` |
| Rate limiting | Increase timeouts, reduce parallelism |

### Recommended Safe Defaults

```python
# Conservative, safe scan profile
NMAP_SCAN_TYPE = "default"
NMAP_TOP_PORTS = 100
NMAP_VULN_SCAN = True
NMAP_VULN_INTENSITY = "light"
NMAP_BRUTE_SCAN = False
NMAP_SCAN_UDP = False
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python-nmap` | ≥0.7.1 | Python nmap wrapper |
| `nmap` | ≥7.80 | Actual scanner (system) |
| `proxychains4` | Any | Tor routing (optional) |
| `tor` | Any | Anonymous network (optional) |

---

## References

- [Nmap Official Documentation](https://nmap.org/docs.html)
- [NSE Script Documentation](https://nmap.org/nsedoc/)
- [Nmap Timing Templates](https://nmap.org/book/performance-timing-templates.html)
- [python-nmap Documentation](https://pypi.org/project/python-nmap/)
- [Vulners NSE Script](https://github.com/vulnersCom/nmap-vulners)
- [CVSS Scoring Guide](https://www.first.org/cvss/specification-document)

---

*Documentation generated for RedAmon v1.0 - Nmap Scanner Module*

