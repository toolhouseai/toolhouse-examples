# ⚡ Quick Start - Invoice Processing Agent

Get started with the Invoice Processing Agent in 5 minutes!

## 🚀 30-Second Setup

```bash
# 1. Navigate to project
cd invoice-processing-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r config/requirements.txt

# 4. Configure API keys
cp config/.env.example .env
# Edit .env and add your API keys

# 5. Run the agent
python src/invoice_agent.py
```

## 🔑 Get API Keys (5 minutes)

### Anthropic Claude
1. Visit: https://console.anthropic.com/
2. Sign up → API Keys → Create Key
3. Copy key to `.env` as `ANTHROPIC_API_KEY`

### Toolhouse
1. Visit: https://app.toolhouse.ai/
2. Sign up → Settings → API Keys → Generate
3. Copy key to `.env` as `TOOLHOUSE_API_KEY`

### Stripe (Test Mode)
1. Visit: https://dashboard.stripe.com/
2. Sign up → Developers → API Keys
3. Copy **Test Mode** secret key to `.env` as `STRIPE_API_KEY`

## 📝 Your First Invoice (2 minutes)

```bash
# Start the agent
python src/invoice_agent.py

# Choose option 1: Process invoice from text
# Paste this sample invoice:
```

```
Invoice #TEST-001
Date: 2025-10-27
Due: 2025-11-27

Customer: John Doe
Email: john@example.com

Services:
- Web Development: $1,500
- Hosting: $50

Total: $1,550
```

```bash
# Press Enter twice (empty line)
# Choose: n (don't auto-send for testing)
# ✅ View your created invoice!
```

## 🎯 Next Steps

1. ✅ Check your [Stripe Dashboard](https://dashboard.stripe.com/test/invoices)
2. 📖 Read [README.md](docs/README.md) for features
3. 📚 Explore [EXAMPLES.md](docs/EXAMPLES.md) for more use cases
4. 🧪 Run tests: `pytest tests/ -v`

## 💡 Quick Tips

- **Always use test mode** keys during development
- **Don't auto-send** invoices while testing
- **Check Stripe Dashboard** to see created invoices
- **View invoice PDFs** in Stripe to verify data

## 🐛 Common Issues

**"ModuleNotFoundError"**: Activate virtual environment
```bash
source venv/bin/activate
```

**"API key not found"**: Check `.env` file exists and has keys
```bash
cat .env  # Verify keys are set
```

**Stripe error**: Make sure you're using `sk_test_` key, not `sk_live_`

## 📚 Full Documentation

- [Complete Setup Guide](docs/SETUP.md)
- [Usage Examples](docs/EXAMPLES.md)
- [Architecture Details](docs/ARCHITECTURE.md)

---

**Ready to process invoices?** 🎉

Run: `python src/invoice_agent.py`
