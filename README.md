# nosh_instacart_backend

A lightweight Flask backend that acts as a **secure server-to-server proxy** for the [Instacart Developer Platform API](https://docs.instacart.com/developer_platform). It exposes a single endpoint your client app can call to generate a shareable Instacart shopping list URL — without ever exposing your API key to the frontend.

---

## Project Structure

```
nosh_backend/
├── instacart_routes.py   # Flask Blueprint — all Instacart route logic
├── main.py               # App factory — imports and registers the Blueprint
├── requirements.txt      # Python dependencies
├── .env.example          # Credential template (safe to commit)
├── .env                  # Your real secrets (git-ignored)
└── .gitignore
```

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```env
INSTACART_API_KEY=your_instacart_api_key_here
```

> **Never commit `.env` to version control.** It is listed in `.gitignore`.

### 4. Run the development server

```bash
python main.py
```

The API will be available at `http://127.0.0.1:5000`.

---

## API Reference

### `POST /api/generate-instacart-list`

Generates a shareable Instacart shopping list and returns its URL.

**Request body**

```json
{
  "title": "Weekly Groceries",
  "link_type": "shopping_list",
  "line_items": [
    { "name": "Apples", "quantity": 6, "unit": "each" },
    { "name": "Milk",   "quantity": 1, "unit": "gallon" }
  ]
}
```

| Field        | Type   | Required | Default           | Description                          |
|--------------|--------|----------|-------------------|--------------------------------------|
| `title`      | string | ✅        | —                 | Name of the shopping list            |
| `link_type`  | string | ❌        | `shopping_list`   | Instacart link type                  |
| `line_items` | array  | ✅        | —                 | Items to add (see fields below)      |

Each `line_items` object:

| Field      | Type           | Required | Description              |
|------------|----------------|----------|--------------------------|
| `name`     | string         | ✅        | Product name             |
| `quantity` | number         | ✅        | Amount                   |
| `unit`     | string         | ✅        | Unit of measure (see below) |

#### Supported Units
The `unit` field must match one of Instacart's official measurement units (case-insensitive). Common values include:
- **Countable:** `each`, `bunch`, `can`, `head`, `package`, `packet`
- **Volume:** `cup`, `gal`, `fl oz`, `ml`, `l`, `pt`, `qt`, `tbsp`, `tsp`
- **Mass:** `oz`, `lb`, `g`, `kg`
- **Size:** `small`, `medium`, `large`

If an invalid unit is provided, the API returns a `400 Bad Request` with fuzzy-matched suggestions (e.g., if you send "gallonx", it suggests "gallon").

**Success response — `200 OK`**

```json
{
  "products_link_url": "https://customers.dev.instacart.tools/store/shopping_lists/..."
}
```

**Error responses**

| Status | Cause                                      |
|--------|--------------------------------------------|
| `400`  | Missing or invalid request fields          |
| `500`  | `INSTACART_API_KEY` not configured         |
| `502`  | Upstream Instacart API error or timeout    |

---

## Adding to an Existing Flask App

The Blueprint is designed to be dropped into any Flask app:

```python
from dotenv import load_dotenv
load_dotenv()

from instacart_routes import instacart_bp

app.register_blueprint(instacart_bp)
```

---

## Dependencies

| Package        | Purpose                              |
|----------------|--------------------------------------|
| `flask`        | Web framework                        |
| `requests`     | HTTP client for the Instacart API    |
| `python-dotenv`| Loads secrets from `.env`            |
