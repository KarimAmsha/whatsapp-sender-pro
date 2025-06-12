import streamlit as st
import pandas as pd
import urllib.parse

# ========== ألوان وستايل جديدة ==========
st.set_page_config(page_title="KARIM | WhatsApp Sender PRO", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Open+Sans:wght@400;700&display=swap');
body, [class*="css"] { font-family: 'Open Sans', 'Cairo', Arial, sans-serif !important;}
.stApp {
  background: linear-gradient(135deg, #F4FFF8 0%, #EEE8FD 55%, #B3E5DF 100%) fixed !important;
  min-height: 100vh;
}
.glass-box {
  background: rgba(255,255,255,0.82);
  border-radius: 24px;
  box-shadow: 0 6px 32px #cdb6fa27, 0 1.5px 18px #91d1ad28;
  backdrop-filter: blur(7.5px); -webkit-backdrop-filter: blur(7.5px);
  padding: 30px 20px 18px 20px;
  margin: 32px auto 16px auto; max-width: 520px;
  border: 1.7px solid #e4e8fd36; animation: floatUp .7s;
}
@keyframes floatUp {
  0% {transform: translateY(40px) scale(.95); opacity:0;}
  60% {transform: translateY(-7px) scale(1.03);}
  100% {transform: translateY(0) scale(1); opacity:1;}
}
.karim-logo {
  display: flex; align-items: center; justify-content: center;
  font-family: 'Cairo', sans-serif; font-size: 2.2rem; font-weight: 900; letter-spacing: 7px;
  margin-bottom: 0.1rem; padding-bottom: 0.4rem; text-align: center;
  background: linear-gradient(90deg, #986ce5 40%, #61beac 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; text-fill-color: transparent; user-select: none;
  text-shadow: 0 4px 12px #91d1ad66;
  filter: drop-shadow(0 1px 8px #aacff9b7);
  animation: popIn 1.1s cubic-bezier(.31,1.37,.71,1);
}
.karim-logo .whats-icon {
  font-size: 1.6rem; margin-left: 11px; margin-right: -7px;
  filter: drop-shadow(0 2px 7px #4be97db8);
  animation: pulseLogo 2.4s infinite alternate;
}
@keyframes popIn { 0% {letter-spacing:0px;opacity:0;transform: scale(.5);}
  80% {letter-spacing:13px;transform: scale(1.08);} 100% {opacity:1;} }
@keyframes pulseLogo {
  0% {filter:drop-shadow(0 0 3px #4be97db0);}
  100% {filter:drop-shadow(0 0 13px #61beac);}}
.title-pro {
  font-size: 1.15rem; margin-bottom: 1.1rem; color: #7e55c9;
  text-align: center; letter-spacing: 1.6px; font-family: 'Cairo', 'Open Sans', sans-serif;
  font-weight: bold; animation: fadeDown .7s;}
@keyframes fadeDown {0% {opacity:0;transform:translateY(-34px);} 100% {opacity:1;transform:translateY(0);}}
.progress-outer { margin: 17px auto 6px auto; width: 64px; height: 64px; position: relative; display: flex; align-items: center; justify-content: center;}
.progress-circle {
  width: 64px; height: 64px; border-radius: 50%;
  background: conic-gradient(#70d1b9 0% {progress}%, #f3ecff {progress}% 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 12px #986ce532;
  position: absolute; top: 0; left: 0; animation: popIn 0.7s;}
.progress-num { font-size: 1.11rem; color: #653d93; font-family: 'Cairo',sans-serif; font-weight: 900; letter-spacing: 2px; z-index: 1;}
.numbers-list-karim {
  display: flex; flex-direction: column; gap: 2.5px; font-size: 13.2px;
  background: #f3ecffad; border-radius: 10px; padding: 7px 10px 7px 14px; margin-bottom: 12px;
  max-height: 90px; overflow-y: auto; color: #6952a6;
  border: 1.1px solid #ede7fa;
  box-shadow: 0 2px 7px #aacff91a;
  font-family: 'Open Sans', Cairo, sans-serif;}
.numbers-list-karim .active {
  background: linear-gradient(90deg,#c8e6df 50%,#e3d6fd 100%);
  border-radius: 7px; font-weight: bold; color: #1fa47e; font-size: 1.01em;}
button[kind="primary"], button[data-testid="baseButton-primary"] {
  background: linear-gradient(90deg, #64cfc1 40%, #986ce5 100%);
  border-radius: 15px !important; color: #fff !important; font-weight: bold;
  transition: box-shadow 0.19s, transform 0.19s; box-shadow: 0 4px 14px #b2e7e732; border: none !important;
  font-family: 'Cairo', 'Open Sans', sans-serif; font-size: 1.02em;}
button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(90deg, #50beaa 25%, #b49bf5 100%);
  box-shadow: 0 8px 22px #b2e7e754;
  transform: translateY(-2px) scale(1.045);}
[data-testid="collapsedControl"] {display: none;}
.footer-karim {
  margin-top: 2.1rem; font-size: 1.1rem; color: #63b37e;
  text-align: center; letter-spacing: 1.2px; font-family: 'Cairo', 'Open Sans', sans-serif;
  opacity: .81; font-weight: bold; padding-bottom: 13px;
  animation: fadeUp 1.2s; text-shadow: 0 1px 7px #b9efd364;}
@keyframes fadeUp {0% {opacity:0;transform:translateY(32px);}100% {opacity:1;transform:translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ========== بيانات القوالب ==========
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

# ========== START UI ==========
with st.container():
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="karim-logo">'
        'KARIM <span class="whats-icon">🟢</span>'
        '</div>', unsafe_allow_html=True
    )
    st.markdown('<div class="title-pro">WhatsApp Broadcast Sender</div>', unsafe_allow_html=True)

    mode = st.radio(
        "اختر النمط:",
        ["النمط البسيط: أرقام فقط", "النمط الذكي: تخصيص اسم ودولة"],
        horizontal=True,
        key="mode"
    )

    # ------ SIMPLE MODE ------
    if mode == "النمط البسيط: أرقام فقط":
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
    # ------ SMART MODE ------
    else:
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio2")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        st.info("يمكنك رفع ملف CSV (number,name,country) أو إدخال البيانات يدويًا 👇")
        data_opt = st.radio("طريقة الإدخال:", ["رفع ملف CSV", "إدخال يدوي"], horizontal=True, key="smart_input")
        import pandas as pd
        df = None
        if data_opt == "رفع ملف CSV":
            uploaded_file = st.file_uploader("ارفع ملف CSV بصيغة (number,name,country)", type=["csv"])
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file).dropna(subset=["number"])
                df = df.astype(str)
                st.success(f"تم تحميل {len(df)} جهة اتصال.")
        else:
            st.info("أدخل البيانات يدويًا (يمكنك إضافة أو حذف الصفوف):")
            example_data = pd.DataFrame({
                'number': ['201111223344', '971500000001'],
                'name': ['محمد', 'أحمد'],
                'country': ['مصر', 'الإمارات']
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
            "اكتب قالب الرسالة (استخدم {name} و{country} و{number} للمتغيرات):",
            value="مرحبًا {name} من {country}، لدينا منتجات جديدة تناسب السوق {country}!",
            height=120,
            key="smart_template"
        )

    if 'current' not in st.session_state:
        st.session_state.current = 0
    if 'skipped' not in st.session_state:
        st.session_state.skipped = set()

    # Progress Circle
    if numbers:
        percent = int((st.session_state.current+1) / len(numbers) * 100)
        st.markdown(
            f'''
            <div class="progress-outer">
                <div class="progress-circle" style="background:conic-gradient(#70d1b9 {percent}%, #f3ecff {percent}% 100%);">
                    <span class="progress-num">{st.session_state.current+1}/{len(numbers)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True
        )

    if st.button("🔄 Reset Progress"):
        st.session_state.current = 0
        st.session_state.skipped = set()

    if numbers:
        # تحديد الرسالة الفعلية لكل جهة اتصال
        try:
            msg_personal = msg_template.format(
                name=names[st.session_state.current] if names else '',
                country=countries[st.session_state.current] if countries else '',
                number=numbers[st.session_state.current]
            )
        except Exception as e:
            msg_personal = "⚠️ تحقق من القالب أو البيانات"
        message = st.text_area(
            "Message",
            value=msg_personal,
            key="msgboxfinal",
            help="يمكنك التعديل قبل الإرسال",
            height=130,
        )
        st.write(f"**Contact:** {min(st.session_state.current+1, len(numbers))} / {len(numbers)}")
        info = f'{numbers[st.session_state.current]}'
        if mode == "النمط الذكي: تخصيص اسم ودولة" and names and countries:
            info += f" — {names[st.session_state.current]} — {countries[st.session_state.current]}"
        st.write(
            f'<span style="display:inline-block;padding:7px 19px;background:linear-gradient(90deg,#70d1b9,#c7bbf4);color:#4a3968;'
            'border-radius:22px;font-family:Cairo,sans-serif;font-size:1.09rem;font-weight:bold;'
            'box-shadow:0 1px 7px #b2e7e7;margin-bottom:10px;">'
            f'{info}</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="numbers-list-karim">' +
            "".join([
                f"<div class='{ 'active' if i == st.session_state.current else ''}'>{i+1}. {numbers[i]}{(' - ' + names[i]) if (mode=='النمط الذكي: تخصيص اسم ودولة' and names and names[i]) else ''}{(' - ' + countries[i]) if (mode=='النمط الذكي: تخصيص اسم ودولة' and countries and countries[i]) else ''}</div>"
                for i in range(len(numbers))
            ]) +
            "</div>", unsafe_allow_html=True
        )

        cols = st.columns([1.2, 1.2, 1.6, 1.2])
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
                f"<a href='{url}' target='_blank' style='font-weight:bold; color:#63b37e; font-size:18px; letter-spacing:.5px;'>"
                "🚀 اضغط هنا إذا لم يفتح واتساب تلقائيًا</a></div>", unsafe_allow_html=True
            )
            st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

        if cols[3].button("Next →", disabled=next_disabled, key="next"):
            if st.session_state.current < len(numbers)-1:
                st.session_state.current += 1

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-karim">✦ Powered by <span style="font-family:Cairo,sans-serif;letter-spacing:2.3px;color:#63b37e;">Karim OTHMAN 😍</span> &copy; 2025</div>', unsafe_allow_html=True)
