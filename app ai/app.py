import streamlit as st
import requests
from bs4 import BeautifulSoup
import tldextract
import whois
import pandas as pd
import matplotlib.pyplot as plt

# ========== Hàm tiện ích ==========
def crawl_url(url):
    """Lấy HTML và text từ URL"""
    try:
        r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        title = soup.title.string if soup.title else ""
        return title + " " + text
    except Exception:
        return ""

def extract_features(url, text):
    features = {}
    ext = tldextract.extract(url)
    domain = ext.domain + "." + ext.suffix
    features["URL"] = url
    features["Domain"] = domain

    # WHOIS + country
    try:
        w = whois.whois(domain)
        features["Registrar"] = str(w.registrar) if w.registrar else "Unknown"
        features["Country"] = str(w.country) if w.country else "Unknown"
    except:
        features["Registrar"] = "Unknown"
        features["Country"] = "Unknown"

    if features["Country"] == "Unknown":
        tld = ext.suffix.lower()
        tld_map = {"vn": "Vietnam", "kh": "Cambodia", "com": "Global", "org": "Global"}
        features["Country"] = tld_map.get(tld, "Unknown")

    # keyword categories
    categories = {
        "Gambling / Cá cược": ["casino", "slot", "baccarat", "poker", "blackjack",
                               "bet", "keonhacai", "odds", "cá cược", "cờ bạc",
                               "bầu cua", "tài xỉu"],
        "Bóng đá cá độ": ["bóng đá", "soi kèo", "keo nha cai", "tỷ lệ kèo", "livescore"],
        "Nội dung cấm": ["lô đề", "xổ số", "crack", "hack", "xxx", "sex", "chịch", "dâm", "lồn"]
    }

    for cat, kws in categories.items():
        features[f"{cat}"] = sum(text.lower().count(k) for k in kws)

    # quyết định loại nghi ngờ
    suspicious = {k: features[k] for k in categories.keys()}
    label, max_score = max(suspicious.items(), key=lambda x: x[1])
    if max_score == 0:
        features["Verdict"] = "✅ An toàn"
        features["Category"] = "Safe"
    else:
        features["Verdict"] = f"⚠️ Nghi ngờ: {label}"
        features["Category"] = label

    return features


# ========== UI Streamlit ==========
st.set_page_config(page_title="AI Website Scanner", page_icon="🌐", layout="wide")

st.title("🌐 DEMO NO LIMIT TEAM – AI Website Scanner")
st.write("Bài dự thi AI phân tích website có dấu hiệu cờ bạc, cá độ bóng đá hoặc nội dung cấm.")
st.write("ĐƯỢC PHÁT TRIỂN BỞI NO LIMIT TEAM **LEADER PHÙNG GIA HUY, PHAN PHÚC THỊNH**.")

urls = st.text_area("Nhập danh sách URL (mỗi dòng 1 URL):", 
                    "https://example.com\nhttps://keonhacai1.tv")

if st.button("🚀 Quét danh sách URL"):
    url_list = [u.strip() for u in urls.strip().split("\n") if u.strip()]
    results = []

    progress = st.progress(0)
    for i, url in enumerate(url_list):
        text = crawl_url(url)
        if not text:
            results.append({"URL": url, "Verdict": "❌ Không lấy được"})
        else:
            features = extract_features(url, text)
            results.append(features)
        progress.progress((i+1)/len(url_list))

    df = pd.DataFrame(results)

    # Bảng kết quả
    st.subheader("📊 Kết quả phân tích")
    st.dataframe(df)

    # Cards đẹp cho từng URL
    for _, row in df.iterrows():
        color = "#4CAF50" if "An toàn" in row["Verdict"] else "#FF5252"
        st.markdown(
            f"""
            <div style="padding:12px; margin:6px 0; border-radius:10px; background:{color}; color:white">
                <b>🔗 URL:</b> {row['URL']} <br>
                <b>📌 Kết quả:</b> {row['Verdict']} <br>
                <b>🌍 Quốc gia:</b> {row.get('Country','Unknown')} <br>
                <b>⚠️ Loại nghi ngờ:</b> {row.get('Category','Safe')}
            </div>
            """, unsafe_allow_html=True
        )

    # DEV ghuy
 
    st.success("✅ Quét xong toàn bộ!")
