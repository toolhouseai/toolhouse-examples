"""
Tests for Invoice Processing Agent
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.invoice_agent import InvoiceProcessingAgent


class TestInvoiceProcessingAgent:
    """Test suite for InvoiceProcessingAgent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        with patch('src.invoice_agent.anthropic_client'), \
             patch('src.invoice_agent.toolhouse_client'), \
             patch('src.invoice_agent.stripe'):
            return InvoiceProcessingAgent()

    @pytest.fixture
    def sample_invoice_data(self):
        """Sample invoice data for testing"""
        return {
            "invoice_number": "INV-2025-001",
            "invoice_date": "2025-10-27",
            "due_date": "2025-11-27",
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "address": "123 Main St"
            },
            "line_items": [
                {
                    "description": "Web Development",
                    "quantity": 1,
                    "unit_price": 2500.00,
                    "amount": 2500.00
                },
                {
                    "description": "Maintenance",
                    "quantity": 3,
                    "unit_price": 200.00,
                    "amount": 600.00
                }
            ],
            "subtotal": 3100.00,
            "tax": 248.00,
            "total": 3348.00,
            "currency": "USD"
        }

    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.anthropic is not None
        assert agent.toolhouse is not None
        assert isinstance(agent.messages, list)
        assert isinstance(agent.conversation_history, list)

    def test_extract_json_from_text(self, agent):
        """Test JSON extraction from text"""
        # Test with markdown code block
        text = '''
        Here is the invoice data:
        ```json
        {"invoice_number": "INV-001", "total": 100.00}
        ```
        '''
        result = agent._extract_json_from_text(text)
        assert result["invoice_number"] == "INV-001"
        assert result["total"] == 100.00

        # Test with raw JSON
        text = '{"invoice_number": "INV-002", "total": 200.00}'
        result = agent._extract_json_from_text(text)
        assert result["invoice_number"] == "INV-002"

    def test_extract_json_from_text_invalid(self, agent):
        """Test JSON extraction with invalid input"""
        with pytest.raises(ValueError):
            agent._extract_json_from_text("No JSON here")

    def test_calculate_days_until_due(self, agent):
        """Test days calculation"""
        days = agent._calculate_days_until_due("2025-10-27", "2025-11-27")
        assert days == 31

        # Test with same date
        days = agent._calculate_days_until_due("2025-10-27", "2025-10-27")
        assert days == 1  # Minimum 1 day

        # Test with invalid dates
        days = agent._calculate_days_until_due("invalid", "invalid")
        assert days == 30  # Default

    @patch('stripe.Customer.list')
    @patch('stripe.Customer.create')
    def test_create_stripe_customer_new(self, mock_create, mock_list, agent):
        """Test creating new Stripe customer"""
        # Mock no existing customer
        mock_list.return_value = MagicMock(data=[])

        # Mock customer creation
        mock_customer = MagicMock()
        mock_customer.id = "cus_123"
        mock_create.return_value = mock_customer

        customer_data = {
            "name": "Jane Doe",
            "email": "jane@example.com"
        }

        customer_id = agent.create_stripe_customer(customer_data)
        assert customer_id == "cus_123"
        mock_create.assert_called_once()

    @patch('stripe.Customer.list')
    def test_create_stripe_customer_existing(self, mock_list, agent):
        """Test retrieving existing Stripe customer"""
        # Mock existing customer
        mock_customer = MagicMock()
        mock_customer.id = "cus_existing"
        mock_list.return_value = MagicMock(data=[mock_customer])

        customer_data = {
            "name": "Jane Doe",
            "email": "jane@example.com"
        }

        customer_id = agent.create_stripe_customer(customer_data)
        assert customer_id == "cus_existing"

    @patch('src.invoice_agent.InvoiceProcessingAgent.create_stripe_customer')
    @patch('stripe.Invoice.create')
    @patch('stripe.InvoiceItem.create')
    @patch('stripe.Invoice.finalize_invoice')
    def test_create_stripe_invoice(
        self,
        mock_finalize,
        mock_item_create,
        mock_invoice_create,
        mock_create_customer,
        agent,
        sample_invoice_data
    ):
        """Test creating Stripe invoice"""
        # Mock customer creation
        mock_create_customer.return_value = "cus_123"

        # Mock invoice creation
        mock_invoice = MagicMock()
        mock_invoice.id = "inv_123"
        mock_invoice_create.return_value = mock_invoice

        # Mock finalized invoice
        mock_finalized = MagicMock()
        mock_finalized.id = "inv_123"
        mock_finalized.number = "INV-STRIPE-001"
        mock_finalized.amount_due = 334800  # In cents
        mock_finalized.currency = "usd"
        mock_finalized.status = "open"
        mock_finalized.hosted_invoice_url = "https://invoice.stripe.com/i/123"
        mock_finalized.invoice_pdf = "https://invoice.stripe.com/i/123/pdf"
        mock_finalize.return_value = mock_finalized

        result = agent.create_stripe_invoice(sample_invoice_data)

        assert result["invoice_id"] == "inv_123"
        assert result["amount_due"] == 3348.00
        assert result["currency"] == "usd"
        assert result["status"] == "open"
        assert "hosted_invoice_url" in result

        # Verify invoice items were created
        assert mock_item_create.call_count == len(sample_invoice_data["line_items"])

    @patch('stripe.Invoice.retrieve')
    def test_check_invoice_status(self, mock_retrieve, agent):
        """Test checking invoice status"""
        # Mock invoice
        mock_invoice = MagicMock()
        mock_invoice.id = "inv_123"
        mock_invoice.number = "INV-001"
        mock_invoice.status = "paid"
        mock_invoice.amount_due = 100000
        mock_invoice.amount_paid = 100000
        mock_invoice.currency = "usd"
        mock_invoice.paid = True
        mock_invoice.attempted = True
        mock_invoice.due_date = 1735689600
        mock_retrieve.return_value = mock_invoice

        result = agent.check_invoice_status("inv_123")

        assert result["invoice_id"] == "inv_123"
        assert result["status"] == "paid"
        assert result["amount_due"] == 1000.00
        assert result["paid"] is True

    @patch('stripe.Invoice.list')
    def test_list_unpaid_invoices(self, mock_list, agent):
        """Test listing unpaid invoices"""
        # Mock invoices
        mock_invoice1 = MagicMock()
        mock_invoice1.id = "inv_1"
        mock_invoice1.number = "INV-001"
        mock_invoice1.customer_email = "customer1@example.com"
        mock_invoice1.amount_due = 100000
        mock_invoice1.currency = "usd"
        mock_invoice1.due_date = 1735689600

        mock_invoice2 = MagicMock()
        mock_invoice2.id = "inv_2"
        mock_invoice2.number = "INV-002"
        mock_invoice2.customer_email = "customer2@example.com"
        mock_invoice2.amount_due = 200000
        mock_invoice2.currency = "usd"
        mock_invoice2.due_date = None

        mock_list.return_value = MagicMock(data=[mock_invoice1, mock_invoice2])

        result = agent.list_unpaid_invoices(limit=10)

        assert len(result) == 2
        assert result[0]["invoice_id"] == "inv_1"
        assert result[0]["amount_due"] == 1000.00
        assert result[1]["due_date"] is None


class TestInvoiceProcessingIntegration:
    """Integration tests for invoice processing workflow"""

    @pytest.fixture
    def agent(self):
        """Create agent for integration testing"""
        with patch('src.invoice_agent.anthropic_client'), \
             patch('src.invoice_agent.toolhouse_client'), \
             patch('src.invoice_agent.stripe'):
            return InvoiceProcessingAgent()

    @patch('src.invoice_agent.InvoiceProcessingAgent.extract_invoice_data')
    @patch('src.invoice_agent.InvoiceProcessingAgent.create_stripe_invoice')
    def test_process_invoice_success(
        self,
        mock_create_invoice,
        mock_extract,
        agent,
    ):
        """Test complete invoice processing workflow"""
        # Mock extraction
        mock_extract.return_value = {
            "invoice_number": "INV-001",
            "invoice_date": "2025-10-27",
            "due_date": "2025-11-27",
            "customer": {
                "name": "Test Customer",
                "email": "test@example.com"
            },
            "line_items": [
                {
                    "description": "Service",
                    "quantity": 1,
                    "unit_price": 100.00,
                    "amount": 100.00
                }
            ],
            "total": 100.00,
            "currency": "USD"
        }

        # Mock Stripe invoice creation
        mock_create_invoice.return_value = {
            "invoice_id": "inv_123",
            "invoice_number": "STRIPE-001",
            "amount_due": 100.00,
            "status": "open"
        }

        # Process invoice
        result = agent.process_invoice("Test invoice text", source_type="text")

        assert result["success"] is True
        assert "extracted_data" in result
        assert "stripe_invoice" in result
        assert result["stripe_invoice"]["invoice_id"] == "inv_123"

    @patch('src.invoice_agent.InvoiceProcessingAgent.extract_invoice_data')
    def test_process_invoice_extraction_error(self, mock_extract, agent):
        """Test invoice processing with extraction error"""
        # Mock extraction error
        mock_extract.return_value = {
            "error": "Failed to extract data"
        }

        result = agent.process_invoice("Invalid invoice", source_type="text")

        assert result["success"] is False
        assert result["stage"] == "extraction"

    @patch('src.invoice_agent.InvoiceProcessingAgent.extract_invoice_data')
    @patch('src.invoice_agent.InvoiceProcessingAgent.create_stripe_invoice')
    def test_process_invoice_stripe_error(
        self,
        mock_create_invoice,
        mock_extract,
        agent
    ):
        """Test invoice processing with Stripe error"""
        # Mock successful extraction
        mock_extract.return_value = {
            "invoice_number": "INV-001",
            "customer": {"name": "Test", "email": "test@example.com"},
            "line_items": [],
            "total": 100.00
        }

        # Mock Stripe error
        mock_create_invoice.side_effect = Exception("Stripe API error")

        result = agent.process_invoice("Test invoice", source_type="text")

        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
