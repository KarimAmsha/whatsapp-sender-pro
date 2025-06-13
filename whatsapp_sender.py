import streamlit as st
import pandas as pd
import urllib.parse
import re

st.set_page_config(
    page_title="KARIM | WhatsApp Sender PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

def extract_numbers(text):
    lines = text.replace(",", "\n").splitlines()
    numbers = []
    for line in lines:
        digits = re.sub(r'\D', '', line)
        if len(digits) >= 8:
            numbers.append(digits)
    return numbers

def clean_number(n):
    # استخرج كل الأرقام فقط (تحذف كل شيء آخر)
    digits = re.sub(r'\D', '', str(n))
    # لو الرقم طويل جدًا وبدايته صفر أو زائد، يمكن تخصصها حسب الدولة، لكن الأفضل فقط الأرقام
    return digits

def copy_to_clipboard_code(content, label="Copy"):
    btn_id = "copybtn" + str(hash(content))
    st.markdown(f"""
    <button id="{btn_id}" style="
        background:linear-gradient(90deg,#38bdf8,#2563eb);
        border:none;border-radius:7px;padding:7px 19px;
        color:#fff;font-size:1em;font-weight:700;
        margin:8px 0;cursor:pointer;">{label}</button>
    <script>
    document.getElementById('{btn_id}').onclick = function() {{
        navigator.clipboard.writeText({content!r});
        this.innerText = 'Copied!';
        setTimeout(()=>{{this.innerText='{label}'}},1400);
    }};
    </script>
    """, unsafe_allow_html=True)

def guess_column(columns, possible_names):
    for name in possible_names:
        for col in columns:
            if name.lower() in col.lower():
                return col
    return None

# أمثلة احتمالات شائعة
number_candidates = ['number', 'phone', 'mobile', 'whatsapp', 'contact', 'num', 'tel']
name_candidates = ['name', 'full name', 'contact', 'person', 'client']
country_candidates = ['country', 'nation', 'state', 'region']

# ==== TEMPLATES ====
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
    # ... نفس القيم للعربية والتركية والفرنسية والإسبانية (احفظها كما في كودك السابق)
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

# ==== CSS (Colors + Dashboard) ====
st.markdown("""
<style>
/* خلفية عامة */
.stApp {
    background: linear-gradient(120deg, #f6fbff 85%, #e0e7ef 100%) fixed !important;
    font-family: 'Inter', Arial, sans-serif !important;
    font-size: 15px !important;
}
.block-container {padding-top:18px; padding-bottom:12px;}

/* الجانبين */
.karim-sider, .karim-sider-right {
    background: linear-gradient(120deg, #e3f0ff 80%, #f3f8ff 100%);
    border-radius: 18px;
    box-shadow: 0 6px 22px #38bdf81a;
    padding: 17px 12px 12px 12px;
    margin: 10px 0 10px 0;
    min-width: 210px; max-width: 340px;
    font-size: 0.97em;
    color:#182244 !important;
}
.karim-sider .sider-title, .karim-sider-right .sider-title {
    color: #1877f2; font-size: 1.10em; font-weight: 900; letter-spacing: 1.5px; margin-bottom: 7px;
}
.karim-sider .sider-label, .karim-sider-right .sider-label {
    color:#1565c0;font-size:1em;font-weight:700;
}
.karim-sider .sider-section, .karim-sider-right .sider-section {margin:8px 0;}
.karim-sider .sider-logo, .karim-sider-right .sider-logo {text-align:center;margin:10px 0;}
.karim-sider .sider-logo span, .karim-sider-right .sider-logo span {font-size:1.7em;}
.karim-sider code, .karim-sider-right code {background:#222f3e;padding:2px 7px;border-radius:4px;font-size:.93em;color:#5eead4;}

/* Main glass box */
.glass-box-main {
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 7px 27px 0 rgba(36, 44, 76, 0.11), 0 1px 5px #38bdf810;
    padding: 26px 21px 25px 21px;
    margin: 10px 0 20px 0;
    border: 1.2px solid #e3e9f8;
    min-width: 340px; max-width: 620px;
}

/* شعار */
.karim-logo {
    font-family: 'Inter', sans-serif;
    font-size: 2rem; font-weight: 900; letter-spacing: 7px;
    margin-bottom: 0.13em; text-align: center;
    background: linear-gradient(90deg, #2563eb 45%, #38bdf8 70%, #22d3ee 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; text-fill-color: transparent;
    user-select: none; text-shadow: 0 1px 10px #38bdf840;
}
.subtitle-karim {
    font-size:1.08rem;
    text-align:center;
    color:#2563eb;
    font-weight:800;
    margin-top:2px; margin-bottom:6px;
    letter-spacing:1.2px;
    font-family: 'Inter', sans-serif;
}

/* Info Box */
.karim-glass-info {
    background: rgba(246, 250, 255, 0.82);
    border-radius: 13px;
    border: 1px solid #b6c7e2;
    box-shadow: 0 2px 10px #38bdf812;
    padding: 11px 15px 10px 15px;
    margin: 13px 0 8px 0;
    color: #174ca1;
    font-size: 1.03em;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    letter-spacing: .03em;
    text-align: center;
    backdrop-filter: blur(2.1px);
}

/* عناوين المجموعات */
.stRadio > label, .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stMarkdown h3 {
    color: #2563eb !important;
    font-weight: 800 !important;
    font-size: 1.05em !important;
    letter-spacing: 0.06em;
    margin-bottom: 0.12em !important;
    margin-top: 0.5em !important;
    display: block;
}
/* تصغير المسافة بين العنوان وخيارات الراديو */
.stRadio > div[role="radiogroup"] {margin-top: -0.7em !important; margin-bottom: 0.1em !important;}
.stRadio {margin-bottom: 0.2em !important;}

/* تصغير حجم الخط وتخفيف الوزن لخانات الراديو والنصوص الفرعية */
.stRadio > div[role="radiogroup"] label,
.stRadio > div[role="radiogroup"] span,
.stRadio > div[role="radiogroup"] div {
    font-size: 0.91em !important;
    font-weight: 500 !important;
    color: #232a3d !important;
}
.stRadio > div[role="radiogroup"] * {font-weight: 500 !important; font-size: 0.91em !important;}
.stRadio [data-baseweb="radio"] {font-weight: 500 !important; color: #232a3d !important;}

/* مدخلات النص */
input, textarea, .stTextInput>div>input, .stTextArea>div>textarea {
    border-radius: 9px !important;
    background: #f4f8fb !important;
    color: #17213d !important;
    border: 1.5px solid #bcd0ee;
    font-size: 1.02em;
    font-weight:600;
    box-shadow: 0 2px 7px #38bdf810;
    transition: border .13s;
}
input:focus, textarea:focus {
    border: 2px solid #38bdf8 !important;
    background: #fff !important;
    color: #1e293b !important;
}

/* زرار */
.stButton>button {
    background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%);
    border-radius: 9px !important;
    color: #fff !important;
    font-weight: bold;
    font-family: 'Inter', sans-serif;
    font-size: 0.97em; letter-spacing:.1px;
    box-shadow: 0 4px 16px #2563eb22;
    border: none !important;
    transition: box-shadow .13s, transform .11s, background .11s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #38bdf8 0%, #22d3ee 100%);
    color: #fff !important;
    box-shadow: 0 9px 20px #2563eb23;
    transform: translateY(-1px) scale(1.03);
}
.stButton>button:active {
    transform: scale(.97);
    box-shadow: 0 1px 3px #2563eb10;
}

/* لائحة الأرقام */
.numbers-list-karim {
    display: flex; flex-direction: column; gap: 2px; font-size: 14.5px;
    background: #f1f7fd; border-radius: 8px; padding: 6px 9px 6px 10px; margin-bottom: 11px;
    max-height: 90px; overflow-y: auto; color: #2563eb;
    border: 1px solid #e5eaf7;
    box-shadow: 0 2px 7px #38bdf80f;
    font-family: 'Inter', sans-serif;
}
.numbers-list-karim .active {
    background: linear-gradient(90deg,#38bdf849 60%,#22d3ee80 100%);
    border-radius: 7px; font-weight: bold; color: #fff;
    font-size: 1em; border-left: 4px solid #2563eb; padding-left: 3px;
    box-shadow: 0 2px 8px #22d3ee18;
}

/* الفوتر */
.footer-karim {
    margin-top: 1.3rem; font-size: 0.98rem; color: #2563eb;
    text-align: center; letter-spacing: 1px;
    font-family: 'Inter', sans-serif;
    opacity: .98; font-weight: bold; padding-bottom: 10px;
}

/* موبايل */
@media (max-width:900px){
    .glass-box-main{padding:4vw 1vw;min-width:unset;max-width:unset;}
    .karim-sider,.karim-sider-right{padding:10px 5vw;}
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2.3,1])

with col1:
    st.markdown("""
    <div class="karim-sider">
        <div class="sider-title">Bulk Tools</div>
        <div class="sider-section">
            <span class="sider-label">Download Clean Numbers:</span><br>
    """, unsafe_allow_html=True)
    st.session_state.setdefault("last_numbers", [])
    if st.session_state.get("last_numbers"):
        st.download_button(
            "⬇️ Download .txt",
            "\n".join(st.session_state["last_numbers"]),
            file_name="clean_numbers.txt",
            key="dl-side"
        )
        copy_to_clipboard_code("\n".join(st.session_state["last_numbers"]), "Copy All Numbers")
    else:
      st.info(
        'Clean numbers will appear here after filtering.',
          icon="ℹ️"
      )
    st.markdown("""</div>""", unsafe_allow_html=True)
    st.markdown("""
        <div class="sider-section">
            <span class="sider-label">Import / Export:</span><br>
            <ul style='margin-top:3px;'>
            <li>Upload <b>CSV</b> or paste numbers.</li>
            <li>Export filtered numbers directly.</li>
            </ul>
        </div>
        <div class="sider-section">
            <span class="sider-label">Recent Feature:</span>
            <div style="color:#0ea5e9;font-weight:700;">One-click copy!</div>
        </div>
        <div class="sider-logo"><span>🛠️</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="karim-sider karim-sider-right">
        <div class="sider-title">Quick Links & News</div>
        <div class="sider-section">
            <span class="sider-label">Official Catalog:</span>
            <a href="https://eurosweet.com.tr" target="_blank" style="color:#2563eb;text-decoration:underline;font-weight:600;">Visit Website</a>
        </div>
        <div class="sider-section">
            <span class="sider-label">Contact Developer:</span>
            <a href="mailto:karim.amsha@gmail.com" style="color:#1976d2;">karim.amsha@gmail.com</a>
        </div>
        <div class="sider-section">
            <span class="sider-label">Latest Update:</span>
            <div style="color:#0ea5e9;font-weight:700;">🚀 Responsive + One-click Copy enabled!</div>
        </div>
        <div class="sider-logo"><span>✨</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
      <div class="glass-box-main">
          <div class="karim-logo">KARIM</div>
          <div class="subtitle-karim">WhatsApp Broadcast Sender</div>
      """, unsafe_allow_html=True)

    # --- أضف CSS مخصص لعناوين الراديو ---
    st.markdown("""
    <style>
    .form-label-karim {
        font-weight: 800;
        color: #1877f2;
        font-size: 1.14em;
        letter-spacing: .03em;
        margin-bottom: 0.2em;
        display: block;
    }
    .stRadio > div[role="radiogroup"] label,
    .stRadio > div[role="radiogroup"] span,
    .stRadio > div[role="radiogroup"] div {
        font-weight: 500 !important;
        color: #21293a !important;
        font-size: 1.09em !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- عناوين الراديو بخط أزرق عريض ---
    st.markdown('<span class="form-label-karim">Choose mode:</span>', unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["Simple: Numbers Only", "Smart: Personalized Name & Country"],
        horizontal=True,
        key="mode"
    )

    if mode == "Simple: Numbers Only":
        st.markdown('<span class="form-label-karim">Language</span>', unsafe_allow_html=True)
        lang = st.radio(
            "",
            ["🇬🇧 English", "🇸🇦 العربية", "🇹🇷 Türkçe", "🇫🇷 Français", "🇪🇸 Español"],
            horizontal=True, key="lang_radio"
        )
        lang_code = {
            "🇬🇧 English": "en",
            "🇸🇦 العربية": "ar",
            "🇹🇷 Türkçe": "tr",
            "🇫🇷 Français": "fr",
            "🇪🇸 Español": "es"
        }[lang]

        st.markdown('<span class="form-label-karim">Send using</span>', unsafe_allow_html=True)
        platform = st.radio(
            "",
            ["💻 WhatsApp Web", "📱 WhatsApp App"],
            horizontal=True, key="plat_radio"
        )
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        numbers_raw = st.text_area(
            "Numbers (comma/newline/any format)", 
            placeholder="Paste numbers, comma, newline, or any format (even tel +254 722 206312)"
        )
        numbers = extract_numbers(numbers_raw)
        names = [''] * len(numbers)
        countries = [''] * len(numbers)
        msg_template = templates[lang_code]
        st.session_state["last_numbers"] = numbers if numbers else []

        if numbers_raw and numbers:
            st.markdown("#### Filtered Numbers:")
            st.code('\n'.join(numbers), language="text")
            copy_to_clipboard_code("\n".join(numbers), "Copy Filtered Numbers")
            st.download_button(
                "⬇️ Download filtered numbers", 
                "\n".join(numbers), 
                file_name="clean_numbers.txt", 
                key="dl-main"
            )

# with col2:
#     st.markdown("""
#       <div class="glass-box-main">
#           <div class="karim-logo">KARIM</div>
#           <div class="subtitle-karim">WhatsApp Broadcast Sender</div>
#           <!-- هنا ضع بقية عناصر الصفحة: الأزرار، الراديو، المدخلات، إلخ -->
#       </div>
#       """, unsafe_allow_html=True)
    
#     mode = st.radio(
#         "Choose mode:",
#         ["Simple: Numbers Only", "Smart: Personalized Name & Country"],
#         horizontal=True,
#         key="mode"
#     )
    
#     # ---- Simple Mode ----
#     if mode == "Simple: Numbers Only":
#         lang = st.radio("Language", [
#             "🇬🇧 English", "🇸🇦 العربية", "🇹🇷 Türkçe", "🇫🇷 Français", "🇪🇸 Español"
#         ], horizontal=True, key="lang_radio")
#         lang_code = {
#             "🇬🇧 English": "en",
#             "🇸🇦 العربية": "ar",
#             "🇹🇷 Türkçe": "tr",
#             "🇫🇷 Français": "fr",
#             "🇪🇸 Español": "es"
#         }[lang]
#         platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio")
#         platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
#         numbers_raw = st.text_area("Numbers (comma/newline/any format)", placeholder="Paste numbers, comma, newline, or any format (even tel +254 722 206312)")
#         numbers = extract_numbers(numbers_raw)
#         names = [''] * len(numbers)
#         countries = [''] * len(numbers)
#         msg_template = templates[lang_code]
#         st.session_state["last_numbers"] = numbers if numbers else []

#         if numbers_raw and numbers:
#             st.markdown("#### Filtered Numbers:")
#             st.code('\n'.join(numbers), language="text")
#             copy_to_clipboard_code("\n".join(numbers), "Copy Filtered Numbers")
#             st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt", key="dl-main")

    # ---- Smart Mode ----
    else:
        platform = st.radio("Send using", ["💻 WhatsApp Web", "📱 WhatsApp App"], horizontal=True, key="plat_radio2")
        platform_type = "web" if platform == "💻 WhatsApp Web" else "mobile"
        st.markdown("""
          <div class="karim-glass-info">
              You can upload a CSV file (<b>number,name,country</b>) or enter data manually 👇
          </div>
          """, unsafe_allow_html=True)
        # st.info("You can upload a CSV file (number,name,country) or enter data manually 👇")
        st.download_button(
            label="⬇️ Download example CSV",
            data="number,name,country\n201111223344,Mohamed,Egypt\n971500000001,Ahmed,UAE\n",
            file_name="example_contacts.csv",
            mime="text/csv",
        )
        data_opt = st.radio("Input method:", ["Upload CSV file", "Manual entry"], horizontal=True, key="smart_input")
        df = None
        if data_opt == "Upload CSV file":
          uploaded_file = st.file_uploader("Upload file (CSV or Excel: number,name,country)", type=["csv", "xlsx", "xls"])
          if uploaded_file is not None:
              try:
                  filename = uploaded_file.name
                  if filename.endswith('.csv'):
                      df = pd.read_csv(uploaded_file)
                  elif filename.endswith(('.xlsx', '.xls')):
                      df = pd.read_excel(uploaded_file)
                  else:
                      st.error("Unsupported file format. Please upload CSV or Excel file.")
                      df = None

                  if df is not None:
                      columns = list(df.columns)
                      # يطلب من المستخدم يختار الأعمدة بنفسه
                      number_col = st.selectbox("Select the column containing WhatsApp numbers:", columns)
                      name_col = st.selectbox("Select the name column (optional):", columns, index=1 if len(columns) > 1 else 0)
                      country_col = st.selectbox("Select the country column (optional):", columns, index=2 if len(columns) > 2 else 0)

                      # فلترة الداتا فريم حسب العمود المختار
                      df = df.dropna(subset=[number_col])
                      df[number_col] = df[number_col].apply(clean_number)
                      df = df[df[number_col].str.len() >= 8]
                      df = df.astype(str)
                      st.success(f"{len(df)} contacts loaded.")

                      # استخراج القيم حسب اختيار المستخدم
                      numbers = df[number_col].tolist()
                      names = df[name_col].tolist() if name_col else ['']*len(df)
                      countries = df[country_col].tolist() if country_col else ['']*len(df)
                  else:
                      numbers, names, countries = [], [], []
              except Exception as e:
                  st.error(f"Failed to process file: {e}")
                  numbers, names, countries = [], [], []
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
          # إذا كان المستخدم رفع ملف: استخدم الأعمدة المختارة
          if data_opt == "Upload CSV file" and 'number_col' in locals():
              numbers = df[number_col].tolist()
              names = df[name_col].tolist() if name_col else ['']*len(df)
              countries = df[country_col].tolist() if country_col else ['']*len(df)
          else:
              # إذا كان الإدخال يدوي (columns ثابتة: number, name, country)
              numbers = df['number'].tolist() if 'number' in df.columns else []
              names = df['name'].tolist() if 'name' in df.columns else ['']*len(df)
              countries = df['country'].tolist() if 'country' in df.columns else ['']*len(df)
        else:
          numbers, names, countries = [], [], []
        msg_template = st.text_area(
            "Write message template (use {name}, {country}, {number}):",
            value=(
                "Hello {name} 👋\n\n"
                "We are the Sales Department at EUROSWEET GIDA LTD. ŞTİ. (Istanbul – Turkey).\n\n"
                "We specialize in producing high-quality snacks such as:\n"
                "🍪 Croissants, Cakes, Biscuits, Donuts, Jelly, and Wafers.\n\n"
                "We’re always eager to connect with reliable partners in {country} and explore new markets together. 🤝\n\n"
                "If you are interested, we’d be happy to share our catalog and price list, and discuss how we can collaborate.\n\n"
                "Looking forward to your reply, {name}!\n\n"
                "Best regards,\n"
                "Sales Department\n"
            ),
            height=220,
            key="smart_template"
        )
        st.session_state["last_numbers"] = numbers if numbers else []
        if df is not None and not df.empty:
            st.markdown("#### Filtered Numbers:")
            st.code('\n'.join(numbers), language="text")
            copy_to_clipboard_code("\n".join(numbers), "Copy Filtered Numbers")
            st.download_button("⬇️ Download filtered numbers", "\n".join(numbers), file_name="clean_numbers.txt", key="dl-main-smart")

    # ======= Progress + Sending =======
    if 'current' not in st.session_state:
        st.session_state.current = 0
    if 'skipped' not in st.session_state:
        st.session_state.skipped = set()

    if numbers:
        percent = int((st.session_state.current+1) / len(numbers) * 100)
        st.markdown(
            f'''
            <div style="margin-bottom:6px;"><b style="color:#1565c0;font-size:1.09rem">Progress:</b></div>
            <div style="margin-bottom:9px;">
                <div style="width:62px;height:62px;margin:auto;position:relative;">
                    <div style="width:62px;height:62px;border-radius:50%;background:conic-gradient(#26c6da {percent}%, #e3f2fd {percent}% 100%);display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px #1976d225;position:absolute;top:0;left:0;animation:popIn .7s;">
                        <span style="font-size:1.15rem;color:#1565c0;font-family:'Cairo',sans-serif;font-weight:900;letter-spacing:2px;z-index:1;margin:auto;">{st.session_state.current+1}/{len(numbers)}</span>
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
