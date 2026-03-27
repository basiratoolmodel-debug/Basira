const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

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

async function handleLoginForm(event) {
  event.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const msg = document.getElementById("loginMessage");

  msg.textContent = "جارٍ التحقق من الحساب والاشتراك...";
  msg.className = "authMessage";

  try {
    await signInUser(email, password);
    const sub = await getMySubscription();
    const check = isSubscriptionValid(sub);

    if (!check.ok) {
      msg.textContent = check.message;
      msg.className = "authMessage authMessage--error";
      return;
    }

    localStorage.setItem("basira_subscription_plan", sub.plan_id || "");
    localStorage.setItem("basira_subscription_status", sub.status || "");
    localStorage.setItem("basira_subscription_end", sub.current_period_end || "");

    msg.textContent = "تم التحقق بنجاح. يمكنك الآن استخدام بصيرة.";
    msg.className = "authMessage authMessage--success";

    setTimeout(() => {
      window.location.href = "index.html";
    }, 1200);
  } catch (err) {
    msg.textContent = err.message || "حدث خطأ أثناء تسجيل الدخول.";
    msg.className = "authMessage authMessage--error";
  }
}

async function handleRegisterForm(event) {
  event.preventDefault();

  const fullName = document.getElementById("fullName").value.trim();
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value;
  const selectedPlanId = document.getElementById("selectedPlan").value;
  const msg = document.getElementById("registerMessage");

  msg.textContent = "جارٍ إنشاء الحساب...";
  msg.className = "authMessage";

  try {
    await signUpUser(fullName, email, password, selectedPlanId);

    msg.textContent =
      "تم إنشاء الحساب بنجاح. تم حفظ الخطة المختارة، ويمكن تفعيل الاشتراك لاحقًا عبر الإدارة أو الدفع التجريبي.";
    msg.className = "authMessage authMessage--success";

    setTimeout(() => {
      window.location.href = "login.html";
    }, 1500);
  } catch (err) {
    msg.textContent = err.message || "حدث خطأ أثناء إنشاء الحساب.";
    msg.className = "authMessage authMessage--error";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLoginForm);
  }

  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", handleRegisterForm);
  }
});
