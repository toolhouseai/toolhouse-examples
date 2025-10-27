# 📚 Usage Examples - Invoice Processing Agent

Comprehensive examples for common invoice processing scenarios.

## 📋 Table of Contents

- [Basic Usage](#basic-usage)
- [Invoice Extraction](#invoice-extraction)
- [Stripe Operations](#stripe-operations)
- [Advanced Workflows](#advanced-workflows)
- [Error Handling](#error-handling)
- [Integration Examples](#integration-examples)

## 🚀 Basic Usage

### Example 1: Process Simple Text Invoice

```python
from src.invoice_agent import InvoiceProcessingAgent

# Initialize agent
agent = InvoiceProcessingAgent()

# Simple invoice text
invoice_text = """
Invoice #INV-2025-001
Date: October 27, 2025
Due: November 27, 2025

Bill To:
John Doe
john@example.com

Services:
Web Development - $2,500
Domain Registration - $15

Total: $2,515
"""

# Process invoice
result = agent.process_invoice(
    source=invoice_text,
    source_type="text",
    auto_send=False
)

# Check result
if result["success"]:
    print(f"✅ Invoice created: {result['stripe_invoice']['invoice_id']}")
    print(f"Amount: ${result['stripe_invoice']['amount_due']}")
    print(f"View: {result['stripe_invoice']['hosted_invoice_url']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 2: Extract from URL

```python
# Process invoice from web page
result = agent.process_invoice(
    source="https://example.com/invoices/123",
    source_type="url",
    auto_send=True  # Automatically send invoice
)

if result["success"]:
    print("Invoice extracted and sent!")
    print(f"Customer: {result['extracted_data']['customer']['email']}")
```

## 🔍 Invoice Extraction

### Example 3: Extract from Complex Invoice

```python
complex_invoice = """
ABC COMPANY INC.
123 Business St, City, ST 12345
Tax ID: 12-3456789

INVOICE

Invoice Number: INV-2025-1234
Invoice Date: 10/27/2025
Due Date: 11/27/2025
Payment Terms: Net 30

BILL TO:
Jane Smith
XYZ Corporation
456 Client Ave
City, ST 67890
jane.smith@xyzcorp.com

DESCRIPTION                    QTY    RATE      AMOUNT
─────────────────────────────────────────────────────
Website Design                  1    $3,500    $3,500.00
Logo Design                     1    $1,200    $1,200.00
Business Cards (1000)          10      $50      $500.00
Hosting (12 months)             1      $180     $180.00
─────────────────────────────────────────────────────

                           Subtotal:           $5,380.00
                          Tax (8%):             $430.40
                              Total:          $5,810.40

Payment due by: November 27, 2025
"""

# Extract and process
result = agent.process_invoice(complex_invoice, source_type="text")

# View extracted data
print("Extracted Invoice Data:")
print(f"Number: {result['extracted_data']['invoice_number']}")
print(f"Customer: {result['extracted_data']['customer']['name']}")
print(f"Total: ${result['extracted_data']['total']}")
print(f"\nLine Items:")
for item in result['extracted_data']['line_items']:
    print(f"  - {item['description']}: ${item['amount']}")
```

### Example 4: Extract from JSON

```python
import json

# Invoice in JSON format
invoice_json = {
    "invoice_number": "INV-2025-500",
    "invoice_date": "2025-10-27",
    "due_date": "2025-12-27",
    "customer": {
        "name": "Alice Johnson",
        "email": "alice@startup.com",
        "address": "789 Startup Blvd, Tech City, CA 94000"
    },
    "line_items": [
        {
            "description": "Monthly SaaS Subscription",
            "quantity": 12,
            "unit_price": 99.00,
            "amount": 1188.00
        },
        {
            "description": "Premium Support",
            "quantity": 12,
            "unit_price": 49.00,
            "amount": 588.00
        }
    ],
    "subtotal": 1776.00,
    "tax": 142.08,
    "total": 1918.08,
    "currency": "USD"
}

# Convert to text for processing
invoice_text = json.dumps(invoice_json, indent=2)

# Process
result = agent.process_invoice(invoice_text, source_type="text")
```

## 💳 Stripe Operations

### Example 5: Create Invoice Without Agent

```python
from src.stripe_integration import StripeInvoiceManager

# Initialize Stripe manager
stripe_manager = StripeInvoiceManager()

# Create or get customer
customer = stripe_manager.get_or_create_customer(
    email="client@example.com",
    name="New Client",
    phone="+1234567890"
)

# Define line items
line_items = [
    {
        "description": "Consulting Services (10 hours)",
        "unit_amount": 150.00,
        "quantity": 10,
        "currency": "usd"
    },
    {
        "description": "Project Management",
        "unit_amount": 500.00,
        "quantity": 1,
        "currency": "usd"
    }
]

# Create invoice
invoice = stripe_manager.create_invoice(
    customer_id=customer.id,
    line_items=line_items,
    days_until_due=30,
    auto_send=True,
    metadata={
        "project": "Website Redesign",
        "po_number": "PO-2025-123"
    }
)

print(f"Invoice created: {invoice.id}")
print(f"Number: {invoice.number}")
print(f"View: {invoice.hosted_invoice_url}")
```

### Example 6: Check Payment Status

```python
# Check invoice status
invoice_id = "inv_1234567890"

status = agent.check_invoice_status(invoice_id)

if status["paid"]:
    print("✅ Invoice is paid!")
else:
    print(f"⏳ Invoice status: {status['status']}")
    print(f"Amount due: ${status['amount_due']}")
    print(f"Due date: {status['due_date']}")
```

### Example 7: List Unpaid Invoices

```python
# Get all unpaid invoices
unpaid_invoices = agent.list_unpaid_invoices(limit=20)

print(f"Found {len(unpaid_invoices)} unpaid invoices:\n")

for invoice in unpaid_invoices:
    print(f"Invoice {invoice['number']}")
    print(f"  Customer: {invoice['customer_email']}")
    print(f"  Amount: ${invoice['amount_due']} {invoice['currency'].upper()}")
    print(f"  Due: {invoice['due_date']}")
    print()
```

## 🔄 Advanced Workflows

### Example 8: Batch Invoice Processing

```python
import os
import glob

# Process multiple invoice files
invoice_dir = "path/to/invoices/"
results = []

for file_path in glob.glob(os.path.join(invoice_dir, "*.txt")):
    with open(file_path, 'r') as f:
        invoice_text = f.read()

    print(f"Processing {file_path}...")

    result = agent.process_invoice(
        source=invoice_text,
        source_type="text",
        auto_send=False
    )

    results.append({
        "file": file_path,
        "result": result
    })

# Summary
successful = sum(1 for r in results if r['result']['success'])
print(f"\n✅ Successfully processed: {successful}/{len(results)}")
```

### Example 9: Recurring Invoice Automation

```python
from datetime import datetime, timedelta
import schedule
import time

def create_monthly_invoice():
    """Create monthly recurring invoice"""

    # Monthly service invoice
    invoice_data = {
        "invoice_number": f"MONTHLY-{datetime.now().strftime('%Y%m')}",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "customer": {
            "name": "Regular Client",
            "email": "client@company.com"
        },
        "line_items": [
            {
                "description": "Monthly Maintenance",
                "quantity": 1,
                "unit_price": 499.00,
                "amount": 499.00
            }
        ],
        "total": 499.00,
        "currency": "USD"
    }

    # Create invoice
    stripe_invoice = agent.create_stripe_invoice(invoice_data)

    # Send invoice
    import stripe
    stripe.Invoice.send_invoice(stripe_invoice['invoice_id'])

    print(f"✅ Monthly invoice created and sent: {stripe_invoice['invoice_number']}")

# Schedule monthly invoice
schedule.every().month.at("09:00").do(create_monthly_invoice)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Example 10: Invoice Reminders

```python
from datetime import datetime, timedelta

def send_payment_reminders():
    """Send reminders for invoices due soon"""

    # Get unpaid invoices
    unpaid = agent.list_unpaid_invoices(limit=50)

    for invoice in unpaid:
        # Parse due date
        due_date = datetime.fromisoformat(invoice['due_date'])
        days_until_due = (due_date - datetime.now()).days

        # Send reminder if due in 3 days or less
        if 0 < days_until_due <= 3:
            import stripe
            stripe.Invoice.send_invoice(invoice['invoice_id'])

            print(f"📧 Reminder sent for invoice {invoice['number']}")
            print(f"   Due in {days_until_due} days")

# Run daily
schedule.every().day.at("10:00").do(send_payment_reminders)
```

## ⚠️ Error Handling

### Example 11: Robust Error Handling

```python
def process_invoice_safely(invoice_text):
    """Process invoice with comprehensive error handling"""

    try:
        # Attempt processing
        result = agent.process_invoice(
            source=invoice_text,
            source_type="text",
            auto_send=False
        )

        if result["success"]:
            print("✅ Invoice processed successfully!")
            return result
        else:
            # Handle processing failure
            error = result.get("error", "Unknown error")
            stage = result.get("stage", "unknown")

            print(f"❌ Processing failed at {stage}: {error}")

            # Log error
            import logging
            logging.error(f"Invoice processing failed: {error}")

            return None

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

        # Log exception
        import logging
        logging.exception("Unexpected error during invoice processing")

        return None

# Usage
result = process_invoice_safely(invoice_text)
```

### Example 12: Validation Before Processing

```python
from src.stripe_integration import InvoiceValidator

def process_with_validation(invoice_data):
    """Validate before processing"""

    try:
        # Validate invoice data
        InvoiceValidator.validate_invoice_data(invoice_data)

        # Create Stripe invoice
        stripe_invoice = agent.create_stripe_invoice(invoice_data)

        print("✅ Invoice validated and created!")
        return stripe_invoice

    except ValueError as e:
        print(f"❌ Validation failed: {str(e)}")
        return None
```

## 🔗 Integration Examples

### Example 13: Webhook Handler (Flask)

```python
from flask import Flask, request
import stripe

app = Flask(__name__)

@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""

    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )

        # Handle invoice.paid event
        if event['type'] == 'invoice.paid':
            invoice = event['data']['object']

            print(f"✅ Invoice paid: {invoice['id']}")

            # Send thank you email, update database, etc.
            # ...

        # Handle invoice.payment_failed event
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']

            print(f"❌ Payment failed: {invoice['id']}")

            # Send payment failure notification
            # ...

        return {'status': 'success'}, 200

    except Exception as e:
        return {'error': str(e)}, 400

if __name__ == '__main__':
    app.run(port=5000)
```

### Example 14: API Endpoint (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class InvoiceRequest(BaseModel):
    invoice_text: str
    auto_send: bool = False

@app.post("/api/invoices/process")
async def process_invoice_endpoint(request: InvoiceRequest):
    """API endpoint to process invoices"""

    agent = InvoiceProcessingAgent()

    result = agent.process_invoice(
        source=request.invoice_text,
        source_type="text",
        auto_send=request.auto_send
    )

    if result["success"]:
        return {
            "status": "success",
            "invoice_id": result["stripe_invoice"]["invoice_id"],
            "invoice_number": result["stripe_invoice"]["invoice_number"],
            "amount_due": result["stripe_invoice"]["amount_due"],
            "url": result["stripe_invoice"]["hosted_invoice_url"]
        }
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.get("/api/invoices/{invoice_id}/status")
async def check_invoice_endpoint(invoice_id: str):
    """Check invoice status"""

    agent = InvoiceProcessingAgent()
    status = agent.check_invoice_status(invoice_id)

    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])

    return status
```

---

## 📝 Notes

- Always test with Stripe **test mode** keys first
- Use `auto_send=False` for testing
- Implement proper error handling in production
- Monitor API usage and rate limits
- Keep API keys secure

For more examples, check the [tests/](../tests/) directory.
