# 🧵 StitchCraft AI - Tailor Job Slip Generator

> **Built for Hacktoberfest 2026 Weekend Challenge: "Build for a Friend"**  
> An offline, private, open-source AI assistant designed for neighborhood tailors and boutique owners to turn chaotic WhatsApp messages and voice transcripts into clean, printable workshop slips.

---

## 💡 The Problem
Small boutique tailors receive dozens of unformatted, casual customer orders over WhatsApp every week:
> *"Bhaiya stitch an anarkali kurti, chest 38, waist 34, length 42, 3/4 sleeves, deep neck back with tassels. Needs by this Thursday urgent, fabric provided by customer. Advance paid 500 total 1200."*

Key body measurements get lost in chat histories, delivery deadlines slip, and manually handwriting paper tickets takes away creative sewing time.

## 🛡️ Why Open-Source AI?
- **100% Data Privacy:** Body measurements and personal customer contact numbers never leave the local workshop device.
- **Zero API Costs:** Micro-businesses operate on tight margins and cannot afford monthly proprietary token subscriptions. Running **Gemma 2 locally via Ollama** is completely free.
- **Offline Reliability:** Continues functioning seamlessly without an active internet connection.

---

## ⚡ Features
- **Zero-Shot Extraction:** Automatically identifies customer details, garment types, 8+ body measurements, styling instructions, fabric source, and balance dues.
- **Resilient JSON Output:** Cleans unstructured outputs with regex parsing guards.
- **One-Click Workshop Slip:** Custom print CSS (`@media print`) isolates the job card, allowing immediate single-page thermal/paper printing with an auto-generated Ticket ID and urgency badge.

---

## 🛠️ Quickstart

### Prerequisites
1. Install [Ollama](https://ollama.ai) and pull the model:
   ```bash
   ollama run gemma2:2b