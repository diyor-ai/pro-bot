# Pro Bot - Telegram E-commerce Bot

A multilingual Telegram bot for e-commerce order management with Google Sheets integration.

## Features

- **Multilingual Support**: Uzbek, Russian, and English languages
- **Product Catalog**: Browse products by category with search functionality
- **Order Management**: Complete order flow with customer details collection
- **Admin Panel**: Order tracking, status updates, and statistics
- **Google Sheets Integration**: Automatic order and customer data storage
- **Fuzzy Search**: Smart product search using rapidfuzz algorithm
- **Phone Validation**: Automatic phone number formatting for Uzbekistan (+998)

## Project Structure

```
pro-bot/
├── bot.py              # Main entry point and handlers
├── config.py           # Configuration and environment variables
├── sheets.py           # Google Sheets integration
├── keyboards.py        # Telegram inline keyboard builders
├── handlers/           # Modular handler components
│   ├── admin.py        # Admin panel handlers
│   ├── catalog.py      # Product catalog handlers
│   ├── order.py        # Order flow handlers
│   ├── search.py       # Search functionality
│   └── start.py        # Start and language selection
├── locales/            # Translation files
│   ├── en.json
│   ├── ru.json
│   └── uz.json
├── credentials.json    # Google Service Account credentials
└── requirements.txt    # Python dependencies
```

## Prerequisites

- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Google Cloud Service Account with Sheets API access
- Google Spreadsheet with product and order data

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pro-bot
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file:
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   ADMIN_CHAT_ID=your_admin_chat_id
   ADMIN_IDS=123456789,987654321
   SHOP_NAME=Your Shop Name
   SHEET_NAME=Your Spreadsheet Name
   ```

4. **Set up Google credentials**
   - Place your `credentials.json` (Google Service Account) in the project root
   - Share your Google Sheet with the service account email

## Google Sheets Setup

The bot expects the following sheet structure:

### Mahsulotlar (Products) - Sheet1
| ID | Nomi | Narxi | Kategoriya | Tavsif | Rasm_URL | Mavjud |

### Buyurtmalar (Orders)
| ID | Sana | Mahsulot | Narx | Kategoriya | Ism | Telefon | Manzil | Til | Status | User_ID |

### Users
| User_ID | Ism | Telefon | Til | Birinchi_sana | Oxirgi_sana | Buyurtmalar_soni |

## Usage

### Start the bot
```bash
python bot.py
```

### Available Commands
- `/start` - Start the bot and choose language
- `/admin` - Access admin panel (admin users only)

### User Flow
1. Select language
2. Browse products or search
3. Select product and confirm purchase
4. Enter name, phone, and address
5. Confirm order

### Admin Features
- View new orders
- Update order status (Processing, Delivering, Delivered)
- View statistics (total orders, today's orders, revenue)
- Broadcast messages to users

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Bot token from BotFather | Required |
| `ADMIN_CHAT_ID` | Telegram chat ID for admin notifications | Required |
| `ADMIN_IDS` | Comma-separated admin user IDs | Required |
| `SHOP_NAME` | Shop display name | "Pro Shop" |
| `SHEET_NAME` | Google Spreadsheet name | "Mahsulotlar" |
| `CACHE_TTL` | Product cache duration (seconds) | 60 |
| `FUZZY_THRESHOLD` | Search match threshold | 65 |

## Deployment

### Using Gunicorn (Production)
```bash
gunicorn bot:main
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## License

MIT License