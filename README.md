# Butter & Crumble Preorder Bot

A Python-based automation tool designed to monitor the Butter and Crumble shop on Hotplate and check if order buttons are active.

## Setup Instructions

### 1. Install Python Virtual Environment Support

On Ubuntu/Debian WSL:
```bash
sudo apt install python3.12-venv
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the Bot

```bash
python main.py
```

## Testing

Run all tests:
```bash
pytest
```

Run with visible browser (debug mode):
```bash
pytest --headed
```

## Features

- ✅ Checks if Order button is active on Hotplate
- ✅ Stealth mode to avoid bot detection
- ✅ Configurable via environment variables
- ✅ Comprehensive logging with timestamps
- ✅ Type-hinted Python code

## Next Steps

This initial version checks if the Order button is active. Future enhancements will include:
- Automated ordering at specific drop times
- Cart management
- Multiple item handling
- Retry logic with exponential backoff
