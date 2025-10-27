# 🏗️ Architecture - Invoice Processing Agent

Technical architecture and design documentation.

## 📋 System Overview

The Invoice Processing Agent is a modular AI-powered system that combines:
- **Anthropic Claude 3.5 Sonnet** - Natural language understanding and extraction
- **Toolhouse SDK** - Tool execution and web scraping capabilities
- **Stripe API** - Payment processing and invoice management

## 🎯 Design Principles

1. **Modularity** - Separate concerns into distinct modules
2. **Extensibility** - Easy to add new data sources and payment providers
3. **Reliability** - Comprehensive error handling and validation
4. **Testability** - High test coverage with unit and integration tests
5. **Security** - Secure API key management and data handling

## 🔧 Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Invoice Source                         │
│         (Text, URL, PDF, Email, etc.)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            InvoiceProcessingAgent                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │         AI-Powered Extraction                    │   │
│  │  - Claude 3.5 Sonnet (LLM)                       │   │
│  │  - Toolhouse Tools (Web scraper, etc.)          │   │
│  │  - JSON Schema Validation                       │   │
│  └─────────────────────────────────────────────────┘   │
│                     │                                    │
│                     ▼                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Data Validation                          │   │
│  │  - InvoiceValidator                             │   │
│  │  - Field Validation                             │   │
│  │  - Business Rules                               │   │
│  └─────────────────────────────────────────────────┘   │
│                     │                                    │
│                     ▼                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Stripe Integration                       │   │
│  │  - StripeInvoiceManager                         │   │
│  │  - Customer Management                          │   │
│  │  - Invoice Creation                             │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Stripe Platform                         │
│  - Invoice Storage                                       │
│  - Payment Processing                                    │
│  - Customer Management                                   │
└─────────────────────────────────────────────────────────┘
```

## 📦 Module Structure

```
invoice-processing-agent/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── invoice_agent.py         # Main agent orchestration
│   └── stripe_integration.py   # Stripe API wrapper
├── tests/
│   ├── __init__.py
│   ├── test_invoice_agent.py   # Agent tests
│   └── test_stripe_integration.py
├── config/
│   ├── requirements.txt         # Dependencies
│   └── .env.example            # Environment template
└── docs/
    ├── README.md               # Main documentation
    ├── SETUP.md               # Setup instructions
    ├── EXAMPLES.md            # Usage examples
    └── ARCHITECTURE.md        # This file
```

## 🧩 Core Components

### 1. InvoiceProcessingAgent

**Responsibility**: Main orchestration and AI-powered extraction

**Key Methods**:
- `extract_invoice_data(source, source_type)` - Extract data using AI
- `create_stripe_invoice(invoice_data)` - Create Stripe invoice
- `process_invoice(source, source_type, auto_send)` - End-to-end workflow
- `check_invoice_status(invoice_id)` - Monitor payment status
- `list_unpaid_invoices(limit)` - List outstanding invoices

**Dependencies**:
- Anthropic Claude API
- Toolhouse SDK
- StripeInvoiceManager

**Flow**:
```
Input → AI Extraction → Validation → Stripe Creation → Output
```

### 2. StripeInvoiceManager

**Responsibility**: Stripe API operations and customer management

**Key Methods**:
- `create_customer(name, email, **kwargs)` - Create customer
- `get_or_create_customer(email, name)` - Idempotent customer creation
- `create_invoice(customer_id, line_items, ...)` - Create invoice
- `retrieve_invoice(invoice_id)` - Get invoice details
- `get_invoice_payment_status(invoice_id)` - Payment status

**Features**:
- Automatic customer deduplication
- Idempotent operations
- Comprehensive error handling
- Metadata tracking

### 3. InvoiceValidator

**Responsibility**: Data validation before Stripe operations

**Validations**:
- Customer data (name, email format)
- Line items (description, amounts, quantities)
- Invoice totals
- Currency codes
- Date formats

**Pattern**:
```python
try:
    InvoiceValidator.validate_invoice_data(data)
    # Proceed with Stripe operations
except ValueError as e:
    # Handle validation error
```

## 🔄 Data Flow

### Invoice Processing Workflow

```
1. User provides invoice source (text/URL/PDF)
   ↓
2. Agent sends to Claude with Toolhouse tools
   ↓
3. Claude analyzes and extracts structured data
   ↓
4. Toolhouse executes web scraping if needed
   ↓
5. Agent parses JSON response
   ↓
6. InvoiceValidator validates data
   ↓
7. StripeInvoiceManager creates customer (if needed)
   ↓
8. StripeInvoiceManager creates invoice items
   ↓
9. Stripe finalizes invoice
   ↓
10. (Optional) Send invoice to customer
    ↓
11. Return result to user
```

### Data Models

**Invoice Data Schema**:
```python
{
    "invoice_number": str,
    "invoice_date": str,  # YYYY-MM-DD
    "due_date": str,      # YYYY-MM-DD
    "customer": {
        "name": str,
        "email": str,
        "address": str
    },
    "line_items": [
        {
            "description": str,
            "quantity": int,
            "unit_price": float,
            "amount": float
        }
    ],
    "subtotal": float,
    "tax": float,
    "total": float,
    "currency": str
}
```

## 🔐 Security Architecture

### API Key Management

```
Environment Variables (.env)
    ↓
Application reads at startup
    ↓
Keys stored in memory (not logged)
    ↓
Used for API authentication
```

**Best Practices**:
- Never commit `.env` to version control
- Use separate keys for dev/test/prod
- Rotate keys regularly
- Use restricted Stripe keys when possible

### Data Handling

- **No persistent storage** of sensitive data
- **In-memory processing** only
- **Stripe handles** payment card data
- **Metadata** for tracking, not sensitive data

## 🧪 Testing Strategy

### Test Pyramid

```
        ┌───────────┐
        │Integration│ (Few)
        │   Tests   │
        └─────┬─────┘
      ┌───────┴───────┐
      │     Unit      │ (Many)
      │     Tests     │
      └───────────────┘
```

### Test Coverage

- **Unit Tests**: Individual methods and functions
- **Integration Tests**: Component interactions
- **Mocking**: External APIs (Stripe, Anthropic, Toolhouse)
- **Fixtures**: Reusable test data

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_invoice_agent.py -v
```

## 🚀 Performance Considerations

### Latency

**Typical Processing Time**:
- AI Extraction: 2-5 seconds
- Stripe Invoice Creation: 1-2 seconds
- **Total**: ~3-7 seconds per invoice

**Optimization Strategies**:
- Use Claude's streaming for real-time feedback
- Batch Stripe operations when possible
- Cache customer lookups
- Parallel processing for multiple invoices

### Rate Limits

**Anthropic**:
- Tier-based rate limits
- Retry with exponential backoff

**Toolhouse**:
- Check tier limits
- Monitor usage

**Stripe**:
- 100 requests/second (test mode)
- 1000 requests/second (live mode)
- Implement rate limiting for bulk operations

## 🔧 Configuration Management

### Environment-Based Config

```python
# Development
STRIPE_API_KEY=sk_test_...
LOG_LEVEL=DEBUG

# Production
STRIPE_API_KEY=sk_live_...
LOG_LEVEL=INFO
```

### Feature Flags

Potential features:
- Auto-send invoices
- Payment reminders
- Multi-currency support
- Webhook handling

## 📈 Extensibility

### Adding New Data Sources

```python
# In invoice_agent.py
def extract_from_pdf(pdf_path: str) -> Dict:
    """Extract from PDF using Toolhouse"""
    # Implementation
    pass

def extract_from_email(email_content: str) -> Dict:
    """Extract from email"""
    # Implementation
    pass
```

### Supporting Multiple Payment Providers

```python
# Abstract payment interface
class PaymentProvider(ABC):
    @abstractmethod
    def create_invoice(self, data): pass

    @abstractmethod
    def check_status(self, invoice_id): pass

# Implementations
class StripeProvider(PaymentProvider): ...
class PayPalProvider(PaymentProvider): ...
class SquareProvider(PaymentProvider): ...
```

## 🐛 Error Handling Strategy

### Error Categories

1. **User Input Errors**: Invalid invoice data
2. **API Errors**: Stripe/Anthropic/Toolhouse failures
3. **Network Errors**: Connectivity issues
4. **System Errors**: Unexpected exceptions

### Error Handling Pattern

```python
try:
    result = process_invoice(source)
except ValidationError as e:
    # User-facing error
    return {"error": str(e), "type": "validation"}
except APIError as e:
    # Retry-able error
    return {"error": str(e), "type": "api", "retry": True}
except Exception as e:
    # Log and return generic error
    logger.exception("Unexpected error")
    return {"error": "Internal error", "type": "system"}
```

## 📊 Monitoring & Observability

### Logging

```python
# Structured logging
logger.info("Invoice processed", extra={
    "invoice_id": invoice_id,
    "customer": customer_email,
    "amount": total,
    "duration_ms": duration
})
```

### Metrics to Track

- Invoice processing success/failure rate
- Average processing time
- API error rates
- Invoice payment completion rate

### Production Monitoring

Recommended tools:
- **Sentry** - Error tracking
- **DataDog** - Application monitoring
- **Stripe Dashboard** - Payment monitoring
- **CloudWatch/Logs** - Infrastructure logging

## 🔮 Future Enhancements

1. **Multi-language support** - Process invoices in multiple languages
2. **OCR integration** - Extract from invoice images
3. **Email integration** - Process invoices from email
4. **Recurring invoices** - Automated subscription billing
5. **Advanced reporting** - Analytics and insights
6. **Webhook handling** - Real-time payment notifications
7. **Multi-currency** - Support for international payments
8. **Tax calculation** - Automated tax computation

---

**Last Updated**: October 2025
**Version**: 1.0.0
