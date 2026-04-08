// // // // // // // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // // // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // // // // // // // // // const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
// // // // // // // // // // const LOCAL_STREAMLIT_URL = "http://127.0.0.1:8501";
// // // // // // // // // // const LOCAL_RUNTIME_DOWNLOADS = {
// // // // // // // // // //   windows: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-win-x64.zip",
// // // // // // // // // //   mac: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-macos.zip"
// // // // // // // // // // };

// // // // // // // // // // let startupState = null;

// // // // // // // // // // function showNote(id, type, message) {
// // // // // // // // // //   const el = document.getElementById(id);
// // // // // // // // // //   if (!el) return;
// // // // // // // // // //   el.innerHTML = message;
// // // // // // // // // //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // // // // // // }

// // // // // // // // // // function $(id) {
// // // // // // // // // //   return document.getElementById(id);
// // // // // // // // // // }

// // // // // // // // // // function showCard(id) {
// // // // // // // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // // // // // // //     const el = $(cardId);
// // // // // // // // // //     if (el) el.classList.add("isHidden");
// // // // // // // // // //   });

// // // // // // // // // //   const target = $(id);
// // // // // // // // // //   if (target) target.classList.remove("isHidden");
// // // // // // // // // // }

// // // // // // // // // // function setStepState(activeIndex) {
// // // // // // // // // //   const steps = Array.from(document.querySelectorAll(".setup-step"));
// // // // // // // // // //   steps.forEach((step, index) => {
// // // // // // // // // //     step.classList.remove("isActive", "isDone");
// // // // // // // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // // // // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // // // // // // //   });
// // // // // // // // // // }

// // // // // // // // // // function setProgress(percent, text) {
// // // // // // // // // //   const fill = $("progressFill");
// // // // // // // // // //   const label = $("progressText");
// // // // // // // // // //   if (fill) fill.style.width = `${percent}%`;
// // // // // // // // // //   if (label) label.textContent = text;
// // // // // // // // // // }

// // // // // // // // // // function getStoredSessionPayload() {
// // // // // // // // // //   return {
// // // // // // // // // //     user_id: localStorage.getItem("basira_user_id") || "",
// // // // // // // // // //     access_token: localStorage.getItem("basira_access_token") || "",
// // // // // // // // // //     refresh_token: localStorage.getItem("basira_refresh_token") || "",
// // // // // // // // // //     expires_at: localStorage.getItem("basira_session_expires_at") || "",
// // // // // // // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // // // // // // //   };
// // // // // // // // // // }

// // // // // // // // // // function detectPlatform() {
// // // // // // // // // //   const ua = navigator.userAgent.toLowerCase();
// // // // // // // // // //   if (ua.includes("mac")) return "mac";
// // // // // // // // // //   return "windows";
// // // // // // // // // // }

// // // // // // // // // // async function apiGet(path) {
// // // // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`);
// // // // // // // // // //   return response.json();
// // // // // // // // // // }

// // // // // // // // // // async function apiPost(path, payload = {}) {
// // // // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // // // // // //     method: "POST",
// // // // // // // // // //     headers: {
// // // // // // // // // //       "Content-Type": "application/json"
// // // // // // // // // //     },
// // // // // // // // // //     body: JSON.stringify(payload)
// // // // // // // // // //   });

// // // // // // // // // //   return response.json();
// // // // // // // // // // }

// // // // // // // // // // async function readCloudUser() {
// // // // // // // // // //   try {
// // // // // // // // // //     const {
// // // // // // // // // //       data: { session }
// // // // // // // // // //     } = await supabaseClient.auth.getSession();

// // // // // // // // // //     if (!session?.user) {
// // // // // // // // // //       $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
// // // // // // // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // // // //       return null;
// // // // // // // // // //     }

// // // // // // // // // //     const userName =
// // // // // // // // // //       session.user.user_metadata?.full_name ||
// // // // // // // // // //       session.user.email ||
// // // // // // // // // //       session.user.id;

// // // // // // // // // //     $("cloudUserLabel").textContent = userName;
// // // // // // // // // //     $("subscriptionLabel").textContent =
// // // // // // // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // // // // // // //     return session;
// // // // // // // // // //   } catch (err) {
// // // // // // // // // //     $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
// // // // // // // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // // // //     return null;
// // // // // // // // // //   }
// // // // // // // // // // }

// // // // // // // // // // async function pushLocalSession() {
// // // // // // // // // //   const payload = getStoredSessionPayload();

// // // // // // // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // // // // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // // // // // // //   }

// // // // // // // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // // // // // // }

// // // // // // // // // // async function initializeStartup() {
// // // // // // // // // //   setStepState(0);

// // // // // // // // // //   try {
// // // // // // // // // //     await readCloudUser();

// // // // // // // // // //     $("startupStatusCard").querySelector(".local-card__title").textContent = "جارٍ التحقق من البيئة المحلية";
// // // // // // // // // //     $("startupStatusCard").querySelector(".local-card__text").textContent =
// // // // // // // // // //       "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";

// // // // // // // // // //     startupState = await apiGet("/api/startup-status");

// // // // // // // // // //     if (!startupState || !startupState.state) {
// // // // // // // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // // // // // // //     }

// // // // // // // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // // // // // // //       showCard("newUserCard");
// // // // // // // // // //       setStepState(1);
// // // // // // // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // // // //       showCard("readyCard");
// // // // // // // // // //       setStepState(3);
// // // // // // // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (startupState.state === "login_required") {
// // // // // // // // // //       showNote(
// // // // // // // // // //         "localSetupMessage",
// // // // // // // // // //         "err",
// // // // // // // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
// // // // // // // // // //       );

// // // // // // // // // //       await pushLocalSession();

// // // // // // // // // //       startupState = await apiGet("/api/startup-status");

// // // // // // // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // // // //         showCard("readyCard");
// // // // // // // // // //         setStepState(3);
// // // // // // // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // // // // // // //       } else {
// // // // // // // // // //         showCard("newUserCard");
// // // // // // // // // //         setStepState(1);
// // // // // // // // // //       }

// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (startupState.state === "recovery_required") {
// // // // // // // // // //       const reason = startupState.reason || "unknown";
// // // // // // // // // //       showCard("recoveryCard");
// // // // // // // // // //       setStepState(1);

// // // // // // // // // //       const recoveryText = $("recoveryText");
// // // // // // // // // //       const recoveryPathField = $("recoveryPathField");
// // // // // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // // // // //       if (reason === "missing_data_dir" || reason === "data_dir_not_found" || reason === "data_dir_not_writable") {
// // // // // // // // // //         recoveryText.textContent =
// // // // // // // // // //           "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
// // // // // // // // // //         recoveryPathField.classList.remove("isHidden");
// // // // // // // // // //         repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
// // // // // // // // // //         repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // // // // // // //       } else if (reason === "missing_model") {
// // // // // // // // // //         recoveryText.textContent =
// // // // // // // // // //           "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // // // //         repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
// // // // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // // // //       } else {
// // // // // // // // // //         recoveryText.textContent =
// // // // // // // // // //           "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // // // //         repairPrimaryBtn.textContent = "إصلاح الآن";
// // // // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // // // //       }

// // // // // // // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (startupState.state === "update_required") {
// // // // // // // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.");
// // // // // // // // // //       showCard("recoveryCard");
// // // // // // // // // //       $("recoveryText").textContent = "يلزم تحديث النسخة المحلية قبل المتابعة.";
// // // // // // // // // //       $("repairPrimaryBtn").textContent = "فتح بوابة التحديث";
// // // // // // // // // //       $("repairPrimaryBtn").dataset.mode = "open-update";
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // // // // // // //   } catch (err) {
// // // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر بدء صفحة التهيئة المحلية.");
// // // // // // // // // //   }
// // // // // // // // // // }

// // // // // // // // // // async function runFirstSetup() {
// // // // // // // // // //   try {
// // // // // // // // // //     const session = await readCloudUser();
// // // // // // // // // //     if (!session?.user) {
// // // // // // // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // // // // // // //     }

// // // // // // // // // //     setStepState(2);
// // // // // // // // // //     showCard("loadingCard");

// // // // // // // // // //     setProgress(10, "تهيئة الحالة المحلية...");
// // // // // // // // // //     await apiPost("/api/setup/init");
// // // // // // // // // //     await pushLocalSession();

// // // // // // // // // //     const dataDir = $("dataDirectory")?.value.trim() || "C:\\BasiraData";

// // // // // // // // // //     setProgress(30, "إنشاء المجلدات المحلية...");
// // // // // // // // // //     await apiPost("/api/setup/select-data-dir", {
// // // // // // // // // //       data_dir: dataDir
// // // // // // // // // //     });

// // // // // // // // // //     const platform = detectPlatform();
// // // // // // // // // //     const runtimeUrl = LOCAL_RUNTIME_DOWNLOADS[platform];

// // // // // // // // // //     setProgress(55, "تنزيل الملفات الأساسية المحلية...");
// // // // // // // // // //     await apiPost("/api/setup/install-models", {
// // // // // // // // // //       runtime_url: runtimeUrl,
// // // // // // // // // //       platform
// // // // // // // // // //     });

// // // // // // // // // //     setProgress(80, "التحقق من الجاهزية...");
// // // // // // // // // //     const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // // // // // // //     }

// // // // // // // // // //     setProgress(95, "اعتماد التهيئة النهائية...");
// // // // // // // // // //     await apiPost("/api/setup/finalize");

// // // // // // // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // // // // // // //     setStepState(3);

// // // // // // // // // //     showCard("readyCard");
// // // // // // // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // // // // // // //   } catch (err) {
// // // // // // // // // //     showCard("recoveryCard");
// // // // // // // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // // // // // // //   }
// // // // // // // // // // }

// // // // // // // // // // async function runRecoveryAction() {
// // // // // // // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // // // // // // //   try {
// // // // // // // // // //     if (mode === "reselect-path") {
// // // // // // // // // //       const pathValue = $("recoveryDataDirectory")?.value.trim() || "C:\\BasiraData";
// // // // // // // // // //       showCard("loadingCard");
// // // // // // // // // //       setProgress(30, "تحديث مسار البيانات...");
// // // // // // // // // //       await apiPost("/api/recovery/reselect-data-dir", {
// // // // // // // // // //         data_dir: pathValue
// // // // // // // // // //       });

// // // // // // // // // //       setProgress(70, "التحقق من البيئة...");
// // // // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // // // // // // //       }

// // // // // // // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // // // // // // //       showCard("readyCard");
// // // // // // // // // //       setStepState(3);
// // // // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (mode === "repair-models") {
// // // // // // // // // //       showCard("loadingCard");
// // // // // // // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // // // // // // // //       await apiPost("/api/recovery/repair-models");

// // // // // // // // // //       setProgress(75, "التحقق النهائي...");
// // // // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // // // // // // //       }

// // // // // // // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // // // // // // //       showCard("readyCard");
// // // // // // // // // //       setStepState(3);
// // // // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // // // //       return;
// // // // // // // // // //     }

// // // // // // // // // //     if (mode === "open-update") {
// // // // // // // // // //       window.open("https://basira.basira-toolmodel.workers.dev", "_blank");
// // // // // // // // // //       return;
// // // // // // // // // //     }
// // // // // // // // // //   } catch (err) {
// // // // // // // // // //     showCard("recoveryCard");
// // // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // // // // // // //   }
// // // // // // // // // // }

// // // // // // // // // // function launchLocalEnvironment() {
// // // // // // // // // //   window.open(LOCAL_STREAMLIT_URL, "_blank");
// // // // // // // // // //   showNote("localSetupMessage", "ok", "تم إرسال أمر تشغيل الواجهة المحلية. إذا لم تعمل بعد، تحققي من خدمة التشغيل المحلي.");
// // // // // // // // // // }

// // // // // // // // // // async function renewSubscriptionDemo() {
// // // // // // // // // //   try {
// // // // // // // // // //     const userId = localStorage.getItem("basira_user_id");
// // // // // // // // // //     if (!userId) {
// // // // // // // // // //       throw new Error("لم يتم العثور على مستخدم محلي مربوط بالجلسة.");
// // // // // // // // // //     }

// // // // // // // // // //     await apiPost("/api/subscription/renew-demo", {
// // // // // // // // // //       user_id: userId
// // // // // // // // // //     });

// // // // // // // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // // // // // // //     $("subscriptionLabel").textContent = "active";

// // // // // // // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // // // // // // //   } catch (err) {
// // // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // // // // // //   }
// // // // // // // // // // }

// // // // // // // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // // // // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // // // // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // // // // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // // // // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // // // // // // //     const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
// // // // // // // // // //     if (useCloud) {
// // // // // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // // // // //     } else {
// // // // // // // // // //       renewSubscriptionDemo();
// // // // // // // // // //     }
// // // // // // // // // //   });

// // // // // // // // // //   await initializeStartup();
// // // // // // // // // // });



// // // // // // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // // // // // // // // const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
// // // // // // // // // const LOCAL_STREAMLIT_URL = "http://127.0.0.1:8501";
// // // // // // // // // const LOCAL_RUNTIME_DOWNLOADS = {
// // // // // // // // //   windows: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-win-x64.zip",
// // // // // // // // //   mac: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-macos.zip"
// // // // // // // // // };

// // // // // // // // // let startupState = null;
// // // // // // // // // let inactivityTimer = null;
// // // // // // // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

// // // // // // // // // function showNote(id, type, message) {
// // // // // // // // //   const el = document.getElementById(id);
// // // // // // // // //   if (!el) return;
// // // // // // // // //   el.innerHTML = message;
// // // // // // // // //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // // // // // }

// // // // // // // // // function $(id) {
// // // // // // // // //   return document.getElementById(id);
// // // // // // // // // }

// // // // // // // // // function showCard(id) {
// // // // // // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // // // // // //     const el = $(cardId);
// // // // // // // // //     if (el) el.classList.add("isHidden");
// // // // // // // // //   });

// // // // // // // // //   const target = $(id);
// // // // // // // // //   if (target) target.classList.remove("isHidden");
// // // // // // // // // }

// // // // // // // // // function setStepState(activeIndex) {
// // // // // // // // //   const steps = Array.from(document.querySelectorAll(".setup-step"));
// // // // // // // // //   steps.forEach((step, index) => {
// // // // // // // // //     step.classList.remove("isActive", "isDone");
// // // // // // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // // // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // // // // // //   });
// // // // // // // // // }

// // // // // // // // // function setProgress(percent, text) {
// // // // // // // // //   const fill = $("progressFill");
// // // // // // // // //   const label = $("progressText");
// // // // // // // // //   if (fill) fill.style.width = `${percent}%`;
// // // // // // // // //   if (label) label.textContent = text;
// // // // // // // // // }

// // // // // // // // // function getStoredSessionPayload() {
// // // // // // // // //   return {
// // // // // // // // //     user_id: localStorage.getItem("basira_user_id") || "",
// // // // // // // // //     access_token: localStorage.getItem("basira_access_token") || "",
// // // // // // // // //     refresh_token: localStorage.getItem("basira_refresh_token") || "",
// // // // // // // // //     expires_at: localStorage.getItem("basira_session_expires_at") || "",
// // // // // // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // // // // // //   };
// // // // // // // // // }

// // // // // // // // // function detectPlatform() {
// // // // // // // // //   const ua = navigator.userAgent.toLowerCase();
// // // // // // // // //   if (ua.includes("mac")) return "mac";
// // // // // // // // //   return "windows";
// // // // // // // // // }

// // // // // // // // // async function apiGet(path) {
// // // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`);
// // // // // // // // //   return response.json();
// // // // // // // // // }

// // // // // // // // // async function apiPost(path, payload = {}) {
// // // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // // // // //     method: "POST",
// // // // // // // // //     headers: {
// // // // // // // // //       "Content-Type": "application/json"
// // // // // // // // //     },
// // // // // // // // //     body: JSON.stringify(payload)
// // // // // // // // //   });

// // // // // // // // //   return response.json();
// // // // // // // // // }

// // // // // // // // // async function readCloudUser() {
// // // // // // // // //   try {
// // // // // // // // //     const {
// // // // // // // // //       data: { session }
// // // // // // // // //     } = await supabaseClient.auth.getSession();

// // // // // // // // //     if (!session?.user) {
// // // // // // // // //       $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
// // // // // // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // // //       return null;
// // // // // // // // //     }

// // // // // // // // //     const userName =
// // // // // // // // //       session.user.user_metadata?.full_name ||
// // // // // // // // //       session.user.email ||
// // // // // // // // //       session.user.id;

// // // // // // // // //     $("cloudUserLabel").textContent = userName;
// // // // // // // // //     $("subscriptionLabel").textContent =
// // // // // // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // // // // // //     return session;
// // // // // // // // //   } catch (err) {
// // // // // // // // //     $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
// // // // // // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // // //     return null;
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // async function pushLocalSession() {
// // // // // // // // //   const payload = getStoredSessionPayload();

// // // // // // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // // // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // // // // // //   }

// // // // // // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // // // // // }

// // // // // // // // // async function sendHeartbeat() {
// // // // // // // // //   try {
// // // // // // // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // // // // // // //       method: "POST",
// // // // // // // // //       headers: {
// // // // // // // // //         "Content-Type": "application/json"
// // // // // // // // //       }
// // // // // // // // //     });

// // // // // // // // //     if (response.status === 401) {
// // // // // // // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // // // // // // //       setTimeout(() => {
// // // // // // // // //         window.location.href = "./login.html";
// // // // // // // // //       }, 1200);
// // // // // // // // //     }
// // // // // // // // //   } catch (err) {
// // // // // // // // //     console.warn("Heartbeat failed:", err);
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // async function autoLogoutNow() {
// // // // // // // // //   try {
// // // // // // // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // // // // // // //       method: "POST",
// // // // // // // // //       headers: {
// // // // // // // // //         "Content-Type": "application/json"
// // // // // // // // //       }
// // // // // // // // //     });
// // // // // // // // //   } catch (err) {
// // // // // // // // //     console.warn("Auto logout request failed:", err);
// // // // // // // // //   }

// // // // // // // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // // // // // // //   setTimeout(() => {
// // // // // // // // //     window.location.href = "./login.html";
// // // // // // // // //   }, 1200);
// // // // // // // // // }

// // // // // // // // // function resetInactivityTimer() {
// // // // // // // // //   if (inactivityTimer) {
// // // // // // // // //     clearTimeout(inactivityTimer);
// // // // // // // // //   }

// // // // // // // // //   inactivityTimer = setTimeout(() => {
// // // // // // // // //     autoLogoutNow();
// // // // // // // // //   }, INACTIVITY_LIMIT_MS);
// // // // // // // // // }

// // // // // // // // // function bindActivityTracking() {
// // // // // // // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // // // // // // //     window.addEventListener(eventName, () => {
// // // // // // // // //       resetInactivityTimer();
// // // // // // // // //     });
// // // // // // // // //   });

// // // // // // // // //   resetInactivityTimer();
// // // // // // // // //   setInterval(sendHeartbeat, 60000);
// // // // // // // // // }

// // // // // // // // // async function initializeStartup() {
// // // // // // // // //   setStepState(0);

// // // // // // // // //   try {
// // // // // // // // //     await readCloudUser();

// // // // // // // // //     $("startupStatusCard").querySelector(".local-card__title").textContent = "جارٍ التحقق من البيئة المحلية";
// // // // // // // // //     $("startupStatusCard").querySelector(".local-card__text").textContent =
// // // // // // // // //       "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";

// // // // // // // // //     startupState = await apiGet("/api/startup-status");

// // // // // // // // //     if (!startupState || !startupState.state) {
// // // // // // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // // // // // //       showCard("newUserCard");
// // // // // // // // //       setStepState(1);
// // // // // // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // // //       showCard("readyCard");
// // // // // // // // //       setStepState(3);
// // // // // // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "login_required") {
// // // // // // // // //       showNote(
// // // // // // // // //         "localSetupMessage",
// // // // // // // // //         "err",
// // // // // // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
// // // // // // // // //       );

// // // // // // // // //       await pushLocalSession();

// // // // // // // // //       startupState = await apiGet("/api/startup-status");

// // // // // // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // // //         showCard("readyCard");
// // // // // // // // //         setStepState(3);
// // // // // // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // // // // // //       } else {
// // // // // // // // //         showCard("newUserCard");
// // // // // // // // //         setStepState(1);
// // // // // // // // //       }

// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "subscription_required") {
// // // // // // // // //       showCard("recoveryCard");
// // // // // // // // //       setStepState(1);
// // // // // // // // //       $("recoveryText").textContent =
// // // // // // // // //         "الاشتراك غير فعال حاليًا. يجب تجديد الاشتراك قبل تشغيل البيئة المحلية.";
// // // // // // // // //       $("repairPrimaryBtn").textContent = "فتح صفحة التجديد";
// // // // // // // // //       $("repairPrimaryBtn").dataset.mode = "open-update";
// // // // // // // // //       showNote("localSetupMessage", "err", "يلزم اشتراك فعال للمتابعة.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "recovery_required") {
// // // // // // // // //       const reason = startupState.reason || "unknown";
// // // // // // // // //       showCard("recoveryCard");
// // // // // // // // //       setStepState(1);

// // // // // // // // //       const recoveryText = $("recoveryText");
// // // // // // // // //       const recoveryPathField = $("recoveryPathField");
// // // // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // // // //       if (reason === "missing_data_dir" || reason === "data_dir_not_found" || reason === "data_dir_not_writable") {
// // // // // // // // //         recoveryText.textContent =
// // // // // // // // //           "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
// // // // // // // // //         recoveryPathField.classList.remove("isHidden");
// // // // // // // // //         repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
// // // // // // // // //         repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // // // // // //       } else if (reason === "missing_model") {
// // // // // // // // //         recoveryText.textContent =
// // // // // // // // //           "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // // //         repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
// // // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // // //       } else {
// // // // // // // // //         recoveryText.textContent =
// // // // // // // // //           "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // // //         repairPrimaryBtn.textContent = "إصلاح الآن";
// // // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // // //       }

// // // // // // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (startupState.state === "update_required") {
// // // // // // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.");
// // // // // // // // //       showCard("recoveryCard");
// // // // // // // // //       $("recoveryText").textContent = "يلزم تحديث النسخة المحلية قبل المتابعة.";
// // // // // // // // //       $("repairPrimaryBtn").textContent = "فتح بوابة التحديث";
// // // // // // // // //       $("repairPrimaryBtn").dataset.mode = "open-update";
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // // // // // //   } catch (err) {
// // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر بدء صفحة التهيئة المحلية.");
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // async function runFirstSetup() {
// // // // // // // // //   try {
// // // // // // // // //     const session = await readCloudUser();
// // // // // // // // //     if (!session?.user) {
// // // // // // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // // // // // //     }

// // // // // // // // //     setStepState(2);
// // // // // // // // //     showCard("loadingCard");

// // // // // // // // //     setProgress(10, "تهيئة الحالة المحلية...");
// // // // // // // // //     await apiPost("/api/setup/init");
// // // // // // // // //     await pushLocalSession();

// // // // // // // // //     const dataDir =
// // // // // // // // //       $("dataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // // // //     setProgress(30, "إنشاء المجلدات المحلية...");
// // // // // // // // //     await apiPost("/api/setup/select-data-dir", {
// // // // // // // // //       data_dir: dataDir
// // // // // // // // //     });

// // // // // // // // //     const platform = detectPlatform();
// // // // // // // // //     const runtimeUrl = LOCAL_RUNTIME_DOWNLOADS[platform];

// // // // // // // // //     setProgress(55, "تنزيل الملفات الأساسية المحلية...");
// // // // // // // // //     await apiPost("/api/setup/install-models", {
// // // // // // // // //       runtime_url: runtimeUrl,
// // // // // // // // //       platform
// // // // // // // // //     });

// // // // // // // // //     setProgress(80, "التحقق من الجاهزية...");
// // // // // // // // //     const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // // // // // //     }

// // // // // // // // //     setProgress(95, "اعتماد التهيئة النهائية...");
// // // // // // // // //     await apiPost("/api/setup/finalize");

// // // // // // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // // // // // //     setStepState(3);

// // // // // // // // //     showCard("readyCard");
// // // // // // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // // // // // //   } catch (err) {
// // // // // // // // //     showCard("recoveryCard");
// // // // // // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // async function runRecoveryAction() {
// // // // // // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // // // // // //   try {
// // // // // // // // //     if (mode === "reselect-path") {
// // // // // // // // //       const pathValue =
// // // // // // // // //         $("recoveryDataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // // // //       showCard("loadingCard");
// // // // // // // // //       setProgress(30, "تحديث مسار البيانات...");
// // // // // // // // //       await apiPost("/api/recovery/reselect-data-dir", {
// // // // // // // // //         data_dir: pathValue
// // // // // // // // //       });

// // // // // // // // //       setProgress(70, "التحقق من البيئة...");
// // // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // // // // // //       }

// // // // // // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // // // // // //       showCard("readyCard");
// // // // // // // // //       setStepState(3);
// // // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (mode === "repair-models") {
// // // // // // // // //       showCard("loadingCard");
// // // // // // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // // // // // // //       await apiPost("/api/recovery/repair-models");

// // // // // // // // //       setProgress(75, "التحقق النهائي...");
// // // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // // // // // //       }

// // // // // // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // // // // // //       showCard("readyCard");
// // // // // // // // //       setStepState(3);
// // // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // // //       return;
// // // // // // // // //     }

// // // // // // // // //     if (mode === "open-update") {
// // // // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // // // //       return;
// // // // // // // // //     }
// // // // // // // // //   } catch (err) {
// // // // // // // // //     showCard("recoveryCard");
// // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // function launchLocalEnvironment() {
// // // // // // // // //   window.open(LOCAL_STREAMLIT_URL, "_blank");
// // // // // // // // //   showNote("localSetupMessage", "ok", "تم إرسال أمر تشغيل الواجهة المحلية. إذا لم تعمل بعد، تحققي من خدمة التشغيل المحلي.");
// // // // // // // // // }

// // // // // // // // // async function renewSubscriptionDemo() {
// // // // // // // // //   try {
// // // // // // // // //     const userId = localStorage.getItem("basira_user_id");
// // // // // // // // //     if (!userId) {
// // // // // // // // //       throw new Error("لم يتم العثور على مستخدم محلي مربوط بالجلسة.");
// // // // // // // // //     }

// // // // // // // // //     await apiPost("/api/subscription/renew-demo", {
// // // // // // // // //       user_id: userId
// // // // // // // // //     });

// // // // // // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // // // // // //     $("subscriptionLabel").textContent = "active";

// // // // // // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // // // // // //   } catch (err) {
// // // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // // // // //   }
// // // // // // // // // }

// // // // // // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // // // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // // // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // // // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // // // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // // // // // //     const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
// // // // // // // // //     if (useCloud) {
// // // // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // // // //     } else {
// // // // // // // // //       renewSubscriptionDemo();
// // // // // // // // //     }
// // // // // // // // //   });

// // // // // // // // //   bindActivityTracking();
// // // // // // // // //   await initializeStartup();
// // // // // // // // // });

// // // // // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // // // // // // // const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
// // // // // // // // const LOCAL_STREAMLIT_URL = "http://127.0.0.1:8501";
// // // // // // // // const LOCAL_RUNTIME_DOWNLOADS = {
// // // // // // // //   windows: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-win-x64.zip",
// // // // // // // //   mac: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-macos.zip"
// // // // // // // // };

// // // // // // // // let startupState = null;
// // // // // // // // let inactivityTimer = null;
// // // // // // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

// // // // // // // // function showNote(id, type, message) {
// // // // // // // //   const el = document.getElementById(id);
// // // // // // // //   if (!el) return;
// // // // // // // //   el.innerHTML = message;
// // // // // // // //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // // // // }

// // // // // // // // function $(id) {
// // // // // // // //   return document.getElementById(id);
// // // // // // // // }

// // // // // // // // function showCard(id) {
// // // // // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // // // // //     const el = $(cardId);
// // // // // // // //     if (el) el.classList.add("isHidden");
// // // // // // // //   });

// // // // // // // //   const target = $(id);
// // // // // // // //   if (target) target.classList.remove("isHidden");
// // // // // // // // }

// // // // // // // // function setStepState(activeIndex) {
// // // // // // // //   const steps = Array.from(document.querySelectorAll(".setup-step"));
// // // // // // // //   steps.forEach((step, index) => {
// // // // // // // //     step.classList.remove("isActive", "isDone");
// // // // // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // // // // //   });
// // // // // // // // }

// // // // // // // // function setProgress(percent, text) {
// // // // // // // //   const fill = $("progressFill");
// // // // // // // //   const label = $("progressText");
// // // // // // // //   if (fill) fill.style.width = `${percent}%`;
// // // // // // // //   if (label) label.textContent = text;
// // // // // // // // }

// // // // // // // // function getStoredSessionPayload() {
// // // // // // // //   return {
// // // // // // // //     user_id: localStorage.getItem("basira_user_id") || "",
// // // // // // // //     access_token: localStorage.getItem("basira_access_token") || "",
// // // // // // // //     refresh_token: localStorage.getItem("basira_refresh_token") || "",
// // // // // // // //     expires_at: localStorage.getItem("basira_session_expires_at") || "",
// // // // // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // // // // //   };
// // // // // // // // }

// // // // // // // // function detectPlatform() {
// // // // // // // //   const ua = navigator.userAgent.toLowerCase();
// // // // // // // //   if (ua.includes("mac")) return "mac";
// // // // // // // //   return "windows";
// // // // // // // // }

// // // // // // // // async function apiGet(path) {
// // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`);
// // // // // // // //   return response.json();
// // // // // // // // }

// // // // // // // // async function apiPost(path, payload = {}) {
// // // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // // // //     method: "POST",
// // // // // // // //     headers: {
// // // // // // // //       "Content-Type": "application/json"
// // // // // // // //     },
// // // // // // // //     body: JSON.stringify(payload)
// // // // // // // //   });

// // // // // // // //   return response.json();
// // // // // // // // }

// // // // // // // // async function readCloudUser() {
// // // // // // // //   try {
// // // // // // // //     const {
// // // // // // // //       data: { session }
// // // // // // // //     } = await supabaseClient.auth.getSession();

// // // // // // // //     if (!session?.user) {
// // // // // // // //       $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
// // // // // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // //       return null;
// // // // // // // //     }

// // // // // // // //     const userName =
// // // // // // // //       session.user.user_metadata?.full_name ||
// // // // // // // //       session.user.email ||
// // // // // // // //       session.user.id;

// // // // // // // //     $("cloudUserLabel").textContent = userName;
// // // // // // // //     $("subscriptionLabel").textContent =
// // // // // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // // // // //     return session;
// // // // // // // //   } catch (err) {
// // // // // // // //     $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
// // // // // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // // // // //     return null;
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // async function pushLocalSession() {
// // // // // // // //   const payload = getStoredSessionPayload();

// // // // // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // // // // //   }

// // // // // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // // // // }

// // // // // // // // async function sendHeartbeat() {
// // // // // // // //   try {
// // // // // // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // // // // // //       method: "POST",
// // // // // // // //       headers: {
// // // // // // // //         "Content-Type": "application/json"
// // // // // // // //       }
// // // // // // // //     });

// // // // // // // //     if (response.status === 401) {
// // // // // // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // // // // // //       setTimeout(() => {
// // // // // // // //         window.location.href = "./login.html";
// // // // // // // //       }, 1200);
// // // // // // // //     }
// // // // // // // //   } catch (err) {
// // // // // // // //     console.warn("Heartbeat failed:", err);
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // async function autoLogoutNow() {
// // // // // // // //   try {
// // // // // // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // // // // // //       method: "POST",
// // // // // // // //       headers: {
// // // // // // // //         "Content-Type": "application/json"
// // // // // // // //       }
// // // // // // // //     });
// // // // // // // //   } catch (err) {
// // // // // // // //     console.warn("Auto logout request failed:", err);
// // // // // // // //   }

// // // // // // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // // // // // //   setTimeout(() => {
// // // // // // // //     window.location.href = "./login.html";
// // // // // // // //   }, 1200);
// // // // // // // // }

// // // // // // // // function resetInactivityTimer() {
// // // // // // // //   if (inactivityTimer) {
// // // // // // // //     clearTimeout(inactivityTimer);
// // // // // // // //   }

// // // // // // // //   inactivityTimer = setTimeout(() => {
// // // // // // // //     autoLogoutNow();
// // // // // // // //   }, INACTIVITY_LIMIT_MS);
// // // // // // // // }

// // // // // // // // function bindActivityTracking() {
// // // // // // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // // // // // //     window.addEventListener(eventName, () => {
// // // // // // // //       resetInactivityTimer();
// // // // // // // //     });
// // // // // // // //   });

// // // // // // // //   resetInactivityTimer();
// // // // // // // //   setInterval(sendHeartbeat, 60000);
// // // // // // // // }

// // // // // // // // async function browseForDataDirectory(targetInputId = "dataDirectory") {
// // // // // // // //   try {
// // // // // // // //     const result = await apiGet("/api/system/pick-data-dir");

// // // // // // // //     if (!result || result.status !== "ok") {
// // // // // // // //       throw new Error(result?.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // // // //     }

// // // // // // // //     if (result.path) {
// // // // // // // //       const input = $(targetInputId);
// // // // // // // //       if (input) {
// // // // // // // //         input.value = result.path;
// // // // // // // //       }
// // // // // // // //     }
// // // // // // // //   } catch (err) {
// // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // async function initializeStartup() {
// // // // // // // //   setStepState(0);

// // // // // // // //   try {
// // // // // // // //     await readCloudUser();

// // // // // // // //     $("startupStatusCard").querySelector(".local-card__title").textContent = "جارٍ التحقق من البيئة المحلية";
// // // // // // // //     $("startupStatusCard").querySelector(".local-card__text").textContent =
// // // // // // // //       "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";

// // // // // // // //     startupState = await apiGet("/api/startup-status");

// // // // // // // //     if (!startupState || !startupState.state) {
// // // // // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // // // // //       showCard("newUserCard");
// // // // // // // //       setStepState(1);
// // // // // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // //       showCard("readyCard");
// // // // // // // //       setStepState(3);
// // // // // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "login_required") {
// // // // // // // //       showNote(
// // // // // // // //         "localSetupMessage",
// // // // // // // //         "err",
// // // // // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
// // // // // // // //       );

// // // // // // // //       await pushLocalSession();

// // // // // // // //       startupState = await apiGet("/api/startup-status");

// // // // // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // // //         showCard("readyCard");
// // // // // // // //         setStepState(3);
// // // // // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // // // // //       } else {
// // // // // // // //         showCard("newUserCard");
// // // // // // // //         setStepState(1);
// // // // // // // //       }

// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "subscription_required") {
// // // // // // // //       showCard("recoveryCard");
// // // // // // // //       setStepState(1);
// // // // // // // //       $("recoveryText").textContent =
// // // // // // // //         "الاشتراك غير فعال حاليًا. يجب تجديد الاشتراك قبل تشغيل البيئة المحلية.";
// // // // // // // //       $("repairPrimaryBtn").textContent = "فتح صفحة التجديد";
// // // // // // // //       $("repairPrimaryBtn").dataset.mode = "open-update";
// // // // // // // //       showNote("localSetupMessage", "err", "يلزم اشتراك فعال للمتابعة.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "recovery_required") {
// // // // // // // //       const reason = startupState.reason || "unknown";
// // // // // // // //       showCard("recoveryCard");
// // // // // // // //       setStepState(1);

// // // // // // // //       const recoveryText = $("recoveryText");
// // // // // // // //       const recoveryPathField = $("recoveryPathField");
// // // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // // //       if (reason === "missing_data_dir" || reason === "data_dir_not_found" || reason === "data_dir_not_writable") {
// // // // // // // //         recoveryText.textContent =
// // // // // // // //           "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
// // // // // // // //         recoveryPathField.classList.remove("isHidden");
// // // // // // // //         repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
// // // // // // // //         repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // // // // //       } else if (reason === "missing_model") {
// // // // // // // //         recoveryText.textContent =
// // // // // // // //           "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // //         repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
// // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // //       } else {
// // // // // // // //         recoveryText.textContent =
// // // // // // // //           "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // // // // //         recoveryPathField.classList.add("isHidden");
// // // // // // // //         repairPrimaryBtn.textContent = "إصلاح الآن";
// // // // // // // //         repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // // //       }

// // // // // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (startupState.state === "update_required") {
// // // // // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.");
// // // // // // // //       showCard("recoveryCard");
// // // // // // // //       $("recoveryText").textContent = "يلزم تحديث النسخة المحلية قبل المتابعة.";
// // // // // // // //       $("repairPrimaryBtn").textContent = "فتح بوابة التحديث";
// // // // // // // //       $("repairPrimaryBtn").dataset.mode = "open-update";
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // // // // //   } catch (err) {
// // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر بدء صفحة التهيئة المحلية.");
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // async function runFirstSetup() {
// // // // // // // //   try {
// // // // // // // //     const session = await readCloudUser();
// // // // // // // //     if (!session?.user) {
// // // // // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // // // // //     }

// // // // // // // //     setStepState(2);
// // // // // // // //     showCard("loadingCard");

// // // // // // // //     setProgress(10, "تهيئة الحالة المحلية...");
// // // // // // // //     await apiPost("/api/setup/init");
// // // // // // // //     await pushLocalSession();

// // // // // // // //     const dataDir =
// // // // // // // //       $("dataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // // //     setProgress(30, "إنشاء المجلدات المحلية...");
// // // // // // // //     await apiPost("/api/setup/select-data-dir", {
// // // // // // // //       data_dir: dataDir
// // // // // // // //     });

// // // // // // // //     const platform = detectPlatform();
// // // // // // // //     const runtimeUrl = LOCAL_RUNTIME_DOWNLOADS[platform];

// // // // // // // //     setProgress(55, "تنزيل الملفات الأساسية المحلية...");
// // // // // // // //     await apiPost("/api/setup/install-models", {
// // // // // // // //       runtime_url: runtimeUrl,
// // // // // // // //       platform
// // // // // // // //     });

// // // // // // // //     setProgress(80, "التحقق من الجاهزية...");
// // // // // // // //     const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // // // // //     }

// // // // // // // //     setProgress(95, "اعتماد التهيئة النهائية...");
// // // // // // // //     await apiPost("/api/setup/finalize");

// // // // // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // // // // //     setStepState(3);

// // // // // // // //     showCard("readyCard");
// // // // // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // // // // //   } catch (err) {
// // // // // // // //     showCard("recoveryCard");
// // // // // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // async function runRecoveryAction() {
// // // // // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // // // // //   try {
// // // // // // // //     if (mode === "reselect-path") {
// // // // // // // //       const pathValue =
// // // // // // // //         $("recoveryDataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // // //       showCard("loadingCard");
// // // // // // // //       setProgress(30, "تحديث مسار البيانات...");
// // // // // // // //       await apiPost("/api/recovery/reselect-data-dir", {
// // // // // // // //         data_dir: pathValue
// // // // // // // //       });

// // // // // // // //       setProgress(70, "التحقق من البيئة...");
// // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // // // // //       }

// // // // // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // // // // //       showCard("readyCard");
// // // // // // // //       setStepState(3);
// // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (mode === "repair-models") {
// // // // // // // //       showCard("loadingCard");
// // // // // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // // // // // //       await apiPost("/api/recovery/repair-models");

// // // // // // // //       setProgress(75, "التحقق النهائي...");
// // // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // // // // //       }

// // // // // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // // // // //       showCard("readyCard");
// // // // // // // //       setStepState(3);
// // // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // // //       return;
// // // // // // // //     }

// // // // // // // //     if (mode === "open-update") {
// // // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // // //       return;
// // // // // // // //     }
// // // // // // // //   } catch (err) {
// // // // // // // //     showCard("recoveryCard");
// // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // function launchLocalEnvironment() {
// // // // // // // //   window.open(LOCAL_STREAMLIT_URL, "_blank");
// // // // // // // //   showNote("localSetupMessage", "ok", "تم إرسال أمر تشغيل الواجهة المحلية. إذا لم تعمل بعد، تحققي من خدمة التشغيل المحلي.");
// // // // // // // // }

// // // // // // // // async function renewSubscriptionDemo() {
// // // // // // // //   try {
// // // // // // // //     const userId = localStorage.getItem("basira_user_id");
// // // // // // // //     if (!userId) {
// // // // // // // //       throw new Error("لم يتم العثور على مستخدم محلي مربوط بالجلسة.");
// // // // // // // //     }

// // // // // // // //     await apiPost("/api/subscription/renew-demo", {
// // // // // // // //       user_id: userId
// // // // // // // //     });

// // // // // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // // // // //     $("subscriptionLabel").textContent = "active";

// // // // // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // // // // //   } catch (err) {
// // // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // // // //   }
// // // // // // // // }

// // // // // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // // // // //   $("browseDataDirectoryBtn")?.addEventListener("click", () => {
// // // // // // // //     browseForDataDirectory("dataDirectory");
// // // // // // // //   });

// // // // // // // //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => {
// // // // // // // //     browseForDataDirectory("recoveryDataDirectory");
// // // // // // // //   });

// // // // // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // // // // //     const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
// // // // // // // //     if (useCloud) {
// // // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // // //     } else {
// // // // // // // //       renewSubscriptionDemo();
// // // // // // // //     }
// // // // // // // //   });

// // // // // // // //   bindActivityTracking();
// // // // // // // //   await initializeStartup();
// // // // // // // // });


// // // // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // // // // // // const LOCAL_APP_URL = "http://127.0.0.1:5000";
// // // // // // // const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";

// // // // // // // let startupState = null;
// // // // // // // let inactivityTimer = null;
// // // // // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

// // // // // // // function $(id) {
// // // // // // //   return document.getElementById(id);
// // // // // // // }

// // // // // // // function showNote(id, type, message) {
// // // // // // //   const el = $(id);
// // // // // // //   if (!el) return;
// // // // // // //   el.innerHTML = message || "";
// // // // // // //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // // // }

// // // // // // // function showCard(id) {
// // // // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // // // //     const el = $(cardId);
// // // // // // //     if (el) el.classList.add("isHidden");
// // // // // // //   });

// // // // // // //   const target = $(id);
// // // // // // //   if (target) target.classList.remove("isHidden");
// // // // // // // }

// // // // // // // function setStepState(activeIndex) {
// // // // // // //   const steps = Array.from(document.querySelectorAll(".setup-step"));
// // // // // // //   steps.forEach((step, index) => {
// // // // // // //     step.classList.remove("isActive", "isDone");
// // // // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // // // //   });
// // // // // // // }

// // // // // // // function setProgress(percent, text) {
// // // // // // //   const fill = $("progressFill");
// // // // // // //   const label = $("progressText");

// // // // // // //   if (fill) fill.style.width = `${percent}%`;
// // // // // // //   if (label) label.textContent = text || "";
// // // // // // // }

// // // // // // // async function apiGet(path) {
// // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // // //     method: "GET",
// // // // // // //     headers: {
// // // // // // //       "Content-Type": "application/json"
// // // // // // //     }
// // // // // // //   });

// // // // // // //   return response.json();
// // // // // // // }

// // // // // // // async function apiPost(path, payload = {}) {
// // // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // // //     method: "POST",
// // // // // // //     headers: {
// // // // // // //       "Content-Type": "application/json"
// // // // // // //     },
// // // // // // //     body: JSON.stringify(payload)
// // // // // // //   });

// // // // // // //   return response.json();
// // // // // // // }

// // // // // // // function getStoredSessionPayload() {
// // // // // // //   return {
// // // // // // //     user_id: localStorage.getItem("basira_user_id") || "",
// // // // // // //     access_token: localStorage.getItem("basira_access_token") || "",
// // // // // // //     refresh_token: localStorage.getItem("basira_refresh_token") || "",
// // // // // // //     expires_at: localStorage.getItem("basira_session_expires_at") || "",
// // // // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // // // //   };
// // // // // // // }

// // // // // // // async function readCloudUser() {
// // // // // // //   try {
// // // // // // //     const {
// // // // // // //       data: { session }
// // // // // // //     } = await supabaseClient.auth.getSession();

// // // // // // //     if (!session?.user) {
// // // // // // //       $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
// // // // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // // // //       return null;
// // // // // // //     }

// // // // // // //     const userName =
// // // // // // //       session.user.user_metadata?.full_name ||
// // // // // // //       session.user.email ||
// // // // // // //       session.user.id;

// // // // // // //     $("cloudUserLabel").textContent = userName;
// // // // // // //     $("subscriptionLabel").textContent =
// // // // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // // // //     return session;
// // // // // // //   } catch (err) {
// // // // // // //     $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
// // // // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // // // //     return null;
// // // // // // //   }
// // // // // // // }

// // // // // // // async function pushLocalSession() {
// // // // // // //   const payload = getStoredSessionPayload();

// // // // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // // // //   }

// // // // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // // // }

// // // // // // // async function sendHeartbeat() {
// // // // // // //   try {
// // // // // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // // // // //       method: "POST",
// // // // // // //       headers: {
// // // // // // //         "Content-Type": "application/json"
// // // // // // //       }
// // // // // // //     });

// // // // // // //     if (response.status === 401) {
// // // // // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // // // // //       setTimeout(() => {
// // // // // // //         window.location.href = "./login.html";
// // // // // // //       }, 1200);
// // // // // // //     }
// // // // // // //   } catch (err) {
// // // // // // //     console.warn("Heartbeat failed:", err);
// // // // // // //   }
// // // // // // // }

// // // // // // // async function autoLogoutNow() {
// // // // // // //   try {
// // // // // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // // // // //       method: "POST",
// // // // // // //       headers: {
// // // // // // //         "Content-Type": "application/json"
// // // // // // //       }
// // // // // // //     });
// // // // // // //   } catch (err) {
// // // // // // //     console.warn("Auto logout request failed:", err);
// // // // // // //   }

// // // // // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // // // // //   setTimeout(() => {
// // // // // // //     window.location.href = "./login.html";
// // // // // // //   }, 1200);
// // // // // // // }

// // // // // // // function resetInactivityTimer() {
// // // // // // //   if (inactivityTimer) {
// // // // // // //     clearTimeout(inactivityTimer);
// // // // // // //   }

// // // // // // //   inactivityTimer = setTimeout(() => {
// // // // // // //     autoLogoutNow();
// // // // // // //   }, INACTIVITY_LIMIT_MS);
// // // // // // // }

// // // // // // // function bindActivityTracking() {
// // // // // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // // // // //     window.addEventListener(eventName, () => {
// // // // // // //       resetInactivityTimer();
// // // // // // //     });
// // // // // // //   });

// // // // // // //   resetInactivityTimer();
// // // // // // //   setInterval(sendHeartbeat, 60000);
// // // // // // // }

// // // // // // // async function browseForDataDirectory(targetInputId = "dataDirectory") {
// // // // // // //   try {
// // // // // // //     const result = await apiGet("/api/system/pick-data-dir");

// // // // // // //     if (!result || result.status !== "ok") {
// // // // // // //       throw new Error(result?.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // // //     }

// // // // // // //     if (result.path) {
// // // // // // //       const input = $(targetInputId);
// // // // // // //       if (input) {
// // // // // // //         input.value = result.path;
// // // // // // //       }
// // // // // // //     }
// // // // // // //   } catch (err) {
// // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // // //   }
// // // // // // // }

// // // // // // // async function initializeStartup() {
// // // // // // //   setStepState(0);

// // // // // // //   try {
// // // // // // //     await readCloudUser();

// // // // // // //     const statusCard = $("startupStatusCard");
// // // // // // //     if (statusCard) {
// // // // // // //       const title = statusCard.querySelector(".local-card__title");
// // // // // // //       const text = statusCard.querySelector(".local-card__text");

// // // // // // //       if (title) title.textContent = "جارٍ التحقق من البيئة المحلية";
// // // // // // //       if (text) {
// // // // // // //         text.textContent =
// // // // // // //           "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";
// // // // // // //       }
// // // // // // //     }

// // // // // // //     startupState = await apiGet("/api/startup-status");

// // // // // // //     if (!startupState || !startupState.state) {
// // // // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // // // //     }

// // // // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // // // //       showCard("newUserCard");
// // // // // // //       setStepState(1);
// // // // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // //       showCard("readyCard");
// // // // // // //       setStepState(3);
// // // // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startupState.state === "login_required") {
// // // // // // //       showNote(
// // // // // // //         "localSetupMessage",
// // // // // // //         "err",
// // // // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
// // // // // // //       );

// // // // // // //       await pushLocalSession();

// // // // // // //       startupState = await apiGet("/api/startup-status");

// // // // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // // //         showCard("readyCard");
// // // // // // //         setStepState(3);
// // // // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // // // //       } else {
// // // // // // //         showCard("newUserCard");
// // // // // // //         setStepState(1);
// // // // // // //       }

// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startupState.state === "subscription_required") {
// // // // // // //       showCard("recoveryCard");
// // // // // // //       setStepState(1);

// // // // // // //       const recoveryText = $("recoveryText");
// // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // //       if (recoveryText) {
// // // // // // //         recoveryText.textContent =
// // // // // // //           "الاشتراك غير فعال حاليًا. يجب تجديد الاشتراك قبل تشغيل البيئة المحلية.";
// // // // // // //       }

// // // // // // //       if (repairPrimaryBtn) {
// // // // // // //         repairPrimaryBtn.textContent = "فتح صفحة التجديد";
// // // // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // // // //       }

// // // // // // //       showNote("localSetupMessage", "err", "يلزم اشتراك فعال للمتابعة.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startupState.state === "recovery_required") {
// // // // // // //       const reason = startupState.reason || "unknown";

// // // // // // //       showCard("recoveryCard");
// // // // // // //       setStepState(1);

// // // // // // //       const recoveryText = $("recoveryText");
// // // // // // //       const recoveryPathField = $("recoveryPathField");
// // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // //       if (
// // // // // // //         reason === "missing_data_dir" ||
// // // // // // //         reason === "data_dir_not_found" ||
// // // // // // //         reason === "data_dir_not_writable"
// // // // // // //       ) {
// // // // // // //         if (recoveryText) {
// // // // // // //           recoveryText.textContent =
// // // // // // //             "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
// // // // // // //         }

// // // // // // //         if (recoveryPathField) {
// // // // // // //           recoveryPathField.classList.remove("isHidden");
// // // // // // //         }

// // // // // // //         if (repairPrimaryBtn) {
// // // // // // //           repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
// // // // // // //           repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // // // //         }
// // // // // // //       } else if (reason === "missing_model") {
// // // // // // //         if (recoveryText) {
// // // // // // //           recoveryText.textContent =
// // // // // // //             "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // // // //         }

// // // // // // //         if (recoveryPathField) {
// // // // // // //           recoveryPathField.classList.add("isHidden");
// // // // // // //         }

// // // // // // //         if (repairPrimaryBtn) {
// // // // // // //           repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
// // // // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // //         }
// // // // // // //       } else {
// // // // // // //         if (recoveryText) {
// // // // // // //           recoveryText.textContent =
// // // // // // //             "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // // // //         }

// // // // // // //         if (recoveryPathField) {
// // // // // // //           recoveryPathField.classList.add("isHidden");
// // // // // // //         }

// // // // // // //         if (repairPrimaryBtn) {
// // // // // // //           repairPrimaryBtn.textContent = "إصلاح الآن";
// // // // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // // //         }
// // // // // // //       }

// // // // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startupState.state === "update_required") {
// // // // // // //       showCard("recoveryCard");
// // // // // // //       setStepState(1);

// // // // // // //       const recoveryText = $("recoveryText");
// // // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");

// // // // // // //       if (recoveryText) {
// // // // // // //         recoveryText.textContent = "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.";
// // // // // // //       }

// // // // // // //       if (repairPrimaryBtn) {
// // // // // // //         repairPrimaryBtn.textContent = "فتح بوابة التحديث";
// // // // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // // // //       }

// // // // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // // // //   } catch (err) {
// // // // // // //     showNote(
// // // // // // //       "localSetupMessage",
// // // // // // //       "err",
// // // // // // //       err.message || "تعذر بدء صفحة التهيئة المحلية. تأكدي من تشغيل Basira Local Launcher."
// // // // // // //     );
// // // // // // //   }
// // // // // // // }

// // // // // // // async function runFirstSetup() {
// // // // // // //   try {
// // // // // // //     const session = await readCloudUser();
// // // // // // //     if (!session?.user) {
// // // // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // // // //     }

// // // // // // //     setStepState(2);
// // // // // // //     showCard("loadingCard");

// // // // // // //     setProgress(10, "تهيئة الحالة المحلية...");
// // // // // // //     await apiPost("/api/setup/init");

// // // // // // //     setProgress(20, "ربط الجلسة المحلية...");
// // // // // // //     await pushLocalSession();

// // // // // // //     const dataDir =
// // // // // // //       $("dataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // //     setProgress(35, "إنشاء المجلدات المحلية...");
// // // // // // //     const dirResult = await apiPost("/api/setup/select-data-dir", {
// // // // // // //       data_dir: dataDir
// // // // // // //     });

// // // // // // //     if (!dirResult || dirResult.status !== "ok") {
// // // // // // //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات المحلية.");
// // // // // // //     }

// // // // // // //     setProgress(60, "تنزيل الملفات الأساسية المحلية...");
// // // // // // //     const installResult = await apiPost("/api/setup/install-models");

// // // // // // //     if (!installResult || installResult.status !== "ok") {
// // // // // // //       throw new Error(installResult?.message || "تعذر تجهيز الملفات الأساسية المحلية.");
// // // // // // //     }

// // // // // // //     setProgress(80, "التحقق من الجاهزية...");
// // // // // // //     const verifyResult = await apiGet("/api/setup/verify");

// // // // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // // // //     }

// // // // // // //     setProgress(95, "اعتماد التهيئة النهائية...");
// // // // // // //     const finalizeResult = await apiPost("/api/setup/finalize");

// // // // // // //     if (!finalizeResult || finalizeResult.status !== "ok") {
// // // // // // //       throw new Error("تعذر اعتماد التهيئة النهائية.");
// // // // // // //     }

// // // // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // // // //     setStepState(3);

// // // // // // //     showCard("readyCard");
// // // // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // // // //   } catch (err) {
// // // // // // //     showCard("recoveryCard");
// // // // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // // // //   }
// // // // // // // }

// // // // // // // async function runRecoveryAction() {
// // // // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // // // //   try {
// // // // // // //     if (mode === "reselect-path") {
// // // // // // //       const pathValue =
// // // // // // //         $("recoveryDataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // // //       showCard("loadingCard");
// // // // // // //       setProgress(30, "تحديث مسار البيانات...");

// // // // // // //       const result = await apiPost("/api/recovery/reselect-data-dir", {
// // // // // // //         data_dir: pathValue
// // // // // // //       });

// // // // // // //       if (!result || result.status !== "ok") {
// // // // // // //         throw new Error(result?.message || "تعذر تحديث مسار البيانات.");
// // // // // // //       }

// // // // // // //       setProgress(70, "التحقق من البيئة...");
// // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // // // //       }

// // // // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // // // //       showCard("readyCard");
// // // // // // //       setStepState(3);
// // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (mode === "repair-models") {
// // // // // // //       showCard("loadingCard");
// // // // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");

// // // // // // //       const result = await apiPost("/api/recovery/repair-models");

// // // // // // //       if (!result || result.status !== "ok") {
// // // // // // //         throw new Error(result?.message || "تعذر إصلاح الملفات الأساسية.");
// // // // // // //       }

// // // // // // //       setProgress(75, "التحقق النهائي...");
// // // // // // //       const verifyResult = await apiGet("/api/setup/verify");

// // // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // // // //       }

// // // // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // // // //       showCard("readyCard");
// // // // // // //       setStepState(3);
// // // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (mode === "open-update") {
// // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // //       return;
// // // // // // //     }
// // // // // // //   } catch (err) {
// // // // // // //     showCard("recoveryCard");
// // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // // // //   }
// // // // // // // }

// // // // // // // async function launchLocalEnvironment() {
// // // // // // //   try {
// // // // // // //     const startup = await apiGet("/api/startup-status");

// // // // // // //     if (!startup || !startup.state) {
// // // // // // //       throw new Error("تعذر التحقق من حالة البيئة المحلية.");
// // // // // // //     }

// // // // // // //     if (startup.state === "healthy" || startup.state === "healthy_with_optional_update") {
// // // // // // //       window.open(LOCAL_APP_URL, "_blank");
// // // // // // //       showNote("localSetupMessage", "ok", "تم فتح التطبيق المحلي بنجاح.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startup.state === "login_required") {
// // // // // // //       showNote("localSetupMessage", "err", "الجلسة المحلية تحتاج إعادة ربط قبل فتح التطبيق.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startup.state === "new_user" || startup.state === "setup_incomplete") {
// // // // // // //       showNote("localSetupMessage", "err", "يجب إكمال التهيئة المحلية أولًا.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startup.state === "recovery_required") {
// // // // // // //       showNote("localSetupMessage", "err", "توجد مشكلة في البيئة المحلية ويجب إصلاحها أولًا.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startup.state === "subscription_required") {
// // // // // // //       showNote("localSetupMessage", "err", "الاشتراك غير فعال حاليًا.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     if (startup.state === "update_required") {
// // // // // // //       showNote("localSetupMessage", "err", "النسخة المحلية تحتاج تحديثًا قبل التشغيل.");
// // // // // // //       return;
// // // // // // //     }

// // // // // // //     throw new Error("الحالة الحالية لا تسمح بفتح التطبيق المحلي.");
// // // // // // //   } catch (err) {
// // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح التطبيق المحلي.");
// // // // // // //   }
// // // // // // // }

// // // // // // // async function renewSubscriptionDemo() {
// // // // // // //   try {
// // // // // // //     const result = await apiPost("/api/subscription/renew-demo");

// // // // // // //     if (!result || result.status !== "ok") {
// // // // // // //       throw new Error(result?.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // // //     }

// // // // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // // // //     $("subscriptionLabel").textContent = "active";

// // // // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // // // //   } catch (err) {
// // // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // // //   }
// // // // // // // }

// // // // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // // // //   $("browseDataDirectoryBtn")?.addEventListener("click", () => {
// // // // // // //     browseForDataDirectory("dataDirectory");
// // // // // // //   });

// // // // // // //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => {
// // // // // // //     browseForDataDirectory("recoveryDataDirectory");
// // // // // // //   });

// // // // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // // // //     const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
// // // // // // //     if (useCloud) {
// // // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // // //     } else {
// // // // // // //       renewSubscriptionDemo();
// // // // // // //     }
// // // // // // //   });

// // // // // // //   bindActivityTracking();
// // // // // // //   await initializeStartup();
// // // // // // // });


// // // // // // /**
// // // // // //  * local-setup.js — Basira Cloud Setup Page Logic
// // // // // //  * ================================================
// // // // // //  * Runs in the browser on the cloud website (local-setup.html).
// // // // // //  * Communicates with the local bootstrap API at http://127.0.0.1:5001
// // // // // //  * to set up or verify the on-premise environment, then opens
// // // // // //  * the main local app at http://127.0.0.1:5000.
// // // // // //  *
// // // // // //  * Prerequisites: supabase-config.js must define SUPABASE_URL and SUPABASE_ANON_KEY.
// // // // // //  */

// // // // // // // ─── Constants ────────────────────────────────────────────────────────────────
// // // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";   // basira_local_bootstrap.py
// // // // // // const LOCAL_APP_URL       = "http://127.0.0.1:5000";   // Basira_app_structure.py
// // // // // // const CLOUD_RENEW_URL     = "https://basira.basira-toolmodel.workers.dev/renew";

// // // // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;  // 20 minutes

// // // // // // let startupState    = null;
// // // // // // let inactivityTimer = null;


// // // // // // // ─── DOM helpers ─────────────────────────────────────────────────────────────
// // // // // // function $(id) {
// // // // // //   return document.getElementById(id);
// // // // // // }

// // // // // // function showNote(id, type, message) {
// // // // // //   const el = $(id);
// // // // // //   if (!el) return;
// // // // // //   el.innerHTML  = message || "";
// // // // // //   el.className  = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // // }

// // // // // // function showCard(id) {
// // // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // // //     const el = $(cardId);
// // // // // //     if (el) el.classList.add("isHidden");
// // // // // //   });
// // // // // //   const target = $(id);
// // // // // //   if (target) target.classList.remove("isHidden");
// // // // // // }

// // // // // // function setStepState(activeIndex) {
// // // // // //   document.querySelectorAll(".setup-step").forEach((step, index) => {
// // // // // //     step.classList.remove("isActive", "isDone");
// // // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // // //   });
// // // // // // }

// // // // // // function setProgress(percent, text) {
// // // // // //   const fill  = $("progressFill");
// // // // // //   const label = $("progressText");
// // // // // //   if (fill)  fill.style.width   = `${percent}%`;
// // // // // //   if (label) label.textContent  = text || "";
// // // // // // }


// // // // // // // ─── API helpers ─────────────────────────────────────────────────────────────
// // // // // // async function apiGet(path) {
// // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // //     method:  "GET",
// // // // // //     headers: { "Content-Type": "application/json" }
// // // // // //   });
// // // // // //   return response.json();
// // // // // // }

// // // // // // async function apiPost(path, payload = {}) {
// // // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // // //     method:  "POST",
// // // // // //     headers: { "Content-Type": "application/json" },
// // // // // //     body:    JSON.stringify(payload)
// // // // // //   });
// // // // // //   return response.json();
// // // // // // }


// // // // // // // ─── Session helpers ──────────────────────────────────────────────────────────
// // // // // // function getStoredSessionPayload() {
// // // // // //   return {
// // // // // //     user_id:             localStorage.getItem("basira_user_id")             || "",
// // // // // //     access_token:        localStorage.getItem("basira_access_token")        || "",
// // // // // //     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
// // // // // //     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
// // // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // // //   };
// // // // // // }

// // // // // // async function readCloudUser() {
// // // // // //   try {
// // // // // //     const { data: { session } } = await supabaseClient.auth.getSession();

// // // // // //     if (!session?.user) {
// // // // // //       $("cloudUserLabel").textContent    = "لم يتم العثور على جلسة مستخدم.";
// // // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // // //       return null;
// // // // // //     }

// // // // // //     const userName =
// // // // // //       session.user.user_metadata?.full_name ||
// // // // // //       session.user.email ||
// // // // // //       session.user.id;

// // // // // //     $("cloudUserLabel").textContent    = userName;
// // // // // //     $("subscriptionLabel").textContent =
// // // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // // //     return session;
// // // // // //   } catch (err) {
// // // // // //     $("cloudUserLabel").textContent    = "تعذر قراءة بيانات المستخدم.";
// // // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // // //     return null;
// // // // // //   }
// // // // // // }

// // // // // // async function pushLocalSession() {
// // // // // //   const payload = getStoredSessionPayload();
// // // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // // //   }
// // // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // // }


// // // // // // // ─── Heartbeat & inactivity ───────────────────────────────────────────────────
// // // // // // async function sendHeartbeat() {
// // // // // //   try {
// // // // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // // // //       method:  "POST",
// // // // // //       headers: { "Content-Type": "application/json" }
// // // // // //     });

// // // // // //     if (response.status === 401) {
// // // // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // // // //       setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // // // //     }
// // // // // //   } catch (err) {
// // // // // //     console.warn("Heartbeat failed:", err);
// // // // // //   }
// // // // // // }

// // // // // // async function autoLogoutNow() {
// // // // // //   try {
// // // // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // // // //       method:  "POST",
// // // // // //       headers: { "Content-Type": "application/json" }
// // // // // //     });
// // // // // //   } catch (err) {
// // // // // //     console.warn("Auto logout request failed:", err);
// // // // // //   }
// // // // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // // // //   setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // // // // }

// // // // // // function resetInactivityTimer() {
// // // // // //   if (inactivityTimer) clearTimeout(inactivityTimer);
// // // // // //   inactivityTimer = setTimeout(autoLogoutNow, INACTIVITY_LIMIT_MS);
// // // // // // }

// // // // // // function bindActivityTracking() {
// // // // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // // // //     window.addEventListener(eventName, resetInactivityTimer);
// // // // // //   });
// // // // // //   resetInactivityTimer();
// // // // // //   setInterval(sendHeartbeat, 60_000);
// // // // // // }


// // // // // // // ─── Folder picker ────────────────────────────────────────────────────────────
// // // // // // async function browseForDataDirectory(targetInputId = "dataDirectory") {
// // // // // //   try {
// // // // // //     const result = await apiGet("/api/system/pick-data-dir");
// // // // // //     if (!result || result.status !== "ok") {
// // // // // //       throw new Error(result?.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // //     }
// // // // // //     if (result.path) {
// // // // // //       const input = $(targetInputId);
// // // // // //       if (input) input.value = result.path;
// // // // // //     }
// // // // // //   } catch (err) {
// // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── Startup / state machine ──────────────────────────────────────────────────
// // // // // // async function initializeStartup() {
// // // // // //   setStepState(0);

// // // // // //   try {
// // // // // //     await readCloudUser();

// // // // // //     const statusCard = $("startupStatusCard");
// // // // // //     if (statusCard) {
// // // // // //       const title = statusCard.querySelector(".local-card__title");
// // // // // //       const text  = statusCard.querySelector(".local-card__text");
// // // // // //       if (title) title.textContent = "جارٍ التحقق من البيئة المحلية";
// // // // // //       if (text)  text.textContent  =
// // // // // //         "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";
// // // // // //     }

// // // // // //     startupState = await apiGet("/api/startup-status");

// // // // // //     if (!startupState || !startupState.state) {
// // // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // // //     }

// // // // // //     // ── New user or incomplete setup ────────────────────────────────────────
// // // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // // //       showCard("newUserCard");
// // // // // //       setStepState(1);
// // // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // // //       return;
// // // // // //     }

// // // // // //     // ── Already healthy ─────────────────────────────────────────────────────
// // // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // //       showCard("readyCard");
// // // // // //       setStepState(3);
// // // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // // //       return;
// // // // // //     }

// // // // // //     // ── Session expired — try to re-link from Supabase ──────────────────────
// // // // // //     if (startupState.state === "login_required") {
// // // // // //       showNote("localSetupMessage", "err",
// // // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية.");

// // // // // //       await pushLocalSession();
// // // // // //       startupState = await apiGet("/api/startup-status");

// // // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // // //         showCard("readyCard");
// // // // // //         setStepState(3);
// // // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // // //       } else {
// // // // // //         showCard("newUserCard");
// // // // // //         setStepState(1);
// // // // // //       }
// // // // // //       return;
// // // // // //     }

// // // // // //     // ── Subscription issue ──────────────────────────────────────────────────
// // // // // //     if (startupState.state === "subscription_required") {
// // // // // //       showCard("recoveryCard");
// // // // // //       setStepState(1);
// // // // // //       const recoveryText    = $("recoveryText");
// // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // // //       if (recoveryText)   recoveryText.textContent   = "الاشتراك غير فعال. يرجى تجديد الاشتراك للمتابعة.";
// // // // // //       if (repairPrimaryBtn) {
// // // // // //         repairPrimaryBtn.textContent  = "فتح بوابة التجديد";
// // // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // // //       }
// // // // // //       showNote("localSetupMessage", "err", "الاشتراك غير فعال حاليًا.");
// // // // // //       return;
// // // // // //     }

// // // // // //     // ── Recovery needed (missing dir / models) ───────────────────────────────
// // // // // //     if (startupState.state === "recovery_required") {
// // // // // //       showCard("recoveryCard");
// // // // // //       setStepState(1);
// // // // // //       const reason          = startupState.reason || "";
// // // // // //       const recoveryText    = $("recoveryText");
// // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // // //       const recoveryPathField = $("recoveryPathField");

// // // // // //       if (reason === "data_dir_missing") {
// // // // // //         if (recoveryText)   recoveryText.textContent   = "مجلد البيانات المحلية غير موجود. اختاري مسارًا جديدًا ثم اضغطي إصلاح.";
// // // // // //         if (recoveryPathField) recoveryPathField.classList.remove("isHidden");
// // // // // //         if (repairPrimaryBtn) {
// // // // // //           repairPrimaryBtn.textContent  = "إصلاح المسار";
// // // // // //           repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // // //         }
// // // // // //       } else if (reason === "models_not_installed") {
// // // // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // // // //         if (repairPrimaryBtn) {
// // // // // //           repairPrimaryBtn.textContent  = "إعادة تنزيل الملفات الأساسية";
// // // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // //         }
// // // // // //       } else {
// // // // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // // // //         if (repairPrimaryBtn) {
// // // // // //           repairPrimaryBtn.textContent  = "إصلاح الآن";
// // // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // // //         }
// // // // // //       }

// // // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // // //       return;
// // // // // //     }

// // // // // //     // ── Mandatory update required ────────────────────────────────────────────
// // // // // //     if (startupState.state === "update_required") {
// // // // // //       showCard("recoveryCard");
// // // // // //       setStepState(1);
// // // // // //       const recoveryText    = $("recoveryText");
// // // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // // //       if (recoveryText)     recoveryText.textContent   = "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.";
// // // // // //       if (repairPrimaryBtn) {
// // // // // //         repairPrimaryBtn.textContent  = "فتح بوابة التحديث";
// // // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // // //       }
// // // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا.");
// // // // // //       return;
// // // // // //     }

// // // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // // //   } catch (err) {
// // // // // //     showNote("localSetupMessage", "err",
// // // // // //       err.message || "تعذر بدء صفحة التهيئة المحلية. تأكدي من تشغيل Basira Local Launcher.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── First-time setup flow ────────────────────────────────────────────────────
// // // // // // async function runFirstSetup() {
// // // // // //   try {
// // // // // //     const session = await readCloudUser();
// // // // // //     if (!session?.user) {
// // // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // // //     }

// // // // // //     setStepState(2);
// // // // // //     showCard("loadingCard");

// // // // // //     setProgress(10,  "تهيئة الحالة المحلية...");
// // // // // //     await apiPost("/api/setup/init");

// // // // // //     setProgress(20,  "ربط الجلسة المحلية...");
// // // // // //     await pushLocalSession();

// // // // // //     const dataDir = $("dataDirectory")?.value.trim()
// // // // // //       || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // //     setProgress(35,  "إنشاء المجلدات المحلية...");
// // // // // //     const dirResult = await apiPost("/api/setup/select-data-dir", { data_dir: dataDir });
// // // // // //     if (!dirResult || dirResult.status !== "ok") {
// // // // // //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات المحلية.");
// // // // // //     }

// // // // // //     setProgress(60,  "تنزيل الملفات الأساسية المحلية...");
// // // // // //     const installResult = await apiPost("/api/setup/install-models");
// // // // // //     if (!installResult || installResult.status !== "ok") {
// // // // // //       throw new Error(installResult?.message || "تعذر تجهيز الملفات الأساسية المحلية.");
// // // // // //     }

// // // // // //     setProgress(80,  "التحقق من الجاهزية...");
// // // // // //     const verifyResult = await apiGet("/api/setup/verify");
// // // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // // //     }

// // // // // //     setProgress(95,  "اعتماد التهيئة النهائية...");
// // // // // //     const finalizeResult = await apiPost("/api/setup/finalize");
// // // // // //     if (!finalizeResult || finalizeResult.status !== "ok") {
// // // // // //       throw new Error("تعذر اعتماد التهيئة النهائية.");
// // // // // //     }

// // // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // // //     setStepState(3);
// // // // // //     showCard("readyCard");
// // // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // // //   } catch (err) {
// // // // // //     showCard("recoveryCard");
// // // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── Recovery flow ────────────────────────────────────────────────────────────
// // // // // // async function runRecoveryAction() {
// // // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // // //   try {
// // // // // //     if (mode === "reselect-path") {
// // // // // //       const pathValue = $("recoveryDataDirectory")?.value.trim()
// // // // // //         || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // // //       showCard("loadingCard");
// // // // // //       setProgress(30, "تحديث مسار البيانات...");
// // // // // //       const result = await apiPost("/api/recovery/reselect-data-dir", { data_dir: pathValue });
// // // // // //       if (!result || result.status !== "ok") {
// // // // // //         throw new Error(result?.message || "تعذر تحديث مسار البيانات.");
// // // // // //       }

// // // // // //       setProgress(70, "التحقق من البيئة...");
// // // // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // // //       }

// // // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // // //       showCard("readyCard");
// // // // // //       setStepState(3);
// // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // //       return;
// // // // // //     }

// // // // // //     if (mode === "repair-models") {
// // // // // //       showCard("loadingCard");
// // // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // // // //       const result = await apiPost("/api/recovery/repair-models");
// // // // // //       if (!result || result.status !== "ok") {
// // // // // //         throw new Error(result?.message || "تعذر إصلاح الملفات الأساسية.");
// // // // // //       }

// // // // // //       setProgress(75, "التحقق النهائي...");
// // // // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // // //       }

// // // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // // //       showCard("readyCard");
// // // // // //       setStepState(3);
// // // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // // //       return;
// // // // // //     }

// // // // // //     if (mode === "open-update") {
// // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // //       return;
// // // // // //     }
// // // // // //   } catch (err) {
// // // // // //     showCard("recoveryCard");
// // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── Launch local app ─────────────────────────────────────────────────────────
// // // // // // async function launchLocalEnvironment() {
// // // // // //   try {
// // // // // //     const startup = await apiGet("/api/startup-status");
// // // // // //     if (!startup || !startup.state) {
// // // // // //       throw new Error("تعذر التحقق من حالة البيئة المحلية.");
// // // // // //     }

// // // // // //     if (startup.state === "healthy" || startup.state === "healthy_with_optional_update") {
// // // // // //       window.open(LOCAL_APP_URL, "_blank");
// // // // // //       showNote("localSetupMessage", "ok", "تم فتح التطبيق المحلي بنجاح.");
// // // // // //       return;
// // // // // //     }

// // // // // //     const messages = {
// // // // // //       login_required:       "الجلسة المحلية تحتاج إعادة ربط قبل فتح التطبيق.",
// // // // // //       new_user:             "يجب إكمال التهيئة المحلية أولًا.",
// // // // // //       setup_incomplete:     "يجب إكمال التهيئة المحلية أولًا.",
// // // // // //       recovery_required:    "توجد مشكلة في البيئة المحلية ويجب إصلاحها أولًا.",
// // // // // //       subscription_required:"الاشتراك غير فعال حاليًا.",
// // // // // //       update_required:      "النسخة المحلية تحتاج تحديثًا قبل التشغيل."
// // // // // //     };

// // // // // //     showNote("localSetupMessage", "err",
// // // // // //       messages[startup.state] || "الحالة الحالية لا تسمح بفتح التطبيق المحلي.");
// // // // // //   } catch (err) {
// // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح التطبيق المحلي.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── Subscription renew (demo / cloud) ───────────────────────────────────────
// // // // // // async function renewSubscriptionDemo() {
// // // // // //   try {
// // // // // //     const result = await apiPost("/api/subscription/renew-demo");
// // // // // //     if (!result || result.status !== "ok") {
// // // // // //       throw new Error(result?.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // //     }
// // // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // // //     $("subscriptionLabel").textContent = "active";
// // // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // // //   } catch (err) {
// // // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // // //   }
// // // // // // }


// // // // // // // ─── Boot ─────────────────────────────────────────────────────────────────────
// // // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // // //   $("browseDataDirectoryBtn")?.addEventListener("click", () => {
// // // // // //     browseForDataDirectory("dataDirectory");
// // // // // //   });

// // // // // //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => {
// // // // // //     browseForDataDirectory("recoveryDataDirectory");
// // // // // //   });

// // // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // // //     const useCloud = confirm(
// // // // // //       "هل تريد فتح صفحة التجديد السحابية؟\nاضغط موافق للتجديد السحابي أو إلغاء لتجديد demo."
// // // // // //     );
// // // // // //     if (useCloud) {
// // // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // // //     } else {
// // // // // //       renewSubscriptionDemo();
// // // // // //     }
// // // // // //   });

// // // // // //   bindActivityTracking();
// // // // // //   await initializeStartup();
// // // // // // });
// // // // // /**
// // // // //  * local-setup.js — Basira Cloud Setup Page Logic
// // // // //  * ================================================
// // // // //  * Runs in the browser on the cloud website (local-setup.html).
// // // // //  * Communicates with the local bootstrap API at http://127.0.0.1:5001
// // // // //  * to set up or verify the on-premise environment, then opens
// // // // //  * the main local app at http://127.0.0.1:5000.
// // // // //  *
// // // // //  * Prerequisites: supabase-config.js must define SUPABASE_URL and SUPABASE_ANON_KEY.
// // // // //  */

// // // // // // ─── Constants ────────────────────────────────────────────────────────────────
// // // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";   // basira_local_bootstrap.py
// // // // // const LOCAL_APP_URL       = "http://127.0.0.1:5000";   // Basira_app_structure.py
// // // // // const CLOUD_RENEW_URL     = "https://basira.basira-toolmodel.workers.dev/renew";

// // // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;  // 20 minutes

// // // // // let startupState    = null;
// // // // // let inactivityTimer = null;


// // // // // // ─── DOM helpers ─────────────────────────────────────────────────────────────
// // // // // function $(id) {
// // // // //   return document.getElementById(id);
// // // // // }

// // // // // function showNote(id, type, message) {
// // // // //   const el = $(id);
// // // // //   if (!el) return;
// // // // //   el.innerHTML  = message || "";
// // // // //   el.className  = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // // }

// // // // // function showCard(id) {
// // // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
// // // // //     const el = $(cardId);
// // // // //     if (el) el.classList.add("isHidden");
// // // // //   });
// // // // //   const target = $(id);
// // // // //   if (target) target.classList.remove("isHidden");
// // // // // }

// // // // // function setStepState(activeIndex) {
// // // // //   document.querySelectorAll(".setup-step").forEach((step, index) => {
// // // // //     step.classList.remove("isActive", "isDone");
// // // // //     if (index < activeIndex) step.classList.add("isDone");
// // // // //     if (index === activeIndex) step.classList.add("isActive");
// // // // //   });
// // // // // }

// // // // // function setProgress(percent, text) {
// // // // //   const fill  = $("progressFill");
// // // // //   const label = $("progressText");
// // // // //   if (fill)  fill.style.width   = `${percent}%`;
// // // // //   if (label) label.textContent  = text || "";
// // // // // }


// // // // // // ─── API helpers ─────────────────────────────────────────────────────────────
// // // // // async function apiGet(path) {
// // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // //     method:  "GET",
// // // // //     headers: { "Content-Type": "application/json" }
// // // // //   });
// // // // //   return response.json();
// // // // // }

// // // // // async function apiPost(path, payload = {}) {
// // // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // // //     method:  "POST",
// // // // //     headers: { "Content-Type": "application/json" },
// // // // //     body:    JSON.stringify(payload)
// // // // //   });
// // // // //   return response.json();
// // // // // }


// // // // // // ─── Session helpers ──────────────────────────────────────────────────────────
// // // // // function getStoredSessionPayload() {
// // // // //   return {
// // // // //     user_id:             localStorage.getItem("basira_user_id")             || "",
// // // // //     access_token:        localStorage.getItem("basira_access_token")        || "",
// // // // //     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
// // // // //     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
// // // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // // //   };
// // // // // }

// // // // // async function readCloudUser() {
// // // // //   try {
// // // // //     const { data: { session } } = await supabaseClient.auth.getSession();

// // // // //     if (!session?.user) {
// // // // //       $("cloudUserLabel").textContent    = "لم يتم العثور على جلسة مستخدم.";
// // // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // // //       return null;
// // // // //     }

// // // // //     const userName =
// // // // //       session.user.user_metadata?.full_name ||
// // // // //       session.user.email ||
// // // // //       session.user.id;

// // // // //     $("cloudUserLabel").textContent    = userName;
// // // // //     $("subscriptionLabel").textContent =
// // // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // // //     return session;
// // // // //   } catch (err) {
// // // // //     $("cloudUserLabel").textContent    = "تعذر قراءة بيانات المستخدم.";
// // // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // // //     return null;
// // // // //   }
// // // // // }

// // // // // async function pushLocalSession() {
// // // // //   const payload = getStoredSessionPayload();
// // // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // // //   }
// // // // //   await apiPost("/api/setup/login-complete", payload);
// // // // // }


// // // // // // ─── Heartbeat & inactivity ───────────────────────────────────────────────────
// // // // // async function sendHeartbeat() {
// // // // //   try {
// // // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // // //       method:  "POST",
// // // // //       headers: { "Content-Type": "application/json" }
// // // // //     });

// // // // //     if (response.status === 401) {
// // // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // // //       setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // // //     }
// // // // //   } catch (err) {
// // // // //     console.warn("Heartbeat failed:", err);
// // // // //   }
// // // // // }

// // // // // async function autoLogoutNow() {
// // // // //   try {
// // // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // // //       method:  "POST",
// // // // //       headers: { "Content-Type": "application/json" }
// // // // //     });
// // // // //   } catch (err) {
// // // // //     console.warn("Auto logout request failed:", err);
// // // // //   }
// // // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // // //   setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // // // }

// // // // // function resetInactivityTimer() {
// // // // //   if (inactivityTimer) clearTimeout(inactivityTimer);
// // // // //   inactivityTimer = setTimeout(autoLogoutNow, INACTIVITY_LIMIT_MS);
// // // // // }

// // // // // function bindActivityTracking() {
// // // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // // //     window.addEventListener(eventName, resetInactivityTimer);
// // // // //   });
// // // // //   resetInactivityTimer();
// // // // //   setInterval(sendHeartbeat, 60_000);
// // // // // }


// // // // // // ─── Folder picker ────────────────────────────────────────────────────────────
// // // // // async function browseForDataDirectory(targetInputId = "dataDirectory") {
// // // // //   try {
// // // // //     const result = await apiGet("/api/system/pick-data-dir");
// // // // //     if (!result || result.status !== "ok") {
// // // // //       throw new Error(result?.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // //     }
// // // // //     if (result.path) {
// // // // //       const input = $(targetInputId);
// // // // //       if (input) input.value = result.path;
// // // // //     }
// // // // //   } catch (err) {
// // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح نافذة اختيار المجلد.");
// // // // //   }
// // // // // }


// // // // // // ─── Startup / state machine ──────────────────────────────────────────────────
// // // // // async function initializeStartup() {
// // // // //   setStepState(0);

// // // // //   try {
// // // // //     await readCloudUser();

// // // // //     const statusCard = $("startupStatusCard");
// // // // //     if (statusCard) {
// // // // //       const title = statusCard.querySelector(".local-card__title");
// // // // //       const text  = statusCard.querySelector(".local-card__text");
// // // // //       if (title) title.textContent = "جارٍ التحقق من البيئة المحلية";
// // // // //       if (text)  text.textContent  =
// // // // //         "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";
// // // // //     }

// // // // //     startupState = await apiGet("/api/startup-status");

// // // // //     if (!startupState || !startupState.state) {
// // // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // // //     }

// // // // //     // ── New user or incomplete setup ────────────────────────────────────────
// // // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // // //       showCard("newUserCard");
// // // // //       setStepState(1);
// // // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // // //       return;
// // // // //     }

// // // // //     // ── Already healthy ─────────────────────────────────────────────────────
// // // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // //       showCard("readyCard");
// // // // //       setStepState(3);
// // // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // // //       return;
// // // // //     }

// // // // //     // ── Session expired — try to re-link from Supabase ──────────────────────
// // // // //     if (startupState.state === "login_required") {
// // // // //       showNote("localSetupMessage", "err",
// // // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية.");

// // // // //       await pushLocalSession();
// // // // //       startupState = await apiGet("/api/startup-status");

// // // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // // //         showCard("readyCard");
// // // // //         setStepState(3);
// // // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // // //       } else {
// // // // //         showCard("newUserCard");
// // // // //         setStepState(1);
// // // // //       }
// // // // //       return;
// // // // //     }

// // // // //     // ── Subscription issue ──────────────────────────────────────────────────
// // // // //     if (startupState.state === "subscription_required") {
// // // // //       showCard("recoveryCard");
// // // // //       setStepState(1);
// // // // //       const recoveryText    = $("recoveryText");
// // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // //       if (recoveryText)   recoveryText.textContent   = "الاشتراك غير فعال. يرجى تجديد الاشتراك للمتابعة.";
// // // // //       if (repairPrimaryBtn) {
// // // // //         repairPrimaryBtn.textContent  = "فتح بوابة التجديد";
// // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // //       }
// // // // //       showNote("localSetupMessage", "err", "الاشتراك غير فعال حاليًا.");
// // // // //       return;
// // // // //     }

// // // // //     // ── Recovery needed (missing dir / models) ───────────────────────────────
// // // // //     if (startupState.state === "recovery_required") {
// // // // //       showCard("recoveryCard");
// // // // //       setStepState(1);
// // // // //       const reason          = startupState.reason || "";
// // // // //       const recoveryText    = $("recoveryText");
// // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // //       const recoveryPathField = $("recoveryPathField");

// // // // //       if (reason === "data_dir_missing") {
// // // // //         if (recoveryText)   recoveryText.textContent   = "مجلد البيانات المحلية غير موجود. اختاري مسارًا جديدًا ثم اضغطي إصلاح.";
// // // // //         if (recoveryPathField) recoveryPathField.classList.remove("isHidden");
// // // // //         if (repairPrimaryBtn) {
// // // // //           repairPrimaryBtn.textContent  = "إصلاح المسار";
// // // // //           repairPrimaryBtn.dataset.mode = "reselect-path";
// // // // //         }
// // // // //       } else if (reason === "models_not_installed") {
// // // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // // //         if (repairPrimaryBtn) {
// // // // //           repairPrimaryBtn.textContent  = "إعادة تنزيل الملفات الأساسية";
// // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // //         }
// // // // //       } else {
// // // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // // //         if (repairPrimaryBtn) {
// // // // //           repairPrimaryBtn.textContent  = "إصلاح الآن";
// // // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // // //         }
// // // // //       }

// // // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // // //       return;
// // // // //     }

// // // // //     // ── Mandatory update required ────────────────────────────────────────────
// // // // //     if (startupState.state === "update_required") {
// // // // //       showCard("recoveryCard");
// // // // //       setStepState(1);
// // // // //       const recoveryText    = $("recoveryText");
// // // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // // //       if (recoveryText)     recoveryText.textContent   = "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.";
// // // // //       if (repairPrimaryBtn) {
// // // // //         repairPrimaryBtn.textContent  = "فتح بوابة التحديث";
// // // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // // //       }
// // // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا.");
// // // // //       return;
// // // // //     }

// // // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // // //   } catch (err) {
// // // // //     showNote("localSetupMessage", "err",
// // // // //       err.message || "تعذر بدء صفحة التهيئة المحلية. تأكدي من تشغيل Basira Local Launcher.");
// // // // //   }
// // // // // }


// // // // // // ─── First-time setup flow ────────────────────────────────────────────────────
// // // // // async function runFirstSetup() {
// // // // //   try {
// // // // //     const session = await readCloudUser();
// // // // //     if (!session?.user) {
// // // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // // //     }

// // // // //     setStepState(2);
// // // // //     showCard("loadingCard");

// // // // //     setProgress(10,  "تهيئة الحالة المحلية...");
// // // // //     await apiPost("/api/setup/init");

// // // // //     setProgress(20,  "ربط الجلسة المحلية...");
// // // // //     await pushLocalSession();

// // // // //     const dataDir = $("dataDirectory")?.value.trim()
// // // // //       || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // //     setProgress(35,  "إنشاء المجلدات المحلية...");
// // // // //     const dirResult = await apiPost("/api/setup/select-data-dir", { data_dir: dataDir });
// // // // //     if (!dirResult || dirResult.status !== "ok") {
// // // // //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات المحلية.");
// // // // //     }

// // // // //     setProgress(60,  "تنزيل الملفات الأساسية المحلية...");
// // // // //     const installResult = await apiPost("/api/setup/install-models");
// // // // //     if (!installResult || installResult.status !== "ok") {
// // // // //       throw new Error(installResult?.message || "تعذر تجهيز الملفات الأساسية المحلية.");
// // // // //     }

// // // // //     setProgress(80,  "التحقق من الجاهزية...");
// // // // //     const verifyResult = await apiGet("/api/setup/verify");
// // // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // // //     }

// // // // //     setProgress(95,  "اعتماد التهيئة النهائية...");
// // // // //     const finalizeResult = await apiPost("/api/setup/finalize");
// // // // //     if (!finalizeResult || finalizeResult.status !== "ok") {
// // // // //       throw new Error("تعذر اعتماد التهيئة النهائية.");
// // // // //     }

// // // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // // //     setStepState(3);
// // // // //     showCard("readyCard");
// // // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // // //   } catch (err) {
// // // // //     showCard("recoveryCard");
// // // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // // //   }
// // // // // }


// // // // // // ─── Recovery flow ────────────────────────────────────────────────────────────
// // // // // async function runRecoveryAction() {
// // // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // // //   try {
// // // // //     if (mode === "reselect-path") {
// // // // //       const pathValue = $("recoveryDataDirectory")?.value.trim()
// // // // //         || "C:\\Users\\Public\\Documents\\BasiraData";

// // // // //       showCard("loadingCard");
// // // // //       setProgress(30, "تحديث مسار البيانات...");
// // // // //       const result = await apiPost("/api/recovery/reselect-data-dir", { data_dir: pathValue });
// // // // //       if (!result || result.status !== "ok") {
// // // // //         throw new Error(result?.message || "تعذر تحديث مسار البيانات.");
// // // // //       }

// // // // //       setProgress(70, "التحقق من البيئة...");
// // // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // // //       }

// // // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // // //       showCard("readyCard");
// // // // //       setStepState(3);
// // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // //       return;
// // // // //     }

// // // // //     if (mode === "repair-models") {
// // // // //       showCard("loadingCard");
// // // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // // //       const result = await apiPost("/api/recovery/repair-models");
// // // // //       if (!result || result.status !== "ok") {
// // // // //         throw new Error(result?.message || "تعذر إصلاح الملفات الأساسية.");
// // // // //       }

// // // // //       setProgress(75, "التحقق النهائي...");
// // // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // // //       }

// // // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // // //       showCard("readyCard");
// // // // //       setStepState(3);
// // // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // // //       return;
// // // // //     }

// // // // //     if (mode === "open-update") {
// // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // //       return;
// // // // //     }
// // // // //   } catch (err) {
// // // // //     showCard("recoveryCard");
// // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // // //   }
// // // // // }


// // // // // // ─── Launch local app ─────────────────────────────────────────────────────────
// // // // // async function launchLocalEnvironment() {
// // // // //   try {
// // // // //     const startup = await apiGet("/api/startup-status");
// // // // //     if (!startup || !startup.state) {
// // // // //       throw new Error("تعذر التحقق من حالة البيئة المحلية.");
// // // // //     }

// // // // //     if (startup.state === "healthy" || startup.state === "healthy_with_optional_update") {
// // // // //       window.open(LOCAL_APP_URL, "_blank");
// // // // //       showNote("localSetupMessage", "ok", "تم فتح التطبيق المحلي بنجاح.");
// // // // //       return;
// // // // //     }

// // // // //     const messages = {
// // // // //       login_required:       "الجلسة المحلية تحتاج إعادة ربط قبل فتح التطبيق.",
// // // // //       new_user:             "يجب إكمال التهيئة المحلية أولًا.",
// // // // //       setup_incomplete:     "يجب إكمال التهيئة المحلية أولًا.",
// // // // //       recovery_required:    "توجد مشكلة في البيئة المحلية ويجب إصلاحها أولًا.",
// // // // //       subscription_required:"الاشتراك غير فعال حاليًا.",
// // // // //       update_required:      "النسخة المحلية تحتاج تحديثًا قبل التشغيل."
// // // // //     };

// // // // //     showNote("localSetupMessage", "err",
// // // // //       messages[startup.state] || "الحالة الحالية لا تسمح بفتح التطبيق المحلي.");
// // // // //   } catch (err) {
// // // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح التطبيق المحلي.");
// // // // //   }
// // // // // }


// // // // // // ─── Subscription renew (demo / cloud) ───────────────────────────────────────
// // // // // async function renewSubscriptionDemo() {
// // // // //   try {
// // // // //     const result = await apiPost("/api/subscription/renew-demo");
// // // // //     if (!result || result.status !== "ok") {
// // // // //       throw new Error(result?.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // //     }
// // // // //     localStorage.setItem("basira_subscription_status", "active");
// // // // //     $("subscriptionLabel").textContent = "active";
// // // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // // //   } catch (err) {
// // // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // // //   }
// // // // // }


// // // // // // ─── Boot ─────────────────────────────────────────────────────────────────────
// // // // // document.addEventListener("DOMContentLoaded", async () => {
// // // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

// // // // //   $("browseDataDirectoryBtn")?.addEventListener("click", () => {
// // // // //     browseForDataDirectory("dataDirectory");
// // // // //   });

// // // // //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => {
// // // // //     browseForDataDirectory("recoveryDataDirectory");
// // // // //   });

// // // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // // //     const useCloud = confirm(
// // // // //       "هل تريد فتح صفحة التجديد السحابية؟\nاضغط موافق للتجديد السحابي أو إلغاء لتجديد demo."
// // // // //     );
// // // // //     if (useCloud) {
// // // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // // //     } else {
// // // // //       renewSubscriptionDemo();
// // // // //     }
// // // // //   });

// // // // //   bindActivityTracking();
// // // // //   await initializeStartup();
// // // // // });

// // // // /**
// // // //  * local-setup.js — Basira Cloud Setup Page Logic
// // // //  * ================================================
// // // //  * Runs in the browser on the cloud website (local-setup.html).
// // // //  * Communicates with the local bootstrap API at http://127.0.0.1:5001
// // // //  * to set up or verify the on-premise environment, then opens
// // // //  * the main local app at http://127.0.0.1:5000.
// // // //  *
// // // //  * Prerequisites: supabase-config.js must define SUPABASE_URL and SUPABASE_ANON_KEY.
// // // //  */

// // // // // ─── Constants ────────────────────────────────────────────────────────────────
// // // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";   // basira_local_bootstrap.py
// // // // const LOCAL_APP_URL       = "http://127.0.0.1:5000";   // Basira_app_structure.py
// // // // const CLOUD_RENEW_URL     = "https://basira.basira-toolmodel.workers.dev/renew";

// // // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;  // 20 minutes

// // // // let startupState    = null;
// // // // let inactivityTimer = null;


// // // // // ─── DOM helpers ─────────────────────────────────────────────────────────────
// // // // function $(id) {
// // // //   return document.getElementById(id);
// // // // }

// // // // function showNote(id, type, message) {
// // // //   const el = $(id);
// // // //   if (!el) return;
// // // //   el.innerHTML  = message || "";
// // // //   el.className  = "note " + (type === "ok" ? "isOk" : "isErr");
// // // // }

// // // // function showCard(id) {
// // // //   ["newUserCard", "loadingCard", "recoveryCard", "readyCard", "notRunningCard"].forEach(cardId => {
// // // //     const el = $(cardId);
// // // //     if (el) el.classList.add("isHidden");
// // // //   });
// // // //   const target = $(id);
// // // //   if (target) target.classList.remove("isHidden");
// // // // }

// // // // async function retryConnection() {
// // // //   const btn = $("retryConnectBtn");
// // // //   if (btn) btn.disabled = true;
// // // //   showNote("localSetupMessage", "ok", "جارٍ إعادة الاتصال بالبيئة المحلية...");
// // // //   await initializeStartup();
// // // //   if (btn) btn.disabled = false;
// // // // }

// // // // function setStepState(activeIndex) {
// // // //   document.querySelectorAll(".setup-step").forEach((step, index) => {
// // // //     step.classList.remove("isActive", "isDone");
// // // //     if (index < activeIndex) step.classList.add("isDone");
// // // //     if (index === activeIndex) step.classList.add("isActive");
// // // //   });
// // // // }

// // // // function setProgress(percent, text) {
// // // //   const fill  = $("progressFill");
// // // //   const label = $("progressText");
// // // //   if (fill)  fill.style.width   = `${percent}%`;
// // // //   if (label) label.textContent  = text || "";
// // // // }


// // // // // ─── API helpers ─────────────────────────────────────────────────────────────
// // // // async function apiGet(path) {
// // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // //     method:  "GET",
// // // //     headers: { "Content-Type": "application/json" }
// // // //   });
// // // //   return response.json();
// // // // }

// // // // async function apiPost(path, payload = {}) {
// // // //   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // // //     method:  "POST",
// // // //     headers: { "Content-Type": "application/json" },
// // // //     body:    JSON.stringify(payload)
// // // //   });
// // // //   return response.json();
// // // // }


// // // // // ─── Session helpers ──────────────────────────────────────────────────────────
// // // // function getStoredSessionPayload() {
// // // //   return {
// // // //     user_id:             localStorage.getItem("basira_user_id")             || "",
// // // //     access_token:        localStorage.getItem("basira_access_token")        || "",
// // // //     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
// // // //     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
// // // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // // //   };
// // // // }

// // // // async function readCloudUser() {
// // // //   try {
// // // //     const { data: { session } } = await supabaseClient.auth.getSession();

// // // //     if (!session?.user) {
// // // //       $("cloudUserLabel").textContent    = "لم يتم العثور على جلسة مستخدم.";
// // // //       $("subscriptionLabel").textContent = "غير معروف";
// // // //       return null;
// // // //     }

// // // //     const userName =
// // // //       session.user.user_metadata?.full_name ||
// // // //       session.user.email ||
// // // //       session.user.id;

// // // //     $("cloudUserLabel").textContent    = userName;
// // // //     $("subscriptionLabel").textContent =
// // // //       localStorage.getItem("basira_subscription_status") || "غير معروف";

// // // //     return session;
// // // //   } catch (err) {
// // // //     $("cloudUserLabel").textContent    = "تعذر قراءة بيانات المستخدم.";
// // // //     $("subscriptionLabel").textContent = "غير معروف";
// // // //     return null;
// // // //   }
// // // // }

// // // // async function pushLocalSession() {
// // // //   const payload = getStoredSessionPayload();
// // // //   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
// // // //     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
// // // //   }
// // // //   await apiPost("/api/setup/login-complete", payload);
// // // // }


// // // // // ─── Heartbeat & inactivity ───────────────────────────────────────────────────
// // // // async function sendHeartbeat() {
// // // //   try {
// // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // // //       method:  "POST",
// // // //       headers: { "Content-Type": "application/json" }
// // // //     });

// // // //     if (response.status === 401) {
// // // //       showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
// // // //       setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // //     }
// // // //   } catch (err) {
// // // //     console.warn("Heartbeat failed:", err);
// // // //   }
// // // // }

// // // // async function autoLogoutNow() {
// // // //   try {
// // // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // // //       method:  "POST",
// // // //       headers: { "Content-Type": "application/json" }
// // // //     });
// // // //   } catch (err) {
// // // //     console.warn("Auto logout request failed:", err);
// // // //   }
// // // //   showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
// // // //   setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // // }

// // // // function resetInactivityTimer() {
// // // //   if (inactivityTimer) clearTimeout(inactivityTimer);
// // // //   inactivityTimer = setTimeout(autoLogoutNow, INACTIVITY_LIMIT_MS);
// // // // }

// // // // function bindActivityTracking() {
// // // //   ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
// // // //     window.addEventListener(eventName, resetInactivityTimer);
// // // //   });
// // // //   resetInactivityTimer();
// // // //   setInterval(sendHeartbeat, 60_000);
// // // // }


// // // // // ─── Folder picker ────────────────────────────────────────────────────────────
// // // // async function browseForDataDirectory(targetInputId = "dataDirectory") {
// // // //   try {
// // // //     const result = await apiGet("/api/system/pick-data-dir");
// // // //     if (!result || result.status !== "ok") {
// // // //       throw new Error(result?.message || "تعذر فتح نافذة اختيار المجلد.");
// // // //     }
// // // //     if (result.path) {
// // // //       const input = $(targetInputId);
// // // //       if (input) input.value = result.path;
// // // //     }
// // // //   } catch (err) {
// // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح نافذة اختيار المجلد.");
// // // //   }
// // // // }


// // // // // ─── Startup / state machine ──────────────────────────────────────────────────
// // // // async function isBootstrapReachable() {
// // // //   try {
// // // //     const ctrl     = new AbortController();
// // // //     const timer    = setTimeout(() => ctrl.abort(), 3000);
// // // //     const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/health`, { signal: ctrl.signal });
// // // //     clearTimeout(timer);
// // // //     return response.ok;
// // // //   } catch {
// // // //     return false;
// // // //   }
// // // // }

// // // // async function initializeStartup() {
// // // //   setStepState(0);

// // // //   try {
// // // //     await readCloudUser();

// // // //     const statusCard = $("startupStatusCard");
// // // //     if (statusCard) {
// // // //       const title = statusCard.querySelector(".local-card__title");
// // // //       const text  = statusCard.querySelector(".local-card__text");
// // // //       if (title) title.textContent = "جارٍ التحقق من البيئة المحلية";
// // // //       if (text)  text.textContent  =
// // // //         "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";
// // // //     }

// // // //     // ── Check if the local launcher is actually running ─────────────────────
// // // //     const reachable = await isBootstrapReachable();
// // // //     if (!reachable) {
// // // //       showCard("notRunningCard");
// // // //       showNote("localSetupMessage", "err",
// // // //         "تعذر الاتصال بالبيئة المحلية. تأكدي من تشغيل Basira Launcher أولًا.");
// // // //       return;
// // // //     }

// // // //     startupState = await apiGet("/api/startup-status");

// // // //     if (!startupState || !startupState.state) {
// // // //       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
// // // //     }

// // // //     // ── New user or incomplete setup ────────────────────────────────────────
// // // //     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
// // // //       showCard("newUserCard");
// // // //       setStepState(1);
// // // //       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
// // // //       return;
// // // //     }

// // // //     // ── Already healthy ─────────────────────────────────────────────────────
// // // //     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // //       showCard("readyCard");
// // // //       setStepState(3);
// // // //       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
// // // //       return;
// // // //     }

// // // //     // ── Session expired — try to re-link from Supabase ──────────────────────
// // // //     if (startupState.state === "login_required") {
// // // //       showNote("localSetupMessage", "err",
// // // //         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية.");

// // // //       await pushLocalSession();
// // // //       startupState = await apiGet("/api/startup-status");

// // // //       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
// // // //         showCard("readyCard");
// // // //         setStepState(3);
// // // //         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
// // // //       } else {
// // // //         showCard("newUserCard");
// // // //         setStepState(1);
// // // //       }
// // // //       return;
// // // //     }

// // // //     // ── Subscription issue ──────────────────────────────────────────────────
// // // //     if (startupState.state === "subscription_required") {
// // // //       showCard("recoveryCard");
// // // //       setStepState(1);
// // // //       const recoveryText    = $("recoveryText");
// // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // //       if (recoveryText)   recoveryText.textContent   = "الاشتراك غير فعال. يرجى تجديد الاشتراك للمتابعة.";
// // // //       if (repairPrimaryBtn) {
// // // //         repairPrimaryBtn.textContent  = "فتح بوابة التجديد";
// // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // //       }
// // // //       showNote("localSetupMessage", "err", "الاشتراك غير فعال حاليًا.");
// // // //       return;
// // // //     }

// // // //     // ── Recovery needed (missing dir / models) ───────────────────────────────
// // // //     if (startupState.state === "recovery_required") {
// // // //       showCard("recoveryCard");
// // // //       setStepState(1);
// // // //       const reason          = startupState.reason || "";
// // // //       const recoveryText    = $("recoveryText");
// // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // //       const recoveryPathField = $("recoveryPathField");

// // // //       if (reason === "data_dir_missing") {
// // // //         if (recoveryText)   recoveryText.textContent   = "مجلد البيانات المحلية غير موجود. اختاري مسارًا جديدًا ثم اضغطي إصلاح.";
// // // //         if (recoveryPathField) recoveryPathField.classList.remove("isHidden");
// // // //         if (repairPrimaryBtn) {
// // // //           repairPrimaryBtn.textContent  = "إصلاح المسار";
// // // //           repairPrimaryBtn.dataset.mode = "reselect-path";
// // // //         }
// // // //       } else if (reason === "models_not_installed") {
// // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
// // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // //         if (repairPrimaryBtn) {
// // // //           repairPrimaryBtn.textContent  = "إعادة تنزيل الملفات الأساسية";
// // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // //         }
// // // //       } else {
// // // //         if (recoveryText)   recoveryText.textContent   = "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
// // // //         if (recoveryPathField) recoveryPathField.classList.add("isHidden");
// // // //         if (repairPrimaryBtn) {
// // // //           repairPrimaryBtn.textContent  = "إصلاح الآن";
// // // //           repairPrimaryBtn.dataset.mode = "repair-models";
// // // //         }
// // // //       }

// // // //       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
// // // //       return;
// // // //     }

// // // //     // ── Mandatory update required ────────────────────────────────────────────
// // // //     if (startupState.state === "update_required") {
// // // //       showCard("recoveryCard");
// // // //       setStepState(1);
// // // //       const recoveryText    = $("recoveryText");
// // // //       const repairPrimaryBtn = $("repairPrimaryBtn");
// // // //       if (recoveryText)     recoveryText.textContent   = "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.";
// // // //       if (repairPrimaryBtn) {
// // // //         repairPrimaryBtn.textContent  = "فتح بوابة التحديث";
// // // //         repairPrimaryBtn.dataset.mode = "open-update";
// // // //       }
// // // //       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا.");
// // // //       return;
// // // //     }

// // // //     throw new Error("حالة تشغيل غير معروفة.");
// // // //   } catch (err) {
// // // //     showNote("localSetupMessage", "err",
// // // //       err.message || "تعذر بدء صفحة التهيئة المحلية. تأكدي من تشغيل Basira Local Launcher.");
// // // //   }
// // // // }


// // // // // ─── First-time setup flow ────────────────────────────────────────────────────
// // // // async function runFirstSetup() {
// // // //   try {
// // // //     const session = await readCloudUser();
// // // //     if (!session?.user) {
// // // //       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
// // // //     }

// // // //     setStepState(2);
// // // //     showCard("loadingCard");

// // // //     setProgress(10,  "تهيئة الحالة المحلية...");
// // // //     await apiPost("/api/setup/init");

// // // //     setProgress(20,  "ربط الجلسة المحلية...");
// // // //     await pushLocalSession();

// // // //     const dataDir = $("dataDirectory")?.value.trim()
// // // //       || "C:\\Users\\Public\\Documents\\BasiraData";

// // // //     setProgress(35,  "إنشاء المجلدات المحلية...");
// // // //     const dirResult = await apiPost("/api/setup/select-data-dir", { data_dir: dataDir });
// // // //     if (!dirResult || dirResult.status !== "ok") {
// // // //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات المحلية.");
// // // //     }

// // // //     setProgress(60,  "تنزيل الملفات الأساسية المحلية...");
// // // //     const installResult = await apiPost("/api/setup/install-models");
// // // //     if (!installResult || installResult.status !== "ok") {
// // // //       throw new Error(installResult?.message || "تعذر تجهيز الملفات الأساسية المحلية.");
// // // //     }

// // // //     setProgress(80,  "التحقق من الجاهزية...");
// // // //     const verifyResult = await apiGet("/api/setup/verify");
// // // //     if (!verifyResult || verifyResult.status !== "ok") {
// // // //       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
// // // //     }

// // // //     setProgress(95,  "اعتماد التهيئة النهائية...");
// // // //     const finalizeResult = await apiPost("/api/setup/finalize");
// // // //     if (!finalizeResult || finalizeResult.status !== "ok") {
// // // //       throw new Error("تعذر اعتماد التهيئة النهائية.");
// // // //     }

// // // //     setProgress(100, "اكتملت التهيئة بنجاح.");
// // // //     setStepState(3);
// // // //     showCard("readyCard");
// // // //     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
// // // //   } catch (err) {
// // // //     showCard("recoveryCard");
// // // //     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
// // // //   }
// // // // }


// // // // // ─── Recovery flow ────────────────────────────────────────────────────────────
// // // // async function runRecoveryAction() {
// // // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// // // //   try {
// // // //     if (mode === "reselect-path") {
// // // //       const pathValue = $("recoveryDataDirectory")?.value.trim()
// // // //         || "C:\\Users\\Public\\Documents\\BasiraData";

// // // //       showCard("loadingCard");
// // // //       setProgress(30, "تحديث مسار البيانات...");
// // // //       const result = await apiPost("/api/recovery/reselect-data-dir", { data_dir: pathValue });
// // // //       if (!result || result.status !== "ok") {
// // // //         throw new Error(result?.message || "تعذر تحديث مسار البيانات.");
// // // //       }

// // // //       setProgress(70, "التحقق من البيئة...");
// // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // //         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
// // // //       }

// // // //       setProgress(100, "تم إصلاح مسار البيانات.");
// // // //       showCard("readyCard");
// // // //       setStepState(3);
// // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // //       return;
// // // //     }

// // // //     if (mode === "repair-models") {
// // // //       showCard("loadingCard");
// // // //       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
// // // //       const result = await apiPost("/api/recovery/repair-models");
// // // //       if (!result || result.status !== "ok") {
// // // //         throw new Error(result?.message || "تعذر إصلاح الملفات الأساسية.");
// // // //       }

// // // //       setProgress(75, "التحقق النهائي...");
// // // //       const verifyResult = await apiGet("/api/setup/verify");
// // // //       if (!verifyResult || verifyResult.status !== "ok") {
// // // //         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
// // // //       }

// // // //       setProgress(100, "تم إصلاح الملفات الأساسية.");
// // // //       showCard("readyCard");
// // // //       setStepState(3);
// // // //       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
// // // //       return;
// // // //     }

// // // //     if (mode === "open-update") {
// // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // //       return;
// // // //     }
// // // //   } catch (err) {
// // // //     showCard("recoveryCard");
// // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
// // // //   }
// // // // }


// // // // // ─── Launch local app ─────────────────────────────────────────────────────────
// // // // async function launchLocalEnvironment() {
// // // //   try {
// // // //     const startup = await apiGet("/api/startup-status");
// // // //     if (!startup || !startup.state) {
// // // //       throw new Error("تعذر التحقق من حالة البيئة المحلية.");
// // // //     }

// // // //     if (startup.state === "healthy" || startup.state === "healthy_with_optional_update") {
// // // //       window.open(LOCAL_APP_URL, "_blank");
// // // //       showNote("localSetupMessage", "ok", "تم فتح التطبيق المحلي بنجاح.");
// // // //       return;
// // // //     }

// // // //     const messages = {
// // // //       login_required:       "الجلسة المحلية تحتاج إعادة ربط قبل فتح التطبيق.",
// // // //       new_user:             "يجب إكمال التهيئة المحلية أولًا.",
// // // //       setup_incomplete:     "يجب إكمال التهيئة المحلية أولًا.",
// // // //       recovery_required:    "توجد مشكلة في البيئة المحلية ويجب إصلاحها أولًا.",
// // // //       subscription_required:"الاشتراك غير فعال حاليًا.",
// // // //       update_required:      "النسخة المحلية تحتاج تحديثًا قبل التشغيل."
// // // //     };

// // // //     showNote("localSetupMessage", "err",
// // // //       messages[startup.state] || "الحالة الحالية لا تسمح بفتح التطبيق المحلي.");
// // // //   } catch (err) {
// // // //     showNote("localSetupMessage", "err", err.message || "تعذر فتح التطبيق المحلي.");
// // // //   }
// // // // }


// // // // // ─── Subscription renew (demo / cloud) ───────────────────────────────────────
// // // // async function renewSubscriptionDemo() {
// // // //   try {
// // // //     const result = await apiPost("/api/subscription/renew-demo");
// // // //     if (!result || result.status !== "ok") {
// // // //       throw new Error(result?.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // //     }
// // // //     localStorage.setItem("basira_subscription_status", "active");
// // // //     $("subscriptionLabel").textContent = "active";
// // // //     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
// // // //   } catch (err) {
// // // //     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
// // // //   }
// // // // }


// // // // // ─── Boot ─────────────────────────────────────────────────────────────────────
// // // // document.addEventListener("DOMContentLoaded", async () => {
// // // //   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
// // // //   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
// // // //   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);
// // // //   $("retryConnectBtn")?.addEventListener("click", retryConnection);

// // // //   $("browseDataDirectoryBtn")?.addEventListener("click", () => {
// // // //     browseForDataDirectory("dataDirectory");
// // // //   });

// // // //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => {
// // // //     browseForDataDirectory("recoveryDataDirectory");
// // // //   });

// // // //   $("renewSubscriptionBtn")?.addEventListener("click", () => {
// // // //     const useCloud = confirm(
// // // //       "هل تريد فتح صفحة التجديد السحابية؟\nاضغط موافق للتجديد السحابي أو إلغاء لتجديد demo."
// // // //     );
// // // //     if (useCloud) {
// // // //       window.open(CLOUD_RENEW_URL, "_blank");
// // // //     } else {
// // // //       renewSubscriptionDemo();
// // // //     }
// // // //   });

// // // //   bindActivityTracking();
// // // //   await initializeStartup();
// // // // });

// // // /**
// // //  * local-setup.js — Basira On-Premise Setup
// // //  * ==========================================
// // //  * STATE MACHINE:
// // //  *
// // //  *  Launcher not running → show "notRunningCard" (retry button)
// // //  *
// // //  *  new_user / setup_incomplete
// // //  *      → show "pickFolderCard" (user picks data folder ONCE)
// // //  *      → on confirm → run setup silently → open app
// // //  *
// // //  *  login_required
// // //  *      → auto re-link Supabase session → re-check state
// // //  *
// // //  *  healthy / healthy_with_optional_update
// // //  *      → open local app automatically (no clicks needed)
// // //  *
// // //  *  recovery_required  → show repair card (one click)
// // //  *  subscription_required → show subscription card
// // //  *  update_required    → show update card
// // //  */

// // // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // // const LOCAL_APP_URL       = "http://127.0.0.1:5000";
// // // const CLOUD_RENEW_URL     = "https://basira.basira-toolmodel.workers.dev/renew";
// // // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

// // // // Suggested default — shown pre-filled in the input but user can change it
// // // const SUGGESTED_DATA_DIR  = "C:\\BasiraData";

// // // let startupState    = null;
// // // let inactivityTimer = null;


// // // // ─── DOM ──────────────────────────────────────────────────────────────────────
// // // function $(id) { return document.getElementById(id); }

// // // function showNote(id, type, message) {
// // //   const el = $(id);
// // //   if (!el) return;
// // //   el.innerHTML = message || "";
// // //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // // }

// // // function showCard(id) {
// // //   ["startupStatusCard","pickFolderCard","loadingCard",
// // //    "recoveryCard","readyCard","notRunningCard","subscriptionCard"
// // //   ].forEach(cardId => {
// // //     const el = $(cardId);
// // //     if (el) el.classList.add("isHidden");
// // //   });
// // //   const target = $(id);
// // //   if (target) target.classList.remove("isHidden");
// // // }

// // // function setStepState(activeIndex) {
// // //   document.querySelectorAll(".setup-step").forEach((step, index) => {
// // //     step.classList.remove("isActive", "isDone");
// // //     if (index < activeIndex) step.classList.add("isDone");
// // //     if (index === activeIndex) step.classList.add("isActive");
// // //   });
// // // }

// // // function setProgress(percent, text) {
// // //   const fill  = $("progressFill");
// // //   const label = $("progressText");
// // //   if (fill)  fill.style.width  = `${percent}%`;
// // //   if (label) label.textContent = text || "";
// // // }


// // // // ─── API ─────────────────────────────────────────────────────────────────────
// // // async function apiGet(path) {
// // //   const ctrl  = new AbortController();
// // //   const timer = setTimeout(() => ctrl.abort(), 8000);
// // //   try {
// // //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // //       method: "GET", headers: { "Content-Type": "application/json" }, signal: ctrl.signal
// // //     });
// // //     clearTimeout(timer);
// // //     return r.json();
// // //   } catch (e) { clearTimeout(timer); throw e; }
// // // }

// // // async function apiPost(path, payload = {}) {
// // //   const ctrl  = new AbortController();
// // //   const timer = setTimeout(() => ctrl.abort(), 8000);
// // //   try {
// // //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// // //       method: "POST",
// // //       headers: { "Content-Type": "application/json" },
// // //       body: JSON.stringify(payload),
// // //       signal: ctrl.signal
// // //     });
// // //     clearTimeout(timer);
// // //     return r.json();
// // //   } catch (e) { clearTimeout(timer); throw e; }
// // // }

// // // async function isBootstrapReachable() {
// // //   try {
// // //     const ctrl  = new AbortController();
// // //     const timer = setTimeout(() => ctrl.abort(), 3000);
// // //     const resp  = await fetch(`${LOCAL_BOOTSTRAP_URL}/health`, { signal: ctrl.signal });
// // //     clearTimeout(timer);
// // //     return resp.ok;
// // //   } catch { return false; }
// // // }


// // // // ─── Session ─────────────────────────────────────────────────────────────────
// // // function getStoredSessionPayload() {
// // //   return {
// // //     user_id:             localStorage.getItem("basira_user_id")             || "",
// // //     access_token:        localStorage.getItem("basira_access_token")        || "",
// // //     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
// // //     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
// // //     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
// // //   };
// // // }

// // // async function readCloudUser() {
// // //   try {
// // //     const { data: { session } } = await supabaseClient.auth.getSession();
// // //     if (!session?.user) {
// // //       if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "لم يتم العثور على جلسة.";
// // //       if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
// // //       return null;
// // //     }
// // //     const name = session.user.user_metadata?.full_name || session.user.email || session.user.id;
// // //     if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = name;
// // //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent =
// // //       localStorage.getItem("basira_subscription_status") || "غير معروف";
// // //     return session;
// // //   } catch {
// // //     if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "تعذر قراءة البيانات.";
// // //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
// // //     return null;
// // //   }
// // // }

// // // async function pushLocalSession() {
// // //   const p = getStoredSessionPayload();
// // //   if (!p.user_id || !p.access_token || !p.expires_at) return;
// // //   try { await apiPost("/api/setup/login-complete", p); } catch {}
// // // }


// // // // ─── Heartbeat & inactivity ───────────────────────────────────────────────────
// // // async function sendHeartbeat() {
// // //   try {
// // //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
// // //       method: "POST", headers: { "Content-Type": "application/json" }
// // //     });
// // //     if (r.status === 401) setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // //   } catch {}
// // // }

// // // async function autoLogoutNow() {
// // //   try {
// // //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
// // //       method: "POST", headers: { "Content-Type": "application/json" }
// // //     });
// // //   } catch {}
// // //   setTimeout(() => { window.location.href = "./login.html"; }, 1200);
// // // }

// // // function resetInactivityTimer() {
// // //   if (inactivityTimer) clearTimeout(inactivityTimer);
// // //   inactivityTimer = setTimeout(autoLogoutNow, INACTIVITY_LIMIT_MS);
// // // }

// // // function bindActivityTracking() {
// // //   ["click","mousemove","keydown","scroll","touchstart"].forEach(ev =>
// // //     window.addEventListener(ev, resetInactivityTimer));
// // //   resetInactivityTimer();
// // //   setInterval(sendHeartbeat, 60_000);
// // // }


// // // // ─── Native folder picker (calls bootstrap API which opens tkinter dialog) ───
// // // async function browseFolder(inputId) {
// // //   try {
// // //     const result = await apiGet("/api/system/pick-data-dir");
// // //     if (result?.status === "ok" && result.path) {
// // //       const input = $(inputId);
// // //       if (input) input.value = result.path;
// // //     } else {
// // //       showNote("localSetupMessage", "err", "تعذر فتح نافذة اختيار المجلد.");
// // //     }
// // //   } catch {
// // //     showNote("localSetupMessage", "err", "تعذر فتح نافذة اختيار المجلد.");
// // //   }
// // // }


// // // // ─── FIRST-TIME SETUP: runs silently after user picks folder ─────────────────
// // // async function runSetupWithDir(dataDir) {
// // //   showCard("loadingCard");
// // //   setStepState(1);

// // //   try {
// // //     setProgress(10, "تهيئة الإعدادات...");
// // //     await apiPost("/api/setup/init", {});

// // //     setProgress(22, "ربط جلسة الدخول...");
// // //     await pushLocalSession();

// // //     setProgress(38, "إنشاء مجلدات البيانات في: " + dataDir);
// // //     const dirResult = await apiPost("/api/setup/select-data-dir", { data_dir: dataDir });
// // //     if (!dirResult || dirResult.status !== "ok") {
// // //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات.");
// // //     }

// // //     setProgress(58, "تثبيت الملفات الأساسية...");
// // //     await apiPost("/api/setup/install-models", {});

// // //     setProgress(78, "التحقق من البيئة...");
// // //     const verify = await apiGet("/api/setup/verify");
// // //     if (!verify || verify.status !== "ok") {
// // //       throw new Error("فشل التحقق من البيئة المحلية بعد الإعداد.");
// // //     }

// // //     setProgress(92, "اعتماد الإعداد...");
// // //     await apiPost("/api/setup/finalize", {});

// // //     setProgress(100, "اكتمل الإعداد بنجاح ✓");
// // //     setStepState(3);
// // //     showCard("readyCard");
// // //     showNote("localSetupMessage", "ok", "تم إعداد البيئة المحلية. جارٍ فتح التطبيق...");
// // //     setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 700);

// // //   } catch (err) {
// // //     showCard("recoveryCard");
// // //     const rt = $("recoveryText");
// // //     if (rt) rt.textContent = err.message || "فشل الإعداد. يرجى المحاولة مجدداً.";
// // //     const rb = $("repairPrimaryBtn");
// // //     if (rb) { rb.textContent = "إعادة المحاولة"; rb.dataset.mode = "retry-setup"; }
// // //     showNote("localSetupMessage", "err", err.message || "فشل الإعداد التلقائي.");
// // //   }
// // // }

// // // // Called when user clicks "بدء الإعداد" on the pick-folder card
// // // async function confirmFolderAndSetup() {
// // //   const input   = $("dataDirectoryInput");
// // //   const dataDir = input?.value.trim() || SUGGESTED_DATA_DIR;
// // //   if (!dataDir) {
// // //     showNote("localSetupMessage", "err", "يرجى اختيار مسار حفظ الملفات أولاً.");
// // //     return;
// // //   }
// // //   await runSetupWithDir(dataDir);
// // // }


// // // // ─── STATE MACHINE ───────────────────────────────────────────────────────────
// // // async function initializeStartup() {
// // //   setStepState(0);
// // //   showCard("startupStatusCard");
// // //   await readCloudUser();

// // //   // 1. Is the local launcher running?
// // //   const reachable = await isBootstrapReachable();
// // //   if (!reachable) {
// // //     showCard("notRunningCard");
// // //     showNote("localSetupMessage", "err", "الخادم المحلي غير مشغّل.");
// // //     return;
// // //   }

// // //   // 2. Get state from bootstrap
// // //   try {
// // //     startupState = await apiGet("/api/startup-status");
// // //   } catch {
// // //     showCard("notRunningCard");
// // //     showNote("localSetupMessage", "err", "تعذر قراءة حالة الخادم المحلي.");
// // //     return;
// // //   }

// // //   const state  = startupState?.state;
// // //   const reason = startupState?.reason || "";

// // //   switch (state) {

// // //     // ── Already fully set up → open app directly ───────────────────────────
// // //     case "healthy":
// // //     case "healthy_with_optional_update":
// // //       setStepState(3);
// // //       showCard("readyCard");
// // //       showNote("localSetupMessage", "ok", "البيئة جاهزة. جارٍ فتح التطبيق...");
// // //       setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 600);
// // //       break;

// // //     // ── First time: ask user to pick their data folder ─────────────────────
// // //     case "new_user":
// // //     case "setup_incomplete":
// // //       setStepState(1);
// // //       showCard("pickFolderCard");
// // //       showNote("localSetupMessage", "ok",
// // //         "هذه أول مرة على هذا الجهاز. اختاري مكان حفظ ملفات بصيرة.");
// // //       break;

// // //     // ── Session expired → auto re-link → re-check ──────────────────────────
// // //     case "login_required":
// // //       await pushLocalSession();
// // //       startupState = await apiGet("/api/startup-status");
// // //       if (startupState?.state === "healthy" ||
// // //           startupState?.state === "healthy_with_optional_update") {
// // //         setStepState(3);
// // //         showCard("readyCard");
// // //         showNote("localSetupMessage", "ok", "تم تجديد الجلسة. جارٍ فتح التطبيق...");
// // //         setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 600);
// // //       } else {
// // //         // Session re-linked but still incomplete setup → show folder picker
// // //         setStepState(1);
// // //         showCard("pickFolderCard");
// // //         showNote("localSetupMessage", "ok", "اختاري مكان حفظ ملفات بصيرة.");
// // //       }
// // //       break;

// // //     // ── Subscription issue ─────────────────────────────────────────────────
// // //     case "subscription_required":
// // //       showCard("subscriptionCard");
// // //       showNote("localSetupMessage", "err", "الاشتراك غير فعال. يرجى التجديد.");
// // //       break;

// // //     // ── Data/models missing → auto repair ─────────────────────────────────
// // //     case "recovery_required": {
// // //       showCard("recoveryCard");
// // //       setStepState(1);
// // //       const rt = $("recoveryText");
// // //       const rb = $("repairPrimaryBtn");
// // //       const rf = $("recoveryPathField");
// // //       if (reason === "data_dir_missing") {
// // //         if (rt) rt.textContent = "مجلد البيانات غير موجود. اختاري مساراً جديداً.";
// // //         if (rf) rf.classList.remove("isHidden");
// // //         if (rb) { rb.textContent = "إصلاح المسار"; rb.dataset.mode = "reselect-path"; }
// // //       } else {
// // //         if (rt) rt.textContent = "تم اكتشاف خلل في الملفات الأساسية.";
// // //         if (rf) rf.classList.add("isHidden");
// // //         if (rb) { rb.textContent = "إصلاح تلقائي"; rb.dataset.mode = "repair-models"; }
// // //       }
// // //       showNote("localSetupMessage", "err", "يلزم إصلاح البيئة المحلية.");
// // //       break;
// // //     }

// // //     // ── Mandatory update ───────────────────────────────────────────────────
// // //     case "update_required": {
// // //       showCard("recoveryCard");
// // //       const rt2 = $("recoveryText");
// // //       const rb2 = $("repairPrimaryBtn");
// // //       const rf2 = $("recoveryPathField");
// // //       if (rt2) rt2.textContent = "النسخة الحالية تحتاج تحديثاً إجبارياً.";
// // //       if (rf2) rf2.classList.add("isHidden");
// // //       if (rb2) { rb2.textContent = "فتح بوابة التحديث"; rb2.dataset.mode = "open-update"; }
// // //       showNote("localSetupMessage", "err", "تحديث إجباري مطلوب.");
// // //       break;
// // //     }

// // //     default:
// // //       showNote("localSetupMessage", "err", "حالة غير معروفة: " + (state || "—"));
// // //   }
// // // }


// // // // ─── Recovery action ──────────────────────────────────────────────────────────
// // // async function runRecoveryAction() {
// // //   const mode = $("repairPrimaryBtn")?.dataset.mode || "repair-models";

// // //   if (mode === "open-update") {
// // //     window.open(CLOUD_RENEW_URL, "_blank");
// // //     return;
// // //   }

// // //   if (mode === "reselect-path") {
// // //     const rf    = $("recoveryPathField");
// // //     const input = rf?.querySelector("input");
// // //     const path  = input?.value.trim() || SUGGESTED_DATA_DIR;
// // //     await runSetupWithDir(path);
// // //     return;
// // //   }

// // //   if (mode === "repair-models") {
// // //     showCard("loadingCard");
// // //     setProgress(30, "إصلاح الملفات الأساسية...");
// // //     try {
// // //       await apiPost("/api/recovery/repair-models");
// // //       setProgress(70, "التحقق النهائي...");
// // //       const verify = await apiGet("/api/setup/verify");
// // //       if (!verify || verify.status !== "ok") throw new Error("الإصلاح لم يكتمل.");
// // //       setProgress(100, "تم الإصلاح.");
// // //       showCard("readyCard");
// // //       setStepState(3);
// // //       showNote("localSetupMessage", "ok", "تم الإصلاح. جارٍ فتح التطبيق...");
// // //       setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 700);
// // //     } catch (err) {
// // //       showCard("recoveryCard");
// // //       showNote("localSetupMessage", "err", err.message || "فشل الإصلاح.");
// // //     }
// // //     return;
// // //   }

// // //   if (mode === "retry-setup") {
// // //     setStepState(1);
// // //     showCard("pickFolderCard");
// // //     return;
// // //   }
// // // }

// // // async function retryConnection() {
// // //   const btn = $("retryConnectBtn");
// // //   if (btn) btn.disabled = true;
// // //   showNote("localSetupMessage", "ok", "جارٍ إعادة الاتصال...");
// // //   await initializeStartup();
// // //   if (btn) btn.disabled = false;
// // // }

// // // async function renewSubscriptionDemo() {
// // //   try {
// // //     await apiPost("/api/subscription/renew-demo");
// // //     localStorage.setItem("basira_subscription_status", "active");
// // //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "active";
// // //     showNote("localSetupMessage", "ok", "تم تجديد الاشتراك. جارٍ إعادة التحقق...");
// // //     setTimeout(initializeStartup, 800);
// // //   } catch (err) {
// // //     showNote("localSetupMessage", "err", err.message || "تعذر تجديد الاشتراك.");
// // //   }
// // // }


// // // // ─── Boot ─────────────────────────────────────────────────────────────────────
// // // document.addEventListener("DOMContentLoaded", async () => {
// // //   // Folder picker card
// // //   $("browseFolderBtn")   ?.addEventListener("click", () => browseFolder("dataDirectoryInput"));
// // //   $("startSetupBtn")     ?.addEventListener("click", confirmFolderAndSetup);

// // //   // Recovery card
// // //   $("repairPrimaryBtn")  ?.addEventListener("click", runRecoveryAction);
// // //   $("browseRecoveryBtn") ?.addEventListener("click", () => browseFolder("recoveryDirInput"));

// // //   // Ready card
// // //   $("launchLocalBtn")    ?.addEventListener("click", () => window.open(LOCAL_APP_URL, "_blank"));

// // //   // Not-running card
// // //   $("retryConnectBtn")   ?.addEventListener("click", retryConnection);

// // //   // Subscription card
// // //   $("renewSubscriptionBtn")?.addEventListener("click", () => window.open(CLOUD_RENEW_URL, "_blank"));
// // //   $("renewDemoBtn")        ?.addEventListener("click", renewSubscriptionDemo);

// // //   bindActivityTracking();
// // //   await initializeStartup();
// // // });
// // /**
// //  * local-setup.js  —  Basira On-Premise Setup
// //  * ===========================================
// //  * Talks to the local bootstrap at http://127.0.0.1:5001
// //  * Opens the main app at http://127.0.0.1:5000 when ready.
// //  *
// //  * FIRST-TIME FLOW:
// //  *   launcher.py running → new_user state detected
// //  *   → show folder picker
// //  *   → user picks a folder (e.g. D:\BasiraData)
// //  *   → create directory tree in that folder
// //  *   → download model files from GitHub via Cloudflare Worker
// //  *   → finalize → open 127.0.0.1:5000 → basira_app.html → analysis UI
// //  *
// //  * RETURNING USER:
// //  *   → state = healthy → open 127.0.0.1:5000 directly
// //  */

// // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// // const LOCAL_APP_URL       = "http://127.0.0.1:5000";
// // const CLOUD_RENEW_URL     = "https://basira.basira-toolmodel.workers.dev/renew";

// // const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

// // let startupState    = null;
// // let inactivityTimer = null;


// // // ─── DOM helpers ─────────────────────────────────────────────────────────────
// // function $(id) { return document.getElementById(id); }

// // function showNote(id, type, msg) {
// //   const el = $(id);
// //   if (!el) return;
// //   el.innerHTML  = msg || "";
// //   el.className  = "note " + (type === "ok" ? "isOk" : "isErr");
// // }

// // const ALL_CARDS = ["startupStatusCard","notRunningCard","newUserCard",
// //                    "loadingCard","recoveryCard","subscriptionCard","readyCard"];

// // function showCard(id) {
// //   ALL_CARDS.forEach(cid => { const el=$(cid); if(el) el.classList.add("isHidden"); });
// //   const t = $(id); if (t) t.classList.remove("isHidden");
// // }

// // function setStepState(idx) {
// //   document.querySelectorAll(".setup-step").forEach((s,i) => {
// //     s.classList.remove("isActive","isDone");
// //     if (i < idx) s.classList.add("isDone");
// //     if (i === idx) s.classList.add("isActive");
// //   });
// // }

// // function setProgress(pct, text) {
// //   const fill = $("progressFill");
// //   const lbl  = $("progressText");
// //   if (fill) fill.style.width = `${Math.min(100, pct)}%`;
// //   if (lbl)  lbl.textContent  = text || "";
// // }

// // function setLoadingDetail(text) {
// //   const el = $("loadingDetail");
// //   if (el) el.textContent = text;
// // }

// // function showDataDirInSidebar(dir) {
// //   const box = $("dataDirBox");
// //   const lbl = $("dataDirLabel");
// //   if (box) box.style.display = "block";
// //   if (lbl) lbl.textContent   = dir;
// // }


// // // ─── API helpers ─────────────────────────────────────────────────────────────
// // async function apiGet(path, timeoutMs = 10000) {
// //   const ctrl = new AbortController();
// //   const t = setTimeout(() => ctrl.abort(), timeoutMs);
// //   try {
// //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`,
// //       { method:"GET", headers:{"Content-Type":"application/json"}, signal:ctrl.signal });
// //     clearTimeout(t); return r.json();
// //   } catch(e) { clearTimeout(t); throw e; }
// // }

// // async function apiPost(path, payload = {}, timeoutMs = 120000) {
// //   // 120s default: downloads can take time
// //   const ctrl = new AbortController();
// //   const t = setTimeout(() => ctrl.abort(), timeoutMs);
// //   try {
// //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
// //       method:"POST", headers:{"Content-Type":"application/json"},
// //       body: JSON.stringify(payload), signal: ctrl.signal,
// //     });
// //     clearTimeout(t); return r.json();
// //   } catch(e) { clearTimeout(t); throw e; }
// // }

// // async function isBootstrapReachable() {
// //   try {
// //     const ctrl = new AbortController();
// //     setTimeout(() => ctrl.abort(), 3000);
// //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}/health`, { signal:ctrl.signal });
// //     return r.ok;
// //   } catch { return false; }
// // }


// // // ─── Supabase session ────────────────────────────────────────────────────────
// // function getStoredSession() {
// //   return {
// //     user_id:             localStorage.getItem("basira_user_id")             || "",
// //     access_token:        localStorage.getItem("basira_access_token")        || "",
// //     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
// //     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
// //     subscription_status: localStorage.getItem("basira_subscription_status") || "active",
// //   };
// // }

// // async function readCloudUser() {
// //   try {
// //     const { data:{ session } } = await supabaseClient.auth.getSession();
// //     if (!session?.user) {
// //       if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "لا توجد جلسة";
// //       if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
// //       return null;
// //     }
// //     const name = session.user.user_metadata?.full_name
// //                || session.user.email || session.user.id;
// //     if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = name;
// //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent =
// //       localStorage.getItem("basira_subscription_status") || "active";
// //     return session;
// //   } catch {
// //     if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "تعذر القراءة";
// //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
// //     return null;
// //   }
// // }

// // async function pushLocalSession() {
// //   const p = getStoredSession();
// //   if (!p.user_id || !p.access_token || !p.expires_at) return;
// //   try { await apiPost("/api/setup/login-complete", p, 10000); } catch {}
// // }

// // // After setup completes, also link session to the main app (port 5000)
// // async function linkSessionToMainApp(payload) {
// //   try {
// //     await fetch(`${LOCAL_APP_URL}/api/auth/session`, {
// //       method:"POST",
// //       headers:{"Content-Type":"application/json"},
// //       body: JSON.stringify(payload),
// //       mode: "cors",
// //     });
// //   } catch {}
// // }


// // // ─── Heartbeat & inactivity ───────────────────────────────────────────────────
// // async function sendHeartbeat() {
// //   try {
// //     const r = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`,
// //       { method:"POST", headers:{"Content-Type":"application/json"} });
// //     if (r.status === 401)
// //       setTimeout(() => { window.location.href = "./login.html"; }, 1500);
// //   } catch {}
// // }

// // async function autoLogoutNow() {
// //   try {
// //     await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`,
// //       { method:"POST", headers:{"Content-Type":"application/json"} });
// //   } catch {}
// //   setTimeout(() => { window.location.href = "./login.html"; }, 1500);
// // }

// // function resetInactivityTimer() {
// //   clearTimeout(inactivityTimer);
// //   inactivityTimer = setTimeout(autoLogoutNow, INACTIVITY_LIMIT_MS);
// // }

// // function bindActivityTracking() {
// //   ["click","mousemove","keydown","scroll","touchstart"]
// //     .forEach(ev => window.addEventListener(ev, resetInactivityTimer));
// //   resetInactivityTimer();
// //   setInterval(sendHeartbeat, 60_000);
// // }


// // // ─── Native folder picker ─────────────────────────────────────────────────────
// // async function browseForFolder(inputId) {
// //   try {
// //     const r = await apiGet("/api/system/pick-data-dir", 30000);
// //     if (r?.status === "ok" && r.path) {
// //       const el = $(inputId); if (el) el.value = r.path;
// //     } else {
// //       showNote("localSetupMessage","err","تعذر فتح نافذة اختيار المجلد.");
// //     }
// //   } catch {
// //     showNote("localSetupMessage","err","تعذر فتح نافذة اختيار المجلد.");
// //   }
// // }


// // // ─── FIRST-TIME SETUP FLOW ───────────────────────────────────────────────────
// // async function runSetupWithDir(dataDir) {
// //   showCard("loadingCard");
// //   setStepState(1);
// //   showNote("localSetupMessage","ok","");

// //   try {
// //     // 1. Init config in AppData
// //     setProgress(5,"تهيئة الإعدادات في AppData...");
// //     setLoadingDetail("إنشاء ملف الإعداد في AppData...");
// //     await apiPost("/api/setup/init", {}, 10000);

// //     // 2. Link cloud session to bootstrap
// //     setProgress(12,"ربط جلسة تسجيل الدخول...");
// //     setLoadingDetail("ربط حساب Supabase بالخادم المحلي...");
// //     await pushLocalSession();

// //     // 3. Create directory structure in chosen folder
// //     setProgress(20,`إنشاء المجلدات في: ${dataDir}`);
// //     setLoadingDetail(`إنشاء مجلدات البيانات في: ${dataDir}`);
// //     const dirResult = await apiPost("/api/setup/select-data-dir",
// //                                     { data_dir: dataDir }, 15000);
// //     if (!dirResult || dirResult.status !== "ok")
// //       throw new Error(dirResult?.message || "تعذر إنشاء مجلدات البيانات.");
// //     showDataDirInSidebar(dataDir);

// //     // 4. Download files from GitHub via Cloudflare
// //     setProgress(30,"جارٍ تنزيل الملفات من GitHub...");
// //     setLoadingDetail("يتم تنزيل نماذج بصيرة من GitHub — قد يستغرق هذا بضع دقائق...");
// //     showNote("localSetupMessage","ok",
// //       "جارٍ التنزيل من GitHub — يرجى عدم إغلاق هذه الصفحة.");

// //     const dlResult = await apiPost("/api/setup/download-files", {}, 180000); // 3 min timeout
// //     if (!dlResult || dlResult.status !== "ok")
// //       throw new Error(dlResult?.message || "تعذر تنزيل الملفات. تحققي من اتصال الإنترنت.");

// //     const downloaded = dlResult.downloaded || [];
// //     setProgress(75,`تم تنزيل: ${downloaded.join("، ")}`);

// //     if (dlResult.warnings?.length > 0) {
// //       console.warn("[setup] warnings:", dlResult.warnings);
// //     }

// //     // 5. Verify
// //     setProgress(85,"التحقق من اكتمال الملفات...");
// //     setLoadingDetail("التحقق من صحة الملفات المُنزَّلة...");
// //     const verify = await apiGet("/api/setup/verify", 15000);
// //     if (!verify || verify.status !== "ok")
// //       throw new Error("فشل التحقق من الملفات. قد تكون بعض الملفات ناقصة.");

// //     // 6. Finalize — saves chosen data_dir permanently
// //     setProgress(95,"حفظ الإعدادات...");
// //     setLoadingDetail("اعتماد وحفظ إعدادات البيئة المحلية...");
// //     const finalResult = await apiPost("/api/setup/finalize", {}, 10000);
// //     if (!finalResult || finalResult.status !== "ok")
// //       throw new Error("تعذر اعتماد الإعداد.");

// //     // 7. Link session to main app (port 5000) so basira_app.html works
// //     const sessionPayload = getStoredSession();
// //     await linkSessionToMainApp(sessionPayload);

// //     // Done!
// //     setProgress(100,"اكتمل الإعداد ✓");
// //     setStepState(3);
// //     showCard("readyCard");

// //     const readyDetail = $("readyDetail");
// //     if (readyDetail) readyDetail.textContent =
// //       `اكتمل الإعداد في: ${dataDir} — يمكنك الآن فتح بصيرة وبدء التحليل.`;

// //     showNote("localSetupMessage","ok","تم الإعداد بنجاح. جارٍ فتح بصيرة...");
// //     setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 900);

// //   } catch (err) {
// //     console.error("[setup] error:", err);
// //     showCard("recoveryCard");
// //     const rt = $("recoveryText");
// //     if (rt) rt.textContent = err.message || "فشل الإعداد. يرجى المحاولة مجدداً.";
// //     const rb = $("repairPrimaryBtn");
// //     if (rb) { rb.textContent = "إعادة المحاولة"; rb.dataset.mode = "retry-setup"; }
// //     showNote("localSetupMessage","err", err.message || "فشل الإعداد.");
// //   }
// // }

// // async function confirmFolderAndSetup() {
// //   const input   = $("dataDirectory");
// //   const dataDir = input?.value.trim() || "C:\\BasiraData";
// //   if (!dataDir) {
// //     showNote("localSetupMessage","err","يرجى اختيار مجلد أولاً.");
// //     return;
// //   }
// //   await runSetupWithDir(dataDir);
// // }


// // // ─── MAIN STATE MACHINE ───────────────────────────────────────────────────────
// // async function initializeStartup() {
// //   setStepState(0);
// //   showCard("startupStatusCard");
// //   showNote("localSetupMessage","ok","");
// //   await readCloudUser();

// //   // Check if launcher.py is running
// //   const alive = await isBootstrapReachable();
// //   if (!alive) {
// //     showCard("notRunningCard");
// //     showNote("localSetupMessage","err","الخادم المحلي غير مشغّل. شغّلي launcher.py أولاً.");
// //     return;
// //   }

// //   // Get state
// //   let state, reason;
// //   try {
// //     startupState = await apiGet("/api/startup-status", 10000);
// //     state  = startupState?.state  || "unknown";
// //     reason = startupState?.reason || "";
// //   } catch {
// //     showCard("notRunningCard");
// //     showNote("localSetupMessage","err","تعذر الاتصال بالخادم المحلي.");
// //     return;
// //   }

// //   switch (state) {

// //     // ── Returning user — healthy ──────────────────────────────────────────
// //     case "healthy":
// //     case "healthy_with_optional_update": {
// //       setStepState(3);
// //       // Re-link session to main app before opening it
// //       const sp = getStoredSession();
// //       await linkSessionToMainApp(sp);
// //       showCard("readyCard");
// //       if (state === "healthy_with_optional_update") {
// //         showNote("localSetupMessage","ok","البيئة جاهزة (يوجد تحديث اختياري). جارٍ فتح التطبيق...");
// //       } else {
// //         showNote("localSetupMessage","ok","البيئة جاهزة. جارٍ فتح التطبيق...");
// //       }
// //       setTimeout(() => { window.open(LOCAL_APP_URL, "_blank"); }, 600);
// //       break;
// //     }

// //     // ── First time or incomplete setup ────────────────────────────────────
// //     case "new_user":
// //     case "setup_incomplete":
// //       setStepState(1);
// //       showCard("newUserCard");
// //       showNote("localSetupMessage","ok","هذه أول مرة على هذا الجهاز. اختاري مجلد حفظ الملفات.");
// //       break;

// //     // ── Session expired — auto re-link ────────────────────────────────────
// //     case "login_required":
// //       await pushLocalSession();
// //       try {
// //         startupState = await apiGet("/api/startup-status", 10000);
// //         const newState = startupState?.state;
// //         if (newState === "healthy" || newState === "healthy_with_optional_update") {
// //           const sp = getStoredSession();
// //           await linkSessionToMainApp(sp);
// //           setStepState(3); showCard("readyCard");
// //           showNote("localSetupMessage","ok","تم تجديد الجلسة. جارٍ فتح التطبيق...");
// //           setTimeout(() => { window.open(LOCAL_APP_URL,"_blank"); }, 600);
// //         } else {
// //           setStepState(1); showCard("newUserCard");
// //           showNote("localSetupMessage","ok","اختاري مجلد حفظ الملفات.");
// //         }
// //       } catch {
// //         setStepState(1); showCard("newUserCard");
// //       }
// //       break;

// //     // ── Files missing — repair ────────────────────────────────────────────
// //     case "recovery_required": {
// //       showCard("recoveryCard"); setStepState(1);
// //       const rt = $("recoveryText");
// //       const rb = $("repairPrimaryBtn");
// //       const rf = $("recoveryPathField");
// //       if (reason === "data_dir_missing") {
// //         if (rt) rt.textContent = "مجلد البيانات غير موجود. اختاري مساراً جديداً ثم اضغطي إصلاح.";
// //         if (rf) rf.classList.remove("isHidden");
// //         if (rb) { rb.textContent = "اختيار مجلد وإعادة الإعداد"; rb.dataset.mode = "reselect-path"; }
// //       } else {
// //         if (rt) rt.textContent = reason === "models_not_installed"
// //           ? "ملفات النماذج غير مثبتة. سيتم إعادة تنزيلها."
// //           : "بعض الملفات ناقصة. سيتم إعادة تنزيلها من GitHub.";
// //         if (rf) rf.classList.add("isHidden");
// //         if (rb) { rb.textContent = "إعادة تنزيل الملفات"; rb.dataset.mode = "repair-files"; }
// //       }
// //       showNote("localSetupMessage","err","يلزم إصلاح البيئة المحلية.");
// //       break;
// //     }

// //     // ── Subscription required ─────────────────────────────────────────────
// //     case "subscription_required":
// //       showCard("subscriptionCard");
// //       showNote("localSetupMessage","err","الاشتراك غير فعال. يرجى التجديد.");
// //       break;

// //     // ── Mandatory update ──────────────────────────────────────────────────
// //     case "update_required": {
// //       showCard("recoveryCard");
// //       const rt2 = $("recoveryText"); const rb2 = $("repairPrimaryBtn");
// //       const rf2 = $("recoveryPathField");
// //       if (rt2) rt2.textContent = "هذه النسخة تحتاج تحديثاً إجبارياً قبل المتابعة.";
// //       if (rf2) rf2.classList.add("isHidden");
// //       if (rb2) { rb2.textContent = "فتح بوابة التحديث"; rb2.dataset.mode = "open-update"; }
// //       showNote("localSetupMessage","err","تحديث إجباري مطلوب.");
// //       break;
// //     }

// //     default:
// //       showNote("localSetupMessage","err","حالة غير معروفة: " + state);
// //   }
// // }


// // // ─── Recovery / repair actions ────────────────────────────────────────────────
// // async function runRecoveryAction() {
// //   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

// //   if (mode === "open-update") {
// //     window.open(CLOUD_RENEW_URL, "_blank"); return;
// //   }

// //   if (mode === "retry-setup" || mode === "reselect-path") {
// //     const dir = $("recoveryDataDirectory")?.value.trim() || "C:\\BasiraData";
// //     await runSetupWithDir(dir); return;
// //   }

// //   if (mode === "repair-files") {
// //     showCard("loadingCard");
// //     setProgress(10,"إعادة تنزيل الملفات من GitHub...");
// //     setLoadingDetail("جارٍ إعادة تنزيل الملفات الناقصة...");
// //     try {
// //       const r = await apiPost("/api/recovery/repair-files", {}, 180000);
// //       if (!r || r.status !== "ok")
// //         throw new Error(r?.errors?.join(", ") || "تعذر إعادة التنزيل.");
// //       setProgress(80,"التحقق...");
// //       const v = await apiGet("/api/setup/verify", 15000);
// //       if (!v || v.status !== "ok") throw new Error("التحقق فشل بعد الإصلاح.");
// //       setProgress(100,"تم الإصلاح.");
// //       const sp = getStoredSession();
// //       await linkSessionToMainApp(sp);
// //       setStepState(3); showCard("readyCard");
// //       showNote("localSetupMessage","ok","تم الإصلاح. جارٍ فتح التطبيق...");
// //       setTimeout(() => { window.open(LOCAL_APP_URL,"_blank"); }, 700);
// //     } catch(err) {
// //       showCard("recoveryCard");
// //       showNote("localSetupMessage","err", err.message || "فشل الإصلاح.");
// //     }
// //   }
// // }

// // async function retryConnection() {
// //   const btn = $("retryConnectBtn");
// //   if (btn) btn.disabled = true;
// //   showNote("localSetupMessage","ok","جارٍ إعادة الاتصال...");
// //   await initializeStartup();
// //   if (btn) btn.disabled = false;
// // }

// // async function renewSubscriptionDemo() {
// //   try {
// //     await apiPost("/api/subscription/renew-demo", {}, 10000);
// //     localStorage.setItem("basira_subscription_status","active");
// //     if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "active";
// //     showNote("localSetupMessage","ok","تم تجديد الاشتراك. جارٍ إعادة التحقق...");
// //     setTimeout(initializeStartup, 800);
// //   } catch(err) {
// //     showNote("localSetupMessage","err", err.message || "تعذر تجديد الاشتراك.");
// //   }
// // }


// // // ─── Boot ─────────────────────────────────────────────────────────────────────
// // document.addEventListener("DOMContentLoaded", async () => {
// //   // Folder picker card
// //   $("browseDataDirectoryBtn")?.addEventListener("click", () => browseForFolder("dataDirectory"));
// //   $("startSetupBtn")          ?.addEventListener("click", confirmFolderAndSetup);

// //   // Recovery card
// //   $("repairPrimaryBtn")        ?.addEventListener("click", runRecoveryAction);
// //   $("browseRecoveryDirectoryBtn")?.addEventListener("click", () => browseForFolder("recoveryDataDirectory"));

// //   // Ready card
// //   $("launchLocalBtn")          ?.addEventListener("click", () => window.open(LOCAL_APP_URL,"_blank"));
// //   $("renewSubscriptionBtnReady")?.addEventListener("click", () => window.open(CLOUD_RENEW_URL,"_blank"));

// //   // Not-running card
// //   $("retryConnectBtn")         ?.addEventListener("click", retryConnection);

// //   // Subscription card
// //   $("renewSubscriptionBtn")    ?.addEventListener("click", () => window.open(CLOUD_RENEW_URL,"_blank"));
// //   $("renewDemoBtn")            ?.addEventListener("click", renewSubscriptionDemo);

// //   bindActivityTracking();
// //   await initializeStartup();
// // });
// /**
//  * local-setup.js  —  Basira Customer Setup Page
//  * ===============================================
//  * This is what the customer sees after logging in.
//  *
//  * CUSTOMER FLOW:
//  *
//  *  [Not installed yet]
//  *    → Show download card with link to Install_Basira.zip
//  *    → Customer downloads, runs Install_Basira.bat (one double-click)
//  *    → Basira installs + registers in Windows startup
//  *    → Customer clicks "تم التثبيت — إعادة المحاولة"
//  *    → Page detects bootstrap is now running
//  *
//  *  [First time, installed but not configured]
//  *    → Show folder picker card
//  *    → Customer picks a folder (e.g. D:\MyWork\BasiraData)
//  *    → Clicks "بدء التنزيل والإعداد"
//  *    → Download animation plays while files download from GitHub
//  *    → Setup completes → browser opens 127.0.0.1:5000 → Basira analysis UI
//  *
//  *  [Returning customer]
//  *    → State = healthy → opens 127.0.0.1:5000 directly (< 1 second)
//  */

// const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// const LOCAL_BOOTSTRAP   = "http://127.0.0.1:5001";
// const LOCAL_APP         = "http://127.0.0.1:5000";
// const CLOUD_BASE        = "https://basira.basira-toolmodel.workers.dev";
// const CLOUD_RENEW_URL   = `${CLOUD_BASE}/renew`;

// const INACTIVITY_MS     = 20 * 60 * 1000;

// let startupState    = null;
// let inactivityTimer = null;
// let dlStartTime     = null;


// // ─── DOM ─────────────────────────────────────────────────────────────────────
// const $ = id => document.getElementById(id);

// const ALL_CARDS = ["checkingCard","notInstalledCard","pickFolderCard",
//                    "downloadingCard","recoveryCard","subscriptionCard","readyCard"];

// function showCard(id) {
//   ALL_CARDS.forEach(c => { const el=$(c); if(el) el.classList.add("isHidden"); });
//   const t = $(id); if(t) t.classList.remove("isHidden");
// }

// function setStep(idx) {
//   document.querySelectorAll(".setup-step").forEach((s,i) => {
//     s.classList.remove("isActive","isDone");
//     if(i < idx) s.classList.add("isDone");
//     if(i === idx) s.classList.add("isActive");
//   });
// }

// function setProgress(pct, text) {
//   const fill = $("progressFill");
//   const pctEl = $("progressPct");
//   const txtEl = $("progressText");
//   if(fill)  fill.style.width    = `${Math.min(100,pct)}%`;
//   if(pctEl) pctEl.textContent   = `${Math.round(pct)}%`;
//   if(txtEl) txtEl.textContent   = text || "";
// }

// function setDlStatus(text, speed = "") {
//   const s = $("dlStatus"); if(s) s.textContent = text;
//   const sp = $("dlSpeed"); if(sp) sp.textContent = speed;
// }

// function showNote(type, msg) {
//   const el = $("setupNote");
//   if(!el) return;
//   el.innerHTML = msg || "";
//   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// }

// function showSavedFolder(dir) {
//   const box = $("savedFolderBox"); const lbl = $("savedFolderLabel");
//   if(box) box.style.display = "block";
//   if(lbl) lbl.textContent   = dir;
// }

// function showChosenFolder(dir) {
//   const el = $("chosenFolderDisplay");
//   if(!el) return;
//   el.classList.remove("isHidden");
//   el.textContent = dir; // ::before adds the 📁
// }


// // ─── API ─────────────────────────────────────────────────────────────────────
// async function apiGet(path, ms=10000) {
//   const c = new AbortController();
//   const t = setTimeout(()=>c.abort(), ms);
//   try {
//     const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`,
//       { method:"GET", headers:{"Content-Type":"application/json"}, signal:c.signal });
//     clearTimeout(t); return r.json();
//   } catch(e) { clearTimeout(t); throw e; }
// }

// async function apiPost(path, body={}, ms=180000) {
//   const c = new AbortController();
//   const t = setTimeout(()=>c.abort(), ms);
//   try {
//     const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`, {
//       method:"POST",
//       headers:{"Content-Type":"application/json"},
//       body: JSON.stringify(body),
//       signal: c.signal,
//     });
//     clearTimeout(t); return r.json();
//   } catch(e) { clearTimeout(t); throw e; }
// }

// async function isBootstrapReachable() {
//   try {
//     const c = new AbortController();
//     setTimeout(()=>c.abort(), 3000);
//     const r = await fetch(`${LOCAL_BOOTSTRAP}/health`, { signal:c.signal });
//     return r.ok;
//   } catch { return false; }
// }


// // ─── Session ─────────────────────────────────────────────────────────────────
// function getSession() {
//   return {
//     user_id:             localStorage.getItem("basira_user_id")             || "",
//     access_token:        localStorage.getItem("basira_access_token")        || "",
//     refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
//     expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
//     subscription_status: localStorage.getItem("basira_subscription_status") || "active",
//   };
// }

// async function readCloudUser() {
//   try {
//     const { data:{ session } } = await supabaseClient.auth.getSession();
//     if(!session?.user) {
//       if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "لا توجد جلسة";
//       if($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
//       return null;
//     }
//     const name = session.user.user_metadata?.full_name
//                || session.user.email || session.user.id;
//     if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = name;
//     if($("subscriptionLabel")) $("subscriptionLabel").textContent =
//       localStorage.getItem("basira_subscription_status") || "active";
//     return session;
//   } catch {
//     if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "تعذر القراءة";
//     if($("subscriptionLabel")) $("subscriptionLabel").textContent = "—";
//     return null;
//   }
// }

// async function pushSession() {
//   const p = getSession();
//   if(!p.user_id || !p.access_token || !p.expires_at) return;
//   try { await apiPost("/api/setup/login-complete", p, 10000); } catch {}
// }

// async function linkToMainApp() {
//   // Also link the session to the main Flask app (:5000) so basira_app.html works
//   const p = getSession();
//   try {
//     await fetch(`${LOCAL_APP}/api/auth/session`, {
//       method:"POST",
//       headers:{"Content-Type":"application/json"},
//       body: JSON.stringify(p),
//       mode:"cors",
//     });
//   } catch {}
// }


// // ─── Heartbeat ───────────────────────────────────────────────────────────────
// async function sendHeartbeat() {
//   try {
//     const r = await fetch(`${LOCAL_BOOTSTRAP}/api/auth/heartbeat`,
//       { method:"POST", headers:{"Content-Type":"application/json"} });
//     if(r.status === 401)
//       setTimeout(()=>{ window.location.href="./login.html"; }, 1500);
//   } catch {}
// }

// function resetInactivity() {
//   clearTimeout(inactivityTimer);
//   inactivityTimer = setTimeout(async () => {
//     try { await fetch(`${LOCAL_BOOTSTRAP}/api/auth/auto-logout`,
//       { method:"POST", headers:{"Content-Type":"application/json"} }); } catch {}
//     window.location.href = "./login.html";
//   }, INACTIVITY_MS);
// }

// function bindActivity() {
//   ["click","mousemove","keydown","scroll","touchstart"]
//     .forEach(ev=>window.addEventListener(ev, resetInactivity));
//   resetInactivity();
//   setInterval(sendHeartbeat, 60_000);
// }


// // ─── Folder picker ────────────────────────────────────────────────────────────
// async function browseFolder(inputId) {
//   try {
//     const r = await apiGet("/api/system/pick-data-dir", 30000);
//     if(r?.status==="ok" && r.path) {
//       const el=$(inputId); if(el) el.value=r.path;
//     }
//   } catch { showNote("err","تعذر فتح نافذة اختيار المجلد."); }
// }


// // ─── FIRST-TIME SETUP ────────────────────────────────────────────────────────
// async function runSetup(dataDir) {
//   showCard("downloadingCard");
//   setStep(2);
//   dlStartTime = Date.now();

//   const steps = [
//     { pct: 5,   status: "تهيئة الإعدادات...",
//       fn: ()=>apiPost("/api/setup/init",{},10000) },

//     { pct: 12,  status: "ربط جلسة تسجيل الدخول...",
//       fn: pushSession },

//     { pct: 22,  status: `إنشاء المجلدات في: ${dataDir}`,
//       fn: async ()=>{
//         const r = await apiPost("/api/setup/select-data-dir",{data_dir:dataDir},15000);
//         if(!r || r.status!=="ok") throw new Error(r?.message||"فشل إنشاء المجلدات.");
//         showChosenFolder(dataDir);
//         showSavedFolder(dataDir);
//         $("savedFolderBox").style.display = "block";
//       }
//     },

//     { pct: 35,  status: "جارٍ تنزيل الملفات من GitHub...",
//       speed: "جارٍ الاتصال بالخادم...",
//       fn: async ()=>{
//         // Animate speed counter while waiting for download
//         let elapsed = 0;
//         const speedInterval = setInterval(()=>{
//           elapsed += 0.5;
//           const kbps = Math.round(50 + Math.random()*150);
//           if($("dlSpeed")) $("dlSpeed").textContent = `${kbps} KB/s · ${elapsed.toFixed(0)}s`;
//         }, 500);

//         try {
//           const r = await apiPost("/api/setup/download-files",{},300000); // 5min
//           clearInterval(speedInterval);
//           if($("dlSpeed")) $("dlSpeed").textContent = "";
//           if(!r || r.status!=="ok")
//             throw new Error(r?.message||"تعذر تنزيل الملفات. تحققي من الاتصال.");
//         } catch(e) {
//           clearInterval(speedInterval);
//           if($("dlSpeed")) $("dlSpeed").textContent = "";
//           throw e;
//         }
//       }
//     },

//     { pct: 80,  status: "التحقق من اكتمال الملفات...",
//       fn: async ()=>{
//         const r = await apiGet("/api/setup/verify",15000);
//         if(!r || r.status!=="ok") throw new Error("فشل التحقق من الملفات.");
//       }
//     },

//     { pct: 93,  status: "حفظ الإعدادات نهائياً...",
//       fn: async ()=>{
//         const r = await apiPost("/api/setup/finalize",{},10000);
//         if(!r || r.status!=="ok") throw new Error("فشل اعتماد الإعداد.");
//       }
//     },

//     { pct: 98,  status: "ربط الجلسة بالتطبيق المحلي...",
//       fn: linkToMainApp },
//   ];

//   try {
//     for(const step of steps) {
//       setDlStatus(step.status, step.speed||"");
//       setProgress(step.pct, step.status);
//       await step.fn();
//     }

//     // Done!
//     setProgress(100, "اكتمل الإعداد ✓");
//     setDlStatus("اكتمل التنزيل والإعداد بنجاح ✓");
//     const elapsed = ((Date.now()-dlStartTime)/1000).toFixed(0);
//     if($("dlSpeed")) $("dlSpeed").textContent = `اكتمل خلال ${elapsed} ثانية`;

//     await new Promise(r=>setTimeout(r, 800));

//     // Show success card
//     setStep(3);
//     showCard("readyCard");
//     const readyFolder = $("readyFolderDisplay");
//     if(readyFolder) { readyFolder.classList.remove("isHidden"); readyFolder.textContent=dataDir; }
//     showNote("ok","✓ تم إعداد بصيرة بنجاح. جارٍ فتح التطبيق...");
//     setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 1000);

//   } catch(err) {
//     console.error("[setup]", err);
//     showCard("recoveryCard");
//     const rt=$("recoveryText");
//     if(rt) rt.textContent = err.message || "حدث خطأ أثناء الإعداد.";
//     const rb=$("repairBtn");
//     if(rb){ rb.textContent="إعادة المحاولة"; rb.dataset.mode="retry"; }
//     showNote("err", err.message||"فشل الإعداد. اضغطي إعادة المحاولة.");
//   }
// }

// async function startSetupFromCard() {
//   const dir = $("dataDirectory")?.value.trim() || "C:\\BasiraData";
//   await runSetup(dir);
// }


// // ─── STATE MACHINE ────────────────────────────────────────────────────────────
// async function initialize() {
//   setStep(0);
//   showCard("checkingCard");
//   showNote("ok","");
//   await readCloudUser();

//   // Is the local launcher running?
//   const alive = await isBootstrapReachable();
//   if(!alive) {
//     // Not installed / not running
//     showCard("notInstalledCard");
//     showNote("err","بصيرة غير مثبتة على هذا الجهاز. نزّلي برنامج التثبيت أولاً.");
//     return;
//   }

//   // Get setup state
//   let state, reason;
//   try {
//     startupState = await apiGet("/api/startup-status", 10000);
//     state  = startupState?.state  || "unknown";
//     reason = startupState?.reason || "";
//   } catch {
//     showCard("notInstalledCard");
//     showNote("err","تعذر الاتصال بالخادم المحلي.");
//     return;
//   }

//   switch(state) {

//     // Returning user — already set up ────────────────────────────────────
//     case "healthy":
//     case "healthy_with_optional_update": {
//       setStep(3);
//       await linkToMainApp();
//       // Get saved data_dir from config to show in sidebar
//       try {
//         const cfg = await apiGet("/api/config", 5000);
//         if(cfg?.data_dir) showSavedFolder(cfg.data_dir);
//       } catch {}
//       showCard("readyCard");
//       const sub = $("readySub");
//       if(sub) sub.textContent = "بصيرة جاهزة. جارٍ فتح التطبيق...";
//       showNote("ok","البيئة المحلية جاهزة. جارٍ فتح بصيرة...");
//       setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 600);
//       break;
//     }

//     // First time / incomplete ────────────────────────────────────────────
//     case "new_user":
//     case "setup_incomplete":
//       setStep(1);
//       showCard("pickFolderCard");
//       showNote("ok","هذه أول مرة على هذا الجهاز. اختاري مجلداً للبدء.");
//       break;

//     // Session expired — auto re-link ────────────────────────────────────
//     case "login_required":
//       await pushSession();
//       try {
//         startupState = await apiGet("/api/startup-status", 8000);
//         const ns = startupState?.state;
//         if(ns==="healthy"||ns==="healthy_with_optional_update") {
//           await linkToMainApp();
//           setStep(3); showCard("readyCard");
//           showNote("ok","تم تجديد الجلسة. جارٍ فتح بصيرة...");
//           setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 600);
//         } else {
//           setStep(1); showCard("pickFolderCard");
//         }
//       } catch { setStep(1); showCard("pickFolderCard"); }
//       break;

//     // Files missing ──────────────────────────────────────────────────────
//     case "recovery_required": {
//       showCard("recoveryCard"); setStep(1);
//       const rt=$("recoveryText"); const rb=$("repairBtn"); const rf=$("recoveryPathField");
//       if(reason==="data_dir_missing") {
//         if(rt) rt.textContent="مجلد البيانات غير موجود. اختاري مساراً جديداً.";
//         if(rf) rf.classList.remove("isHidden");
//         if(rb){ rb.textContent="اختيار مجلد جديد وإعادة التنزيل"; rb.dataset.mode="reselect"; }
//       } else {
//         if(rt) rt.textContent="بعض الملفات ناقصة. سيتم إعادة تنزيلها من GitHub.";
//         if(rf) rf.classList.add("isHidden");
//         if(rb){ rb.textContent="إعادة تنزيل الملفات"; rb.dataset.mode="repair-files"; }
//       }
//       showNote("err","يلزم إصلاح البيئة المحلية.");
//       break;
//     }

//     // Subscription ───────────────────────────────────────────────────────
//     case "subscription_required":
//       showCard("subscriptionCard");
//       showNote("err","الاشتراك غير فعال.");
//       break;

//     // Mandatory update ───────────────────────────────────────────────────
//     case "update_required": {
//       showCard("recoveryCard");
//       const rt2=$("recoveryText"); const rb2=$("repairBtn");
//       if(rt2) rt2.textContent="هذه النسخة تحتاج تحديثاً إجبارياً.";
//       if(rb2){ rb2.textContent="فتح بوابة التحديث"; rb2.dataset.mode="update"; }
//       break;
//     }

//     default:
//       showNote("err","حالة غير معروفة: "+state);
//   }
// }


// // ─── Recovery / repair ────────────────────────────────────────────────────────
// async function handleRepair() {
//   const mode = $("repairBtn")?.dataset.mode || "";

//   if(mode==="update") {
//     window.open(CLOUD_RENEW_URL,"_blank"); return;
//   }
//   if(mode==="retry" || mode==="reselect") {
//     const dir = $("recoveryDir")?.value.trim() || "C:\\BasiraData";
//     await runSetup(dir); return;
//   }
//   if(mode==="repair-files") {
//     showCard("downloadingCard"); setStep(2);
//     setDlStatus("إعادة تنزيل الملفات من GitHub...");
//     try {
//       const r = await apiPost("/api/recovery/repair-files",{},300000);
//       if(!r||r.status!=="ok") throw new Error(r?.errors?.join(", ")||"فشل الإصلاح.");
//       setProgress(80,"التحقق..."); setDlStatus("التحقق من الملفات...");
//       const v = await apiGet("/api/setup/verify",15000);
//       if(!v||v.status!=="ok") throw new Error("التحقق فشل بعد الإصلاح.");
//       setProgress(100,"تم الإصلاح ✓");
//       await linkToMainApp();
//       setStep(3); showCard("readyCard");
//       showNote("ok","تم الإصلاح. جارٍ فتح بصيرة...");
//       setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 700);
//     } catch(err) {
//       showCard("recoveryCard");
//       showNote("err", err.message||"فشل الإصلاح.");
//     }
//   }
// }

// async function retryConnect() {
//   const btn=$("retryConnectBtn");
//   if(btn) btn.disabled=true;
//   showNote("ok","جارٍ الاتصال...");
//   await initialize();
//   if(btn) btn.disabled=false;
// }

// async function renewDemo() {
//   try {
//     await apiPost("/api/subscription/renew-demo",{},10000);
//     localStorage.setItem("basira_subscription_status","active");
//     if($("subscriptionLabel")) $("subscriptionLabel").textContent="active";
//     showNote("ok","تم تجديد الاشتراك.");
//     setTimeout(initialize, 800);
//   } catch(err) { showNote("err",err.message||"تعذر التجديد."); }
// }


// // ─── Boot ─────────────────────────────────────────────────────────────────────
// document.addEventListener("DOMContentLoaded", async ()=>{
//   $("browseBtn")           ?.addEventListener("click",()=>browseFolder("dataDirectory"));
//   $("startSetupBtn")       ?.addEventListener("click", startSetupFromCard);
//   $("repairBtn")           ?.addEventListener("click", handleRepair);
//   $("browseRecoveryBtn")   ?.addEventListener("click",()=>browseFolder("recoveryDir"));
//   $("launchBtn")           ?.addEventListener("click",()=>window.open(LOCAL_APP,"_blank"));
//   $("retryConnectBtn")     ?.addEventListener("click", retryConnect);
//   $("renewSubBtn")         ?.addEventListener("click",()=>window.open(CLOUD_RENEW_URL,"_blank"));
//   $("renewSubBtnReady")    ?.addEventListener("click",()=>window.open(CLOUD_RENEW_URL,"_blank"));
//   $("renewDemoBtn")        ?.addEventListener("click", renewDemo);

//   bindActivity();
//   await initialize();
// });
/**
 * local-setup.js  —  Basira Customer Setup Page
 * ===============================================
 * This is what the customer sees after logging in.
 *
 * CUSTOMER FLOW:
 *
 *  [Not installed yet]
 *    → Show download card with link to Install_Basira.zip
 *    → Customer downloads, runs Install_Basira.bat (one double-click)
 *    → Basira installs + registers in Windows startup
 *    → Customer clicks "تم التثبيت — إعادة المحاولة"
 *    → Page detects bootstrap is now running
 *
 *  [First time, installed but not configured]
 *    → Show folder picker card
 *    → Customer picks a folder (e.g. D:\MyWork\BasiraData)
 *    → Clicks "بدء التنزيل والإعداد"
 *    → Download animation plays while files download from GitHub
 *    → Setup completes → browser opens 127.0.0.1:5000 → Basira analysis UI
 *
 *  [Returning customer]
 *    → State = healthy → opens 127.0.0.1:5000 directly (< 1 second)
 */

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const LOCAL_BOOTSTRAP   = "http://127.0.0.1:5001";
const LOCAL_APP         = "http://127.0.0.1:5000";
const CLOUD_BASE        = "https://basira.basira-toolmodel.workers.dev";
const CLOUD_RENEW_URL   = `${CLOUD_BASE}/renew`;

const INACTIVITY_MS     = 20 * 60 * 1000;

let startupState    = null;
let inactivityTimer = null;
let dlStartTime     = null;


// ─── DOM ─────────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const ALL_CARDS = ["checkingCard","notInstalledCard","pickFolderCard",
                   "downloadingCard","recoveryCard","subscriptionCard","readyCard"];

function showCard(id) {
  ALL_CARDS.forEach(c => { const el=$(c); if(el) el.classList.add("isHidden"); });
  const t = $(id); if(t) t.classList.remove("isHidden");
}

function setStep(idx) {
  document.querySelectorAll(".setup-step").forEach((s,i) => {
    s.classList.remove("isActive","isDone");
    if(i < idx) s.classList.add("isDone");
    if(i === idx) s.classList.add("isActive");
  });
}

function setProgress(pct, text) {
  const fill = $("progressFill");
  const pctEl = $("progressPct");
  const txtEl = $("progressText");
  if(fill)  fill.style.width    = `${Math.min(100,pct)}%`;
  if(pctEl) pctEl.textContent   = `${Math.round(pct)}%`;
  if(txtEl) txtEl.textContent   = text || "";
}

function setDlStatus(text, speed = "") {
  const s = $("dlStatus"); if(s) s.textContent = text;
  const sp = $("dlSpeed"); if(sp) sp.textContent = speed;
}

function showNote(type, msg) {
  const el = $("setupNote");
  if(!el) return;
  el.innerHTML = msg || "";
  el.className = "note " + (type === "ok" ? "isOk" : "isErr");
}

function showSavedFolder(dir) {
  const box = $("savedFolderBox"); const lbl = $("savedFolderLabel");
  if(box) box.style.display = "block";
  if(lbl) lbl.textContent   = dir;
}

function showChosenFolder(dir) {
  const el = $("chosenFolderDisplay");
  if(!el) return;
  el.classList.remove("isHidden");
  el.textContent = dir; // ::before adds the 📁
}


// ─── API ─────────────────────────────────────────────────────────────────────
async function apiGet(path, ms=10000) {
  const c = new AbortController();
  const t = setTimeout(()=>c.abort(), ms);
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`,
      { method:"GET", headers:{"Content-Type":"application/json"}, signal:c.signal });
    clearTimeout(t); return r.json();
  } catch(e) { clearTimeout(t); throw e; }
}

async function apiPost(path, body={}, ms=180000) {
  const c = new AbortController();
  const t = setTimeout(()=>c.abort(), ms);
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(body),
      signal: c.signal,
    });
    clearTimeout(t); return r.json();
  } catch(e) { clearTimeout(t); throw e; }
}

async function isBootstrapReachable() {
  try {
    const c = new AbortController();
    setTimeout(()=>c.abort(), 3000);
    const r = await fetch(`${LOCAL_BOOTSTRAP}/health`, { signal:c.signal });
    return r.ok;
  } catch { return false; }
}


// ─── Session ─────────────────────────────────────────────────────────────────
function getSession() {
  return {
    user_id:             localStorage.getItem("basira_user_id")             || "",
    access_token:        localStorage.getItem("basira_access_token")        || "",
    refresh_token:       localStorage.getItem("basira_refresh_token")       || "",
    expires_at:          localStorage.getItem("basira_session_expires_at")  || "",
    subscription_status: localStorage.getItem("basira_subscription_status") || "active",
  };
}

async function readCloudUser() {
  try {
    const { data:{ session } } = await supabaseClient.auth.getSession();
    if(!session?.user) {
      if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "لا توجد جلسة";
      if($("subscriptionLabel")) $("subscriptionLabel").textContent = "غير معروف";
      return null;
    }
    const name = session.user.user_metadata?.full_name
               || session.user.email || session.user.id;
    if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = name;
    if($("subscriptionLabel")) $("subscriptionLabel").textContent =
      localStorage.getItem("basira_subscription_status") || "active";
    return session;
  } catch {
    if($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "تعذر القراءة";
    if($("subscriptionLabel")) $("subscriptionLabel").textContent = "—";
    return null;
  }
}

async function pushSession() {
  const p = getSession();
  if(!p.user_id || !p.access_token || !p.expires_at) return;
  try { await apiPost("/api/setup/login-complete", p, 10000); } catch {}
}

async function linkToMainApp() {
  // Also link the session to the main Flask app (:5000) so basira_app.html works
  const p = getSession();
  try {
    await fetch(`${LOCAL_APP}/api/auth/session`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(p),
      mode:"cors",
    });
  } catch {}
}


// ─── Heartbeat ───────────────────────────────────────────────────────────────
async function sendHeartbeat() {
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}/api/auth/heartbeat`,
      { method:"POST", headers:{"Content-Type":"application/json"} });
    if(r.status === 401)
      setTimeout(()=>{ window.location.href="./login.html"; }, 1500);
  } catch {}
}

function resetInactivity() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(async () => {
    try { await fetch(`${LOCAL_BOOTSTRAP}/api/auth/auto-logout`,
      { method:"POST", headers:{"Content-Type":"application/json"} }); } catch {}
    window.location.href = "./login.html";
  }, INACTIVITY_MS);
}

function bindActivity() {
  ["click","mousemove","keydown","scroll","touchstart"]
    .forEach(ev=>window.addEventListener(ev, resetInactivity));
  resetInactivity();
  setInterval(sendHeartbeat, 60_000);
}


// ─── Folder picker ────────────────────────────────────────────────────────────
async function browseFolder(inputId) {
  try {
    const r = await apiGet("/api/system/pick-data-dir", 30000);
    if(r?.status==="ok" && r.path) {
      const el=$(inputId); if(el) el.value=r.path;
    }
  } catch { showNote("err","تعذر فتح نافذة اختيار المجلد."); }
}


// ─── FIRST-TIME SETUP ────────────────────────────────────────────────────────
async function runSetup(dataDir) {
  showCard("downloadingCard");
  setStep(2);
  dlStartTime = Date.now();

  const steps = [
    { pct: 5,   status: "تهيئة الإعدادات...",
      fn: ()=>apiPost("/api/setup/init",{},10000) },

    { pct: 12,  status: "ربط جلسة تسجيل الدخول...",
      fn: pushSession },

    { pct: 22,  status: `إنشاء المجلدات في: ${dataDir}`,
      fn: async ()=>{
        const r = await apiPost("/api/setup/select-data-dir",{data_dir:dataDir},15000);
        if(!r || r.status!=="ok") throw new Error(r?.message||"فشل إنشاء المجلدات.");
        showChosenFolder(dataDir);
        showSavedFolder(dataDir);
        $("savedFolderBox").style.display = "block";
      }
    },

    { pct: 35,  status: "جارٍ تنزيل الملفات من GitHub...",
      speed: "جارٍ الاتصال بالخادم...",
      fn: async ()=>{
        // Animate speed counter while waiting for download
        let elapsed = 0;
        const speedInterval = setInterval(()=>{
          elapsed += 0.5;
          const kbps = Math.round(50 + Math.random()*150);
          if($("dlSpeed")) $("dlSpeed").textContent = `${kbps} KB/s · ${elapsed.toFixed(0)}s`;
        }, 500);

        try {
          const r = await apiPost("/api/setup/download-files",{},300000); // 5min
          clearInterval(speedInterval);
          if($("dlSpeed")) $("dlSpeed").textContent = "";
          if(!r || r.status!=="ok")
            throw new Error(r?.message||"تعذر تنزيل الملفات. تحققي من الاتصال.");
        } catch(e) {
          clearInterval(speedInterval);
          if($("dlSpeed")) $("dlSpeed").textContent = "";
          throw e;
        }
      }
    },

    { pct: 80,  status: "التحقق من اكتمال الملفات...",
      fn: async ()=>{
        const r = await apiGet("/api/setup/verify",15000);
        if(!r || r.status!=="ok") throw new Error("فشل التحقق من الملفات.");
      }
    },

    { pct: 93,  status: "حفظ الإعدادات نهائياً...",
      fn: async ()=>{
        const r = await apiPost("/api/setup/finalize",{},10000);
        if(!r || r.status!=="ok") throw new Error("فشل اعتماد الإعداد.");
      }
    },

    { pct: 98,  status: "ربط الجلسة بالتطبيق المحلي...",
      fn: linkToMainApp },
  ];

  try {
    for(const step of steps) {
      setDlStatus(step.status, step.speed||"");
      setProgress(step.pct, step.status);
      await step.fn();
    }

    // Done!
    setProgress(100, "اكتمل الإعداد ✓");
    setDlStatus("اكتمل التنزيل والإعداد بنجاح ✓");
    const elapsed = ((Date.now()-dlStartTime)/1000).toFixed(0);
    if($("dlSpeed")) $("dlSpeed").textContent = `اكتمل خلال ${elapsed} ثانية`;

    await new Promise(r=>setTimeout(r, 800));

    // Show success card
    setStep(3);
    showCard("readyCard");
    const readyFolder = $("readyFolderDisplay");
    if(readyFolder) { readyFolder.classList.remove("isHidden"); readyFolder.textContent=dataDir; }
    showNote("ok","✓ تم إعداد بصيرة بنجاح. جارٍ فتح التطبيق...");
    setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 1000);

  } catch(err) {
    console.error("[setup]", err);
    showCard("recoveryCard");
    const rt=$("recoveryText");
    if(rt) rt.textContent = err.message || "حدث خطأ أثناء الإعداد.";
    const rb=$("repairBtn");
    if(rb){ rb.textContent="إعادة المحاولة"; rb.dataset.mode="retry"; }
    showNote("err", err.message||"فشل الإعداد. اضغطي إعادة المحاولة.");
  }
}

async function startSetupFromCard() {
  const dir = $("dataDirectory")?.value.trim() || "C:\\BasiraData";
  await runSetup(dir);
}


// ─── STATE MACHINE ────────────────────────────────────────────────────────────
async function initialize() {
  setStep(0);
  showCard("checkingCard");
  showNote("ok","");
  await readCloudUser();

  // Is the local launcher running?
  const alive = await isBootstrapReachable();
  if(!alive) {
    // Not installed / not running
    showCard("notInstalledCard");
    showNote("err","بصيرة غير مثبتة على هذا الجهاز. نزّلي برنامج التثبيت أولاً.");
    return;
  }

  // Get setup state
  let state, reason;
  try {
    startupState = await apiGet("/api/startup-status", 10000);
    state  = startupState?.state  || "unknown";
    reason = startupState?.reason || "";
  } catch {
    showCard("notInstalledCard");
    showNote("err","تعذر الاتصال بالخادم المحلي.");
    return;
  }

  switch(state) {

    // Returning user — already set up ────────────────────────────────────
    case "healthy":
    case "healthy_with_optional_update": {
      setStep(3);
      await linkToMainApp();
      // Get saved data_dir from config to show in sidebar
      try {
        const cfg = await apiGet("/api/config", 5000);
        if(cfg?.data_dir) showSavedFolder(cfg.data_dir);
      } catch {}
      showCard("readyCard");
      const sub = $("readySub");
      if(sub) sub.textContent = "بصيرة جاهزة. جارٍ فتح التطبيق...";
      showNote("ok","البيئة المحلية جاهزة. جارٍ فتح بصيرة...");
      setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 600);
      break;
    }

    // First time / incomplete ────────────────────────────────────────────
    case "new_user":
    case "setup_incomplete":
      setStep(1);
      showCard("pickFolderCard");
      showNote("ok","هذه أول مرة على هذا الجهاز. اختاري مجلداً للبدء.");
      break;

    // Session expired — auto re-link ────────────────────────────────────
    case "login_required":
      await pushSession();
      try {
        startupState = await apiGet("/api/startup-status", 8000);
        const ns = startupState?.state;
        if(ns==="healthy"||ns==="healthy_with_optional_update") {
          await linkToMainApp();
          setStep(3); showCard("readyCard");
          showNote("ok","تم تجديد الجلسة. جارٍ فتح بصيرة...");
          setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 600);
        } else {
          setStep(1); showCard("pickFolderCard");
        }
      } catch { setStep(1); showCard("pickFolderCard"); }
      break;

    // Files missing ──────────────────────────────────────────────────────
    case "recovery_required": {
      showCard("recoveryCard"); setStep(1);
      const rt=$("recoveryText"); const rb=$("repairBtn"); const rf=$("recoveryPathField");
      if(reason==="data_dir_missing") {
        if(rt) rt.textContent="مجلد البيانات غير موجود. اختاري مساراً جديداً.";
        if(rf) rf.classList.remove("isHidden");
        if(rb){ rb.textContent="اختيار مجلد جديد وإعادة التنزيل"; rb.dataset.mode="reselect"; }
      } else {
        if(rt) rt.textContent="بعض الملفات ناقصة. سيتم إعادة تنزيلها من GitHub.";
        if(rf) rf.classList.add("isHidden");
        if(rb){ rb.textContent="إعادة تنزيل الملفات"; rb.dataset.mode="repair-files"; }
      }
      showNote("err","يلزم إصلاح البيئة المحلية.");
      break;
    }

    // Subscription ───────────────────────────────────────────────────────
    case "subscription_required":
      showCard("subscriptionCard");
      showNote("err","الاشتراك غير فعال.");
      break;

    // Mandatory update ───────────────────────────────────────────────────
    case "update_required": {
      showCard("recoveryCard");
      const rt2=$("recoveryText"); const rb2=$("repairBtn");
      if(rt2) rt2.textContent="هذه النسخة تحتاج تحديثاً إجبارياً.";
      if(rb2){ rb2.textContent="فتح بوابة التحديث"; rb2.dataset.mode="update"; }
      break;
    }

    default:
      showNote("err","حالة غير معروفة: "+state);
  }
}


// ─── Recovery / repair ────────────────────────────────────────────────────────
async function handleRepair() {
  const mode = $("repairBtn")?.dataset.mode || "";

  if(mode==="update") {
    window.open(CLOUD_RENEW_URL,"_blank"); return;
  }
  if(mode==="retry" || mode==="reselect") {
    const dir = $("recoveryDir")?.value.trim() || "C:\\BasiraData";
    await runSetup(dir); return;
  }
  if(mode==="repair-files") {
    showCard("downloadingCard"); setStep(2);
    setDlStatus("إعادة تنزيل الملفات من GitHub...");
    try {
      const r = await apiPost("/api/recovery/repair-files",{},300000);
      if(!r||r.status!=="ok") throw new Error(r?.errors?.join(", ")||"فشل الإصلاح.");
      setProgress(80,"التحقق..."); setDlStatus("التحقق من الملفات...");
      const v = await apiGet("/api/setup/verify",15000);
      if(!v||v.status!=="ok") throw new Error("التحقق فشل بعد الإصلاح.");
      setProgress(100,"تم الإصلاح ✓");
      await linkToMainApp();
      setStep(3); showCard("readyCard");
      showNote("ok","تم الإصلاح. جارٍ فتح بصيرة...");
      setTimeout(()=>{ window.open(LOCAL_APP,"_blank"); }, 700);
    } catch(err) {
      showCard("recoveryCard");
      showNote("err", err.message||"فشل الإصلاح.");
    }
  }
}

async function retryConnect() {
  const btn=$("retryConnectBtn");
  if(btn) btn.disabled=true;
  showNote("ok","جارٍ الاتصال...");
  await initialize();
  if(btn) btn.disabled=false;
}

async function renewDemo() {
  try {
    await apiPost("/api/subscription/renew-demo",{},10000);
    localStorage.setItem("basira_subscription_status","active");
    if($("subscriptionLabel")) $("subscriptionLabel").textContent="active";
    showNote("ok","تم تجديد الاشتراك.");
    setTimeout(initialize, 800);
  } catch(err) { showNote("err",err.message||"تعذر التجديد."); }
}


// ─── Boot ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async ()=>{
  $("browseBtn")           ?.addEventListener("click",()=>browseFolder("dataDirectory"));
  $("startSetupBtn")       ?.addEventListener("click", startSetupFromCard);
  $("repairBtn")           ?.addEventListener("click", handleRepair);
  $("browseRecoveryBtn")   ?.addEventListener("click",()=>browseFolder("recoveryDir"));
  $("launchBtn")           ?.addEventListener("click",()=>window.open(LOCAL_APP,"_blank"));
  $("retryConnectBtn")     ?.addEventListener("click", retryConnect);
  $("renewSubBtn")         ?.addEventListener("click",()=>window.open(CLOUD_RENEW_URL,"_blank"));
  $("renewSubBtnReady")    ?.addEventListener("click",()=>window.open(CLOUD_RENEW_URL,"_blank"));
  $("renewDemoBtn")        ?.addEventListener("click", renewDemo);

  bindActivity();
  await initialize();
});
