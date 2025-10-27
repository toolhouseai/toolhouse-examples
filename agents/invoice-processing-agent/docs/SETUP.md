# 🛠️ Setup Guide - Invoice Processing Agent

Complete setup instructions for the Invoice Processing Agent.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **pip** or **poetry** package manager
3. **Git** for cloning the repository

## 🔑 Required API Keys

You'll need to obtain API keys from these services:

### 1. Anthropic (Claude AI)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

**Pricing**: Pay-as-you-go. Approximately $3-15 per 1M tokens depending on model.

### 2. Toolhouse

1. Visit [Toolhouse](https://app.toolhouse.ai/)
2. Create an account
3. Go to **Settings** → **API Keys**
4. Click **Generate New Key**
5. Copy the API key

**Pricing**: Free tier available. Check [pricing](https://toolhouse.ai/pricing) for limits.

### 3. Stripe

1. Visit [Stripe Dashboard](https://dashboard.stripe.com/)
2. Create an account (or log in)
3. Go to **Developers** → **API Keys**
4. For development: Copy the **Test Mode** secret key (`sk_test_...`)
5. For production: Copy the **Live Mode** secret key (`sk_live_...`)

**⚠️ Important**: Always use test mode keys during development!

**Pricing**: Transaction fees apply (2.9% + $0.30 per successful charge in US).

## 🚀 Installation Steps

### Step 1: Clone or Download

```bash
# If you haven't already
cd invoice-processing-agent
```

### Step 2: Create Virtual Environment

**Using venv (recommended):**
```bash
python3 -m venv venv
```

**Activate the environment:**
- **macOS/Linux**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

**Using conda:**
```bash
conda create -n invoice-agent python=3.10
conda activate invoice-agent
```

### Step 3: Install Dependencies

```bash
pip install -r config/requirements.txt
```

**Expected output:**
```
Successfully installed anthropic-X.X.X toolhouse-X.X.X stripe-X.X.X ...
```

### Step 4: Configure Environment Variables

1. **Copy the example environment file:**
```bash
cp config/.env.example .env
```

2. **Edit `.env` file** with your API keys:
```bash
# Use your preferred editor
nano .env
# or
vim .env
# or
code .env
```

3. **Add your keys:**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
TOOLHOUSE_API_KEY=your-toolhouse-key-here
STRIPE_API_KEY=sk_test_your-stripe-test-key-here
```

4. **Save and close** the file

### Step 5: Verify Installation

Run the verification script:

```bash
python -c "
import anthropic
import toolhouse
import stripe
print('✅ All packages installed successfully!')
"
```

Expected output:
```
✅ All packages installed successfully!
```

### Step 6: Test the Agent

Start the agent:

```bash
python src/invoice_agent.py
```

You should see:
```
🧾 Invoice Processing Agent with Stripe Integration
============================================================

Available commands:
  1. Process invoice from text
  2. Process invoice from URL
  3. Check invoice status
  4. List unpaid invoices
  /quit - Exit the agent
============================================================

💬 Enter command number (or /quit):
```

## 🧪 Verify with Test Invoice

Test the agent with a sample invoice:

1. Start the agent: `python src/invoice_agent.py`
2. Enter command: `1` (Process invoice from text)
3. Paste this test invoice:

```
Invoice #TEST-001
Date: 2025-10-27
Due: 2025-11-27

Customer: Test User
Email: test@example.com

Items:
- Test Service: $100.00

Total: $100.00
```

4. Press Enter twice (empty line to finish)
5. Choose: `n` (don't send automatically)
6. Check the output for success

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r config/requirements.txt
```

### Issue: "API key not found"

**Solution:**
1. Check `.env` file exists in project root
2. Verify API keys are correctly set (no extra spaces)
3. Ensure no quotes around keys in `.env`

**Correct format:**
```env
ANTHROPIC_API_KEY=sk-ant-key-here
```

**Incorrect format:**
```env
ANTHROPIC_API_KEY="sk-ant-key-here"  # ❌ No quotes needed
```

### Issue: "stripe.error.AuthenticationError"

**Solution:**
1. Verify Stripe API key starts with `sk_test_` or `sk_live_`
2. Check key is not expired
3. Ensure test mode is enabled in Stripe Dashboard
4. Try regenerating the key

### Issue: "Toolhouse connection failed"

**Solution:**
1. Check Toolhouse API key is valid
2. Verify internet connection
3. Visit [Toolhouse Status](https://status.toolhouse.ai/) for outages
4. Try regenerating the API key

### Issue: Import errors or package conflicts

**Solution:**
```bash
# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r config/requirements.txt
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** to version control
   ```bash
   # Already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use test keys for development**
   - Stripe: `sk_test_...`
   - Never use live keys locally

3. **Rotate keys regularly**
   - Change API keys every 90 days
   - Immediately if compromised

4. **Restrict key permissions**
   - Stripe: Use restricted keys when possible
   - Limit scope to minimum required

## 📱 IDE Setup (Optional)

### VS Code

1. **Install Python extension**
2. **Select interpreter:**
   - `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
   - Type: "Python: Select Interpreter"
   - Choose: `./venv/bin/python`

3. **Install recommended extensions:**
   - Python
   - Pylance
   - Python Test Explorer

### PyCharm

1. **Configure interpreter:**
   - Settings → Project → Python Interpreter
   - Add Interpreter → Existing
   - Select: `./venv/bin/python`

2. **Enable pytest:**
   - Settings → Tools → Python Integrated Tools
   - Default test runner: pytest

## 🧹 Clean Development Environment

**Reset everything:**
```bash
# Remove virtual environment
rm -rf venv

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

## 📦 Optional: Production Setup

For production deployment:

1. **Use live Stripe keys** (after thorough testing)
2. **Set up Stripe webhooks**
3. **Configure logging** to files/services
4. **Add monitoring** (Sentry, DataDog, etc.)
5. **Implement rate limiting**
6. **Use environment-specific configs**

## ✅ Next Steps

Once setup is complete:

1. ✅ Read [README.md](README.md) for usage examples
2. ✅ Review [EXAMPLES.md](EXAMPLES.md) for common patterns
3. ✅ Run tests: `pytest tests/ -v`
4. ✅ Start building your invoice workflows!

## 🆘 Still Having Issues?

- Check [Troubleshooting](#-troubleshooting) section
- Review error messages carefully
- Search [GitHub Issues](https://github.com/toolhouseai/toolhouse-examples/issues)
- Ask in [Toolhouse Discord](https://discord.gg/toolhouse)

---

**Setup complete!** 🎉 You're ready to start processing invoices.
