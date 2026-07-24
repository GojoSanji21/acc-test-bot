<p align="center">
  <img src="https://imgyx.pages.dev/lcdDn" alt="Telegram ID Storage Bot Banner" width="100%" style="border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 15px 40px rgba(0, 0, 0, 0.8);" />
</p>

<h1 align="center">🤖 Telegram ID Storage Bot</h1>

<p align="center">
  <b>A secure, production-ready private Telegram ID and Session Storage Bot. Orchestrates dual framework client gateways, rotates premium proxy pools, and encrypts sensitive sessions with hybrid shifted cryptos.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Maintained%20With-❤️-blue?style=for-the-badge&labelColor=111111" alt="Maintained with Love">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=111111" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-Aiogram_v3-26A69A?style=for-the-badge&logo=telegram&logoColor=white&labelColor=111111" alt="Framework">
  <img src="https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white&labelColor=111111" alt="Database">
</p>

---

## 📡 System Architecture & Flow (Roadmap)

This non-linear technical blueprint illustrates the parallel routing paths of our bot's session lifecycle, security gateway, and database storage:

```mermaid
graph TD
    User[👤 Telegram User] -->|1. Requests Login| Bot[🤖 Aiogram v3 Bot]
    Admin[👑 Bot Admin] -->|Manage / Broadcast| Bot
    
    Bot -->|2. Rotates IP| Proxy[⚙️ Proxy Pool]
    Bot -.->|Async Listen| OTP[💬 OTP Interceptor]
    
    Proxy -->|3. Route Gateway| TG[💬 Telegram Core API]
    OTP -.->|Intercept Codes| TG
    
    TG -->|4. Generates String Session| Client[📦 Pyrogram Client]
    Client -->|5. Shifted AES-256| Crypt[🔐 Hybrid Encryption Engine]
    Crypt -->|6. Encrypted Store| DB[(🍃 MongoDB Atlas)]

    style User fill:#000,stroke:#333,color:#fff
    style Admin fill:#000,stroke:#6366f1,color:#fff
    style Bot fill:#000,stroke:#2563eb,color:#fff
    style Proxy fill:#000,stroke:#7c3aed,color:#fff
    style OTP fill:#000,stroke:#f43f5e,color:#fff
    style TG fill:#000,stroke:#0284c7,color:#fff
    style Client fill:#000,stroke:#0ea5e9,color:#fff
    style Crypt fill:#000,stroke:#ea580c,color:#fff
    style DB fill:#000,stroke:#16a34a,color:#fff
```

---

## ⚡ Core Features (Website Blocks)

### 🔑 Secure Login & Generation
> **AUTOMATED SESSION GENERATOR**
> Log in securely directly from your private bot panel. It seamlessly generates, extracts, and caches Pyrogram session strings on-demand, automating the tedious manual session-creation process.

### 📡 OTP Interception
> **BACKGROUND INTERCEPTOR**
> Equipped with a high-fidelity internal listener that automatically catches and intercepts background Telegram login codes (OTPs) during sign-in, enabling swift setups without session timeouts.

### 🔐 Robust Hybrid Encryption
> **AES-256 CYBER-SECURITY SHIELD**
> Features a robust, multi-layered, ASCII-shifted AES-256 style substitution mapping. All session strings are strictly encrypted *before* they are sent to the database, ensuring zero data exposure even in the event of a raw database breach.

### ⚙️ SOCKS5 Proxy Pooling
> **RATE-LIMIT BYPASS**
> Integrates an advanced proxy pool system with support for custom rotation (either loaded dynamically via environment variables or loaded locally from a `proxies.txt` file). Bypasses strict API rate limits and prevents server IP bans.

### 📦 Compact Multi-Stage Docker
> **PRODUCTION-READY IMAGES**
> Uses an optimized multi-stage Docker build to keep final container images extremely lightweight and secure, while fully preserving native C-extensions for maximum execution speedups.

---

## ⚙️ Environment Configuration

Ensure these variables are properly mapped inside your deployment console:

```text
🔑 BOT_TOKEN  ──► Token key fetched from t.me/BotFather
🆔 ADMIN_IDS  ──► Authorized Telegram User IDs (comma-separated)
🆔 API_ID     ──► Telegram App ID from my.telegram.org
🔐 API_HASH   ──► Telegram API Hash from my.telegram.org
🍃 MONGO_URI  ──► MongoDB Atlas connection string
```

---

## 🛠️ Quick Start with Docker

### 1. Configure Environment Variables
Copy the example environment file and fill in your variables:
```bash
cp .env.example .env
```

### 2. Configure SOCKS5 Proxies (Optional)
You can configure proxy rotation in two dynamic ways:

*   **Option A: Cloud Environment Variables (Recommended):**
    Simply set a `PROXY` or `PROXIES` environment variable in your cloud hosting dashboard (e.g. Koyeb, Render, Railway). You can separate multiple proxies with commas:
    ```text
    PROXY=socks5://user:pass@host:port,socks5://another_host:port
    ```
*   **Option B: Local Proxies File (`proxies.txt`):**
    Create or edit `proxies.txt` in the root folder of your project:
    ```text
    socks5://user:pass@host:port
    socks5://host:port
    ```

### 3. Deploy via Docker Compose
Build and run the bot container quietly in the background:
```bash
docker compose up -d --build
```

Monitor live container logs:
```bash
docker compose logs -f
```

Stop and destroy the active container:
```bash
docker compose down
```

---

## 📦 Manual VPS Deployment (Alternative)

If you prefer to host and execute the codebase natively on your virtual machine:

### 1. Install Required Packages
```bash
pip3 install -r requirements.txt
```

### 2. Run the Engine
```bash
python3 bot.py
```

---

## 📢 Support & Updates
Modified, optimized, and maintained with ❤️ by **[@UNRATED_CODER](https://t.me/UNRATED_CODER)**. 

Join our official channel for instant support, updates, and more elite open-source projects:

<p align="left">
  <a href="https://t.me/UNRATED_CODER">
    <img src="https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram&logoColor=white&labelColor=111111" alt="Telegram Channel" />
  </a>
</p>

---

## ✨ Developers
<div align="center">

| [**➳≛⃝ Gojo ×͜×**](https://t.me/DoraShin_hlo) | [**Lᴜғғʏᴛᴀʀᴏ シ︎**](https://t.me/Og_Luffytaro)j

</div>
