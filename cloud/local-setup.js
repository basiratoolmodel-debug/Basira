// const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
// const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
// const LOCAL_STREAMLIT_URL = "http://127.0.0.1:8501";
// const LOCAL_RUNTIME_DOWNLOADS = {
//   windows: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-win-x64.zip",
//   mac: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-macos.zip"
// };

// let startupState = null;

// function showNote(id, type, message) {
//   const el = document.getElementById(id);
//   if (!el) return;
//   el.innerHTML = message;
//   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// }

// function $(id) {
//   return document.getElementById(id);
// }

// function showCard(id) {
//   ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
//     const el = $(cardId);
//     if (el) el.classList.add("isHidden");
//   });

//   const target = $(id);
//   if (target) target.classList.remove("isHidden");
// }

// function setStepState(activeIndex) {
//   const steps = Array.from(document.querySelectorAll(".setup-step"));
//   steps.forEach((step, index) => {
//     step.classList.remove("isActive", "isDone");
//     if (index < activeIndex) step.classList.add("isDone");
//     if (index === activeIndex) step.classList.add("isActive");
//   });
// }

// function setProgress(percent, text) {
//   const fill = $("progressFill");
//   const label = $("progressText");
//   if (fill) fill.style.width = `${percent}%`;
//   if (label) label.textContent = text;
// }

// function getStoredSessionPayload() {
//   return {
//     user_id: localStorage.getItem("basira_user_id") || "",
//     access_token: localStorage.getItem("basira_access_token") || "",
//     refresh_token: localStorage.getItem("basira_refresh_token") || "",
//     expires_at: localStorage.getItem("basira_session_expires_at") || "",
//     subscription_status: localStorage.getItem("basira_subscription_status") || "active"
//   };
// }

// function detectPlatform() {
//   const ua = navigator.userAgent.toLowerCase();
//   if (ua.includes("mac")) return "mac";
//   return "windows";
// }

// async function apiGet(path) {
//   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`);
//   return response.json();
// }

// async function apiPost(path, payload = {}) {
//   const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json"
//     },
//     body: JSON.stringify(payload)
//   });

//   return response.json();
// }

// async function readCloudUser() {
//   try {
//     const {
//       data: { session }
//     } = await supabaseClient.auth.getSession();

//     if (!session?.user) {
//       $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
//       $("subscriptionLabel").textContent = "غير معروف";
//       return null;
//     }

//     const userName =
//       session.user.user_metadata?.full_name ||
//       session.user.email ||
//       session.user.id;

//     $("cloudUserLabel").textContent = userName;
//     $("subscriptionLabel").textContent =
//       localStorage.getItem("basira_subscription_status") || "غير معروف";

//     return session;
//   } catch (err) {
//     $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
//     $("subscriptionLabel").textContent = "غير معروف";
//     return null;
//   }
// }

// async function pushLocalSession() {
//   const payload = getStoredSessionPayload();

//   if (!payload.user_id || !payload.access_token || !payload.expires_at) {
//     throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
//   }

//   await apiPost("/api/setup/login-complete", payload);
// }

// async function initializeStartup() {
//   setStepState(0);

//   try {
//     await readCloudUser();

//     $("startupStatusCard").querySelector(".local-card__title").textContent = "جارٍ التحقق من البيئة المحلية";
//     $("startupStatusCard").querySelector(".local-card__text").textContent =
//       "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";

//     startupState = await apiGet("/api/startup-status");

//     if (!startupState || !startupState.state) {
//       throw new Error("تعذر قراءة حالة التشغيل المحلي.");
//     }

//     if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
//       showCard("newUserCard");
//       setStepState(1);
//       showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
//       return;
//     }

//     if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
//       showCard("readyCard");
//       setStepState(3);
//       showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
//       return;
//     }

//     if (startupState.state === "login_required") {
//       showNote(
//         "localSetupMessage",
//         "err",
//         "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
//       );

//       await pushLocalSession();

//       startupState = await apiGet("/api/startup-status");

//       if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
//         showCard("readyCard");
//         setStepState(3);
//         showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
//       } else {
//         showCard("newUserCard");
//         setStepState(1);
//       }

//       return;
//     }

//     if (startupState.state === "recovery_required") {
//       const reason = startupState.reason || "unknown";
//       showCard("recoveryCard");
//       setStepState(1);

//       const recoveryText = $("recoveryText");
//       const recoveryPathField = $("recoveryPathField");
//       const repairPrimaryBtn = $("repairPrimaryBtn");

//       if (reason === "missing_data_dir" || reason === "data_dir_not_found" || reason === "data_dir_not_writable") {
//         recoveryText.textContent =
//           "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
//         recoveryPathField.classList.remove("isHidden");
//         repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
//         repairPrimaryBtn.dataset.mode = "reselect-path";
//       } else if (reason === "missing_model") {
//         recoveryText.textContent =
//           "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
//         recoveryPathField.classList.add("isHidden");
//         repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
//         repairPrimaryBtn.dataset.mode = "repair-models";
//       } else {
//         recoveryText.textContent =
//           "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
//         recoveryPathField.classList.add("isHidden");
//         repairPrimaryBtn.textContent = "إصلاح الآن";
//         repairPrimaryBtn.dataset.mode = "repair-models";
//       }

//       showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
//       return;
//     }

//     if (startupState.state === "update_required") {
//       showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.");
//       showCard("recoveryCard");
//       $("recoveryText").textContent = "يلزم تحديث النسخة المحلية قبل المتابعة.";
//       $("repairPrimaryBtn").textContent = "فتح بوابة التحديث";
//       $("repairPrimaryBtn").dataset.mode = "open-update";
//       return;
//     }

//     throw new Error("حالة تشغيل غير معروفة.");
//   } catch (err) {
//     showNote("localSetupMessage", "err", err.message || "تعذر بدء صفحة التهيئة المحلية.");
//   }
// }

// async function runFirstSetup() {
//   try {
//     const session = await readCloudUser();
//     if (!session?.user) {
//       throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
//     }

//     setStepState(2);
//     showCard("loadingCard");

//     setProgress(10, "تهيئة الحالة المحلية...");
//     await apiPost("/api/setup/init");
//     await pushLocalSession();

//     const dataDir = $("dataDirectory")?.value.trim() || "C:\\BasiraData";

//     setProgress(30, "إنشاء المجلدات المحلية...");
//     await apiPost("/api/setup/select-data-dir", {
//       data_dir: dataDir
//     });

//     const platform = detectPlatform();
//     const runtimeUrl = LOCAL_RUNTIME_DOWNLOADS[platform];

//     setProgress(55, "تنزيل الملفات الأساسية المحلية...");
//     await apiPost("/api/setup/install-models", {
//       runtime_url: runtimeUrl,
//       platform
//     });

//     setProgress(80, "التحقق من الجاهزية...");
//     const verifyResult = await apiGet("/api/setup/verify");

//     if (!verifyResult || verifyResult.status !== "ok") {
//       throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
//     }

//     setProgress(95, "اعتماد التهيئة النهائية...");
//     await apiPost("/api/setup/finalize");

//     setProgress(100, "اكتملت التهيئة بنجاح.");
//     setStepState(3);

//     showCard("readyCard");
//     showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
//   } catch (err) {
//     showCard("recoveryCard");
//     showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
//   }
// }

// async function runRecoveryAction() {
//   const mode = $("repairPrimaryBtn")?.dataset.mode || "";

//   try {
//     if (mode === "reselect-path") {
//       const pathValue = $("recoveryDataDirectory")?.value.trim() || "C:\\BasiraData";
//       showCard("loadingCard");
//       setProgress(30, "تحديث مسار البيانات...");
//       await apiPost("/api/recovery/reselect-data-dir", {
//         data_dir: pathValue
//       });

//       setProgress(70, "التحقق من البيئة...");
//       const verifyResult = await apiGet("/api/setup/verify");

//       if (!verifyResult || verifyResult.status !== "ok") {
//         throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
//       }

//       setProgress(100, "تم إصلاح مسار البيانات.");
//       showCard("readyCard");
//       setStepState(3);
//       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
//       return;
//     }

//     if (mode === "repair-models") {
//       showCard("loadingCard");
//       setProgress(35, "إعادة تنزيل الملفات الأساسية...");
//       await apiPost("/api/recovery/repair-models");

//       setProgress(75, "التحقق النهائي...");
//       const verifyResult = await apiGet("/api/setup/verify");

//       if (!verifyResult || verifyResult.status !== "ok") {
//         throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
//       }

//       setProgress(100, "تم إصلاح الملفات الأساسية.");
//       showCard("readyCard");
//       setStepState(3);
//       showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
//       return;
//     }

//     if (mode === "open-update") {
//       window.open("https://basira.basira-toolmodel.workers.dev", "_blank");
//       return;
//     }
//   } catch (err) {
//     showCard("recoveryCard");
//     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
//   }
// }

// function launchLocalEnvironment() {
//   window.open(LOCAL_STREAMLIT_URL, "_blank");
//   showNote("localSetupMessage", "ok", "تم إرسال أمر تشغيل الواجهة المحلية. إذا لم تعمل بعد، تحققي من خدمة التشغيل المحلي.");
// }

// async function renewSubscriptionDemo() {
//   try {
//     const userId = localStorage.getItem("basira_user_id");
//     if (!userId) {
//       throw new Error("لم يتم العثور على مستخدم محلي مربوط بالجلسة.");
//     }

//     await apiPost("/api/subscription/renew-demo", {
//       user_id: userId
//     });

//     localStorage.setItem("basira_subscription_status", "active");
//     $("subscriptionLabel").textContent = "active";

//     showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
//   } catch (err) {
//     showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
//   }
// }

// document.addEventListener("DOMContentLoaded", async () => {
//   $("startSetupBtn")?.addEventListener("click", runFirstSetup);
//   $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
//   $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

//   $("renewSubscriptionBtn")?.addEventListener("click", () => {
//     const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
//     if (useCloud) {
//       window.open(CLOUD_RENEW_URL, "_blank");
//     } else {
//       renewSubscriptionDemo();
//     }
//   });

//   await initializeStartup();
// });



const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const LOCAL_BOOTSTRAP_URL = "http://127.0.0.1:5001";
const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
const LOCAL_STREAMLIT_URL = "http://127.0.0.1:8501";
const LOCAL_RUNTIME_DOWNLOADS = {
  windows: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-win-x64.zip",
  mac: "https://basira.basira-toolmodel.workers.dev/downloads/basira-local-runtime-macos.zip"
};

let startupState = null;
let inactivityTimer = null;
const INACTIVITY_LIMIT_MS = 20 * 60 * 1000;

function showNote(id, type, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = message;
  el.className = "note " + (type === "ok" ? "isOk" : "isErr");
}

function $(id) {
  return document.getElementById(id);
}

function showCard(id) {
  ["newUserCard", "loadingCard", "recoveryCard", "readyCard"].forEach(cardId => {
    const el = $(cardId);
    if (el) el.classList.add("isHidden");
  });

  const target = $(id);
  if (target) target.classList.remove("isHidden");
}

function setStepState(activeIndex) {
  const steps = Array.from(document.querySelectorAll(".setup-step"));
  steps.forEach((step, index) => {
    step.classList.remove("isActive", "isDone");
    if (index < activeIndex) step.classList.add("isDone");
    if (index === activeIndex) step.classList.add("isActive");
  });
}

function setProgress(percent, text) {
  const fill = $("progressFill");
  const label = $("progressText");
  if (fill) fill.style.width = `${percent}%`;
  if (label) label.textContent = text;
}

function getStoredSessionPayload() {
  return {
    user_id: localStorage.getItem("basira_user_id") || "",
    access_token: localStorage.getItem("basira_access_token") || "",
    refresh_token: localStorage.getItem("basira_refresh_token") || "",
    expires_at: localStorage.getItem("basira_session_expires_at") || "",
    subscription_status: localStorage.getItem("basira_subscription_status") || "active"
  };
}

function detectPlatform() {
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes("mac")) return "mac";
  return "windows";
}

async function apiGet(path) {
  const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`);
  return response.json();
}

async function apiPost(path, payload = {}) {
  const response = await fetch(`${LOCAL_BOOTSTRAP_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return response.json();
}

async function readCloudUser() {
  try {
    const {
      data: { session }
    } = await supabaseClient.auth.getSession();

    if (!session?.user) {
      $("cloudUserLabel").textContent = "لم يتم العثور على جلسة مستخدم.";
      $("subscriptionLabel").textContent = "غير معروف";
      return null;
    }

    const userName =
      session.user.user_metadata?.full_name ||
      session.user.email ||
      session.user.id;

    $("cloudUserLabel").textContent = userName;
    $("subscriptionLabel").textContent =
      localStorage.getItem("basira_subscription_status") || "غير معروف";

    return session;
  } catch (err) {
    $("cloudUserLabel").textContent = "تعذر قراءة بيانات المستخدم.";
    $("subscriptionLabel").textContent = "غير معروف";
    return null;
  }
}

async function pushLocalSession() {
  const payload = getStoredSessionPayload();

  if (!payload.user_id || !payload.access_token || !payload.expires_at) {
    throw new Error("بيانات الجلسة المحلية غير مكتملة بعد تسجيل الدخول.");
  }

  await apiPost("/api/setup/login-complete", payload);
}

async function sendHeartbeat() {
  try {
    const response = await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/heartbeat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });

    if (response.status === 401) {
      showNote("localSetupMessage", "err", "انتهت الجلسة المحلية بسبب الخمول أو انتهاء الصلاحية.");
      setTimeout(() => {
        window.location.href = "./login.html";
      }, 1200);
    }
  } catch (err) {
    console.warn("Heartbeat failed:", err);
  }
}

async function autoLogoutNow() {
  try {
    await fetch(`${LOCAL_BOOTSTRAP_URL}/api/auth/auto-logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });
  } catch (err) {
    console.warn("Auto logout request failed:", err);
  }

  showNote("localSetupMessage", "err", "تم تسجيل الخروج تلقائيًا بعد 20 دقيقة من عدم النشاط.");
  setTimeout(() => {
    window.location.href = "./login.html";
  }, 1200);
}

function resetInactivityTimer() {
  if (inactivityTimer) {
    clearTimeout(inactivityTimer);
  }

  inactivityTimer = setTimeout(() => {
    autoLogoutNow();
  }, INACTIVITY_LIMIT_MS);
}

function bindActivityTracking() {
  ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(eventName => {
    window.addEventListener(eventName, () => {
      resetInactivityTimer();
    });
  });

  resetInactivityTimer();
  setInterval(sendHeartbeat, 60000);
}

async function initializeStartup() {
  setStepState(0);

  try {
    await readCloudUser();

    $("startupStatusCard").querySelector(".local-card__title").textContent = "جارٍ التحقق من البيئة المحلية";
    $("startupStatusCard").querySelector(".local-card__text").textContent =
      "يتم الآن فحص config المحلي، حالة الجلسة، data directory، وملفات البيئة المحلية على هذا الجهاز.";

    startupState = await apiGet("/api/startup-status");

    if (!startupState || !startupState.state) {
      throw new Error("تعذر قراءة حالة التشغيل المحلي.");
    }

    if (startupState.state === "new_user" || startupState.state === "setup_incomplete") {
      showCard("newUserCard");
      setStepState(1);
      showNote("localSetupMessage", "ok", "هذه أول مرة على هذا الجهاز أو أن التهيئة السابقة غير مكتملة.");
      return;
    }

    if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
      showCard("readyCard");
      setStepState(3);
      showNote("localSetupMessage", "ok", "تم العثور على بيئة محلية جاهزة. يمكنك تشغيلها مباشرة.");
      return;
    }

    if (startupState.state === "login_required") {
      showNote(
        "localSetupMessage",
        "err",
        "انتهت الجلسة المحلية أو لم تُربط بعد. سيتم إعادة ربطها الآن من جلسة تسجيل الدخول الحالية."
      );

      await pushLocalSession();

      startupState = await apiGet("/api/startup-status");

      if (startupState.state === "healthy" || startupState.state === "healthy_with_optional_update") {
        showCard("readyCard");
        setStepState(3);
        showNote("localSetupMessage", "ok", "تم تحديث الجلسة المحلية بنجاح.");
      } else {
        showCard("newUserCard");
        setStepState(1);
      }

      return;
    }

    if (startupState.state === "subscription_required") {
      showCard("recoveryCard");
      setStepState(1);
      $("recoveryText").textContent =
        "الاشتراك غير فعال حاليًا. يجب تجديد الاشتراك قبل تشغيل البيئة المحلية.";
      $("repairPrimaryBtn").textContent = "فتح صفحة التجديد";
      $("repairPrimaryBtn").dataset.mode = "open-update";
      showNote("localSetupMessage", "err", "يلزم اشتراك فعال للمتابعة.");
      return;
    }

    if (startupState.state === "recovery_required") {
      const reason = startupState.reason || "unknown";
      showCard("recoveryCard");
      setStepState(1);

      const recoveryText = $("recoveryText");
      const recoveryPathField = $("recoveryPathField");
      const repairPrimaryBtn = $("repairPrimaryBtn");

      if (reason === "missing_data_dir" || reason === "data_dir_not_found" || reason === "data_dir_not_writable") {
        recoveryText.textContent =
          "تم اكتشاف مشكلة في مسار حفظ الملفات المحلية. حددي مسارًا جديدًا ليتم إصلاح البيئة المحلية.";
        recoveryPathField.classList.remove("isHidden");
        repairPrimaryBtn.textContent = "تحديث المسار وإصلاح البيئة";
        repairPrimaryBtn.dataset.mode = "reselect-path";
      } else if (reason === "missing_model") {
        recoveryText.textContent =
          "تم اكتشاف ملفات محلية ناقصة. يمكن إصلاح البيئة عبر إعادة تنزيل الملفات الأساسية.";
        recoveryPathField.classList.add("isHidden");
        repairPrimaryBtn.textContent = "إعادة تنزيل الملفات الأساسية";
        repairPrimaryBtn.dataset.mode = "repair-models";
      } else {
        recoveryText.textContent =
          "تم اكتشاف خلل جزئي في البيئة المحلية. سنحاول إصلاحه دون إعادة إعداد كامل.";
        recoveryPathField.classList.add("isHidden");
        repairPrimaryBtn.textContent = "إصلاح الآن";
        repairPrimaryBtn.dataset.mode = "repair-models";
      }

      showNote("localSetupMessage", "err", "تم اكتشاف حالة recovery ويمكن إصلاحها من هذه الصفحة.");
      return;
    }

    if (startupState.state === "update_required") {
      showNote("localSetupMessage", "err", "هذه النسخة المحلية تحتاج تحديثًا إجباريًا قبل المتابعة.");
      showCard("recoveryCard");
      $("recoveryText").textContent = "يلزم تحديث النسخة المحلية قبل المتابعة.";
      $("repairPrimaryBtn").textContent = "فتح بوابة التحديث";
      $("repairPrimaryBtn").dataset.mode = "open-update";
      return;
    }

    throw new Error("حالة تشغيل غير معروفة.");
  } catch (err) {
    showNote("localSetupMessage", "err", err.message || "تعذر بدء صفحة التهيئة المحلية.");
  }
}

async function runFirstSetup() {
  try {
    const session = await readCloudUser();
    if (!session?.user) {
      throw new Error("لا توجد جلسة مستخدم صالحة. الرجاء تسجيل الدخول مجددًا.");
    }

    setStepState(2);
    showCard("loadingCard");

    setProgress(10, "تهيئة الحالة المحلية...");
    await apiPost("/api/setup/init");
    await pushLocalSession();

    const dataDir =
      $("dataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

    setProgress(30, "إنشاء المجلدات المحلية...");
    await apiPost("/api/setup/select-data-dir", {
      data_dir: dataDir
    });

    const platform = detectPlatform();
    const runtimeUrl = LOCAL_RUNTIME_DOWNLOADS[platform];

    setProgress(55, "تنزيل الملفات الأساسية المحلية...");
    await apiPost("/api/setup/install-models", {
      runtime_url: runtimeUrl,
      platform
    });

    setProgress(80, "التحقق من الجاهزية...");
    const verifyResult = await apiGet("/api/setup/verify");

    if (!verifyResult || verifyResult.status !== "ok") {
      throw new Error("فشل التحقق من البيئة المحلية بعد التهيئة.");
    }

    setProgress(95, "اعتماد التهيئة النهائية...");
    await apiPost("/api/setup/finalize");

    setProgress(100, "اكتملت التهيئة بنجاح.");
    setStepState(3);

    showCard("readyCard");
    showNote("localSetupMessage", "ok", "تم تجهيز البيئة المحلية بنجاح على هذا الجهاز.");
  } catch (err) {
    showCard("recoveryCard");
    showNote("localSetupMessage", "err", err.message || "حدث خطأ أثناء التهيئة المحلية.");
  }
}

async function runRecoveryAction() {
  const mode = $("repairPrimaryBtn")?.dataset.mode || "";

  try {
    if (mode === "reselect-path") {
      const pathValue =
        $("recoveryDataDirectory")?.value.trim() || "C:\\Users\\Public\\Documents\\BasiraData";

      showCard("loadingCard");
      setProgress(30, "تحديث مسار البيانات...");
      await apiPost("/api/recovery/reselect-data-dir", {
        data_dir: pathValue
      });

      setProgress(70, "التحقق من البيئة...");
      const verifyResult = await apiGet("/api/setup/verify");

      if (!verifyResult || verifyResult.status !== "ok") {
        throw new Error("ما زالت البيئة تحتاج إصلاحًا إضافيًا.");
      }

      setProgress(100, "تم إصلاح مسار البيانات.");
      showCard("readyCard");
      setStepState(3);
      showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
      return;
    }

    if (mode === "repair-models") {
      showCard("loadingCard");
      setProgress(35, "إعادة تنزيل الملفات الأساسية...");
      await apiPost("/api/recovery/repair-models");

      setProgress(75, "التحقق النهائي...");
      const verifyResult = await apiGet("/api/setup/verify");

      if (!verifyResult || verifyResult.status !== "ok") {
        throw new Error("إصلاح الملفات لم يكتمل بنجاح.");
      }

      setProgress(100, "تم إصلاح الملفات الأساسية.");
      showCard("readyCard");
      setStepState(3);
      showNote("localSetupMessage", "ok", "تم إصلاح البيئة المحلية بنجاح.");
      return;
    }

    if (mode === "open-update") {
      window.open(CLOUD_RENEW_URL, "_blank");
      return;
    }
  } catch (err) {
    showCard("recoveryCard");
    showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ recovery.");
  }
}

function launchLocalEnvironment() {
  window.open(LOCAL_STREAMLIT_URL, "_blank");
  showNote("localSetupMessage", "ok", "تم إرسال أمر تشغيل الواجهة المحلية. إذا لم تعمل بعد، تحققي من خدمة التشغيل المحلي.");
}

async function renewSubscriptionDemo() {
  try {
    const userId = localStorage.getItem("basira_user_id");
    if (!userId) {
      throw new Error("لم يتم العثور على مستخدم محلي مربوط بالجلسة.");
    }

    await apiPost("/api/subscription/renew-demo", {
      user_id: userId
    });

    localStorage.setItem("basira_subscription_status", "active");
    $("subscriptionLabel").textContent = "active";

    showNote("localSetupMessage", "ok", "تم تحديث الاشتراك محليًا في وضع demo.");
  } catch (err) {
    showNote("localSetupMessage", "err", err.message || "تعذر تنفيذ تجديد الاشتراك.");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  $("startSetupBtn")?.addEventListener("click", runFirstSetup);
  $("repairPrimaryBtn")?.addEventListener("click", runRecoveryAction);
  $("launchLocalBtn")?.addEventListener("click", launchLocalEnvironment);

  $("renewSubscriptionBtn")?.addEventListener("click", () => {
    const useCloud = confirm("هل تريد فتح صفحة التجديد السحابية؟ اضغط موافق للتجديد السحابي أو إلغاء لتجديد demo.");
    if (useCloud) {
      window.open(CLOUD_RENEW_URL, "_blank");
    } else {
      renewSubscriptionDemo();
    }
  });

  bindActivityTracking();
  await initializeStartup();
});