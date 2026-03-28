const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

function showNote(id, type, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.className = "note " + (type === "ok" ? "isOk" : "isErr");
}

function setFlash(title, text) {
  localStorage.setItem("basira_flash_title", title);
  localStorage.setItem("basira_flash_text", text);
}

async function signInUser(email, password) {
  const { data, error } = await supabaseClient.auth.signInWithPassword({
    email,
    password
  });

  if (error) throw error;
  return data;
}

async function signUpUser(fullName, email, password, selectedPlanId) {
  const { data, error } = await supabaseClient.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name: fullName
      }
    }
  });

  if (error) throw error;
  if (!data.user) {
    throw new Error("تعذر إنشاء الحساب.");
  }

  const { error: profileError } = await supabaseClient
    .from("profiles")
    .update({
      full_name: fullName,
      email: email,
      selected_plan_id: selectedPlanId
    })
    .eq("user_id", data.user.id);

  if (profileError) throw profileError;

  return data;
}

async function getMySubscription() {
  const {
    data: { session }
  } = await supabaseClient.auth.getSession();

  if (!session) {
    throw new Error("لا توجد جلسة دخول نشطة.");
  }

  const { data, error } = await supabaseClient
    .from("subscriptions")
    .select("plan_id,status,current_period_end")
    .limit(1);

  if (error) throw error;

  return data && data.length ? data[0] : null;
}

function isSubscriptionValid(sub) {
  if (!sub) {
    return {
      ok: false,
      message: "لا يوجد اشتراك مفعّل لهذا الحساب."
    };
  }

  const status = (sub.status || "").toLowerCase();

  if (status !== "active") {
    return {
      ok: false,
      message: "الاشتراك غير فعال حاليًا."
    };
  }

  if (!sub.current_period_end) {
    return {
      ok: true,
      message: "الاشتراك فعال."
    };
  }

  const now = new Date();
  const end = new Date(sub.current_period_end);

  if (end >= now) {
    return {
      ok: true,
      message: "الاشتراك فعال وصالح للاستخدام."
    };
  }

  return {
    ok: false,
    message: "انتهت صلاحية الاشتراك."
  };
}

function validateStrongPassword(password) {
  const hasLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);

  return hasLength && hasUpper && hasLower && hasNumber && hasSpecial;
}

async function handleRegisterForm(event) {
  event.preventDefault();

  const fullName = document.getElementById("fullName")?.value.trim() || "";
  const email = document.getElementById("registerEmail")?.value.trim() || "";
  const password = document.getElementById("registerPassword")?.value || "";
  const selectedPlanId = document.getElementById("selectedPlan")?.value || "";

  if (!fullName) {
    showNote("registerMessage", "err", "الاسم الكامل مطلوب.");
    return;
  }

  if (!selectedPlanId) {
    showNote("registerMessage", "err", "يرجى اختيار الخطة.");
    return;
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showNote("registerMessage", "err", "البريد الإلكتروني غير صحيح.");
    return;
  }

  if (!validateStrongPassword(password)) {
    showNote("registerMessage", "err", "كلمة المرور يجب أن تكون قوية وتحتوي على 8 أحرف على الأقل مع حرف كبير وصغير ورقم ورمز خاص.");
    return;
  }

  showNote("registerMessage", "ok", "جارٍ إنشاء الحساب...");

  try {
    await signUpUser(fullName, email, password, selectedPlanId);

    localStorage.setItem("basira_user_name", fullName);
    localStorage.setItem("basira_selected_plan", selectedPlanId);
    setFlash("تم إنشاء الحساب بنجاح", `أهلًا ${fullName}، تم تسجيل الخطة ${selectedPlanId} بنجاح.`);

    const popup = document.getElementById("successPopup");
    const popupText = document.getElementById("successPopupText");
    if (popup && popupText) {
      popupText.textContent = `أهلًا ${fullName}، تم إنشاء الحساب بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
      popup.classList.add("show");
    }

    setTimeout(() => {
      window.location.href = "home-test.html";
    }, 1800);
  } catch (err) {
    showNote("registerMessage", "err", err.message || "حدث خطأ أثناء إنشاء الحساب.");
  }
}

async function handleLoginForm(event) {
  event.preventDefault();

  const email = document.getElementById("email")?.value.trim() || "";
  const password = document.getElementById("password")?.value || "";

  showNote("loginMessage", "ok", "جارٍ التحقق من الحساب والاشتراك...");

  try {
    const result = await signInUser(email, password);
    const sub = await getMySubscription();
    const check = isSubscriptionValid(sub);

    if (!check.ok) {
      showNote("loginMessage", "err", check.message);
      return;
    }

    const userName = result?.user?.user_metadata?.full_name || email;
    localStorage.setItem("basira_user_name", userName);
    localStorage.setItem("basira_subscription_plan", sub.plan_id || "");
    localStorage.setItem("basira_subscription_status", sub.status || "");
    localStorage.setItem("basira_subscription_end", sub.current_period_end || "");

    setFlash("تم تسجيل الدخول بنجاح", `أهلًا ${userName}، تم التحقق من اشتراكك بنجاح.`);

    const popup = document.getElementById("loginSuccessPopup");
    const popupText = document.getElementById("loginSuccessPopupText");
    if (popup && popupText) {
      popupText.textContent = `أهلًا ${userName}، تم تسجيل الدخول بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
      popup.classList.add("show");
    }

    showNote("loginMessage", "ok", "تم تسجيل الدخول بنجاح. سيتم تحويلك الآن.");

    setTimeout(() => {
      window.location.href = "home-test.html";
    }, 1500);
  } catch (err) {
    showNote("loginMessage", "err", err.message || "حدث خطأ أثناء تسجيل الدخول.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", handleRegisterForm);
  }

  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLoginForm);
  }
});
