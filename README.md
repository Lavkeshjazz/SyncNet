# 🚀 SYNC-NET: Multicast File Sharing System  

**A secure, high-speed, and platform-independent peer-to-peer file sharing system for local networks — built entirely in Python.**  


![Language](https://img.shields.io/badge/language-Python%203.x-yellow)  
![Platform](https://img.shields.io/badge/platform-Cross--Platform-lightgrey)  

---

## 📌 Overview  
**SYNC-NET** is a **custom peer-to-peer file sharing system** designed for **fast, secure, and offline transfers** (up to 1–2 GB) over **local networks**.  
It uses **UDP multicast** for efficient group transfers and **TCP fallback** for reliable delivery, combined with **AES-256 encryption** and **BLAKE2b hashing** for maximum security — all implemented in **pure Python**, ensuring **cross-platform compatibility**.  

🏆 Developed during the **Tally CodeBrewers National Hackathon**  
🏅 **Top Finalist (National Level)** & **Institute Rank 1 – BIT Mesra**  

---

## ✨ Features  

✅ **Fast Transfers** – UDP multicast for speed, TCP fallback for reliability  
✅ **Secure Communication** – AES-256 encryption for end-to-end security  
✅ **Data Integrity** – File verification with BLAKE2b hashing  
✅ **Automatic Peer Discovery** – Zeroconf/mDNS service discovery  
✅ **Dynamic Group Management** – Scoped sharing for multiple user groups  
✅ **Platform Independent** – Runs on Windows, macOS, and Linux with Python 3.x  

---

## 🎯 Real-World Problem & Solution  

**Problem:**  
In our lab, file sharing during remote sessions (e.g., via PuTTY) relied on third-party platforms, making **daily transfers tedious, slow, and dependent on the internet**.  

**Solution:**  
We built **SYNC-NET**, a **Python-based, platform-independent, offline file sharing system** using **UDP multicast + TCP fallback** to transfer large files quickly within a local network, removing third-party dependencies and improving workflow efficiency.  

---

## 🛠️ Tech Stack  

- **Language:** Python 3.x  
- **Networking:** UDP Multicast, TCP  
- **Security:** AES-256 Encryption, BLAKE2b Hashing  
- **Service Discovery:** Zeroconf / mDNS  
- **UI & Utilities:** Tkinter, Custom Python Scripts  

---

## 📂 Project Structure  

```plaintext
SYNC-NET/
│
├── group_mgmnt/           # Group management logic
├── multicast_receiver/    # Receiver implementation
├── multicast_sender/      # Sender implementation
├── Secure_Receiver.py     # Secure file receiver logic
├── advertise.py           # Service advertisement
├── config.py              # Configuration settings
├── discovery_ui.py        # UI for service discovery
├── network_scan.py        # Network scanning utility
├── requirements.txt       # Python dependencies
└── sample.png             # UI/Architecture screenshots
## ⚡ Getting Started  

Follow these steps to set up and run **SYNC-NET** on your system:  

---

1️⃣ Clone the Repository

git clone https://github.com/Lavkeshjazz/SyncNet.git
cd SyncNet
pip install -r requirements.txt
python Secure_Receiver.py

