import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعداد الاتصال بقاعدة البيانات (Google Sheets) ---
def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # التحقق أولاً إذا كان الموقع يعمل على الإنترنت ويستخدم الأسرار (Secrets)
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # إذا كان يعمل محلياً على جهازك، سيستخدم الملف العادي
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

# --- واجهة المستخدم الرئيسية للتطبيق ---
st.title("🎓 منصة تعليم الطلاب الرقمية")
st.write("أهلاً بكم في المنصة التعليمية. يمكنكم تصفح الدروس والاختبارات المتاحة أدناه:")

col_video, col_quiz = st.columns(2)

if db:
    try:
        all_records = db.get_all_records()
        
        with col_video:
            st.header("📺 فيديوهات الدروس")
            videos = [r for r in all_records if str(r.get('نوع الرابط')).strip() == 'فيديو']
            if videos:
                for v in videos:
                    st.subheader(f"📖 درس رقم {v.get('رقم الدرس', '#')}: {v.get('وصف الدرس', '')}")
                    st.video(v['الرابط'])
                    st.markdown("---")
            else:
                st.info("لا توجد فيديوهات مضافة بعد.")
                
        with col_quiz:
            st.header("📝 الاختبارات المتاحة")
            quizzes = [r for r in all_records if str(r.get('نوع الرابط')).strip() == 'اختبار']
            if quizzes:
                for q in quizzes:
                    st.subheader(f"🎯 اختبار الدرس رقم {q.get('رقم الدرس', '#')}")
                    if q.get('وصف الدرس'):
                        st.caption(f"ملاحظة: {q.get('وصف الدرس')}")
                    st.link_button(url=q['الرابط'], label=f"🔗 دخول الاختبار")
                    st.markdown("---")
            else:
                st.info("لا توجد اختبارات مضافة بعد.")
    except Exception as e:
        st.warning("الجدول فارغ حالياً، قم بتسجيل الدخول كمعلم لإضافة المحتوى الأول.")

# --- لوحة التحكم المغلقة بكلمة السر (7962400) ---
st.sidebar.title("🔐 لوحة تحكم المعلم")
password_input = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")

if password_input == "7962400":
    st.sidebar.success("تم تسجيل الدخول بنجاح!")
    
    # خيارات لوحة التحكم (إضافة أو حذف)
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
                # جلب البيانات مع أرقام الصفوف لسهولة الحذف
                raw_rows = db.get_all_values()
                if len(raw_rows) > 1: # التأكد من وجود بيانات عدا العناوين
                    options_to_delete = []
                    # نمر على الصفوف بدءاً من الصف الثاني (السطر الأول عناوين)
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