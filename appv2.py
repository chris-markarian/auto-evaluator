import streamlit as st
import anthropic
import json
import re

# Page config
st.set_page_config(
    page_title="Vehicle Evaluator",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    .main-title {
        font-family: 'Georgia', serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
        background: linear-gradient(135deg, #ffffff 0%, #a3a3a3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        color: #737373;
        font-size: 1rem;
        margin-bottom: 2rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }
    
    .vehicle-title {
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .vehicle-meta {
        color: #737373;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    
    .spec-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid #262626;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    
    .spec-label {
        font-size: 0.7rem;
        color: #525252;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .spec-value {
        font-size: 0.95rem;
        color: #e5e5e5;
        font-weight: 500;
    }
    
    .section-label {
        font-size: 0.75rem;
        color: #525252;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .overview-text {
        color: #a3a3a3;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    .tag {
        display: inline-block;
        padding: 8px 14px;
        background: rgba(30, 58, 95, 0.2);
        border: 1px solid #1e3a5f;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #93c5fd;
        margin: 4px;
    }
    
    .tag-concern {
        background: rgba(127, 29, 29, 0.2);
        border-color: #7f1d1d;
        color: #fca5a5;
    }
    
    .tag-option {
        background: rgba(39, 39, 42, 0.5);
        border-color: #3f3f46;
        color: #a1a1aa;
    }
    
    .value-card {
        background: rgba(0,0,0,0.3);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
    }
    
    .value-card-medium {
        border-color: #1e3a5f;
        background: rgba(30,58,95,0.2);
    }
    
    .value-amount {
        font-family: 'Georgia', serif;
        font-size: 1.75rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .value-label {
        font-size: 0.8rem;
        color: #737373;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .value-factors {
        color: #525252;
        font-size: 0.9rem;
        font-style: italic;
        text-align: center;
        margin-top: 1rem;
    }
    
    .result-container {
        background: linear-gradient(180deg, #141414 0%, #0d0d0d 100%);
        border: 1px solid #262626;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 2rem;
    }
    
    .stTextInput > div > div > input {
        background-color: #111;
        border: 1px solid #333;
        color: #fff;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #111;
        border: 1px solid #333;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

def get_placeholder_image(make, model, year):
    """Generate a placeholder image URL based on make"""
    brand_colors = {
        'Porsche': 'dc2626',
        'Ferrari': 'dc2626',
        'BMW': '1e40af',
        'Mercedes': '1f2937',
        'Mercedes-Benz': '1f2937',
        'Audi': '374151',
        'Lamborghini': 'eab308',
        'McLaren': 'ea580c',
        'Toyota': '16a34a',
        'Honda': 'dc2626',
        'Ford': '2563eb',
        'Chevrolet': 'eab308',
        'Nissan': 'dc2626',
        'Mazda': 'dc2626',
        'Subaru': '2563eb',
        'Volkswagen': '1e40af',
        'Lexus': '1f2937',
        'Acura': '374151',
        'Jeep': '16a34a',
        'Land Rover': '16a34a',
        'Jaguar': '16a34a',
        'Aston Martin': '16a34a',
        'Bentley': '1f2937',
        'Rolls-Royce': '1f2937',
        'Maserati': '1e40af',
        'Alfa Romeo': 'dc2626',
    }
    bg_color = brand_colors.get(make, '0f172a')
    text = f"{year or ''} {make or 'Vehicle'}%0A{model or ''}"
    return f"https://placehold.co/400x280/{bg_color}/ffffff?text={text}"

def analyze_vehicle(content, url):
    """Send the listing content to Claude for analysis"""
    
    # Check if we have content
    if not content or len(content.strip()) < 100:
        raise ValueError("Listing content is too short or empty. Please paste more content from the listing.")
    
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
    prompt = f"""You are a vehicle valuation expert. Analyze this car listing and extract ALL actual data from the listing - DO NOT estimate or guess any values.

LISTING URL: {url}

LISTING CONTENT:
{content[:50000]}

Extract the EXACT information from the listing:
1. Year, make, model, and trim level
2. Exterior color
3. ACTUAL mileage as listed
4. Location (where the car is being sold)
5. Engine specs, transmission type, drivetrain
6. Notable options and features mentioned
7. Condition notes, service history, modifications
8. Any issues or flaws mentioned
9. Current bid/price if shown

Then provide:
- A compelling 2-paragraph overview discussing what makes this PARTICULAR car interesting
- Three value estimates based on the ACTUAL condition and mileage: Low (quick sale), Medium (fair market), High (patient seller)

IMPORTANT: Use ONLY data from the listing. If something isn't mentioned, say "Not specified".

Respond ONLY with valid JSON:
{{
  "title": "Year Make Model Trim",
  "year": 2003,
  "make": "Porsche",
  "model": "911 Carrera 4S",
  "color": "Guards Red",
  "location": "City, State",
  "specs": {{
    "engine": "Exact engine from listing",
    "power": "HP if listed",
    "torque": "Torque if listed",
    "transmission": "Exact transmission",
    "drivetrain": "AWD/RWD/FWD"
  }},
  "mileage": "Exact mileage from listing",
  "options": ["Option 1", "Option 2", "Option 3"],
  "highlights": ["Notable feature 1", "Recent service item", "Special history"],
  "concerns": ["Any issues mentioned", "Wear items noted"],
  "overview": "Two paragraphs analyzing THIS specific car...",
  "values": {{
    "low": 44500,
    "medium": 49000,
    "high": 55000
  }},
  "valueFactors": "Brief explanation referencing actual condition, mileage, options"
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    except anthropic.APIError as e:
        raise ValueError(f"API error: {str(e)}")
    
    if not message.content:
        raise ValueError("Empty response from Claude API")
    
    response_text = message.content[0].text
    
    if not response_text:
        raise ValueError("Empty text in Claude response")
    
    # Clean up the response
    response_text = re.sub(r'```json\n?', '', response_text)
    response_text = re.sub(r'```\n?', '', response_text)
    response_text = response_text.strip()
    
    if not response_text:
        raise ValueError("Response was empty after cleanup")
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        # Show first 500 chars of response for debugging
        raise ValueError(f"Invalid JSON response. First 500 chars: {response_text[:500]}")

def format_currency(value):
    """Format a number as currency"""
    return f"${value:,.0f}"

def render_tags(items, tag_class="tag"):
    """Render a list of items as styled tags"""
    html = ""
    for item in items:
        html += f'<span class="{tag_class}">{item}</span>'
    return html

# Main app
st.markdown('<h1 class="main-title">Vehicle Evaluator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Market Intelligence</p>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([5, 1])
with col1:
    url = st.text_input("Paste vehicle listing URL", placeholder="https://bringatrailer.com/listing/...", label_visibility="collapsed")
with col2:
    submit_clicked = st.button("Submit", type="primary", use_container_width=True)

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'show_paste' not in st.session_state:
    st.session_state.show_paste = False

# Handle submission
if submit_clicked and url:
    with st.spinner("Fetching listing data..."):
        import requests
        
        listing_content = None
        
        # Try CORS proxies
        proxies = [
            f"https://api.allorigins.win/raw?url={requests.utils.quote(url)}",
            f"https://api.codetabs.com/v1/proxy?quest={requests.utils.quote(url)}"
        ]
        
        for proxy_url in proxies:
            try:
                response = requests.get(proxy_url, timeout=15)
                if response.ok and len(response.text) > 1000 and 'Access Denied' not in response.text:
                    listing_content = response.text
                    break
            except:
                continue
        
        if not listing_content:
            st.session_state.show_paste = True
            st.session_state.result = None
        else:
            with st.spinner("Analyzing vehicle details..."):
                try:
                    st.session_state.result = analyze_vehicle(listing_content, url)
                    st.session_state.show_paste = False
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

# Show paste area if auto-fetch failed
if st.session_state.show_paste:
    st.warning("Couldn't auto-fetch the listing. Please paste the listing content below.")
    listing_text = st.text_area(
        "Paste listing content",
        placeholder="Copy all text from the listing page and paste here...",
        height=200,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Analyze", type="primary", use_container_width=True):
            if listing_text:
                with st.spinner("Analyzing vehicle details..."):
                    try:
                        st.session_state.result = analyze_vehicle(listing_text, url)
                        st.session_state.show_paste = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

# Display results
if st.session_state.result:
    result = st.session_state.result
    
    st.markdown("---")
    
    # Header
    st.markdown(f'<h2 class="vehicle-title">{result.get("title", "Vehicle")}</h2>', unsafe_allow_html=True)
    
    meta_parts = []
    if result.get("color"):
        meta_parts.append(f"🎨 {result['color']}")
    if result.get("mileage"):
        meta_parts.append(result['mileage'])
    if result.get("location"):
        meta_parts.append(f"📍 {result['location']}")
    
    st.markdown(f'<p class="vehicle-meta">{" &nbsp;•&nbsp; ".join(meta_parts)}</p>', unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Vehicle image
        img_url = get_placeholder_image(result.get("make"), result.get("model"), result.get("year"))
        st.image(img_url, use_container_width=True)
        
        # Specs grid
        specs = result.get("specs", {})
        
        spec_col1, spec_col2 = st.columns(2)
        
        with spec_col1:
            if specs.get("engine"):
                st.markdown(f"""
                <div class="spec-card">
                    <div class="spec-label">Engine</div>
                    <div class="spec-value">{specs['engine']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if specs.get("transmission"):
                st.markdown(f"""
                <div class="spec-card" style="margin-top: 12px;">
                    <div class="spec-label">Trans</div>
                    <div class="spec-value">{specs['transmission']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            if result.get("mileage"):
                st.markdown(f"""
                <div class="spec-card" style="margin-top: 12px;">
                    <div class="spec-label">Mileage</div>
                    <div class="spec-value">{result['mileage']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with spec_col2:
            if specs.get("power"):
                st.markdown(f"""
                <div class="spec-card">
                    <div class="spec-label">Power</div>
                    <div class="spec-value">{specs['power']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if specs.get("drivetrain"):
                st.markdown(f"""
                <div class="spec-card" style="margin-top: 12px;">
                    <div class="spec-label">Drive</div>
                    <div class="spec-value">{specs['drivetrain']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Overview
        st.markdown('<p class="section-label">Overview</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="overview-text">{result.get("overview", "")}</p>', unsafe_allow_html=True)
    
    # Options & Features
    if result.get("options"):
        st.markdown("---")
        st.markdown('<p class="section-label">Options & Features</p>', unsafe_allow_html=True)
        st.markdown(render_tags(result["options"], "tag tag-option"), unsafe_allow_html=True)
    
    # Highlights
    if result.get("highlights"):
        st.markdown("---")
        st.markdown('<p class="section-label">Highlights</p>', unsafe_allow_html=True)
        st.markdown(render_tags(result["highlights"], "tag"), unsafe_allow_html=True)
    
    # Concerns
    if result.get("concerns") and result["concerns"][0] != "None mentioned":
        st.markdown("---")
        st.markdown('<p class="section-label">Notes & Concerns</p>', unsafe_allow_html=True)
        st.markdown(render_tags(result["concerns"], "tag tag-concern"), unsafe_allow_html=True)
    
    # Values
    st.markdown("---")
    st.markdown('<p class="section-label">Estimated Value</p>', unsafe_allow_html=True)
    
    values = result.get("values", {})
    val_col1, val_col2, val_col3 = st.columns(3)
    
    with val_col1:
        st.markdown(f"""
        <div class="value-card">
            <div class="value-amount">{format_currency(values.get('low', 0))}</div>
            <div class="value-label">Low</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_col2:
        st.markdown(f"""
        <div class="value-card value-card-medium">
            <div class="value-amount">{format_currency(values.get('medium', 0))}</div>
            <div class="value-label">Medium</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_col3:
        st.markdown(f"""
        <div class="value-card">
            <div class="value-amount">{format_currency(values.get('high', 0))}</div>
            <div class="value-label">High</div>
        </div>
        """, unsafe_allow_html=True)
    
    if result.get("valueFactors"):
        st.markdown(f'<p class="value-factors">{result["valueFactors"]}</p>', unsafe_allow_html=True)
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 New Search"):
        st.session_state.result = None
        st.session_state.show_paste = False
        st.rerun()
