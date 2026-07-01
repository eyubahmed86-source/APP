import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة الافتراضية ---
st.set_page_config(page_title="منصة تعليم الطلاب الرقمية", page_icon="🎓", layout="wide")

# --- إضافة الستايل المطور والآمن تماماً (CSS) ---
st.markdown("""
    <style>
    /* تطبيق الخط العربي والمحاذاة على النصوص والبطاقات فقط دون التأثير على تقسيم الموقع */
    .main-title, .main-subtitle, .section-title, .content-card, .quiz-card, p, h1, h2, h3 {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    
    /* ستايل البطاقات المخصصة للدروس */
    .content-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-right: 5px solid #4A90E2;
    }
    
    /* ستايل البطاقات المخصصة للاختبارات */
    .quiz-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-right: 5px solid #2ECC71;
    }
    
    /* تنسيق العناوين الرئيسية */
    .main-title {
        color: #2C3E50;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .main-subtitle {
        text-align: center !important;
        color: #7F8C8D;
        font-size: 1.1rem !important;
        margin-bottom: 30px;
    }
    .section-title {
        color: #34495E;
        font-size: 1.5rem !important;
        margin-bottom: 20px;
        border-bottom: 2px solid #ECF0F1;
        padding-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- إعداد الاتصال بقاعدة البيانات (Google Sheets) ---
def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/1o1dk1mQdXOTR_6x8H-_iWMVg_vQAaMB0UUav3aSKlyU/edit?usp=sharing"
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet

try:
    db = connect_to_sheets()
except Exception as e:
    st.error("فشل الاتصال بقاعدة البيانات. تأكد من إعداد المفاتيح السرية بشكل صحيح.")
    db = None

# --- دالة ذكية لإصلاح روابط اليوتيوب المأخوذة من الهاتف ---
def get_clean_youtube_url(url):
    url = str(url).strip()
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    elif "youtube.com/shorts/" in url:
        video_id = url.split("youtube.com/shorts/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# --- واجهة المستخدم الرئيسية للتطبيق ---
st.markdown("<div class='main-title'>🎓 منصة تعليم الطلاب الرقمية</div>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>أهلاً بكم في المنصة التعليمية الرقمية. يمكنكم تصفح الدروس وحل الاختبارات المتاحة أدناه بسهولة:</div>", unsafe_allow_html=True)

# نظام تقسيم الأعمدة الآمن من Streamlit
col_video, col_quiz = st.columns(2)

if db:
    try:
        all_records = db.get_all_records()
        
        with col_video:
            st.markdown("<div class='section-title'>📺 فيديوهات الدروس المشروحة</div>", unsafe_allow_html=True)
            for r in all_records:
                if str(r.get('نوع الرابط', '')).strip() == 'فيديو':
                    lesson_num = r.get('رقم الدرس', '#')
                    lesson_desc = r.get('وصف الدرس', '')
                    clean_url = get_clean_youtube_url(r.get('الرابط', ''))
                    
                    st.markdown(f"""
                    <div class="content-card">
                        <h3 style="margin:0;">📖 درس رقم {lesson_num}: {lesson_desc}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video(clean_url)
                    # زر احتياطي يأخذ الطالب إلى يوتيوب مباشرة في حال لم يعمل المشغل المدمج
                    st.link_button(url=clean_url, label="📺 فتح الفيديو مباشرة على يوتيوب", use_container_width=True)
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    
        with col_quiz:
            st.markdown("<div class='section-title'>📝 الاختبارات والتقييمات المتاحة</div>", unsafe_allow_html=True)
            for r in all_records:
                if str(r.get('نوع الرابط', '')).strip() == 'اختبار':
                    quiz_num = r.get('رقم الدرس', '#')
                    quiz_desc = r.get('وصف الدرس', 'لا توجد ملاحظات إضافية')
                    quiz_url = r.get('الرابط', '#')
                    
                    st.markdown(f"""
                    <div class="quiz-card">
                        <h3 style="margin:0;">🎯 اختبار الدرس رقم {quiz_num}</h3>
                        <p style='color: #7F8C8D; margin: 5px 0 0 0;'>ملاحظة: {quiz_desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button(url=quiz_url, label=f"🔗 دخول الاختبار السريع", use_container_width=True)
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    
    except Exception as e:
        st.warning("الجدول فارغ حالياً، قم بتسجيل الدخول كمعلم لإضافة المحتوى الأول.")

# --- لوحة التحكم المغلقة بكلمة السر (7962400) ---
st.sidebar.title("🔐 لوحة تحكم المعلم")
password_input = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")

if password_input == "7962400":
    st.sidebar.success("تم تسجيل الدخول بنجاح!")
    
    admin_mode = st.sidebar.radio("اختر العملية:", ("➕ إضافة محتوى جديد", "🗑️ حذف محتوى حالي"))
    
    if admin_mode == "➕ إضافة محتوى جديد":
        action = st.sidebar.radio("نوع المحتوى:", ("إضافة رابط اختبار", "إضافة فيديو الدرس (يوتيوب)"))
        
        lesson_num = st.sidebar.text_input("رقم الدرس (مثال: 1 أو 2):")
        lesson_desc = st.sidebar.text_input("وصف الدرس (مثال: شرح الجمع والطرح):")
        
        if action == "إضافة رابط اختبار":
            quiz_url = st.sidebar.text_input("أدخل رابط الاختبار:")
            if st.sidebar.button("حفظ رابط الاختبار"):
                if quiz_url and db:
                    db.append_row(["اختبار", quiz_url, lesson_desc, lesson_num])
                    st.sidebar.success("تم حفظ الاختبار بنجاح!")
                    st.rerun()
                else:
                    st.sidebar.error("الرجاء إدخال رابط صحيح.")
                    
        elif action == "إضافة فيديو الدرس (يوتيوب)":
            video_url = st.sidebar.text_input("أدخل رابط فيديو اليوتيوب:")
            if st.sidebar.button("حفظ فيديو الدرس"):
                if video_url and db:
                    db.append_row(["فيديو", video_url, lesson_desc, lesson_num])
                    st.sidebar.success("تم حفظ فيديو الدرس بنجاح!")
                    st.rerun()
                else:
                    st.sidebar.error("الرجاء إدخال رابط صحيح.")
                    
    elif admin_mode == "🗑️ حذف محتوى حالي":
        st.sidebar.markdown("### اختر المحتوى المراد حذفه:")
        if db:
            try:
                raw_rows = db.get_all_values()
                if len(raw_rows) > 1:
                    options_to_delete = []
                    for idx, row in enumerate(raw_rows[1:], start=2):
                        if len(row) >= 4:
                            display_text = f"[{row[0]}] درس {row[3]}: {row[2][:20]}"
                            options_to_delete.append((idx, display_text))
                    
                    selected_item = st.sidebar.selectbox(
                        "اختر العنصر للحذف:", 
                        options=options_to_delete, 
                        format_func=lambda x: x[1]
                    )
                    
                    if st.sidebar.button("❌ تأكيد الحذف النهائي"):
                        row_index_to_delete = selected_item[0]
                        db.delete_rows(row_index_to_delete)
                        st.sidebar.success("تم حذف العنصر بنجاح من قاعدة البيانات!")
                        st.rerun()
                else:
                    st.sidebar.info("قاعدة البيانات فارغة تماماً، لا يوجد ما يمكن حذفه.")
            except Exception as e:
                st.sidebar.error("حدث خطأ أثناء محاولة جلب قائمة الحذف.")

elif password_input != "":
    st.sidebar.error("كلمة السر غير صحيحة!")