# ============================================
# FRAUD SMS DETECTOR - STREAMLIT APP
# Built by Maureen for My 3MTT NextGen Project 
# ============================================

# Imported the libraries we needed 
import streamlit as st          # For building the web app interface
import pickle                   # To load our saved model and vectorizer
import re                       # For cleaning text (removing punctuation)

# ============================================
# LOADED THE TRAINED MODEL AND VECTORIZER
# ============================================

# These files were saved from my Google Colab training
# 'Maureen_Fraud_Model.pkl' contains the trained Logistic Regression model
# I chose Logistic Regression because it gave a higher RECALL score,
# which means it catches more fraud messages, meaning (fewer false negatives).

model = pickle.load(open('Maureen_Fraud_Model.pkl', 'rb'))
vectorizer = pickle.load(open('Maureen_Vectorizer.pkl', 'rb'))

# ============================================
# SET UP THE APP INTERFACE
# ============================================

st.set_page_config(page_title="Fraud SMS Detector", page_icon="🛡️")

st.title("🛡️ Fraud SMS Detector")
st.write("Built with ❤️ by **Maureen** for 3MTT NextGen")
st.markdown("---")

# ============================================
# USER INPUT SECTION
# ============================================

st.subheader("📩 Enter an SMS to check:")
user_input = st.text_area("", height=100, placeholder="Type or paste an SMS message here...")

# ============================================
# PREDICTION LOGIC  
# This is where the model evaluates the user's input
# and decides whether the message is fraud or safe.
# (It's basically where the fun happens 😉)
# ============================================

if st.button("🔍 Check Message"):
    if user_input.strip():
        
        # STEP 1: Clean the text (same cleaning I used in training)
        # Remove punctuation and convert to lowercase
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', user_input.lower())
        
        # STEP 2: Convert text to numbers using the same vectorizer
        vectorized = vectorizer.transform([cleaned])
        
        # STEP 3: Predict if it's fraud (1) or safe (0)
        prediction = model.predict(vectorized)[0]
        confidence = model.predict_proba(vectorized)[0]
        
        # STEP 4: Show the result to the user
        if prediction == 1:
            st.error(f"⚠️ **FRAUD DETECTED!** (Confidence: {confidence[1]*100:.1f}%)")
            st.warning("This message appears to be fraudulent. Do not respond or click any links.")
        else:
            st.success(f"✅ **SAFE MESSAGE** (Confidence: {confidence[0]*100:.1f}%)")
            st.info("This message appears to be legitimate.")
    
    else:
        st.warning("⚠️ Please enter a message first.")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("© 2026 Maureen | 3MTT NextGen Project - Fraud SMS Classifier")
