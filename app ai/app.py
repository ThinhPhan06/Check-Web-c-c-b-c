import streamlit as st
import requests
from bs4 import BeautifulSoup
import tldextract
import whois
import pandas as pd
import socket

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

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return "Không xác định"

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

    # Thêm IP
    features["IP"] = get_ip(domain)

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

# Hiệu ứng nền mưa sao băng + giao diện dark cố định
# ...existing code...
st.markdown("""
<style>
body {
  background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%) !important;
  min-height: 100vh;
  overflow-x: hidden;
  font-family: 'Inter', 'Anton', sans-serif;
  color: #e6eef6;
}
.night {
  position: fixed;
  width: 100vw;
  height: 100vh;
  left: 0; top: 0;
  pointer-events: none;
  z-index: -10;
  transform: rotateZ(45deg);
}
.shooting_star {
  position: absolute;
  width: 100px;
  height: 2px;
  background: linear-gradient(-45deg, rgba(95,145,255,1), rgba(0,0,255,0));
  border-radius: 999px;
  filter: drop-shadow(0 0 6px rgba(105,155,255,1));
  opacity: 0.7;
  animation:
    tail 3s ease-in-out infinite,
    shooting 3s ease-in-out infinite;
}
.shooting_star::before,
.shooting_star::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(-45deg, rgba(0,0,255,0), rgba(95,145,255,1), rgba(0,0,255,0));
  border-radius: 100%;
  animation: shining 3s ease-in-out infinite;
}
.shooting_star::before {
  width: 30px;
  transform: translateX(50%) rotateZ(45deg);
}
.shooting_star::after {
  width: 30px;
  transform: translateX(50%) rotateZ(-45deg);
}
.shooting_star:nth-child(1)  { top: 10%; left: 15%; animation-delay: 0s; }
.shooting_star:nth-child(2)  { top: 20%; left: 80%; animation-delay: 1s; }
.shooting_star:nth-child(3)  { top: 30%; left: 60%; animation-delay: 2s; }
.shooting_star:nth-child(4)  { top: 40%; left: 25%; animation-delay: 1.5s; }
.shooting_star:nth-child(5)  { top: 50%; left: 70%; animation-delay: 0.5s; }
.shooting_star:nth-child(6)  { top: 60%; left: 40%; animation-delay: 2.5s; }
.shooting_star:nth-child(7)  { top: 70%; left: 55%; animation-delay: 1.2s; }
.shooting_star:nth-child(8)  { top: 80%; left: 30%; animation-delay: 2.2s; }
.shooting_star:nth-child(9)  { top: 90%; left: 75%; animation-delay: 0.8s; }
.shooting_star:nth-child(10) { top: 15%; left: 50%; animation-delay: 1.8s; }
.shooting_star:nth-child(11) { top: 25%; left: 35%; animation-delay: 2.8s; }
.shooting_star:nth-child(12) { top: 35%; left: 85%; animation-delay: 1.1s; }
.shooting_star:nth-child(13) { top: 45%; left: 20%; animation-delay: 2.1s; }
.shooting_star:nth-child(14) { top: 55%; left: 65%; animation-delay: 0.3s; }
.shooting_star:nth-child(15) { top: 65%; left: 10%; animation-delay: 1.6s; }
.shooting_star:nth-child(16) { top: 75%; left: 60%; animation-delay: 2.6s; }
.shooting_star:nth-child(17) { top: 85%; left: 45%; animation-delay: 0.9s; }
.shooting_star:nth-child(18) { top: 95%; left: 80%; animation-delay: 1.4s; }
.shooting_star:nth-child(19) { top: 20%; left: 20%; animation-delay: 2.4s; }
.shooting_star:nth-child(20) { top: 80%; left: 85%; animation-delay: 0.7s; }
@keyframes tail {
  0%   { width: 0; opacity: 0; }
  10%  { width: 100px; opacity: 1; }
  100% { width: 0; opacity: 0; }
}
@keyframes shining {
  0%   { width: 0; opacity: 0; }
  50%  { width: 30px; opacity: 1; }
  100% { width: 0; opacity: 0; }
}
@keyframes shooting {
  0%   { transform: translateX(0); }
  100% { transform: translateX(300px); }
}
.main-container {
  max-width: 800px;
  margin: 48px auto 0 auto;
  background: rgba(24, 31, 43, 0.96);
  border-radius: 22px;
  box-shadow: 0 8px 40px #0008;
  padding: 40px 32px 32px 32px;
  position: relative;
  z-index: 2;
}
.app-title {
  font-size: 2.5rem;
  font-weight: 900;
  letter-spacing: 1px;
  color: #7c5cff;
  text-align: center;
  margin-bottom: 10px;
  text-shadow: 0 2px 16px #3db5ff44;
}
.app-desc {
  text-align: center;
  color: #b6c3e0;
  font-size: 1.15rem;
  margin-bottom: 8px;
}
.author {
  text-align: center;
  color: #8ecfff;
  font-size: 1rem;
  margin-bottom: 28px;
  font-weight: 600;
}
/* Đổi màu nền và chữ cho textarea và input thành trắng */
.stTextArea textarea, .stTextInput input {
  border-radius: 12px;
  border: 1.5px solid #7c5cff55;
  background: #fff !important;
  color: #222b3a !important;
  font-size: 1.08em;
  min-height: 110px;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border: 2px solid #3db5ff;
  background: #f3f6fa !important;
  color: #222b3a !important;
}
.stButton > button {
  background: linear-gradient(90deg, #7c5cff 0%, #3db5ff 100%);
  color: #fff;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  padding: 0.8em 2.2em;
  box-shadow: 0 4px 16px #7c5cff55;
  transition: background 0.3s, transform 0.15s, box-shadow 0.3s;
  font-size: 1.15em;
  letter-spacing: 0.03em;
  outline: none;
  cursor: pointer;
  position: relative;
  z-index: 1;
  margin-top: 10px;
  margin-bottom: 18px;
}
.stButton > button:hover {
  background: linear-gradient(90deg, #3db5ff 0%, #7c5cff 100%);
  color: #fff;
  transform: scale(1.06) translateY(-2px);
  box-shadow: 0 8px 32px #3db5ff99, 0 2px 8px #7c5cff44;
}
.stDataFrame, .stTable {
  border-radius: 14px;
  overflow: hidden;
  background: #181f2b;
  margin-top: 18px;
}
.result-card {
  padding:18px; 
  margin:14px 0; 
  border-radius:14px; 
  background:linear-gradient(90deg, #232b3a 60%, #2e3a5a 100%);
  color:white; 
  box-shadow:0 4px 24px #0005;
  border: 1.5px solid #7c5cff55;
  font-size: 1.08em;
}
.result-card.safe {
  background:linear-gradient(90deg, #1e3a2e 60%, #3db5ff 100%);
  border: 1.5px solid #3db5ff99;
}
.result-card.danger {
  background:linear-gradient(90deg, #4d2323 60%, #ff5252 100%);
  border: 1.5px solid #ff525299;
}
@media (max-width: 900px) {
  .main-container { padding: 18px 4vw; }
  .app-title { font-size: 1.5rem; }
}
</style>
<div class="night">
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
  <div class="shooting_star"></div>
</div>
""", unsafe_allow_html=True)
# ...existing code...

# Main container layout
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="app-title">🌐 DEMO NO LIMIT TEAM – AI Website Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-desc">Bài dự thi AI phân tích website có dấu hiệu cờ bạc, cá độ bóng đá hoặc nội dung cấm.</div>', unsafe_allow_html=True)
    st.markdown('<div class="author">ĐƯỢC PHÁT TRIỂN BỞI NO LIMIT TEAM <b>LEADER PHÙNG GIA HUY, PHAN PHÚC THỊNH</b>.</div>', unsafe_allow_html=True)

    urls = st.text_area("Nhập danh sách URL (mỗi dòng 1 URL):", 
                        "https://example.com\nhttps://keonhacai1.tv")

    if st.button("🚀 Quét danh sách URL"):
        url_list = [u.strip() for u in urls.strip().split("\n") if u.strip()]
        results = []

        progress = st.progress(0)
        for i, url in enumerate(url_list):
            text = crawl_url(url)
            if not text:
                features = {"URL": url, "Verdict": "❌ Không lấy được", "IP": "Không xác định"}
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
            verdict = row.get("Verdict", "")
            card_class = "result-card safe" if "An toàn" in verdict else "result-card danger"
            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>🔗 URL:</b> {row.get('URL','')} <br>
                    <b>📌 Kết quả:</b> {row.get('Verdict','')} <br>
                    <b>🌍 Quốc gia:</b> {row.get('Country','Unknown')} <br>
                    <b>🌐 IP:</b> {row.get('IP','Không xác định')} <br>
                    <b>⚠️ Loại nghi ngờ:</b> {row.get('Category','Safe')}
                </div>
                """, unsafe_allow_html=True
            )

        st.success("✅ Quét hoàn tất!")
    st.markdown('</div>', unsafe_allow_html=True)