import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(
    page_title="KARIM | WhatsApp Sender PRO",
    layout="wide",  # تغيير إلى wide لاستغلال العرض
    initial_sidebar_state="expanded"
)

# فلترة الأرقام لأي نص وتوحيدها بصيغة رقمية فقط
def extract_numbers(text):
    lines = text.replace(",", "\n").splitlines()
    numbers = []
    for line in lines:
        digits = re.sub(r'\D', '', line)  # يزيل أي شيء غير رقم
        if len(digits) >= 8:
            numbers.append(digits)
    return numbers

def clean_number(n):
    return re.sub(r'\D', '', str(n))

#########################
# ---------- CSS -----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
body, [class*="css"] {
  font-family: 'Inter', Arial, sans-serif !important;
}
.stApp {
  background: linear-gradient(120deg, #f7fafd 70%, #e0e7ef 100%) fixed !important;
  min-height: 100vh;
}
#top-bar-karim {
  width: 100vw; 
  background: linear-gradient(90deg,#e3f2fd 50%,#b3ecf7 100%);
  margin: 0 -6vw 35px -6vw;
  padding: 19px 0 12px 0;
  text-align: center;
  border-radius: 0 0 32px 32px;
  box-shadow: 0 5px 24px 0 #38bdf820;
  font-size: 1.17rem; font-family:'Inter',sans-serif;
  color: #1674db;
  font-weight: 700;
  letter-spacing: 2px;
}
.glass-box-main {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 32px 0 rgba(24, 40, 100, 0.12), 0 2px 8px #38bdf822;
  padding: 38px 40px 38px 40px;
  margin: 22px 0 28px 0;
  border: 1.6px solid #e3e9f8;
  min-width: 440px;
  max-width: 650px;
  animation: popUp .7s cubic-bezier(.56,.19,.34,.98);
  transition: box-shadow .19s, transform .14s;
}
@media (max-width: 1100px) {
  .glass-box-main {max-width: 95vw; padding: 18px 2vw;}
}
@keyframes popUp {
  0% {opacity:0;transform: scale(.96) translateY(32px);}
  100% {opacity:1;transform: scale(1) translateY(0);}
}
.karim-logo {
  font-family: 'Inter', sans-serif;
  font-size: 2.8rem; font-weight: 900; letter-spacing: 9px;
  margin-bottom: 0.3rem; text-align: center;
  background: linear-gradient(90deg, #2563eb 35%, #38bdf8 90%, #22d3ee 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; text-fill-color: transparent;
  user-select: none;
  text-shadow: 0 2px 18px #38bdf866;
  animation: popLogo 1s cubic-bezier(.18,1.6,.52,1);
}
@keyframes popLogo {
  0% {letter-spacing:0px;opacity:0;transform: scale(.7);}
  80% {letter-spacing:19px;}
  100% {opacity:1;}
}
.title-pro {
  font-size: 1.28rem;
  margin-bottom: 1.2rem;
  color: #2563eb;
  text-align: center;
  letter-spacing: 1.7px;
  font-family: 'Inter', sans-serif;
  font-weight: bold;
  animation: fadeDown .7s;
}
@keyframes fadeDown {
  0% {opacity:0;transform:translateY(-22px);}
  100% {opacity:1;transform:translateY(0);}
}
.stRadio label, .stTextInput label, .stTextArea label, .stMarkdown h3, .stSelectbox label {
  color: #2563eb !important;
  font-weight: 700 !important;
  letter-spacing: .04em;
  font-size: 1.03em;
}
.stRadio span, .stRadio div, .stRadio p, .stInfo {
  color: #334155 !important;
  font-weight: 600 !important;
}
input, textarea {
  border-radius: 10px !important;
  background: #f4f8fb !important;
  color: #0f172a !important;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 2px 7px #38bdf812;
  font-size: 1.09em;
  transition: border .12s;
}
input:focus, textarea:focus {
  border: 2.2px solid #38bdf8 !important;
  background: #fff !important;
}
.stButton>button {
  background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%);
  border-radius: 12px !important;
  color: #fff !important;
  font-weight: bold;
  font-family: 'Inter', sans-serif;
  font-size: 1.09em; letter-spacing:.1px;
  box-shadow: 0 4px 16px #2563eb25;
  border: none !important;
  transition: box-shadow .16s, transform .11s, background .16s;
}
.stButton>button:hover {
  background: linear-gradient(90deg, #38bdf8 0%, #22d3ee 100%);
  color: #fff !important;
  box-shadow: 0 10px 26px #2563eb44;
  transform: translateY(-2px) scale(1.03);
}
.stButton>button:active {
  transform: scale(.98);
  box-shadow: 0 2px 4px #2563eb29;
}
.numbers-list-karim {
  display: flex; flex-direction: column; gap: 2.5px; font-size: 13.6px;
  background: #f1f7fd; border-radius: 7px; padding: 7px 11px 7px 13px; margin-bottom: 11px;
  max-height: 95px; overflow-y: auto; color: #2563eb;
  border: 1.2px solid #e5eaf7;
  box-shadow: 0 2px 8px #38bdf80f;
  font-family: 'Inter', sans-serif;
}
.numbers-list-karim .active {
  background: linear-gradient(90deg,#38bdf845 60%,#22d3ee70 100%);
  border-radius: 6px; font-weight: bold; color: #fff;
  font-size: 1.08em; border-left: 4px solid #2563eb; padding-left: 3px;
  box-shadow: 0 2px 9px #22d3ee29;
}
.footer-karim {
  margin-top: 2.1rem; font-size: 1.05rem; color: #2563eb;
  text-align: center; letter-spacing: 1.1px;
  font-family: 'Inter', sans-serif;
  opacity: .97; font-weight: bold; padding-bottom: 13px;
  animation: fadeUp 1.2s; text-shadow: 0 1px 7px #38bdf811;
}
@keyframes fadeUp {0% {opacity:0;transform:translateY(22px);}100% {opacity:1;transform:translateY(0);}
}
.sider-karim {
  background: linear-gradient(120deg, #e0eaff 80%, #f1f5f9 100%);
  border-radius: 24px;
  box-shadow: 0 8px 24px 0 #dbeafe25;
  padding: 29px 18px 25px 18px;
  margin: 29px 0;
  min-width: 240px; max-width: 310px;
  font-family:'Inter',sans-serif;
  font-size: 1.05em;
}
.sider-karim .sider-title {
  color: #1877f2; font-size: 1.14em; font-weight: 900; letter-spacing: 2.4px; margin-bottom: 10px;
  margin-top: 1px;
}
.sider-karim .sider-note {
  color: #0ea5e9; font-size: 1.01em; margin-bottom: 6px; margin-top: 0;
  font-weight: bold;
}
.sider-karim .sider-mini {
  color: #475569; font-size: .97em; margin-bottom: 13px; margin-top: 9px;
}
.sider-karim .sider-logo {
  text-align:center; margin-top:27px;
}
.sider-karim .sider-logo span {
  font-size: 2.1em; color: #2563eb; font-weight: 900; letter-spacing:7px; text-shadow: 0 2px 8px #a1cdf733;
}
</style>
""", unsafe_allow_html=True)

#########################
# ---- TEMPLATES --------
templates = { ... } # لا تغير هذا الجزء! نفس الموجود في كودك

# ======== Layout structure =========
# جانب يمين | وسط | جانب يسار
col1, col2, col3 = st.columns([1, 2.2, 1])

with col1:
    st.markdown("""
    <div class="sider-karim">
        <div class="sider-title">About</div>
        <div class="sider-mini">👋 This tool helps you send bulk WhatsApp messages to any country with filtering and cleaning numbers.</div>
        <div class="sider-note">✨ Supports both manual input and smart CSV uploading.</div>
        <hr style="margin:11px 0;">
        <div class="sider-mini">
        <b>How to use?</b>
        <ol>
            <li>Paste or upload your contact list.</li>
            <li>Filter numbers and preview your message.</li>
            <li>Send via WhatsApp Web/App.</li>
        </ol>
        </div>
        <div class="sider-logo"><span>K</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="sider-karim">
        <div class="sider-title">Quick Tips</div>
        <div class="sider-mini">
        <b>• CSV Example:</b><br>
        <code>number,name,country</code><br>
        <code>201111223344,Mohamed,Egypt</code>
        <br><br>
        <b>• Clean numbers auto</b><br>
        <b>• Works with all countries</b>
        <br><br>
        <b>Contact: </b> <a href="mailto:karim.amsha@gmail.com">karim.amsha@gmail.com</a>
        </div>
        <div class="sider-logo"><span>💬</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div id="top-bar-karim">Welcome to <span style="color:#1976d2">KARIM WhatsApp Sender PRO</span> | 🚀 Clean, Filter & Broadcast like a Pro!</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-box-main">', unsafe_allow_html=True)

    st.markdown('<div class="karim-logo">KARIM</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-pro">WhatsApp Broadcast Sender</div>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    mode = st.radio(
        "Choose mode:",
        ["Simple: Numbers Only", "Smart: Personalized Name & Country"],
        horizontal=True,
        key="mode"
    )

    st.markdown('<hr>', unsafe_allow_html=True)

    # ------------- Simple Mode -------------
    if mode == "Simple: Numbers Only":
        lang = st.radio("Language", [
            "🇬🇧 English", "🇸🇦 العربية", "🇹🇷 Türkçe", "🇫🇷 Français", "🇪🇸 Español"
        ], horizontal=True, key="lang_radio")
        lang_code = {
            "🇬🇧 English": "en",
            "🇸🇦 العربية": "ar",
            "🇹🇷 Türkçe": "tr",
            "🇫🇷 Français": "fr",
            "🇪🇸 Español": "es"
        }[lang]
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        numbers_raw = st.text_area("Numbers (comma/newline/any format)", placeholder="Paste numbers, comma, newline, or any format (even tel +254 722 206312)")
        numbers = extract_numbers(numbers_raw)
        names = [''] * len(numbers)
        countries = [''] * len(numbers)
        msg_template = templates[lang_code]

        if numbers_raw:
            st.markdown("#### Filtered Numbers:")
            st.code('\n'.join(numbers), language="text")
            st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt")

    # ------------- Smart Mode -------------
    else:
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio2")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        st.info("You can upload a CSV file (number,name,country) or enter data manually 👇")
        st.download_button(
            label="⬇️ Download example CSV",
            data="number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n",
            file_name="example_contacts.csv",
            mime="text/csv",
        )
        data_opt = st.radio("Input method:", ["Upload CSV file", "Manual entry"], horizontal=True, key="smart_input")
        df = None
        if data_opt == "Upload CSV file":
            uploaded_file = st.file_uploader("Upload CSV (number,name,country)", type=["csv"])
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file).dropna(subset=["number"])
                    df["number"] = df["number"].apply(clean_number)
                    df = df[df["number"].str.len() >= 8]
                    df = df.astype(str)
                    st.success(f"{len(df)} contacts loaded.")
                except Exception as e:
                    st.error("Invalid CSV file or missing columns (number,name,country).")
        else:
            st.info("Enter data manually (add/remove rows as needed):")
            example_data = pd.DataFrame({
                'number': ['201111223344', '971500000001'],
                'name': ['Mohamed', 'Ahmed'],
                'country': ['Egypt', 'UAE']
            })
            df = st.data_editor(
                example_data,
                num_rows="dynamic",
                use_container_width=True,
                key="editor"
            )
            df["number"] = df["number"].apply(clean_number)
            df = df[df["number"].str.len() >= 8]
            df = df.astype(str)
        if df is not None and not df.empty:
            numbers = df['number'].tolist()
            names = df['name'].tolist() if 'name' in df.columns else ['']*len(df)
            countries = df['country'].tolist() if 'country' in df.columns else ['']*len(df)
        else:
            numbers, names, countries = [], [], []
        msg_template = st.text_area(
            "Write message template (use {name}, {country}, {number}):",
            value="Hello {name} from {country}, we have new products for the {country} market!",
            height=120,
            key="smart_template"
        )

        if df is not None and not df.empty:
            st.markdown("#### Filtered Numbers:")
            st.code('\n'.join(numbers), language="text")
            st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt")

    # ======= حافظ التقدم حتى بعد الريفرش (باستخدام session_state) =======
    if 'current' not in st.session_state:
        st.session_state.current = 0
    if 'skipped' not in st.session_state:
        st.session_state.skipped = set()

    # -------- Progress Circle --------
    if numbers:
        percent = int((st.session_state.current+1) / len(numbers) * 100)
        st.markdown(
            f'''
            <div style="margin-bottom:6px;"><b style="color:#1565c0;font-size:1.05rem">Progress:</b></div>
            <div style="margin-bottom:9px;">
                <div style="width:62px;height:62px;margin:auto;position:relative;">
                    <div style="width:62px;height:62px;border-radius:50%;background:conic-gradient(#26c6da {percent}%, #e3f2fd {percent}% 100%);display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px #1976d225;position:absolute;top:0;left:0;animation:popIn .7s;">
                        <span style="font-size:1.1rem;color:#1565c0;font-family:'Cairo',sans-serif;font-weight:900;letter-spacing:2px;z-index:1;margin:auto;">{st.session_state.current+1}/{len(numbers)}</span>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True
        )

    if st.button("🔄 Reset Progress"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    if numbers:
        try:
            msg_personal = msg_template.format(
                name=names[st.session_state.current] if names else '',
                country=countries[st.session_state.current] if countries else '',
                number=numbers[st.session_state.current]
            )
        except Exception as e:
            msg_personal = "⚠️ Please check your template or data"
        message = st.text_area(
            "Message",
            value=msg_personal,
            key="msgboxfinal",
            help="Edit before sending if you want",
            height=120,
        )
        st.write(f"**Contact:** {min(st.session_state.current+1, len(numbers))} / {len(numbers)}")
        info = f'{numbers[st.session_state.current]}'
        if mode == "Smart: Personalized Name & Country" and names and countries:
            info += f" — {names[st.session_state.current]} — {countries[st.session_state.current]}"
        st.write(
            f'<span style="display:inline-block;padding:7px 19px;background:linear-gradient(90deg,#e3f2fd,#b3ecf7);color:#1565c0;'
            'border-radius:20px;font-family:Roboto,sans-serif;font-size:1.07rem;font-weight:bold;'
            'box-shadow:0 1px 7px #1976d217;margin-bottom:9px;">'
            f'{info}</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="numbers-list-karim">' +
            "".join([
                f"<div class='{ 'active' if i == st.session_state.current else ''}'>{i+1}. {numbers[i]}{(' - ' + names[i]) if (mode=='Smart: Personalized Name & Country' and names and names[i]) else ''}{(' - ' + countries[i]) if (mode=='Smart: Personalized Name & Country' and countries and countries[i]) else ''}</div>"
                for i in range(len(numbers))
            ]) +
            "</div>", unsafe_allow_html=True
        )

        cols = st.columns([1.2, 1.2, 1.7, 1.2])
        prev_disabled = st.session_state.current <= 0
        next_disabled = st.session_state.current >= len(numbers)-1
        skip_disabled = numbers[st.session_state.current] in st.session_state.skipped

        if cols[0].button("← Prev", disabled=prev_disabled, key="prev"):
            if st.session_state.current > 0:
                st.session_state.current -= 1

        if cols[1].button("Skip", disabled=skip_disabled, key="skip"):
            st.session_state.skipped.add(numbers[st.session_state.current])
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

        if cols[2].button("Open WhatsApp", disabled=not message.strip(), key="open"):
            msg_encoded = urllib.parse.quote(message.strip())
            num = numbers[st.session_state.current]
            if platform_type == "web":
                url = f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"
            else:
                url = f"https://wa.me/{num}?text={msg_encoded}"
            st.markdown(
                f"<div style='text-align:center; margin-top:6px;'>"
                f"<a href='{url}' target='_blank' style='font-weight:bold; color:#1976d2; font-size:18px; letter-spacing:.5px;'>"
                "🚀 Click here if WhatsApp didn't open automatically</a></div>", unsafe_allow_html=True
            )
            st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

        if cols[3].button("Next →", disabled=next_disabled, key="next"):
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-karim">✦ Powered by <span style="font-family:Cairo,sans-serif;letter-spacing:2.3px;color:#1976d2;">Karim OTHMAN 😍</span> &copy; 2025</div>', unsafe_allow_html=True)
