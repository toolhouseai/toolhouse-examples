# 🧾 Invoice Processing Agent with Stripe Integration

An intelligent AI agent built with Toolhouse and Stripe that automates invoice processing workflows.

## 🚀 Features

### 📄 Invoice Data Extraction
- Extract invoice data from multiple sources (text, PDFs, web pages, emails)
- AI-powered field detection and validation
- Support for various invoice formats
- Automatic currency and amount parsing

### 💳 Stripe Integration
- Automatic customer creation/retrieval
- Invoice generation with line items
- Payment processing automation
- Invoice status tracking
- Payment reminders and notifications

### 🤖 AI-Powered Automation
- Intelligent data extraction using Claude 3.5 Sonnet
- Toolhouse tools for web scraping and data processing
- Natural language interaction
- Error handling and validation

### 🔄 Workflow Automation
- End-to-end invoice processing
- Automated follow-ups for unpaid invoices
- Payment status monitoring
- Receipt generation

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip or poetry package manager
- Active accounts for:
  - [Anthropic](https://console.anthropic.com/)
  - [Toolhouse](https://app.toolhouse.ai/)
  - [Stripe](https://dashboard.stripe.com/)

### Setup Instructions

1. **Clone the repository**
```bash
cd invoice-processing-agent
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r config/requirements.txt
```

4. **Configure environment variables**
```bash
cp config/.env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_key_here
TOOLHOUSE_API_KEY=your_toolhouse_key_here
STRIPE_API_KEY=your_stripe_test_key_here
```

5. **Verify installation**
```bash
python src/invoice_agent.py
```

## 🎯 Usage

### Interactive Mode

Run the agent in interactive mode:

```bash
python src/invoice_agent.py
```

Available commands:
1. **Process invoice from text** - Paste invoice text directly
2. **Process invoice from URL** - Extract from web page
3. **Check invoice status** - Monitor payment status
4. **List unpaid invoices** - View outstanding invoices

### Programmatic Usage

```python
from invoice_agent import InvoiceProcessingAgent

# Initialize agent
agent = InvoiceProcessingAgent()

# Process invoice from text
invoice_text = """
Invoice #INV-001
Date: 2025-10-27
Due: 2025-11-27

Customer: John Doe
Email: john@example.com

Items:
- Web Development Services: $1,500
- Hosting (3 months): $150

Total: $1,650
"""

result = agent.process_invoice(
    source=invoice_text,
    source_type="text",
    auto_send=True
)

print(result)
```

### Extract Invoice from URL

```python
# Process invoice from web page
result = agent.process_invoice(
    source="https://example.com/invoice/123",
    source_type="url",
    auto_send=False
)
```

### Check Invoice Status

```python
# Monitor invoice payment status
status = agent.check_invoice_status("inv_1234567890")
print(f"Status: {status['status']}")
print(f"Amount Due: ${status['amount_due']}")
```

### List Unpaid Invoices

```python
# Get all unpaid invoices
unpaid = agent.list_unpaid_invoices(limit=10)
for invoice in unpaid:
    print(f"{invoice['number']}: ${invoice['amount_due']}")
```

## 🏗️ Architecture

### Components

1. **InvoiceProcessingAgent** (`src/invoice_agent.py`)
   - Main agent orchestration
   - AI-powered data extraction
   - Workflow management

2. **StripeInvoiceManager** (`src/stripe_integration.py`)
   - Stripe API operations
   - Customer management
   - Invoice creation and tracking

3. **InvoiceValidator** (`src/stripe_integration.py`)
   - Data validation
   - Error checking
   - Format verification

### Workflow

```
┌─────────────────┐
│  Invoice Source │
│  (Text/URL/PDF) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Extraction  │
│   (Toolhouse)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stripe Invoice  │
│    Creation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send Invoice   │
│  (Optional)     │
└─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes |
| `TOOLHOUSE_API_KEY` | Toolhouse API key | Yes |
| `STRIPE_API_KEY` | Stripe API key (test/live) | Yes |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | No |
| `LOG_LEVEL` | Logging level (INFO/DEBUG) | No |

### Stripe Configuration

For development:
- Use **test mode** API keys (`sk_test_...`)
- Test with [Stripe test cards](https://stripe.com/docs/testing)
- View invoices in [Stripe Dashboard](https://dashboard.stripe.com/test/invoices)

For production:
- Use **live mode** API keys (`sk_live_...`)
- Configure webhooks for payment events
- Set up proper error handling

## 📊 Example Invoice Formats

### Text Format
```
Invoice #: INV-2025-001
Date: October 27, 2025
Due Date: November 27, 2025

Bill To:
John Doe
john.doe@example.com
123 Main St, City, State 12345

Description                 Qty    Price     Total
Web Development             1      $2,500    $2,500
Monthly Maintenance (3mo)   3      $200      $600
Domain Registration         1      $15       $15

Subtotal:                             $3,115
Tax (8%):                             $249.20
Total:                                $3,364.20
```

### JSON Format
```json
{
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-10-27",
  "due_date": "2025-11-27",
  "customer": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "address": "123 Main St, City, State 12345"
  },
  "line_items": [
    {
      "description": "Web Development",
      "quantity": 1,
      "unit_price": 2500.00,
      "amount": 2500.00
    },
    {
      "description": "Monthly Maintenance (3mo)",
      "quantity": 3,
      "unit_price": 200.00,
      "amount": 600.00
    }
  ],
  "subtotal": 3115.00,
  "tax": 249.20,
  "total": 3364.20,
  "currency": "USD"
}
```

## 🧪 Testing

Run tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 🔐 Security

- **Never commit** API keys to version control
- Use **test mode** keys for development
- Validate all input data
- Implement rate limiting for production
- Use HTTPS for all API calls
- Monitor webhook signatures

## 🐛 Troubleshooting

### Common Issues

**Issue**: "API key not found"
- **Solution**: Check `.env` file and ensure all keys are set

**Issue**: "Stripe customer creation failed"
- **Solution**: Verify email format and Stripe API key

**Issue**: "Invoice extraction returned no data"
- **Solution**: Ensure invoice source is accessible and properly formatted

**Issue**: "Tool execution timeout"
- **Solution**: Check Toolhouse API key and network connectivity

## 📚 Resources

- [Toolhouse Documentation](https://docs.toolhouse.ai/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Example Repository](https://github.com/toolhouseai/toolhouse-examples)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Support

- [Toolhouse Discord](https://discord.gg/toolhouse)
- [GitHub Issues](https://github.com/your-repo/issues)
- Email: support@example.com

## 🎯 Roadmap

- [ ] Support for more invoice formats (PDF, images)
- [ ] Multi-currency support
- [ ] Recurring invoice automation
- [ ] Advanced payment reminders
- [ ] Dashboard UI
- [ ] Batch invoice processing
- [ ] Integration with accounting software
- [ ] Mobile app

---

**Built with ❤️ using Toolhouse, Anthropic Claude, and Stripe**
