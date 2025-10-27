"""
Invoice Processing Agent with Stripe Integration using Toolhouse

This agent uses Toolhouse AI tools and Stripe API to:
- Extract invoice data from various sources (PDFs, emails, web pages)
- Validate and process invoice information
- Create invoices in Stripe
- Process payments automatically
- Send notifications and receipts
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
from toolhouse import Toolhouse, Provider
import stripe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load API keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TOOLHOUSE_API_KEY = os.getenv("TOOLHOUSE_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# Initialize clients
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
toolhouse_client = Toolhouse(api_key=TOOLHOUSE_API_KEY, provider=Provider.ANTHROPIC)
stripe.api_key = STRIPE_API_KEY


class InvoiceProcessingAgent:
    """
    AI Agent for processing invoices using Toolhouse and Stripe
    """

    def __init__(self):
        """Initialize the invoice processing agent"""
        self.anthropic = anthropic_client
        self.toolhouse = toolhouse_client
        self.messages: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, Any]] = []

        # Set timezone metadata for accurate time handling
        self.toolhouse.set_metadata("timezone", self._get_system_timezone())

        # System prompt for the agent
        self.system_prompt = """
        You are an expert invoice processing AI agent with the following capabilities:

        1. INVOICE DATA EXTRACTION:
           - Extract invoice data from PDFs, emails, web pages, or text
           - Identify key fields: invoice number, date, due date, customer info, line items, amounts
           - Validate data completeness and accuracy

        2. STRIPE INVOICE CREATION:
           - Create customer records in Stripe if needed
           - Generate line items for products/services
           - Calculate totals, taxes, and discounts
           - Set payment terms and due dates

        3. PAYMENT PROCESSING:
           - Monitor invoice payment status
           - Process payments automatically when received
           - Handle payment failures and retries
           - Send payment receipts

        4. WORKFLOW AUTOMATION:
           - Schedule automated follow-ups for unpaid invoices
           - Send payment reminders before due dates
           - Track invoice lifecycle (draft → sent → paid)
           - Generate financial reports

        IMPORTANT GUIDELINES:
        - Always validate invoice data before creating in Stripe
        - Use current_time tool to check dates and due dates
        - Be precise with currency and amount calculations
        - Provide clear summaries of actions taken
        - Ask for confirmation before finalizing payments
        """

    def _get_system_timezone(self) -> str:
        """Get system timezone offset"""
        now = datetime.now()
        offset = now.astimezone().strftime('%z')
        hours = int(offset[:3])
        return str(hours)

    def extract_invoice_data(self, source: str, source_type: str = "text") -> Dict[str, Any]:
        """
        Extract invoice data from various sources using Toolhouse

        Args:
            source: Invoice source (URL, text, file path)
            source_type: Type of source (text, url, pdf)

        Returns:
            Extracted invoice data
        """
        logger.info(f"Extracting invoice data from {source_type}: {source[:100]}...")

        # Create extraction prompt
        extraction_prompt = f"""
        Extract all invoice information from the following {source_type}:

        {source}

        Return the data in JSON format with these fields:
        {{
            "invoice_number": "string",
            "invoice_date": "YYYY-MM-DD",
            "due_date": "YYYY-MM-DD",
            "customer": {{
                "name": "string",
                "email": "string",
                "address": "string"
            }},
            "line_items": [
                {{
                    "description": "string",
                    "quantity": number,
                    "unit_price": number,
                    "amount": number
                }}
            ],
            "subtotal": number,
            "tax": number,
            "total": number,
            "currency": "USD"
        }}

        If scraping is needed, use the web scraper tool. Ensure all amounts are decimal numbers.
        """

        # Add to messages
        self.messages.append({
            "role": "user",
            "content": extraction_prompt
        })

        # Call Claude with Toolhouse tools
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            system=self.system_prompt,
            tools=self.toolhouse.get_tools(),
            messages=self.messages
        )

        # Run tools if needed
        tool_results = self.toolhouse.run_tools(response)
        self.messages.extend(tool_results)

        # Get final response
        final_response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            system=self.system_prompt,
            tools=self.toolhouse.get_tools(),
            messages=self.messages
        )

        # Extract JSON from response
        response_text = final_response.content[0].text

        # Add to conversation history
        self.conversation_history.append({
            "action": "extract_invoice_data",
            "source_type": source_type,
            "response": response_text,
            "timestamp": datetime.now().isoformat()
        })

        try:
            # Try to extract JSON from response
            invoice_data = self._extract_json_from_text(response_text)
            logger.info(f"Successfully extracted invoice data: {invoice_data.get('invoice_number', 'N/A')}")
            return invoice_data
        except Exception as e:
            logger.error(f"Failed to extract invoice data: {str(e)}")
            return {"error": str(e), "raw_response": response_text}

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from text response"""
        # Try to find JSON in markdown code blocks
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, text)

        if matches:
            return json.loads(matches[0])

        # Try to find raw JSON
        try:
            # Find JSON object in text
            start = text.find('{')
            if start == -1:
                raise ValueError("No JSON object found")

            # Count braces to find matching closing brace
            brace_count = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return json.loads(text[start:i+1])

            raise ValueError("Malformed JSON object")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}")

    def create_stripe_customer(self, customer_data: Dict[str, Any]) -> str:
        """
        Create or retrieve Stripe customer

        Args:
            customer_data: Customer information

        Returns:
            Stripe customer ID
        """
        logger.info(f"Creating/retrieving Stripe customer: {customer_data.get('email')}")

        try:
            # Check if customer exists
            customers = stripe.Customer.list(email=customer_data.get('email'), limit=1)

            if customers.data:
                customer = customers.data[0]
                logger.info(f"Found existing customer: {customer.id}")
            else:
                # Create new customer
                customer = stripe.Customer.create(
                    name=customer_data.get('name'),
                    email=customer_data.get('email'),
                    address={
                        'line1': customer_data.get('address', ''),
                    },
                    metadata={
                        'source': 'invoice_processing_agent',
                        'created_at': datetime.now().isoformat()
                    }
                )
                logger.info(f"Created new customer: {customer.id}")

            return customer.id
        except Exception as e:
            logger.error(f"Failed to create/retrieve customer: {str(e)}")
            raise

    def create_stripe_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create invoice in Stripe

        Args:
            invoice_data: Extracted invoice data

        Returns:
            Created Stripe invoice details
        """
        logger.info(f"Creating Stripe invoice: {invoice_data.get('invoice_number')}")

        try:
            # Create customer
            customer_id = self.create_stripe_customer(invoice_data['customer'])

            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer_id,
                collection_method='send_invoice',
                days_until_due=self._calculate_days_until_due(
                    invoice_data.get('invoice_date'),
                    invoice_data.get('due_date')
                ),
                metadata={
                    'original_invoice_number': invoice_data.get('invoice_number', ''),
                    'source': 'invoice_processing_agent'
                }
            )

            # Add line items
            for item in invoice_data.get('line_items', []):
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=invoice.id,
                    description=item['description'],
                    quantity=int(item.get('quantity', 1)),
                    unit_amount=int(item['unit_price'] * 100),  # Convert to cents
                    currency=invoice_data.get('currency', 'usd').lower()
                )

            # Finalize invoice
            finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)

            logger.info(f"Successfully created Stripe invoice: {finalized_invoice.id}")

            return {
                "invoice_id": finalized_invoice.id,
                "invoice_number": finalized_invoice.number,
                "amount_due": finalized_invoice.amount_due / 100,
                "currency": finalized_invoice.currency,
                "status": finalized_invoice.status,
                "hosted_invoice_url": finalized_invoice.hosted_invoice_url,
                "invoice_pdf": finalized_invoice.invoice_pdf,
                "customer_email": invoice_data['customer']['email']
            }
        except Exception as e:
            logger.error(f"Failed to create Stripe invoice: {str(e)}")
            raise

    def _calculate_days_until_due(self, invoice_date: str, due_date: str) -> int:
        """Calculate days between invoice and due date"""
        try:
            invoice_dt = datetime.fromisoformat(invoice_date)
            due_dt = datetime.fromisoformat(due_date)
            days = (due_dt - invoice_dt).days
            return max(1, days)  # Minimum 1 day
        except Exception:
            return 30  # Default to 30 days

    def process_invoice(self, source: str, source_type: str = "text", auto_send: bool = False) -> Dict[str, Any]:
        """
        Complete invoice processing workflow

        Args:
            source: Invoice source
            source_type: Type of source
            auto_send: Whether to automatically send the invoice

        Returns:
            Processing results
        """
        logger.info("Starting invoice processing workflow")

        try:
            # Step 1: Extract invoice data
            invoice_data = self.extract_invoice_data(source, source_type)

            if 'error' in invoice_data:
                return {
                    "success": False,
                    "error": invoice_data['error'],
                    "stage": "extraction"
                }

            # Step 2: Create Stripe invoice
            stripe_invoice = self.create_stripe_invoice(invoice_data)

            # Step 3: Optionally send invoice
            if auto_send:
                sent_invoice = stripe.Invoice.send_invoice(stripe_invoice['invoice_id'])
                stripe_invoice['sent'] = True
                stripe_invoice['sent_at'] = datetime.now().isoformat()

            # Return results
            result = {
                "success": True,
                "extracted_data": invoice_data,
                "stripe_invoice": stripe_invoice,
                "timestamp": datetime.now().isoformat()
            }

            logger.info("Invoice processing completed successfully")
            return result

        except Exception as e:
            logger.error(f"Invoice processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def check_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """
        Check Stripe invoice status

        Args:
            invoice_id: Stripe invoice ID

        Returns:
            Invoice status details
        """
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)

            return {
                "invoice_id": invoice.id,
                "number": invoice.number,
                "status": invoice.status,
                "amount_due": invoice.amount_due / 100,
                "amount_paid": invoice.amount_paid / 100,
                "currency": invoice.currency,
                "paid": invoice.paid,
                "attempted": invoice.attempted,
                "due_date": datetime.fromtimestamp(invoice.due_date).isoformat() if invoice.due_date else None
            }
        except Exception as e:
            logger.error(f"Failed to check invoice status: {str(e)}")
            return {"error": str(e)}

    def list_unpaid_invoices(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List unpaid invoices

        Args:
            limit: Maximum number of invoices to return

        Returns:
            List of unpaid invoices
        """
        try:
            invoices = stripe.Invoice.list(
                status='open',
                limit=limit
            )

            return [
                {
                    "invoice_id": inv.id,
                    "number": inv.number,
                    "customer_email": inv.customer_email,
                    "amount_due": inv.amount_due / 100,
                    "currency": inv.currency,
                    "due_date": datetime.fromtimestamp(inv.due_date).isoformat() if inv.due_date else None
                }
                for inv in invoices.data
            ]
        except Exception as e:
            logger.error(f"Failed to list unpaid invoices: {str(e)}")
            return []


def main():
    """Main function for interactive invoice processing"""
    print("🧾 Invoice Processing Agent with Stripe Integration")
    print("=" * 60)

    agent = InvoiceProcessingAgent()

    print("\nAvailable commands:")
    print("  1. Process invoice from text")
    print("  2. Process invoice from URL")
    print("  3. Check invoice status")
    print("  4. List unpaid invoices")
    print("  /quit - Exit the agent")
    print("=" * 60)

    while True:
        try:
            choice = input("\n💬 Enter command number (or /quit): ").strip()

            if choice.lower() in ['/quit', '/exit']:
                print("\n👋 Goodbye!")
                break

            if choice == '1':
                # Process invoice from text
                print("\n📝 Paste invoice text (end with empty line):")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)

                invoice_text = '\n'.join(lines)

                auto_send = input("Send invoice automatically? (y/n): ").lower() == 'y'

                print("\n⏳ Processing invoice...")
                result = agent.process_invoice(invoice_text, source_type="text", auto_send=auto_send)

                print(f"\n✅ Result:")
                print(json.dumps(result, indent=2))

            elif choice == '2':
                # Process invoice from URL
                url = input("\n🔗 Enter invoice URL: ").strip()
                auto_send = input("Send invoice automatically? (y/n): ").lower() == 'y'

                print("\n⏳ Processing invoice from URL...")
                result = agent.process_invoice(url, source_type="url", auto_send=auto_send)

                print(f"\n✅ Result:")
                print(json.dumps(result, indent=2))

            elif choice == '3':
                # Check invoice status
                invoice_id = input("\n🔍 Enter Stripe invoice ID: ").strip()

                print("\n⏳ Checking invoice status...")
                status = agent.check_invoice_status(invoice_id)

                print(f"\n📊 Invoice Status:")
                print(json.dumps(status, indent=2))

            elif choice == '4':
                # List unpaid invoices
                limit = int(input("\n📋 How many invoices to show? (default 10): ").strip() or "10")

                print("\n⏳ Fetching unpaid invoices...")
                invoices = agent.list_unpaid_invoices(limit=limit)

                print(f"\n💰 Unpaid Invoices ({len(invoices)}):")
                for inv in invoices:
                    print(json.dumps(inv, indent=2))
                    print("-" * 40)

            else:
                print("❌ Invalid command. Please try again.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
