"""
Tests for Stripe Integration Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import stripe

from src.stripe_integration import (
    StripeInvoiceManager,
    InvoiceValidator,
    format_currency,
    calculate_invoice_total
)


class TestStripeInvoiceManager:
    """Test suite for StripeInvoiceManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        with patch.dict('os.environ', {'STRIPE_API_KEY': 'sk_test_123'}):
            return StripeInvoiceManager()

    @patch('stripe.Customer.create')
    def test_create_customer(self, mock_create, manager):
        """Test customer creation"""
        mock_customer = MagicMock()
        mock_customer.id = "cus_123"
        mock_create.return_value = mock_customer

        customer = manager.create_customer(
            name="John Doe",
            email="john@example.com"
        )

        assert customer.id == "cus_123"
        mock_create.assert_called_once()

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    def test_get_or_create_customer_existing(
        self,
        mock_create,
        mock_list,
        manager
    ):
        """Test getting existing customer"""
        mock_customer = MagicMock()
        mock_customer.id = "cus_existing"
        mock_list.return_value = MagicMock(data=[mock_customer])

        customer = manager.get_or_create_customer(
            email="existing@example.com",
            name="Existing User"
        )

        assert customer.id == "cus_existing"
        mock_create.assert_not_called()

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    def test_get_or_create_customer_new(
        self,
        mock_create,
        mock_list,
        manager
    ):
        """Test creating new customer"""
        mock_list.return_value = MagicMock(data=[])
        mock_customer = MagicMock()
        mock_customer.id = "cus_new"
        mock_create.return_value = mock_customer

        customer = manager.get_or_create_customer(
            email="new@example.com",
            name="New User"
        )

        assert customer.id == "cus_new"
        mock_create.assert_called_once()

    @patch('stripe.Invoice.create')
    @patch('stripe.InvoiceItem.create')
    @patch('stripe.Invoice.finalize_invoice')
    def test_create_invoice(
        self,
        mock_finalize,
        mock_item_create,
        mock_invoice_create,
        manager
    ):
        """Test invoice creation"""
        mock_invoice = MagicMock()
        mock_invoice.id = "inv_123"
        mock_invoice_create.return_value = mock_invoice

        mock_finalized = MagicMock()
        mock_finalized.id = "inv_123"
        mock_finalize.return_value = mock_finalized

        line_items = [
            {
                "description": "Service A",
                "unit_amount": 100.00,
                "quantity": 2,
                "currency": "usd"
            }
        ]

        invoice = manager.create_invoice(
            customer_id="cus_123",
            line_items=line_items,
            days_until_due=30
        )

        assert invoice.id == "inv_123"
        mock_invoice_create.assert_called_once()
        mock_item_create.assert_called_once()
        mock_finalize.assert_called_once()

    @patch('stripe.Invoice.retrieve')
    def test_retrieve_invoice(self, mock_retrieve, manager):
        """Test invoice retrieval"""
        mock_invoice = MagicMock()
        mock_invoice.id = "inv_123"
        mock_retrieve.return_value = mock_invoice

        invoice = manager.retrieve_invoice("inv_123")

        assert invoice.id == "inv_123"
        mock_retrieve.assert_called_with("inv_123")

    @patch('stripe.Invoice.list')
    def test_list_invoices(self, mock_list, manager):
        """Test listing invoices"""
        mock_invoice1 = MagicMock()
        mock_invoice1.id = "inv_1"
        mock_invoice2 = MagicMock()
        mock_invoice2.id = "inv_2"

        mock_list.return_value = MagicMock(data=[mock_invoice1, mock_invoice2])

        invoices = manager.list_invoices(limit=10)

        assert len(invoices) == 2
        assert invoices[0].id == "inv_1"

    @patch('stripe.Invoice.retrieve')
    def test_get_invoice_payment_status(self, mock_retrieve, manager):
        """Test getting payment status"""
        mock_invoice = MagicMock()
        mock_invoice.id = "inv_123"
        mock_invoice.number = "INV-001"
        mock_invoice.status = "paid"
        mock_invoice.paid = True
        mock_invoice.amount_due = 100000
        mock_invoice.amount_paid = 100000
        mock_invoice.amount_remaining = 0
        mock_invoice.currency = "usd"
        mock_invoice.created = 1735689600
        mock_invoice.due_date = 1735776000
        mock_invoice.hosted_invoice_url = "https://invoice.stripe.com/i/123"
        mock_invoice.invoice_pdf = "https://invoice.stripe.com/i/123/pdf"
        mock_retrieve.return_value = mock_invoice

        status = manager.get_invoice_payment_status("inv_123")

        assert status["invoice_id"] == "inv_123"
        assert status["paid"] is True
        assert status["amount_due"] == 1000.00
        assert status["amount_paid"] == 1000.00

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_create, manager):
        """Test payment intent creation"""
        mock_intent = MagicMock()
        mock_intent.id = "pi_123"
        mock_create.return_value = mock_intent

        intent = manager.create_payment_intent(
            amount=100.00,
            currency="usd",
            customer_id="cus_123"
        )

        assert intent.id == "pi_123"
        mock_create.assert_called_once()


class TestInvoiceValidator:
    """Test suite for InvoiceValidator"""

    def test_validate_customer_data_valid(self):
        """Test valid customer data"""
        customer = {
            "name": "John Doe",
            "email": "john@example.com"
        }

        assert InvoiceValidator.validate_customer_data(customer) is True

    def test_validate_customer_data_missing_name(self):
        """Test missing customer name"""
        customer = {
            "email": "john@example.com"
        }

        with pytest.raises(ValueError, match="Missing required customer field: name"):
            InvoiceValidator.validate_customer_data(customer)

    def test_validate_customer_data_invalid_email(self):
        """Test invalid email format"""
        customer = {
            "name": "John Doe",
            "email": "invalid-email"
        }

        with pytest.raises(ValueError, match="Invalid email format"):
            InvoiceValidator.validate_customer_data(customer)

    def test_validate_line_items_valid(self):
        """Test valid line items"""
        line_items = [
            {
                "description": "Service A",
                "unit_amount": 100.00,
                "quantity": 1
            }
        ]

        assert InvoiceValidator.validate_line_items(line_items) is True

    def test_validate_line_items_empty(self):
        """Test empty line items"""
        with pytest.raises(ValueError, match="Invoice must have at least one line item"):
            InvoiceValidator.validate_line_items([])

    def test_validate_line_items_missing_description(self):
        """Test missing description"""
        line_items = [
            {
                "unit_amount": 100.00,
                "quantity": 1
            }
        ]

        with pytest.raises(ValueError, match="missing description"):
            InvoiceValidator.validate_line_items(line_items)

    def test_validate_line_items_invalid_amount(self):
        """Test invalid amount"""
        line_items = [
            {
                "description": "Service",
                "unit_amount": 0,
                "quantity": 1
            }
        ]

        with pytest.raises(ValueError, match="invalid amount"):
            InvoiceValidator.validate_line_items(line_items)

    def test_validate_invoice_data_valid(self):
        """Test valid invoice data"""
        invoice_data = {
            "customer": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "line_items": [
                {
                    "description": "Service",
                    "unit_amount": 100.00,
                    "quantity": 1
                }
            ],
            "total": 100.00
        }

        assert InvoiceValidator.validate_invoice_data(invoice_data) is True

    def test_validate_invoice_data_missing_customer(self):
        """Test missing customer"""
        invoice_data = {
            "line_items": []
        }

        with pytest.raises(ValueError, match="missing customer data"):
            InvoiceValidator.validate_invoice_data(invoice_data)


class TestUtilityFunctions:
    """Test suite for utility functions"""

    def test_format_currency_usd(self):
        """Test USD currency formatting"""
        result = format_currency(1234.56, "USD")
        assert result == "$1,234.56"

    def test_format_currency_eur(self):
        """Test EUR currency formatting"""
        result = format_currency(1234.56, "EUR")
        assert result == "€1,234.56"

    def test_format_currency_unknown(self):
        """Test unknown currency"""
        result = format_currency(1234.56, "XXX")
        assert result == "XXX1,234.56"

    def test_calculate_invoice_total(self):
        """Test invoice total calculation"""
        line_items = [
            {"unit_amount": 100.00, "quantity": 2},
            {"unit_amount": 50.00, "quantity": 1},
            {"unit_amount": 75.00, "quantity": 3}
        ]

        result = calculate_invoice_total(line_items)

        assert result["subtotal"] == 475.00
        assert result["tax"] == 0
        assert result["total"] == 475.00


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
