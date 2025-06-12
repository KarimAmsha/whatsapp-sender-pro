import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="KARIM | WhatsApp Sender PRO", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
body, [class*="css"] {
  font-family: 'Inter', Arial, sans-serif !important;
}
.stApp {
  background: linear-gradient(120deg, #f9fafb 70%, #e0e7ef 100%) fixed !important;
  min-height: 100vh;
}
.glass-box {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 6px 24px 0 rgba(24, 40, 100, 0.08), 0 1px 4px #38bdf844;
  padding: 32px 24px 20px 24px;
  margin: 36px auto 12px auto;
  max-width: 540px;
  border: 1.3px solid #e3e9f8;
  animation: popUp .7s cubic-bezier(.56,.19,.34,.98);
  transition: box-shadow .19s, transform .14s;
}
.glass-box:hover {
  box-shadow: 0 14px 38px 0 #2563eb19, 0 1px 7px #22d3ee22;
  transform: translateY(-3px) scale(1.012);
}
@keyframes popUp {
  0% {opacity:0;transform: scale(.95) translateY(32px);}
  100% {opacity:1;transform: scale(1) translateY(0);}
}
.karim-logo {
  font-family: 'Inter', sans-serif;
  font-size: 2.25rem; font-weight: 900; letter-spacing: 8px;
  margin-bottom: 0.1rem; text-align: center;
  background: linear-gradient(90deg, #2563eb 35%, #38bdf8 90%, #22d3ee 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; text-fill-color: transparent;
  user-select: none;
  text-shadow: 0 2px 14px #38bdf866;
  animation: popLogo 1s cubic-bezier(.18,1.6,.52,1);
}
@keyframes popLogo {
  0% {letter-spacing:0px;opacity:0;transform: scale(.7);}
  80% {letter-spacing:16px;}
  100% {opacity:1;}
}
.title-pro {
  font-size: 1.19rem;
  margin-bottom: 1.1rem;
  color: #2563eb;
  text-align: center;
  letter-spacing: 1.6px;
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
  font-size: 1.01em;
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
  font-size: 1.07em;
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
  font-size: 1.08em; letter-spacing:.1px;
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
@keyframes fadeUp {0% {opacity:0;transform:translateY(22px);}100% {opacity:1;transform:translateY(0);}}
</style>
""", unsafe_allow_html=True)

# === Templates ===
templates = {
    'en': """Hello 👋

We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).

We specialize in producing high-quality snacks such as:
🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.

We're always eager to connect with reliable partners and explore new markets together. 🤝

If you are interested, we are happy to share our catalog, price list, and discuss how we can work together.

Looking forward to your reply!

Best regards,
Sales Department""",
    'ar': """مرحبًا 👋

نحن قسم المبيعات في شركة EUROSWEET GIDA LTD. ŞTİ. (إسطنبول - تركيا).

نحن متخصصون في إنتاج سناكات عالية الجودة مثل:
🍪 الكرواسون، الكيك، البسكويت، الدونات، الجيلي، والويفر.

نسعى دائمًا للتواصل مع شركاء موثوقين واستكشاف أسواق جديدة معًا 🤝

إذا كنت مهتمًا، يسعدنا أن نرسل لك الكتالوج وقائمة الأسعار ومناقشة فرص التعاون المشترك.

بانتظار ردكم الكريم!

تحياتنا،
قسم المبيعات""",
    'tr': """Merhaba 👋

Biz EUROSWEET GIDA LTD. ŞTİ. (İstanbul – Türkiye) Satış Departmanıyız.

Aşağıdaki yüksek kaliteli atıştırmalıkları üretiyoruz:
🍪 Kruvasan, Kek, Bisküvi, Donut, Jöle ve Gofret.

Her zaman güvenilir ortaklarla bağlantı kurmak ve yeni pazarları birlikte keşfetmek isteriz. 🤝

İlgileniyorsanız, size kataloğumuzu ve fiyat listemizi paylaşabilir, iş birliğini konuşabiliriz.

Cevabınızı dört gözle bekliyoruz!

Saygılarımızla,
Satış Departmanı""",
    'fr': """Bonjour 👋

Nous sommes le département commercial de EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turquie).

Nous sommes spécialisés dans la production de snacks de haute qualité tels que :
🍪 Croissants, gâteaux, biscuits, donuts, gelées et gaufrettes.

Nous sommes toujours prêts à collaborer avec des partenaires fiables et à explorer de nouveaux marchés ensemble. 🤝

Si vous êtes intéressé, nous serions heureux de partager notre catalogue, notre liste de prix et de discuter des opportunités de collaboration.

Dans l’attente de votre réponse !

Cordialement,
Département des ventes""",
    'es': """Hola 👋

Somos el Departamento de Ventas de EUROSWEET GIDA LTD. ŞTİ. (Estambul – Turquía).

Estamos especializados en la producción de snacks de alta calidad como:
🍪 Cruasanes, pasteles, galletas, donas, gelatinas y barquillos.

Siempre estamos dispuestos a conectar con socios confiables y explorar juntos nuevos mercados. 🤝

Si está interesado, estaremos encantados de compartir nuestro catálogo, lista de precios y hablar sobre cómo podemos colaborar.

¡Esperamos su respuesta!

Saludos cordiales,
Departamento de Ventas"""
}

with st.container():
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="karim-logo">KARIM</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-pro">WhatsApp Broadcast Sender</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Choose mode:",
        ["Simple: Numbers Only", "Smart: Personalized Name & Country"],
        horizontal=True,
        key="mode"
    )

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
        numbers_raw = st.text_area("Numbers (comma/newline separated)", placeholder="Paste numbers, comma or newline separated")
        numbers = [
            n.strip().replace("-", "").replace(" ", "")
            for n in numbers_raw.replace(",", "\n").split("\n")
            if n.strip() and n.strip().replace("-", "").replace(" ", "").isdigit() and len(n.strip().replace("-", "").replace(" ", "")) >= 8
        ]
        names = [''] * len(numbers)
        countries = [''] * len(numbers)
        msg_template = templates[lang_code]
    # ------------- Smart Mode -------------
    else:
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio2")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        st.info("You can upload a CSV file (number,name,country) or enter data manually 👇")
        data_opt = st.radio("Input method:", ["Upload CSV file", "Manual entry"], horizontal=True, key="smart_input")
        df = None
        if data_opt == "Upload CSV file":
            uploaded_file = st.file_uploader("Upload CSV (number,name,country)", type=["csv"])
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file).dropna(subset=["number"])
                df = df.astype(str)
                st.success(f"{len(df)} contacts loaded.")
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
        # Personalized msg for smart mode
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
