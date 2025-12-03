# Vehicle Evaluator

A tool to evaluate cars that are on sale, anywhere. Paste a listing URL and get an AI-powered analysis including specs, condition assessment, and market valuation.

## Features

- 🔗 Paste any car listing URL (Bring a Trailer, Cars & Bids, Craigslist, etc.)
- 📊 Extracts actual listing data (mileage, specs, options, condition)
- 💰 Provides value estimates (Low / Medium / High)
- 🎨 Clean, dark-themed UI

## Deploy to Streamlit Community Cloud (Free)

### Step 1: Push to GitHub

1. Create a new GitHub repository
2. Upload these files:
   - `app.py`
   - `requirements.txt`
3. Commit and push

### Step 2: Deploy on Streamlit

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository, branch (`main`), and file (`app.py`)
5. Click **"Deploy"**

### Step 3: Add Your API Key

1. In Streamlit Cloud, go to your app's **Settings** → **Secrets**
2. Add your Anthropic API key:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

3. Click **Save**

Your app will restart and be ready to use!

## Local Development

1. Clone this repo
2. Create a `.streamlit/secrets.toml` file:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

## Get an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / Sign in
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-`)

## Notes

- Some car listing sites block automated access. If auto-fetch fails, you'll be prompted to paste the listing content manually.
- Valuations are AI-generated estimates based on the listing details and Claude's knowledge of market values.
