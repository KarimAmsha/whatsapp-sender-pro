import streamlit as st
import pandas as pd
import urllib.parse

# ---- صفحة وإعدادات ستايل ----
st.set_page_config(page_title="KARIM | WhatsApp Sender PRO", layout="centered")
st.markdown("""
<style>
body, [class*="css"] { font-family: 'Open Sans', 'Cairo', Arial, sans-serif !important;}
.stApp {background: linear-gradient(135deg, #13a7df 0%, #71e6fc 50%, #aefaf6 100%) fixed !important; min-height: 100vh;}
.glass-box {background: rgba(255,255,255,0.68);border-radius: 28px;box-shadow: 0 8px 44px 0 #b3eafd4a, 0 1.5px 18px #12b5de38;
backdrop-filter: blur(7.2px);-webkit-backdrop-filter: blur(7.2px);padding: 34px 22px 18px 22px;margin: 32px auto 14px auto;max-width: 520px;
border: 1.6px solid #e0f8fe33;animation: floatUp .8s cubic-bezier(.56,.19,.34,.98);}
@keyframes floatUp {0% {transform: translateY(40px) scale(.95); opacity:0;}60% {transform: translateY(-9px) scale(1.02);}
100% {transform: translateY(0) scale(1); opacity:1;}}
.karim-logo {font-family: 'Cairo', sans-serif; font-size: 2.3rem; font-weight: 900; letter-spacing: 8px; margin-bottom: 0.1rem; padding-bottom: 0.5rem;
text-align: center;background: linear-gradient(90deg, #1e86e4 45%, #1bd6c4 90%, #84e9fb 100%);-webkit-background-clip: text;-webkit-text-fill-color: transparent;
background-clip: text;text-fill-color: transparent;user-select: none;text-shadow: 0 4px 16px #10b7d466;filter: drop-shadow(0 1px 8px #48baff70);
animation: popIn 1.1s cubic-bezier(.31,1.37,.71,1);}
@keyframes popIn {0% {letter-spacing:0px;opacity:0;transform: scale(.5);}80% {letter-spacing:13px;transform: scale(1.08);}
100% {opacity:1;}}
.title-pro {font-size: 1.10rem;margin-bottom: 1.1rem;color: #1297e0;text-align: center;letter-spacing: 1.6px;font-family: 'Cairo', 'Open Sans', sans-serif;
font-weight: bold;animation: fadeDown .7s;}
@keyframes fadeDown {0% {opacity:0;transform:translateY(-34px);}100% {opacity:1;transform:translateY(0);}}
.numbers-list-karim {display: flex; flex-direction: column; gap: 2.5px; font-size: 13.2px;
background: #f6faffb7;border-radius: 10px; padding: 8px 10px 8px 14px; margin-bottom: 12px;
max-height: 90px; overflow-y: auto; color: #397bbf;border: 1.1px solid #e5f2fa;
box-shadow: 0 2px 7px #beeafd1a;font-family: 'Open Sans', Cairo, sans-serif;}
.numbers-list-karim .active {background: linear-gradient(90deg,#beeafd 60%,#bffcf9 100%);
border-radius: 7px;font-weight: bold;color: #10b7d4;font-size: 1.02em;}
.footer-karim {margin-top: 2.1rem; font-size: 1.1rem; color: #1e86e4;text-align: center; letter-spacing: 1.2px;
font-family: 'Cairo', 'Open Sans', sans-serif;opacity: .78;font-weight: bold;padding-bottom: 13px;
animation: fadeUp 1.2s;text-shadow: 0 1px 7px #beeafd64;}
@keyframes fadeUp {0% {opacity:0;transform:translateY(32px);}100% {opacity:1;transform:translateY(0);}}
</style>
""", unsafe_allow_html=True)

# ---- واجهة التطبيق ----
st.markdown('<div class="glass-box">', unsafe_allow_html=True)
st.markdown('<div class="karim-logo">KARIM</div>', unsafe_allow_html=True)
st.markdown('<div class="title-pro">WhatsApp Sender PRO | تخصيص الرسائل تلقائياً</div>', unsafe_allow_html=True)

st.write("👈 يمكنك إدخال البيانات يدويًا أو رفع ملف CSV (number, name, country):")

# اختيار طريقة الإدخال
option = st.radio("طريقة الإدخال:", ["رفع ملف CSV", "إدخال يدوي"], horizontal=True)

df = None
if option == "رفع ملف CSV":
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

# التحكم بحالة التنقل والرسائل
if 'current' not in st.session_state:
    st.session_state.current = 0
if 'skipped' not in st.session_state:
    st.session_state.skipped = set()
if 'msg_template' not in st.session_state:
    st.session_state.msg_template = "مرحبًا {name} من {country}، لدينا منتجات جديدة تناسب السوق {country}!"

# فورم القالب
st.session_state.msg_template = st.text_area(
    "قالب الرسالة (استخدم {name} و{country} و{number} للمتغيرات):",
    value=st.session_state.msg_template,
    height=100,
    key="msgtpl"
)

if df is not None and not df.empty:
    names = df['name'].tolist() if 'name' in df.columns else ['']*len(df)
    numbers = df['number'].tolist()
    countries = df['country'].tolist() if 'country' in df.columns else ['']*len(df)
    total = len(numbers)

    # اجبار current للمدى الصحيح
    st.session_state.current = max(0, min(st.session_state.current, total-1))
    i = st.session_state.current

    # توليد الرسالة الشخصية
    try:
        personalized_msg = st.session_state.msg_template.format(
            name=names[i], country=countries[i], number=numbers[i]
        )
    except Exception as e:
        personalized_msg = "⚠️ تحقق من صياغة القالب!"

    st.write(f"**الرقم الحالي:** `{numbers[i]}`")
    st.write(f"**اسم المستلم:** {names[i]}")
    st.write(f"**الدولة:** {countries[i]}")

    # معاينة الرسالة المعدلة (قابلة للتعديل قبل الإرسال)
    message_final = st.text_area("الرسالة الجاهزة للإرسال (يمكنك التعديل قبل الفتح):", value=personalized_msg, height=100, key="msgfinal")

    # قائمة الأرقام
    st.markdown('<div class="numbers-list-karim">' +
        "".join([
            f"<div class='{ 'active' if j == i else ''}'>{j+1}. {numbers[j]} - {names[j]} - {countries[j]}</div>"
            for j in range(total)
        ]) +
        "</div>", unsafe_allow_html=True
    )

    # أزرار التنقل
    cols = st.columns([1,1,1,1])
    prev_disabled = i <= 0
    next_disabled = i >= total - 1
    skip_disabled = numbers[i] in st.session_state.skipped

    if cols[0].button("← السابق", disabled=prev_disabled):
        if st.session_state.current > 0:
            st.session_state.current -= 1

    if cols[1].button("تخطي", disabled=skip_disabled):
        st.session_state.skipped.add(numbers[i])
        if st.session_state.current < total - 1:
            st.session_state.current += 1

    if cols[2].button("فتح واتساب", disabled=not message_final.strip()):
        msg_encoded = urllib.parse.quote(message_final.strip())
        num = numbers[i]
        url = f"https://web.whatsapp.com/send?phone={num}&text={msg_encoded}"
        st.markdown(
            f"<div style='text-align:center; margin-top:6px;'>"
            f"<a href='{url}' target='_blank' style='font-weight:bold; color:#009be2; font-size:18px; letter-spacing:.5px;'>"
            "🚀 اضغط هنا إذا لم يفتح واتساب تلقائيًا</a></div>", unsafe_allow_html=True
        )
        st.components.v1.html(f"""<script>window.open("{url}", "_blank");</script>""")

    if cols[3].button("التالي →", disabled=next_disabled):
        if st.session_state.current < total - 1:
            st.session_state.current += 1

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-karim">✦ Powered by <span style="font-family:Cairo,sans-serif;letter-spacing:2.3px;color:#1092d4;">Karim Amsha</span> &copy; 2025</div>', unsafe_allow_html=True)
