# xenu-python

A lightweight Python URL and IP metadata scanner that processes targets from a TXT file and exports HTTP response metadata to CSV.

The scanner supports:
- Domains
- IP addresses
- Custom ports
- HTTP and HTTPS
- Self-signed certificates
- Invalid SSL certificates
- Automatic HTTPS → HTTP fallback
- Pause/Resume/Quit controls during scanning

---

# Features

- Reads targets from a TXT file
- Prompts user for:
  - Input TXT file
  - HTTP or HTTPS preference
  - Output CSV filename
- Extracts:
  - HTTP response status
  - Content length
  - HTML page title
  - Server banner
- Ignores invalid SSL certificates
- Automatically retries HTTP if HTTPS fails
- Real-time progress display
- Pause/Resume/Quit controls
- CSV output with incremental saving

---

# Requirements

Python 3.8+

No third-party libraries required.

Uses only native Python libraries.

---



---

# Usage

Create a TXT file containing targets:

```txt
google.com
url.com
192.168.1.1
10.0.0.5:8443
example.org
```

Run the scanner:

```bash
python3 scanner.py
```

Example prompts:

```txt
Enter path to TXT file containing URLs/IPs: targets.txt
Use https or http? [https/http]: https
Enter output CSV filename: results
```

---

# Runtime Controls

During scanning:

```txt
p + Enter = Pause
r + Enter = Resume
q + Enter = Quit and save progress
```

---

# Output

Example CSV output:

```csv
input_url,final_url,domain,status,content_length,title,server
https://google.com,https://www.google.com,www.google.com,200,54821,Google,gws
https://192.168.1.1,https://192.168.1.1,192.168.1.1,200,10342,Router Login,nginx
https://10.0.0.5:8443,https://10.0.0.5:8443,10.0.0.5:8443,401,,,
```

---

# SSL Handling

The scanner globally disables SSL certificate validation:

- Self-signed certificates
- Expired certificates
- Invalid certificate chains
- Hostname mismatches
- Internal PKI certificates

If HTTPS fails due to protocol mismatch or SSL negotiation issues, the scanner automatically retries using HTTP.

---

# Use Cases

- Web inventory collection
- Internal network reconnaissance
- HTTP banner collection
- Asset metadata enrichment
- Security assessments
- Infrastructure validation
- Web service discovery

---

# Notes

- Some services may not return HTML titles
- Non-web services may return blank metadata
- HTTPS on incorrect ports may automatically downgrade to HTTP
- CSV is written incrementally to preserve progress

---

# License

MIT License
