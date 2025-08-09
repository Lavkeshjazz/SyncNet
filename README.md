# 🚀 SYNC-NET: Multicast File Sharing System  

**A secure, high-speed, and platform-independent peer-to-peer file sharing system for local networks.**  

---

## 📌 Overview  
**SYNC-NET** is a **custom peer-to-peer file sharing system** designed for **fast and secure file transfers** (up to 1–2 GB) over **local networks without internet access**.  
It uses **UDP multicast** for efficient group transfers and **TCP fallback** for reliable delivery, combined with **AES-256 encryption** and **BLAKE2b hashing** for maximum security.  

🏆 Developed during the **Tally CodeBrewers National Hackathon**  
🏅 **Top Finalist (National Level)** & **Institute Rank 1 – BIT Mesra**  

---

## ✨ Features  

✅ **Fast  Transfers** – UDP multicast for speed, TCP fallback for reliability  
✅ **Secure Communication** – AES-256 encryption for end-to-end security  
✅ **Data Integrity** – File verification with BLAKE2b hashing  
✅ **Peer Discovery** – Automatic detection using Zeroconf/mDNS  
✅ **Dynamic Group Management** – Scoped sharing for different groups  
✅ **Cross-Platform Ready** – Works on Linux; adaptable for other platforms  

---

## 🎯 Real-World Problem & Solution  

**Problem:**  
In our lab, file sharing during remote sessions (e.g., via PuTTY) relied on third-party platforms, making **daily transfers tedious, slow, and dependent on the internet**.  

**Solution:**  
We built **SYNC-NET**, a **platform-independent, offline file sharing system** using **UDP multicast + TCP fallback** to transfer large files quickly within a local network, removing third-party dependencies and improving workflow efficiency.  

---

## 🛠️ Tech Stack  

- **Networking:** UDP Multicast, TCP  
- **Security:** AES-256 Encryption, BLAKE2b Hashing  
- **Service Discovery:** Zeroconf / mDNS  





