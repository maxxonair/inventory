<h1 align="center">inventory</h1>
<p align="center">A minimal asset management tool</p>

---

A lightweight inventory management system for tracking physical assets in a digital database. Assets are uniquely identified by auto-generated QR code labels, enabling you to manage storage locations and lending status with ease.

**Key Features**
- 📦 Simple, maintainable inventory database
- 🏷️ QR label generation for assets and storage locations
- 💻 Minimal hardware requirements
- 🔐 Built-in authentication, or bring your own
- 🌐 Web app frontend built with [Svelte](https://svelte.dev/)
- 🔍 Track and match assets to storage locations

![Inventory example screenshot](https://github.com/maxxonair/inventory/blob/0.0.2/imgs/inv_example.png?raw=true)

---

## Architecture

The application is composed of three independent modules that can run on a single machine or be distributed across several (distribution is recommended):

- **Database** — stores all asset and location records
- **Inventory Server** — backend API and business logic
- **Inventory App** — Svelte-based web frontend

![Architecture diagram](https://github.com/maxxonair/inventory/blob/0.0.2/imgs/inventory_sketch_light.drawio.png?raw=true)

---

## Setup

> Tested on **Ubuntu 24.04 LTS**, **macOS** and **Windows 11 (WSL)**.

### 1. Install Dependencies

#### Podman

Install [Podman](https://podman.io/docs/installation). For desktop environments, [Podman Desktop](https://podman-desktop.io/downloads) is also recommended for easier container management.

Install `podman-compose` (used by support scripts):

```bash
pip3 install podman-compose
```

#### Python & uv

This project requires Python. Dependencies are managed with [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once installed, create the virtual environment and install all dependencies:

```bash
cd inventory
uv sync
```

#### Frontend Tools *(Development Only)*

Only required if building and running the frontend manually on the host machine:

```bash
# Install npm: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
curl -fsSL https://bun.sh/install | bash   # Install bun (follow PATH instructions at end)
# Install svelte-kit: https://svelte.dev/docs/kit/introduction
bun install -D vite
```

> ⚠️ After installing bun, make sure to update your `PATH` as instructed by the installer.

---

### 2. First-Time Setup

#### 2.1 Run the Installer

The installer pre-compiles configuration files, builds all Podman images, and launches all containers:

```bash
uv run install.py
```

#### 2.2 First Time Log-in

On first startup a default user is created by the system.


| Username | **admin** |
| ---| ---|
| Password | **admin** |

Once the first admin user is created, additional users can be managed within the app under **Settings → User Settings**

:warning: Make sure to remove the initial admin user once that setup is completed! 

#### User Privilege Levels

| Privilege         | GUEST | REPORTER | DEVELOPER | MAINTAINER | OWNER |
| ----------------- | :---: | :------: | :-------: | :--------: | :---: |
| **Add Item**      |       |          | ✅        | ✅         | ✅    |
| **Delete Item**   |       |          | ✅        | ✅         | ✅    |
| **Modify Item**   |       |          | ✅        | ✅         | ✅    |
| **Export to CSV** |       | ✅       | ✅        | ✅         | ✅    |
| **Add User**      |       |          |           | ✅         | ✅    |

---

## Manual Operation (for Developers)

### Running the Frontend

#### Configure and Build

Set the correct IP addresses for the server and inventory services in `app.env`, then build:

```bash
cd app
bun run build
```

Start the built server manually:

```bash
bun run build/index.js
```

#### Development Mode

To build and run the frontend in development mode with hot-reload:

```bash
cd app
bun run dev
```

---

## Browser Requirements

### Camera Access

Any browser will block camera access unless the app is served over **HTTPS** or accessed via **localhost**.

### Label Printing (Web Bluetooth)

The printer connection requires Web Bluetooth, which has limited browser support:

| Browser / Platform           | Supported?         |
| ---------------------------- | ------------------ |
| Chrome (desktop)             | ✅ Yes             |
| Chrome on Android            | ✅ Yes             |
| localhost                    | ✅ Yes             |
| Edge (Chromium)              | ⚠️ Partial         |
| Firefox                      | ❌ No              |
| Safari (Mac / iOS)           | ❌ No              |
| Any browser in an iframe     | ❌ No*             |
| Over `http://` URLs          | ❌ No              |

*Unless special flags are set.

To enable Web Bluetooth in Chrome, navigate to:

```
chrome://flags/#enable-web-bluetooth
```

---

## Data Reference

### Item Metadata

| Field                    | Description                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| **ID**                   | Unique identifier, auto-managed by the database. Read-only.                                     |
| **Name**                 | Item name. Does not need to be unique.                                                          |
| **Description**          | Detailed description of the item.                                                               |
| **Manufacturer**         | Manufacturer name.                                                                              |
| **Manufacturer Link**    | Link to the manufacturer's product page.                                                        |
| **Manufacturer Location**| Location of the manufacturer.                                                                   |
| **Details**              | Manufacturer or miscellaneous details.                                                          |
| **Image**                | Item image (stored as PNG outside the database; database holds a hashed filename).              |
| **Check-out Status**     | Boolean flag — `true` if the item is currently checked out.                                     |
| **Check-out Date**       | Date and time the item was checked out.                                                         |
| **Check-out PoC**        | The person responsible for the item while it is checked out.                                    |
| **Date Added**           | Date the item was added to the database. Auto-managed.                                          |
| **Tags**                 | Semicolon-separated tags for flexible searching.                                                |
| **Type**                 | Item type/category.                                                                             |
| **Color**                | Product colour.                                                                                 |
| **Product Use**          | Intended use of the product.                                                                    |
| **Material**             | Product material.                                                                               |
| **Storage Location**     | ID of the storage location where this item is kept.                                             |

### Storage Location Data

Storage locations are tracked in a separate table. Each item maps to a single storage location, but each storage location can hold multiple items. The relationship is recorded via the **Storage Location** field on each item.

---

## Hardware

Inventory is fully containerised and can run on any system capable of running Podman containers. It has been developed and tested with:

- **BMAX mini PC** running Ubuntu Desktop 24.04.1 (also tested on macOS Tahoe and Windows 11)
- **USB webcam** *(optional — any device camera works)*
- **Niimbot D110** label printer for QR code labels

The web app runs on any device with a browser and has been tested on desktops, laptops, tablets, and smartphones. For full functionality (camera + Bluetooth printing), **Google Chrome** is required. Some Apple devices do not support Web Bluetooth and cannot print labels.