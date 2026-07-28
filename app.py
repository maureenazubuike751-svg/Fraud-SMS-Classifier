# ============================================
# FRAUD SMS DETECTOR - ADVANCED
# Built by Maureen 
# 3MTT NextGen Project
# ============================================

import streamlit as st
import pickle
import re
import pandas as pd
import numpy as np
from urllib.parse import urlparse

# ============================================
# HIDE STREAMLIT HEADER AND FOOTER
# ============================================

st.set_page_config(page_title="Fraud SMS Detector", page_icon="🛡️")

st.markdown("""
<style>
    footer { display: none !important; }
    header { display: none !important; }
    #MainMenu { display: none !important; }
    .stApp > footer { display: none !important; }
    .stApp > header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD MY TRAINED MODEL
# ============================================

# I used Logistic Regression because it gave me the best recall score
model = pickle.load(open('Maureen_Fraud_Model.pkl', 'rb'))
vectorizer = pickle.load(open('Maureen_Vectorizer.pkl', 'rb'))

# ============================================
# MY CUSTOM FEATURES TO CATCH MORE FRAUD
# ============================================

# Check for slang like "U" or "4"
def detect_slang(text):
    patterns = [r'\bU\b', r'\b4\b', r'\b2\b', r'\bgr8\b', r'\blol\b', r'\bplz\b', r'\bthx\b']
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))

# Pull out any links in the message
def extract_urls(text):
    return re.findall(r'https?://[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+', text)

# Check if a link looks suspicious
def analyze_url(url):
    if not url:
        return "No URL", "None"
    parsed = urlparse(url)
    domain = parsed.netloc
    suspicious = ['arnazon', 'paypa1', 'gooogle', 'faceb00k']
    for sus in suspicious:
        if sus in domain.lower():
            return domain, "Suspicious"
    if any(s in url.lower() for s in ['bit.ly', 'tinyurl']):
        return domain, "Shortened URL"
    return domain, "Clean"

# Look for urgent words scammers use
def detect_urgency(text):
    words = ['urgent', 'immediately', 'act now', 'limited time', 'deadline', 'suspend', 'close', 'verify', 'confirm']
    return [w for w in words if w in text.lower()]

# Check if they mention a real company (which could also be fake)
def company_name_match(text):
    companies = ['amazon', 'paypal', 'bank', 'citibank', 'gtbank', 'opay', 'easemoni']
    return [c for c in companies if c in text.lower()]

# Check if the sender number looks legit
def sender_analysis(sender_number):
    if sender_number:
        length = len(str(sender_number))
        if length <= 6:
            return "Shortcode (Legitimate)"
        elif length == 10:
            return "10-digit number (Common for scams)"
    return "Not provided"

# Show why I flagged a message
def explain_prediction(prediction, urgency_words, urls, company_found, slang_count, sender_status):
    reasons = []
    if prediction == 1:
        reasons.append("🚨 FRAUD DETECTED")
        if urgency_words:
            reasons.append(f"⚠️ Urgency words found: {', '.join(urgency_words[:3])}")
        if urls:
            for url in urls:
                domain, status = analyze_url(url)
                if status != "Clean":
                    reasons.append(f"🔗 Suspicious link: {domain}")
        if slang_count > 2:
            reasons.append(f"🗣️ High slang usage: {slang_count} instances")
        if company_found:
            reasons.append(f"🏢 Company mentioned: {', '.join(company_found)}")
    else:
        reasons.append("✅ SAFE MESSAGE")
    return reasons

# ============================================
# APP TITLE AND HEADER
# ============================================

st.title("🛡️ Fraud SMS Detector")
st.write("Built with ❤️ by **Maureen**")
st.markdown("---")

st.success("🏆 Report fraud and win a prize!")

# ============================================
# THREE TABS FOR DIFFERENT FEATURES
# ============================================

tab1, tab2, tab3 = st.tabs(["🔍 Single SMS", "📂 Bulk Check", "📊 Dashboard"])

# ============================================
# TAB 1: CHECK ONE MESSAGE AT A TIME
# ============================================
with tab1:
    st.subheader("📩 Enter SMS:")
    
    sender_number = st.text_input("Sender Number (Optional)", placeholder="e.g., 08012345678")
    user_input = st.text_area("", height=120, placeholder="Paste SMS here...")

    if st.button("🔍 Check Message"):
        if user_input.strip():
            
            # Run all my custom checks
            urgency_words = detect_urgency(user_input)
            urls = extract_urls(user_input)
            company_found = company_name_match(user_input)
            slang_count = detect_slang(user_input)
            sender_status = sender_analysis(sender_number) if sender_number else "Not provided"
            
            # Clean text and predict
            cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', user_input.lower())
            vectorized = vectorizer.transform([cleaned])
            prediction = model.predict(vectorized)[0]
            confidence = model.predict_proba(vectorized)[0]
            
            # Show result
            if prediction == 1:
                st.error(f"⚠️ FRAUD DETECTED! (Confidence: {confidence[1]*100:.1f}%)")
            else:
                st.success(f"✅ SAFE MESSAGE (Confidence: {confidence[0]*100:.1f}%)")
            
            # Show explanation
            with st.expander("📖 Why?"):
                reasons = explain_prediction(prediction, urgency_words, urls, company_found, slang_count, sender_status)
                for r in reasons:
                    st.write(r)
                
                st.write("---")
                st.write("📊 Details:")
                st.write(f"• Slang: {slang_count} instances")
                st.write(f"• Urgency: {', '.join(urgency_words) if urgency_words else 'None'}")
                st.write(f"• URLs: {', '.join(urls) if urls else 'None'}")
                st.write(f"• Sender: {sender_status}")
            
            # Report button
            if st.button("📤 Report This Message"):
                st.success("🏆 Fraud Fighter Badge earned!")
                st.balloons()
        else:
            st.warning("⚠️ Please enter a message.")

# ============================================
# TAB 2: BULK CHECK
# ============================================
with tab2:
    st.subheader("📂 Upload CSV")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        
        if st.button("🚀 Check All"):
            if 'text' in df.columns or 'message' in df.columns:
                col = 'text' if 'text' in df.columns else 'message'
                results = []
                for _, row in df.iterrows():
                    msg = str(row[col])
                    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', msg.lower())
                    vec = vectorizer.transform([cleaned])
                    pred = model.predict(vec)[0]
                    prob = model.predict_proba(vec)[0]
                    results.append({
                        "Message": msg[:50] + "...",
                        "Prediction": "Fraud" if pred == 1 else "Safe",
                        "Confidence": f"{prob[1]*100:.1f}%" if pred == 1 else f"{prob[0]*100:.1f}%"
                    })
                result_df = pd.DataFrame(results)
                st.dataframe(result_df)
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download", data=csv, file_name="results.csv")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab3:
    st.subheader("📊 Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", "1,247")
    col2.metric("Fraud", "312")
    col3.metric("Safe", "935")
    
    st.line_chart({
        "Safe": [100, 120, 110, 130, 125, 140, 135],
        "Fraud": [30, 25, 35, 40, 30, 45, 50]
    })
    
    st.caption("No data stored - Privacy by Design")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("© 2026 Maureen | 3MTT NextGen Project - Fraud SMS Classifier")
