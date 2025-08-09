SYNC-NET: Multicast File Sharing System
A secure, high-speed, and platform-independent peer-to-peer file sharing system for local networks.



 Overview
SYNC-NET is a custom peer-to-peer file sharing system designed to transfer large files (1–2 GB) quickly and securely over local networks without requiring internet access.
It uses UDP multicast for efficient group transfers and TCP fallback for reliable delivery, combined with AES-256 encryption and BLAKE2b hashing for data integrity.

This project was developed during the Tally CodeBrewers National Hackathon, where it achieved Institute Rank 1 at BIT Mesra and was recognized as a Top Finalist at the national level.

Features
Fast Online  Transfers – Uses UDP multicast for group file sharing and TCP for reliability when needed.

Secure Communication – End-to-end encryption with AES-256.

Data Integrity – File verification using BLAKE2b hashing.

Peer Discovery – Automatic detection of devices using Zeroconf/mDNS.

Dynamic Group Management – Create and manage groups for scoped file sharing.

Cross-Platform Ready – Works on Linux and adaptable for other platforms.

** Real-World Problem Solved**
In our lab, file sharing during remote sessions (e.g., via PuTTY) relied on third-party platforms, making daily transfers tedious and time-consuming.
SYNC-NET eliminates these inefficiencies by enabling platform-independent, offline file sharing integrated into local workflows, ensuring faster collaboration and reduced dependency on external services.
