import streamlit as st
import spacy
import pytextrank
import re

# --- Page Configuration ---
st.set_page_config(page_title="T&C Simplifier", page_icon="⚖️", layout="wide")

# --- Custom CSS (Professional UI) ---
st.markdown("""
    <style>
    /* 1. Main Background */
    .main { background-color: var(--primary-background-color); }
    
    /* 2. Risk Card Styling */
    .risk-card {
        padding: 15px;
        background-color: rgba(231, 76, 60, 0.1);
        border-left: 5px solid #e74c3c;
        border-radius: 8px;
        margin-bottom: 12px;
        border: 1px solid rgba(231, 76, 60, 0.2);
    }
    
    /* 3. Safe Card Styling */
    .safe-card {
        padding: 15px;
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 5px solid #2ecc71;
        border-radius: 8px;
        border: 1px solid rgba(46, 204, 113, 0.2);
    }
    
    /* 4. Summary Box Styling */
    .summary-box {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        line-height: 1.6;
    }
    
    /* 5. Highlight Keyword */
    .highlight-risk {
        background-color: #e74c3c;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }

    /* 6. Footer */
    .footer {
        width: 100%;
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        opacity: 0.7;
    }
    
    /* 7. Button Styling - Makes it pop */
    div.stButton > button {
        font-weight: bold;
        font-size: 18px;
        padding: 15px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. Load NLP Models ---
@st.cache_resource
def load_nlp():
    try:
        nlp = spacy.load("en_core_web_sm")
        nlp.add_pipe("textrank")
        return nlp
    except OSError:
        st.error("⚠️ Model not found. Please run: python -m spacy download en_core_web_sm")
        return None

nlp = load_nlp()

# --- 2. Logic Functions ---
def extract_summary(text, limit=5):
    if not nlp: return []
    doc = nlp(text)
    summary_sentences = []
    for sent in doc._.textrank.summary(limit_phrases=15, limit_sentences=limit):
        summary_sentences.append(sent.text)
    return summary_sentences

def analyze_risks(text):
    if not nlp: return []
    risk_keywords = {
        "sell your data": "Data Privacy",
        "third party": "Data Sharing",
        "third-party": "Data Sharing",
        "liability": "Legal Liability",
        "indemnify": "Legal Responsibility",
        "termination": "Account Termination",
        "terminate": "Account Termination",
        "track": "Tracking/Surveillance",
        "cookies": "Tracking",
        "arbitration": "Legal Rights",
        "class action": "Legal Rights",
        "monitor": "Surveillance"
    }
    doc = nlp(text)
    found_risks = []
    for sent in doc.sents:
        sent_text = sent.text.lower()
        for keyword, category in risk_keywords.items():
            if keyword in sent_text:
                found_risks.append({"sentence": sent.text, "category": category, "keyword": keyword})
                break 
    return found_risks

def calculate_safety_score(num_risks, total_sentences):
    if total_sentences == 0: return 0
    score = 100
    penalty = num_risks * 15
    return max(0, score - penalty)

# --- 3. UI Layout ---

st.title("⚖️ Terms & Conditions Simplifier")
st.markdown("<p style='opacity: 0.7; margin-top: -10px;'>Don't blindly click 'I Agree'. Detect privacy risks instantly.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Input Section (Professional Card Layout) ---
st.markdown("### 📄 Input Contract")
text_input = st.text_area("Legal Text", height=300, 
                          placeholder="Paste the Terms of Service or Privacy Policy here...",
                          label_visibility="collapsed")

# Button is now FULL WIDTH - looks like a professional tool
analyze_btn = st.button("🔍 Analyze Risks Now", type="primary", use_container_width=True)

# --- Results Section ---
if analyze_btn:
    if not text_input.strip():
        st.warning("⚠️ Please paste some text to analyze.")
    elif nlp:
        with st.spinner("Scanning document for red flags..."):
            summary = extract_summary(text_input)
            risks = analyze_risks(text_input)
            doc_len = len(list(nlp(text_input).sents))
            score = calculate_safety_score(len(risks), doc_len)
            
            st.markdown("###") # Spacer
            
            # --- Score Dashboard ---
            st.markdown("#### 🛡️ Safety Analysis Report")
            
            # Create a nice container for metrics
            with st.container():
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    # Score Coloring
                    if score > 80: color = "#2ecc71"
                    elif score > 50: color = "#f1c40f"
                    else: color = "#e74c3c"
                    
                    st.markdown(f"""
                        <div style="background-color: var(--secondary-background-color); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid {color};">
                            <h2 style="color: {color}; margin: 0; font-size: 48px;">{score}</h2>
                            <p style="margin: 0; opacity: 0.8;">Safety Score</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with c2:
                    st.markdown(f"""
                        <div style="background-color: var(--secondary-background-color); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(128,128,128,0.2);">
                            <h2 style="margin: 0; font-size: 48px;">{len(risks)}</h2>
                            <p style="margin: 0; opacity: 0.8;">Red Flags Found</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with c3:
                    st.markdown(f"""
                        <div style="background-color: var(--secondary-background-color); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(128,128,128,0.2);">
                            <h2 style="margin: 0; font-size: 48px;">{doc_len}</h2>
                            <p style="margin: 0; opacity: 0.8;">Sentences Scanned</p>
                        </div>
                    """, unsafe_allow_html=True)

            # --- Red Flags List ---
            st.markdown("###")
            st.subheader("🚩 Detected Risks")
            
            if risks:
                for risk in risks:
                    pattern = re.compile(re.escape(risk['keyword']), re.IGNORECASE)
                    highlighted_sent = pattern.sub(f'<span class="highlight-risk">{risk["keyword"]}</span>', risk['sentence'])
                    
                    st.markdown(f"""
                    <div class="risk-card">
                        <strong style="color: #e74c3c;">⚠️ {risk['category']}</strong><br>
                        <span style="opacity: 0.9;">"{highlighted_sent}"</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No obvious red flags detected in this text.")

            # --- Summary ---
            st.markdown("###")
            st.subheader("📝 Quick Summary (TL;DR)")
            
            summary_html = '<div class="summary-box"><ul>'
            for sent in summary:
                summary_html += f"<li style='margin-bottom: 10px;'>{sent}</li>"
            summary_html += "</ul></div>"
            
            st.markdown(summary_html, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div class="footer">
        Developed by <b>Nayan Kshirsagar</b> | NLP Mini Project
    </div>
""", unsafe_allow_html=True)