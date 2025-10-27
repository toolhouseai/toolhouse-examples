"""
Stripe Integration Module for Invoice Processing

This module provides helper functions and classes for Stripe operations
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import stripe

logger = logging.getLogger(__name__)


class StripeInvoiceManager:
    """Manager for Stripe invoice operations"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe manager"""
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        stripe.api_key = self.api_key

    def create_customer(self, name: str, email: str, **kwargs) -> stripe.Customer:
        """Create a new Stripe customer"""
        customer_data = {
            "name": name,
            "email": email,
            "metadata": {
                "created_by": "invoice_processing_agent",
                "created_at": datetime.now().isoformat()
            }
        }

        # Add optional fields
        if "address" in kwargs:
            customer_data["address"] = kwargs["address"]
        if "phone" in kwargs:
            customer_data["phone"] = kwargs["phone"]

        return stripe.Customer.create(**customer_data)

    def get_or_create_customer(self, email: str, name: str, **kwargs) -> stripe.Customer:
        """Get existing customer or create new one"""
        # Search for existing customer
        customers = stripe.Customer.list(email=email, limit=1)

        if customers.data:
            return customers.data[0]

        return self.create_customer(name, email, **kwargs)

    def create_product(self, name: str, description: str = "") -> stripe.Product:
        """Create a Stripe product"""
        return stripe.Product.create(
            name=name,
            description=description,
            metadata={
                "created_by": "invoice_processing_agent"
            }
        )

    def create_price(self, product_id: str, unit_amount: int, currency: str = "usd") -> stripe.Price:
        """Create a price for a product"""
        return stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,
            currency=currency
        )

    def create_invoice_item(
        self,
        customer_id: str,
        description: str,
        amount: float,
        currency: str = "usd",
        quantity: int = 1
    ) -> stripe.InvoiceItem:
        """Create an invoice item"""
        return stripe.InvoiceItem.create(
            customer=customer_id,
            description=description,
            unit_amount=int(amount * 100),  # Convert to cents
            currency=currency,
            quantity=quantity
        )

    def create_invoice(
        self,
        customer_id: str,
        line_items: List[Dict[str, Any]],
        days_until_due: int = 30,
        auto_send: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Invoice:
        """
        Create a complete invoice with line items

        Args:
            customer_id: Stripe customer ID
            line_items: List of line items with description, amount, quantity
            days_until_due: Payment terms
            auto_send: Whether to automatically send the invoice
            metadata: Additional metadata

        Returns:
            Created Stripe invoice
        """
        # Create invoice
        invoice_data = {
            "customer": customer_id,
            "collection_method": "send_invoice",
            "days_until_due": days_until_due,
            "metadata": metadata or {}
        }

        invoice = stripe.Invoice.create(**invoice_data)

        # Add line items
        for item in line_items:
            stripe.InvoiceItem.create(
                customer=customer_id,
                invoice=invoice.id,
                description=item["description"],
                unit_amount=int(item["unit_amount"] * 100),
                quantity=item.get("quantity", 1),
                currency=item.get("currency", "usd").lower()
            )

        # Finalize invoice
        invoice = stripe.Invoice.finalize_invoice(invoice.id)

        # Send if requested
        if auto_send:
            invoice = stripe.Invoice.send_invoice(invoice.id)

        return invoice

    def retrieve_invoice(self, invoice_id: str) -> stripe.Invoice:
        """Retrieve an invoice by ID"""
        return stripe.Invoice.retrieve(invoice_id)

    def list_invoices(
        self,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[stripe.Invoice]:
        """List invoices with filters"""
        params = {"limit": limit}

        if customer_id:
            params["customer"] = customer_id
        if status:
            params["status"] = status

        invoices = stripe.Invoice.list(**params)
        return invoices.data

    def pay_invoice(self, invoice_id: str, payment_method: Optional[str] = None) -> stripe.Invoice:
        """Pay an invoice"""
        if payment_method:
            return stripe.Invoice.pay(invoice_id, payment_method=payment_method)
        return stripe.Invoice.pay(invoice_id)

    def void_invoice(self, invoice_id: str) -> stripe.Invoice:
        """Void an invoice"""
        return stripe.Invoice.void_invoice(invoice_id)

    def send_invoice_reminder(self, invoice_id: str) -> stripe.Invoice:
        """Send a reminder for an invoice"""
        return stripe.Invoice.send_invoice(invoice_id)

    def get_invoice_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Get detailed payment status of an invoice"""
        invoice = self.retrieve_invoice(invoice_id)

        return {
            "invoice_id": invoice.id,
            "number": invoice.number,
            "status": invoice.status,
            "paid": invoice.paid,
            "amount_due": invoice.amount_due / 100,
            "amount_paid": invoice.amount_paid / 100,
            "amount_remaining": invoice.amount_remaining / 100,
            "currency": invoice.currency,
            "created": datetime.fromtimestamp(invoice.created).isoformat(),
            "due_date": datetime.fromtimestamp(invoice.due_date).isoformat() if invoice.due_date else None,
            "hosted_invoice_url": invoice.hosted_invoice_url,
            "invoice_pdf": invoice.invoice_pdf
        }

    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.PaymentIntent:
        """Create a payment intent for manual payment processing"""
        params = {
            "amount": int(amount * 100),
            "currency": currency,
            "metadata": metadata or {}
        }

        if customer_id:
            params["customer"] = customer_id

        return stripe.PaymentIntent.create(**params)

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> stripe.Subscription:
        """Create a subscription for recurring billing"""
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata=metadata or {}
        )

    def list_webhook_events(self, limit: int = 10) -> List[stripe.Event]:
        """List recent webhook events"""
        events = stripe.Event.list(limit=limit)
        return events.data


class InvoiceValidator:
    """Validator for invoice data before sending to Stripe"""

    @staticmethod
    def validate_customer_data(customer: Dict[str, Any]) -> bool:
        """Validate customer data"""
        required_fields = ["name", "email"]

        for field in required_fields:
            if field not in customer or not customer[field]:
                raise ValueError(f"Missing required customer field: {field}")

        # Validate email format
        email = customer["email"]
        if "@" not in email or "." not in email.split("@")[1]:
            raise ValueError(f"Invalid email format: {email}")

        return True

    @staticmethod
    def validate_line_items(line_items: List[Dict[str, Any]]) -> bool:
        """Validate line items"""
        if not line_items:
            raise ValueError("Invoice must have at least one line item")

        for i, item in enumerate(line_items):
            if "description" not in item or not item["description"]:
                raise ValueError(f"Line item {i} missing description")

            if "unit_amount" not in item or item["unit_amount"] <= 0:
                raise ValueError(f"Line item {i} has invalid amount")

            if "quantity" in item and item["quantity"] <= 0:
                raise ValueError(f"Line item {i} has invalid quantity")

        return True

    @staticmethod
    def validate_invoice_data(invoice_data: Dict[str, Any]) -> bool:
        """Validate complete invoice data"""
        # Validate customer
        if "customer" not in invoice_data:
            raise ValueError("Invoice missing customer data")

        InvoiceValidator.validate_customer_data(invoice_data["customer"])

        # Validate line items
        if "line_items" not in invoice_data:
            raise ValueError("Invoice missing line items")

        InvoiceValidator.validate_line_items(invoice_data["line_items"])

        # Validate amounts
        if "total" in invoice_data and invoice_data["total"] <= 0:
            raise ValueError("Invoice total must be positive")

        return True


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }

    symbol = symbols.get(currency.upper(), currency.upper())
    return f"{symbol}{amount:,.2f}"


def calculate_invoice_total(line_items: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate invoice totals from line items"""
    subtotal = sum(item["unit_amount"] * item.get("quantity", 1) for item in line_items)
    tax = 0  # Calculate tax if needed
    total = subtotal + tax

    return {
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }
