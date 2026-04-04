import os
import time
import json
import requests
import streamlit as st
from pathlib import Path

LOCAL_API = "http://127.0.0.1:5001"
CLOUD_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
CLOUD_LOGIN_URL = f"{CLOUD_BASE_URL}/login.html"
CLOUD_REGISTER_URL = f"{CLOUD_BASE_URL}/register.html"
CLOUD_RENEW_URL = f"{CLOUD_BASE_URL}/renew"
LOADING_GIF_PATH = "images/loading_B.gif"

st.set_page_config(
    page_title="Basira Local" 
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# UTILITIES
# =========================================================

def api_get(path: str):
    try:
        return requests.get(f"{LOCAL_API}{path}", timeout=10)
    except Exception as e:
        return None


def api_post(path: str, payload=None):
    try:
        return requests.post(f"{LOCAL_API}{path}", json=payload or {}, timeout=20)
    except Exception:
        return None


def init_session_state():
    defaults = {
        "startup_checked": False,
        "startup_status": None,
        "setup_step": 1,
        "login_completed": False,
        "user_id": "",
        "access_token": "",
        "refresh_token": "",
        "expires_at": "",
        "subscription_status": "active",
        "data_dir": "",
        "setup_finished": False,
        "entered_app": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def refresh_startup_status():
    response = api_get("/api/startup-status")
    if response and response.ok:
        st.session_state.startup_status = response.json()
        st.session_state.startup_checked = True
    else:
        st.session_state.startup_status = {
            "state": "backend_unreachable",
            "reason": "local_backend_not_running"
        }
        st.session_state.startup_checked = True


def setup_initialize():
    response = api_post("/api/setup/init")
    return response is not None and response.ok


def complete_local_login(user_id, access_token, refresh_token, expires_at, subscription_status):
    payload = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "subscription_status": subscription_status
    }
    response = api_post("/api/setup/login-complete", payload)
    return response is not None and response.ok


def configure_data_dir(data_dir):
    response = api_post("/api/setup/select-data-dir", {"data_dir": data_dir})
    return response


def install_models():
    response = api_post("/api/setup/install-models")
    return response


def verify_setup():
    response = api_get("/api/setup/verify")
    return response


def finalize_setup():
    response = api_post("/api/setup/finalize")
    return response is not None and response.ok


def repair_models():
    response = api_post("/api/recovery/repair-models")
    return response is not None and response.ok


def reselect_data_dir(data_dir):
    response = api_post("/api/recovery/reselect-data-dir", {"data_dir": data_dir})
    return response


def refresh_session(user_id, access_token, refresh_token, expires_at, subscription_status):
    payload = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "subscription_status": subscription_status
    }
    response = api_post("/api/session/refresh", payload)
    return response is not None and response.ok


def renew_demo():
    response = api_post("/api/subscription/renew-demo")
    return response is not None and response.ok


def get_config():
    response = api_get("/api/config")
    if response and response.ok:
        return response.json()
    return None


def show_loading_gif():
    if os.path.exists(LOADING_GIF_PATH):
        st.image(LOADING_GIF_PATH, use_container_width=False, width=260)
    else:
        st.info("ضع ملف GIF هنا: images/loading_B.gif")


# =========================================================
# UI HELPERS
# =========================================================

def render_header():
    st.markdown(
        """
        <div style="padding: 12px 0 4px 0;">
            <h1 style="margin:0; font-size: 2.2rem;">Basira Local Environment</h1>
            <p style="margin: 6px 0 0 0; color: #6b7280;">
                Secure local setup, validation, and recovery for the on-device Basira environment.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_state_badge(label, color="#2563eb"):
    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:8px 14px;
            border-radius:999px;
            background:{color}15;
            color:{color};
            font-weight:600;
            font-size:0.9rem;
            border:1px solid {color}33;
            margin-bottom:16px;
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_login_capture_form(title_text="Link your cloud login"):
    st.subheader(title_text)
    st.write("بعد تسجيل الدخول من الكلاود، الصقي بيانات الجلسة هنا مؤقتًا في مرحلة MVP حتى نربط الحساب بالبيئة المحلية.")

    with st.form("local_login_capture_form"):
        user_id = st.text_input("User ID")
        access_token = st.text_area("Access Token", height=100)
        refresh_token = st.text_area("Refresh Token", height=100)
        expires_at = st.text_input("Session Expiry ISO", placeholder="2026-01-01T12:00:00+00:00")
        subscription_status = st.selectbox(
            "Subscription Status",
            ["active", "trialing", "inactive", "expired", "cancelled"],
            index=0
        )

        submitted = st.form_submit_button("ربط الجلسة المحلية")

    if submitted:
        if not user_id or not access_token or not expires_at:
            st.error("الرجاء تعبئة User ID و Access Token و Session Expiry على الأقل.")
        else:
            ok = complete_local_login(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                subscription_status=subscription_status
            )
            if ok:
                st.session_state.user_id = user_id
                st.session_state.access_token = access_token
                st.session_state.refresh_token = refresh_token
                st.session_state.expires_at = expires_at
                st.session_state.subscription_status = subscription_status
                st.session_state.login_completed = True
                st.success("تم ربط الجلسة المحلية بنجاح.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("تعذر ربط الجلسة المحلية. تأكدي أن local bootstrap backend يعمل.")


def render_open_cloud_buttons(show_register=False, show_renew=False):
    cols = st.columns(3 if show_register else 2)

    with cols[0]:
        st.link_button("فتح صفحة تسجيل الدخول", CLOUD_LOGIN_URL, use_container_width=True)

    if show_register:
        with cols[1]:
            st.link_button("فتح صفحة إنشاء حساب", CLOUD_REGISTER_URL, use_container_width=True)

        if show_renew:
            with cols[2]:
                st.link_button("فتح صفحة التجديد", CLOUD_RENEW_URL, use_container_width=True)
    else:
        if show_renew:
            with cols[1]:
                st.link_button("فتح صفحة التجديد", CLOUD_RENEW_URL, use_container_width=True)


def render_divider():
    st.markdown("---")


# =========================================================
# NEW USER SETUP FLOW
# =========================================================

def render_new_user_setup():
    render_state_badge("New User Setup", "#16a34a")
    st.success("لا توجد تهيئة محلية سابقة على هذا الجهاز. سنبدأ تجهيز البيئة المحلية للمستخدم الجديد.")

    if not st.session_state.login_completed:
        st.subheader("الخطوة 1: تسجيل الدخول من الكلاود")
        st.write("إذا كان المستخدم أنشأ حسابًا جديدًا، فالمفترض بعد التسجيل أن يذهب إلى صفحة تسجيل الدخول ثم يعود هنا لإكمال التهيئة المحلية.")
        render_open_cloud_buttons(show_register=True, show_renew=False)
        render_divider()
        render_login_capture_form("الخطوة 2: ربط جلسة تسجيل الدخول المحلية")
        return

    st.subheader("الخطوة 3: اختيار Data Directory")
    st.write("اختاري المكان الذي سيتم فيه حفظ المودلز، المخرجات، الأصول، والملفات المؤقتة.")

    default_data_dir = str(Path.home() / "BasiraData")
    data_dir = st.text_input("Data Directory", value=st.session_state.data_dir or default_data_dir)

    if st.button("حفظ المسار والبدء بالتجهيز", use_container_width=True):
        st.session_state.data_dir = data_dir
        with st.spinner("جارٍ إنشاء المجلدات الأساسية..."):
            response = configure_data_dir(data_dir)

        if response and response.ok:
            st.success("تم تجهيز مجلدات البيانات بنجاح.")
            st.session_state.setup_step = 3
            st.rerun()
        else:
            try:
                msg = response.json().get("message", "تعذر تجهيز مجلدات البيانات.")
            except Exception:
                msg = "تعذر تجهيز مجلدات البيانات."
            st.error(msg)
            return

    if st.session_state.setup_step >= 3:
        render_divider()
        st.subheader("الخطوة 4: تجهيز البيئة المحلية")
        st.write("في هذه المرحلة يتم تنزيل أو تجهيز الملفات الأساسية وإعداد البيئة المحلية للتشغيل.")
        show_loading_gif()

        if st.button("ابدأ تجهيز البيئة", type="primary", use_container_width=True):
            progress = st.progress(0)
            status_box = st.empty()

            status_box.info("تهيئة البيئة المحلية...")
            progress.progress(15)
            time.sleep(0.5)

            status_box.info("تجهيز ملفات النموذج الأساسية...")
            install_response = install_models()
            progress.progress(55)
            time.sleep(0.5)

            if not install_response or not install_response.ok:
                st.error("فشل تجهيز الملفات الأساسية.")
                return

            status_box.info("التحقق من البيئة المحلية...")
            verify_response = verify_setup()
            progress.progress(80)
            time.sleep(0.5)

            if not verify_response or not verify_response.ok:
                st.error("فشل التحقق من البيئة المحلية.")
                return

            verify_payload = verify_response.json()
            if verify_payload.get("status") != "ok":
                st.error("التحقق لم ينجح. راجعي تفاصيل البيئة المحلية.")
                st.json(verify_payload)
                return

            status_box.info("اعتماد الإعداد النهائي...")
            finalize_ok = finalize_setup()
            progress.progress(100)
            time.sleep(0.5)

            if finalize_ok:
                st.success("اكتملت التهيئة المحلية بنجاح. سيتم فتح التطبيق المحلي.")
                st.session_state.setup_finished = True
                time.sleep(1)
                refresh_startup_status()
                st.rerun()
            else:
                st.error("تعذر اعتماد التهيئة النهائية.")

    if st.session_state.setup_finished:
        render_divider()
        st.success("البيئة المحلية جاهزة الآن.")
        if st.button("الدخول إلى Basira Local", use_container_width=True):
            st.session_state.entered_app = True
            st.rerun()


# =========================================================
# EXISTING USER FLOW
# =========================================================

def render_existing_user_healthy(state):
    color = "#2563eb"
    label = "Healthy Startup"
    if state["state"] == "healthy_with_optional_update":
        color = "#f59e0b"
        label = "Healthy with Optional Update"

    render_state_badge(label, color)

    config = get_config()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("App State", state["state"])

    with col2:
        st.metric("Subscription", config.get("subscription_status", "unknown") if config else "unknown")

    with col3:
        st.metric("Setup Completed", "Yes" if config and config.get("setup_completed") else "No")

    st.success("البيئة المحلية سليمة ويمكن الدخول مباشرة.")

    if state["state"] == "healthy_with_optional_update":
        st.info("يوجد تحديث اختياري متاح، لكن يمكن للمستخدم المتابعة الآن بدون إجباريته.")

    if st.button("فتح التطبيق المحلي", type="primary", use_container_width=True):
        st.session_state.entered_app = True
        st.rerun()


def render_login_required(state):
    render_state_badge("Login Required", "#dc2626")
    st.warning("هذه ليست حالة مستخدم جديد. التهيئة المحلية موجودة، لكن الجلسة منتهية أو غير موجودة ويجب فقط إعادة تسجيل الدخول.")

    render_open_cloud_buttons(show_register=False, show_renew=False)
    render_divider()

    render_login_capture_form("إعادة ربط الجلسة المحلية")

    if st.session_state.login_completed:
        if st.button("تحديث الجلسة والمتابعة", type="primary", use_container_width=True):
            ok = refresh_session(
                st.session_state.user_id,
                st.session_state.access_token,
                st.session_state.refresh_token,
                st.session_state.expires_at,
                st.session_state.subscription_status
            )
            if ok:
                st.success("تم تحديث الجلسة بنجاح.")
                time.sleep(1)
                refresh_startup_status()
                st.rerun()
            else:
                st.error("تعذر تحديث الجلسة.")


def render_update_required():
    render_state_badge("Mandatory Update Required", "#ef4444")
    st.error("هذه النسخة من التطبيق المحلي تتطلب تحديثًا إجباريًا قبل المتابعة.")
    st.write("يجب تنزيل النسخة الأحدث من Basira Local.")
    st.link_button("فتح بوابة التحديث / الكلاود", CLOUD_BASE_URL, use_container_width=True)


# =========================================================
# RECOVERY FLOW
# =========================================================

def render_recovery(state):
    render_state_badge("Recovery Required", "#f97316")
    reason = state.get("reason", "unknown")
    st.warning(f"تم اكتشاف مشكلة جزئية في البيئة المحلية: {reason}")

    if reason in ["config_corrupted", "config_invalid"]:
        st.error("ملف الإعداد المحلي تالف أو غير صالح.")
        st.write("في MVP الحالي، أفضل معالجة هي إعادة التهيئة المحلية أو استرجاع الإعداد.")
        if st.button("بدء تهيئة محلية جديدة", type="primary", use_container_width=True):
            setup_initialize()
            st.session_state.login_completed = False
            st.session_state.setup_step = 1
            st.session_state.setup_finished = False
            refresh_startup_status()
            st.rerun()

    elif reason in ["missing_data_dir", "data_dir_not_found", "data_dir_not_writable"]:
        st.write("مجلد البيانات غير موجود أو لم يعد صالحًا أو لا يملك صلاحية كتابة.")
        new_dir = st.text_input("اختيار Data Directory جديد", value=str(Path.home() / "BasiraData"))
        if st.button("تحديث مسار البيانات", use_container_width=True):
            response = reselect_data_dir(new_dir)
            if response and response.ok:
                st.success("تم تحديث مسار البيانات.")
                time.sleep(1)
                refresh_startup_status()
                st.rerun()
            else:
                st.error("تعذر تحديث مسار البيانات.")

    elif reason == "missing_model":
        missing_models = state.get("missing_models", [])
        st.write("هناك ملفات نماذج مفقودة ويجب إصلاحها قبل المتابعة.")
        if missing_models:
            st.json({"missing_models": missing_models})

        if st.button("إصلاح ملفات النموذج", type="primary", use_container_width=True):
            ok = repair_models()
            if ok:
                st.success("تم إصلاح ملفات النموذج بنجاح.")
                time.sleep(1)
                refresh_startup_status()
                st.rerun()
            else:
                st.error("تعذر إصلاح ملفات النموذج.")

    else:
        st.write("تم اكتشاف حالة recovery غير مصنفة بشكل تفصيلي بعد.")
        if st.button("إعادة التحقق", use_container_width=True):
            refresh_startup_status()
            st.rerun()


# =========================================================
# SUBSCRIPTION PANEL
# =========================================================

def render_subscription_panel():
    st.subheader("Subscription")
    st.write("إذا احتاج المستخدم تجديد الاشتراك، يمكن إما فتح صفحة التجديد السحابية أو تنفيذ تجديد تجريبي محليًا.")

    col1, col2 = st.columns(2)

    with col1:
        st.link_button("فتح صفحة التجديد في الكلاود", CLOUD_RENEW_URL, use_container_width=True)

    with col2:
        if st.button("تجديد الاشتراك Demo", use_container_width=True):
            ok = renew_demo()
            if ok:
                st.success("تم تحديث الاشتراك إلى active في وضع demo.")
                time.sleep(1)
                refresh_startup_status()
                st.rerun()
            else:
                st.error("تعذر تنفيذ تجديد الاشتراك demo.")


# =========================================================
# LOCAL APP SHELL
# =========================================================

def render_local_app_shell():
    st.success("تم دخول البيئة المحلية بنجاح.")
    st.title("Basira Local Workspace")

    config = get_config()

    tab1, tab2, tab3 = st.tabs(["Home", "Settings", "Subscription"])

    with tab1:
        st.write("هذه واجهة محلية أولية. هنا لاحقًا تربطين صفحات التحليل المحلي وواجهة التشغيل الفعلية.")
        if config:
            st.json({
                "user_id": config.get("user_id"),
                "data_dir": config.get("data_dir"),
                "models_dir": config.get("models_dir"),
                "subscription_status": config.get("subscription_status")
            })

    with tab2:
        st.write("إعدادات البيئة المحلية")
        if config:
            st.json(config)

    with tab3:
        render_subscription_panel()


# =========================================================
# MAIN
# =========================================================

def main():
    init_session_state()
    render_header()

    if not st.session_state.startup_checked:
        refresh_startup_status()

    state = st.session_state.startup_status or {
        "state": "unknown",
        "reason": "not_checked"
    }

    if st.session_state.entered_app:
        render_local_app_shell()
        return

    current_state = state.get("state")

    if current_state == "backend_unreachable":
        render_state_badge("Local Backend Not Running", "#ef4444")
        st.error("تعذر الوصول إلى local bootstrap backend على localhost:5001")
        st.code("شغلي basira_local_bootstrap.py أولًا", language="bash")
        return

    if current_state in ["new_user", "setup_incomplete"]:
        setup_initialize()
        render_new_user_setup()
        return

    if current_state in ["healthy", "healthy_with_optional_update"]:
        render_existing_user_healthy(state)
        return

    if current_state == "login_required":
        render_login_required(state)
        return

    if current_state == "update_required":
        render_update_required()
        return

    if current_state == "recovery_required":
        render_recovery(state)
        return

    render_state_badge("Unknown State", "#6b7280")
    st.info("حالة غير معروفة. أعيدي التحقق من startup logic.")
    if st.button("إعادة التحقق", use_container_width=True):
        refresh_startup_status()
        st.rerun()


if __name__ == "__main__":
    main()