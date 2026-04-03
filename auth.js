// // const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// // function showNote(id, type, message) {
// //   const el = document.getElementById(id);
// //   if (!el) return;
// //   el.textContent = message;
// //   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// // }

// // function setFlash(title, text) {
// //   localStorage.setItem("basira_flash_title", title);
// //   localStorage.setItem("basira_flash_text", text);
// // }

// // async function signInUser(email, password) {
// //   const { data, error } = await supabaseClient.auth.signInWithPassword({
// //     email,
// //     password
// //   });

// //   if (error) throw error;
// //   return data;
// // }

// // async function signUpUser(fullName, email, password, selectedPlanId) {
// //   const { data, error } = await supabaseClient.auth.signUp({
// //     email,
// //     password,
// //     options: {
// //       data: {
// //         full_name: fullName
// //       }
// //     }
// //   });

// //   if (error) throw error;
// //   if (!data.user) {
// //     throw new Error("تعذر إنشاء الحساب.");
// //   }

// //   const { error: profileError } = await supabaseClient
// //     .from("profiles")
// //     .update({
// //       full_name: fullName,
// //       email: email,
// //       selected_plan_id: selectedPlanId
// //     })
// //     .eq("user_id", data.user.id);

// //   if (profileError) throw profileError;

// //   return data;
// // }

// // async function getMySubscription() {
// //   const {
// //     data: { session }
// //   } = await supabaseClient.auth.getSession();

// //   if (!session) {
// //     throw new Error("لا توجد جلسة دخول نشطة.");
// //   }

// //   const { data, error } = await supabaseClient
// //     .from("subscriptions")
// //     .select("plan_id,status,current_period_end")
// //     .limit(1);

// //   if (error) throw error;

// //   return data && data.length ? data[0] : null;
// // }

// // function isSubscriptionValid(sub) {
// //   if (!sub) {
// //     return {
// //       ok: false,
// //       message: "لا يوجد اشتراك مفعّل لهذا الحساب."
// //     };
// //   }

// //   const status = (sub.status || "").toLowerCase();

// //   if (status !== "active") {
// //     return {
// //       ok: false,
// //       message: "الاشتراك غير فعال حاليًا."
// //     };
// //   }

// //   if (!sub.current_period_end) {
// //     return {
// //       ok: true,
// //       message: "الاشتراك فعال."
// //     };
// //   }

// //   const now = new Date();
// //   const end = new Date(sub.current_period_end);

// //   if (end >= now) {
// //     return {
// //       ok: true,
// //       message: "الاشتراك فعال وصالح للاستخدام."
// //     };
// //   }

// //   return {
// //     ok: false,
// //     message: "انتهت صلاحية الاشتراك."
// //   };
// // }

// // function validateStrongPassword(password) {
// //   const hasLength = password.length >= 8;
// //   const hasUpper = /[A-Z]/.test(password);
// //   const hasLower = /[a-z]/.test(password);
// //   const hasNumber = /[0-9]/.test(password);
// //   const hasSpecial = /[^A-Za-z0-9]/.test(password);

// //   return hasLength && hasUpper && hasLower && hasNumber && hasSpecial;
// // }

// // async function handleRegisterForm(event) {
// //   event.preventDefault();

// //   const fullName = document.getElementById("fullName")?.value.trim() || "";
// //   const email = document.getElementById("registerEmail")?.value.trim() || "";
// //   const password = document.getElementById("registerPassword")?.value || "";
// //   const selectedPlanId = document.getElementById("selectedPlan")?.value || "";

// //   if (!fullName) {
// //     showNote("registerMessage", "err", "الاسم الكامل مطلوب.");
// //     return;
// //   }

// //   if (!selectedPlanId) {
// //     showNote("registerMessage", "err", "يرجى اختيار الخطة.");
// //     return;
// //   }

// //   if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
// //     showNote("registerMessage", "err", "البريد الإلكتروني غير صحيح.");
// //     return;
// //   }

// //   if (!validateStrongPassword(password)) {
// //     showNote("registerMessage", "err", "كلمة المرور يجب أن تكون قوية وتحتوي على 8 أحرف على الأقل مع حرف كبير وصغير ورقم ورمز خاص.");
// //     return;
// //   }

// //   showNote("registerMessage", "ok", "جارٍ إنشاء الحساب...");

// //   try {
// //     await signUpUser(fullName, email, password, selectedPlanId);

// //     localStorage.setItem("basira_user_name", fullName);
// //     localStorage.setItem("basira_selected_plan", selectedPlanId);
// //     setFlash("تم إنشاء الحساب بنجاح", `أهلًا ${fullName}، تم تسجيل الخطة ${selectedPlanId} بنجاح.`);

// //     const popup = document.getElementById("successPopup");
// //     const popupText = document.getElementById("successPopupText");
// //     if (popup && popupText) {
// //       popupText.textContent = `أهلًا ${fullName}، تم إنشاء الحساب بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
// //       popup.classList.add("show");
// //     }

// //     setTimeout(() => {
// //       window.location.href = "home-test.html";
// //     }, 1800);
// //   } catch (err) {
// //     showNote("registerMessage", "err", err.message || "حدث خطأ أثناء إنشاء الحساب.");
// //   }
// // }

// // async function handleLoginForm(event) {
// //   event.preventDefault();

// //   const email = document.getElementById("email")?.value.trim() || "";
// //   const password = document.getElementById("password")?.value || "";

// //   showNote("loginMessage", "ok", "جارٍ التحقق من الحساب والاشتراك...");

// //   try {
// //     const result = await signInUser(email, password);
// //     const sub = await getMySubscription();
// //     const check = isSubscriptionValid(sub);

// //     if (!check.ok) {
// //       showNote("loginMessage", "err", check.message);
// //       return;
// //     }

// //     const userName = result?.user?.user_metadata?.full_name || email;
// //     localStorage.setItem("basira_user_name", userName);
// //     localStorage.setItem("basira_subscription_plan", sub.plan_id || "");
// //     localStorage.setItem("basira_subscription_status", sub.status || "");
// //     localStorage.setItem("basira_subscription_end", sub.current_period_end || "");

// //     setFlash("تم تسجيل الدخول بنجاح", `أهلًا ${userName}، تم التحقق من اشتراكك بنجاح.`);

// //     const popup = document.getElementById("loginSuccessPopup");
// //     const popupText = document.getElementById("loginSuccessPopupText");
// //     if (popup && popupText) {
// //       popupText.textContent = `أهلًا ${userName}، تم تسجيل الدخول بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
// //       popup.classList.add("show");
// //     }

// //     showNote("loginMessage", "ok", "تم تسجيل الدخول بنجاح. سيتم تحويلك الآن.");

// //     setTimeout(() => {
// //       window.location.href = "home-test.html";
// //     }, 1500);
// //   } catch (err) {
// //     showNote("loginMessage", "err", err.message || "حدث خطأ أثناء تسجيل الدخول.");
// //   }
// // }

// // document.addEventListener("DOMContentLoaded", () => {
// //   const registerForm = document.getElementById("registerForm");
// //   if (registerForm) {
// //     registerForm.addEventListener("submit", handleRegisterForm);
// //   }

// //   const loginForm = document.getElementById("loginForm");
// //   if (loginForm) {
// //     loginForm.addEventListener("submit", handleLoginForm);
// //   }
// // });
// const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// let pendingLoginContext = null;

// function showNote(id, type, message) {
//   const el = document.getElementById(id);
//   if (!el) return;
//   el.textContent = message;
//   el.className = "note " + (type === "ok" ? "isOk" : "isErr");
// }

// function setFlash(title, text) {
//   localStorage.setItem("basira_flash_title", title);
//   localStorage.setItem("basira_flash_text", text);
// }

// function formatDate(value) {
//   if (!value) return "غير محدد";

//   const date = new Date(value);
//   if (Number.isNaN(date.getTime())) return "غير محدد";

//   return new Intl.DateTimeFormat("ar-SA", {
//     year: "numeric",
//     month: "long",
//     day: "numeric"
//   }).format(date);
// }

// function escapeHtml(value) {
//   return String(value || "")
//     .replace(/&/g, "&amp;")
//     .replace(/</g, "&lt;")
//     .replace(/>/g, "&gt;")
//     .replace(/\"/g, "&quot;")
//     .replace(/'/g, "&#039;");
// }

// async function signInUser(email, password) {
//   const { data, error } = await supabaseClient.auth.signInWithPassword({
//     email,
//     password
//   });

//   if (error) throw error;
//   return data;
// }

// async function signUpUser(fullName, email, password, selectedPlanId) {
//   const { data, error } = await supabaseClient.auth.signUp({
//     email,
//     password,
//     options: {
//       data: {
//         full_name: fullName
//       }
//     }
//   });

//   if (error) throw error;
//   if (!data.user) {
//     throw new Error("تعذر إنشاء الحساب.");
//   }

//   const userId = data.user.id;

//   const { error: profileError } = await supabaseClient
//     .from("profiles")
//     .upsert(
//       {
//         user_id: userId,
//         full_name: fullName,
//         email: email,
//         selected_plan_id: selectedPlanId
//       },
//       { onConflict: "user_id" }
//     );

//   if (profileError) throw profileError;

//   const { data: existingSubscription, error: existingSubscriptionError } = await supabaseClient
//     .from("subscriptions")
//     .select("id")
//     .eq("user_id", userId)
//     .maybeSingle();

//   if (existingSubscriptionError) throw existingSubscriptionError;

//   if (!existingSubscription) {
//     const { error: subscriptionInsertError } = await supabaseClient
//       .from("subscriptions")
//       .insert({
//         user_id: userId,
//         plan_id: selectedPlanId,
//         status: "inactive",
//         current_period_end: null
//       });

//     if (subscriptionInsertError) throw subscriptionInsertError;
//   }

//   return data;
// }

// async function getMySubscription() {
//   const {
//     data: { session }
//   } = await supabaseClient.auth.getSession();

//   if (!session) {
//     throw new Error("لا توجد جلسة دخول نشطة.");
//   }

//   const userId = session.user.id;

//   const { data: profile, error: profileError } = await supabaseClient
//     .from("profiles")
//     .select("selected_plan_id,full_name,email")
//     .eq("user_id", userId)
//     .maybeSingle();

//   if (profileError) throw profileError;

//   const { data: subscription, error: subscriptionError } = await supabaseClient
//     .from("subscriptions")
//     .select("id,user_id,plan_id,status,current_period_end")
//     .eq("user_id", userId)
//     .order("current_period_end", { ascending: false, nullsFirst: false })
//     .limit(1)
//     .maybeSingle();

//   if (subscriptionError) throw subscriptionError;

//   return {
//     subscription: subscription || null,
//     profile: profile || null
//   };
// }

// function isSubscriptionValid(sub) {
//   if (!sub) {
//     return {
//       ok: false,
//       message: "لا يوجد اشتراك لهذا الحساب.",
//       stateLabel: "غير موجود"
//     };
//   }

//   const status = (sub.status || "").toLowerCase();

//   if (status !== "active") {
//     return {
//       ok: false,
//       message: "الاشتراك غير فعال حاليًا.",
//       stateLabel: status || "غير معروف"
//     };
//   }

//   if (!sub.current_period_end) {
//     return {
//       ok: true,
//       message: "الاشتراك فعال.",
//       stateLabel: "active"
//     };
//   }

//   const now = new Date();
//   const end = new Date(sub.current_period_end);

//   if (end >= now) {
//     return {
//       ok: true,
//       message: "الاشتراك فعال وصالح للاستخدام.",
//       stateLabel: "active"
//     };
//   }

//   return {
//     ok: false,
//     message: "انتهت صلاحية الاشتراك.",
//     stateLabel: "منتهي"
//   };
// }

// function validateStrongPassword(password) {
//   const hasLength = password.length >= 8;
//   const hasUpper = /[A-Z]/.test(password);
//   const hasLower = /[a-z]/.test(password);
//   const hasNumber = /[0-9]/.test(password);
//   const hasSpecial = /[^A-Za-z0-9]/.test(password);

//   return hasLength && hasUpper && hasLower && hasNumber && hasSpecial;
// }

// function hideSubscriptionNotice() {
//   const box = document.getElementById("subscriptionNotice");
//   if (!box) return;
//   box.hidden = true;
//   box.innerHTML = "";
// }

// function showSubscriptionNotice(details) {
//   const box = document.getElementById("subscriptionNotice");
//   if (!box) return;

//   const plan = details.planId || "لا توجد خطة محددة";
//   const status = details.statusText || "غير معروف";
//   const endDate = details.endDateText || "غير محدد";

//   box.hidden = false;
//   box.innerHTML = `
//     <div class="subscription-alert">
//       <div class="subscription-alert__header">
//         <h3 class="subscription-alert__title">الاشتراك غير متاح للدخول</h3>
//         <p class="subscription-alert__subtitle">يجب تفعيل الاشتراك أو تجديده قبل المتابعة إلى النظام.</p>
//       </div>

//       <div class="subscription-alert__grid">
//         <div class="subscription-alert__item">
//           <span class="subscription-alert__label">حالة الاشتراك</span>
//           <strong class="subscription-alert__value">${escapeHtml(status)}</strong>
//         </div>
//         <div class="subscription-alert__item">
//           <span class="subscription-alert__label">الخطة الحالية</span>
//           <strong class="subscription-alert__value">${escapeHtml(plan)}</strong>
//         </div>
//         <div class="subscription-alert__item">
//           <span class="subscription-alert__label">نهاية الاشتراك</span>
//           <strong class="subscription-alert__value">${escapeHtml(endDate)}</strong>
//         </div>
//       </div>

//       <button class="btn btn--primary btn--lg subscription-alert__button" id="renewSubscriptionBtn" type="button">
//         تجديد الاشتراك
//       </button>
//     </div>
//   `;

//   const renewBtn = document.getElementById("renewSubscriptionBtn");
//   if (renewBtn) {
//     renewBtn.addEventListener("click", handleRenewSubscription);
//   }
// }

// async function renewMySubscription(planId) {
//   const {
//     data: { session }
//   } = await supabaseClient.auth.getSession();

//   if (!session) {
//     throw new Error("تعذر تحديث الاشتراك لعدم وجود جلسة نشطة.");
//   }

//   const userId = session.user.id;
//   const nextEnd = new Date();
//   nextEnd.setMonth(nextEnd.getMonth() + 1);

//   const { data: existingSubscription, error: fetchError } = await supabaseClient
//     .from("subscriptions")
//     .select("id,plan_id")
//     .eq("user_id", userId)
//     .limit(1)
//     .maybeSingle();

//   if (fetchError) throw fetchError;

//   if (existingSubscription?.id) {
//     const { error: updateError } = await supabaseClient
//       .from("subscriptions")
//       .update({
//         plan_id: planId || existingSubscription.plan_id || "starter",
//         status: "active",
//         current_period_end: nextEnd.toISOString()
//       })
//       .eq("id", existingSubscription.id);

//     if (updateError) throw updateError;
//   } else {
//     const { error: insertError } = await supabaseClient
//       .from("subscriptions")
//       .insert({
//         user_id: userId,
//         plan_id: planId || "starter",
//         status: "active",
//         current_period_end: nextEnd.toISOString()
//       });

//     if (insertError) throw insertError;
//   }

//   return {
//     status: "active",
//     plan_id: planId || existingSubscription?.plan_id || "starter",
//     current_period_end: nextEnd.toISOString()
//   };
// }

// function saveUserSubscriptionLocally(userName, sub) {
//   localStorage.setItem("basira_user_name", userName);
//   localStorage.setItem("basira_subscription_plan", sub.plan_id || "");
//   localStorage.setItem("basira_subscription_status", sub.status || "");
//   localStorage.setItem("basira_subscription_end", sub.current_period_end || "");
// }

// async function completeLoginSuccess(userName, sub) {
//   saveUserSubscriptionLocally(userName, sub);

//   setFlash("تم تسجيل الدخول بنجاح", `أهلًا ${userName}، تم التحقق من اشتراكك بنجاح.`);

//   const popup = document.getElementById("loginSuccessPopup");
//   const popupText = document.getElementById("loginSuccessPopupText");
//   if (popup && popupText) {
//     popupText.textContent = `أهلًا ${userName}، تم تسجيل الدخول بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
//     popup.classList.add("show");
//   }

//   showNote("loginMessage", "ok", "تم تسجيل الدخول بنجاح. سيتم تحويلك الآن.");
//   hideSubscriptionNotice();

//   setTimeout(() => {
//     window.location.href = "home-test.html";
//   }, 1500);
// }

// async function handleRegisterForm(event) {
//   event.preventDefault();

//   const fullName = document.getElementById("fullName")?.value.trim() || "";
//   const email = document.getElementById("registerEmail")?.value.trim() || "";
//   const password = document.getElementById("registerPassword")?.value || "";
//   const selectedPlanId = document.getElementById("selectedPlan")?.value || "";

//   if (!fullName) {
//     showNote("registerMessage", "err", "الاسم الكامل مطلوب.");
//     return;
//   }

//   if (!selectedPlanId) {
//     showNote("registerMessage", "err", "يرجى اختيار الخطة.");
//     return;
//   }

//   if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
//     showNote("registerMessage", "err", "البريد الإلكتروني غير صحيح.");
//     return;
//   }

//   if (!validateStrongPassword(password)) {
//     showNote("registerMessage", "err", "كلمة المرور يجب أن تكون قوية وتحتوي على 8 أحرف على الأقل مع حرف كبير وصغير ورقم ورمز خاص.");
//     return;
//   }

//   showNote("registerMessage", "ok", "جارٍ إنشاء الحساب...");

//   try {
//     await signUpUser(fullName, email, password, selectedPlanId);

//     localStorage.setItem("basira_user_name", fullName);
//     localStorage.setItem("basira_selected_plan", selectedPlanId);
//     setFlash("تم إنشاء الحساب بنجاح", `أهلًا ${fullName}، تم تسجيل الخطة ${selectedPlanId} بنجاح.`);

//     const popup = document.getElementById("successPopup");
//     const popupText = document.getElementById("successPopupText");
//     if (popup && popupText) {
//       popupText.textContent = `أهلًا ${fullName}، تم إنشاء الحساب بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
//       popup.classList.add("show");
//     }

//     setTimeout(() => {
//       window.location.href = "login.html";
//     }, 1800);
//   } catch (err) {
//     showNote("registerMessage", "err", err.message || "حدث خطأ أثناء إنشاء الحساب.");
//   }
// }

// async function handleLoginForm(event) {
//   event.preventDefault();

//   const email = document.getElementById("email")?.value.trim() || "";
//   const password = document.getElementById("password")?.value || "";

//   hideSubscriptionNotice();
//   showNote("loginMessage", "ok", "جارٍ التحقق من الحساب والاشتراك...");

//   try {
//     const result = await signInUser(email, password);
//     const { subscription, profile } = await getMySubscription();
//     const check = isSubscriptionValid(subscription);

//     const userName = result?.user?.user_metadata?.full_name || profile?.full_name || email;
//     const planId = subscription?.plan_id || profile?.selected_plan_id || "";

//     if (!check.ok) {
//       pendingLoginContext = {
//         userName,
//         planId
//       };

//       showNote("loginMessage", "err", check.message);
//       showSubscriptionNotice({
//         statusText: check.stateLabel,
//         planId,
//         endDateText: formatDate(subscription?.current_period_end)
//       });
//       return;
//     }

//     await completeLoginSuccess(userName, {
//       plan_id: planId,
//       status: subscription.status,
//       current_period_end: subscription.current_period_end
//     });
//   } catch (err) {
//     pendingLoginContext = null;
//     hideSubscriptionNotice();
//     showNote("loginMessage", "err", err.message || "حدث خطأ أثناء تسجيل الدخول.");
//   }
// }

// async function handleRenewSubscription() {
//   const button = document.getElementById("renewSubscriptionBtn");
//   if (button) {
//     button.disabled = true;
//     button.textContent = "جارٍ تحديث الاشتراك...";
//   }

//   try {
//     const renewedSubscription = await renewMySubscription(pendingLoginContext?.planId);
//     const userName = pendingLoginContext?.userName || localStorage.getItem("basira_user_name") || "المستخدم";

//     showNote("loginMessage", "ok", "تم تجديد الاشتراك بنجاح. سيتم إكمال تسجيل الدخول الآن.");

//     await completeLoginSuccess(userName, renewedSubscription);
//   } catch (err) {
//     showNote("loginMessage", "err", err.message || "تعذر تجديد الاشتراك.");
//     if (button) {
//       button.disabled = false;
//       button.textContent = "تجديد الاشتراك";
//     }
//   }
// }

// document.addEventListener("DOMContentLoaded", () => {
//   const registerForm = document.getElementById("registerForm");
//   if (registerForm) {
//     registerForm.addEventListener("submit", handleRegisterForm);
//   }

//   const loginForm = document.getElementById("loginForm");
//   if (loginForm) {
//     loginForm.addEventListener("submit", handleLoginForm);
//   }
// });


const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

let pendingLoginContext = null;

function showNote(id, type, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = message;
  el.className = "note " + (type === "ok" ? "isOk" : "isErr");
}

function setFlash(title, text) {
  localStorage.setItem("basira_flash_title", title);
  localStorage.setItem("basira_flash_text", text);
}

function formatDate(value) {
  if (!value) return "غير محدد";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "غير محدد";

  return new Intl.DateTimeFormat("ar-SA", {
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(date);
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
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
        full_name: fullName,
        selected_plan_id: selectedPlanId
      }
    }
  });

  if (error) throw error;
  if (!data.user) {
    throw new Error("تعذر إنشاء الحساب.");
  }

  return data;
}

async function getCurrentSessionUser() {
  const {
    data: { session }
  } = await supabaseClient.auth.getSession();

  if (!session || !session.user) {
    throw new Error("لا توجد جلسة دخول نشطة.");
  }

  return session.user;
}

async function getMyProfile() {
  const user = await getCurrentSessionUser();

  const { data, error } = await supabaseClient
    .from("profiles")
    .select("user_id,full_name,email,selected_plan_id")
    .eq("user_id", user.id)
    .maybeSingle();

  if (error) throw error;
  return data || null;
}

async function getMySubscription() {
  const user = await getCurrentSessionUser();

  const { data, error } = await supabaseClient
    .from("subscriptions")
    .select("id,user_id,plan_id,status,current_period_end")
    .eq("user_id", user.id)
    .maybeSingle();

  if (error) throw error;
  return data || null;
}

async function ensureMyProfileAndSubscription() {
  const user = await getCurrentSessionUser();

  const fullName = user.user_metadata?.full_name || "";
  const email = user.email || "";
  const selectedPlanId = user.user_metadata?.selected_plan_id || "starter";

  const existingProfile = await getMyProfile();

  if (!existingProfile) {
    const { error: profileInsertError } = await supabaseClient
      .from("profiles")
      .insert({
        user_id: user.id,
        full_name: fullName,
        email: email,
        selected_plan_id: selectedPlanId
      });

    if (profileInsertError) throw profileInsertError;
  } else {
    const { error: profileUpdateError } = await supabaseClient
      .from("profiles")
      .update({
        full_name: existingProfile.full_name || fullName,
        email: existingProfile.email || email,
        selected_plan_id: existingProfile.selected_plan_id || selectedPlanId
      })
      .eq("user_id", user.id);

    if (profileUpdateError) throw profileUpdateError;
  }

  const existingSubscription = await getMySubscription();

  if (!existingSubscription) {
    const { error: subInsertError } = await supabaseClient
      .from("subscriptions")
      .insert({
        user_id: user.id,
        plan_id: selectedPlanId,
        status: "inactive",
        current_period_end: null
      });

    if (subInsertError) throw subInsertError;
  } else if (!existingSubscription.plan_id) {
    const { error: subUpdateError } = await supabaseClient
      .from("subscriptions")
      .update({
        plan_id: selectedPlanId
      })
      .eq("user_id", user.id);

    if (subUpdateError) throw subUpdateError;
  }

  return {
    profile: await getMyProfile(),
    subscription: await getMySubscription()
  };
}

function isSubscriptionValid(sub) {
  if (!sub) {
    return {
      ok: false,
      message: "لا يوجد اشتراك لهذا الحساب.",
      stateLabel: "غير موجود"
    };
  }

  const status = (sub.status || "").toLowerCase();

  if (status !== "active") {
    return {
      ok: false,
      message: "الاشتراك غير فعال حاليًا.",
      stateLabel: status || "غير معروف"
    };
  }

  if (!sub.current_period_end) {
    return {
      ok: true,
      message: "الاشتراك فعال.",
      stateLabel: "active"
    };
  }

  const now = new Date();
  const end = new Date(sub.current_period_end);

  if (end >= now) {
    return {
      ok: true,
      message: "الاشتراك فعال وصالح للاستخدام.",
      stateLabel: "active"
    };
  }

  return {
    ok: false,
    message: "انتهت صلاحية الاشتراك.",
    stateLabel: "منتهي"
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

function hideSubscriptionNotice() {
  const box = document.getElementById("subscriptionNotice");
  if (!box) return;
  box.hidden = true;
  box.innerHTML = "";
}

function showSubscriptionNotice(details) {
  const box = document.getElementById("subscriptionNotice");
  if (!box) return;

  const plan = details.planId || "لا توجد خطة محددة";
  const status = details.statusText || "غير معروف";
  const endDate = details.endDateText || "غير محدد";

  box.hidden = false;
  box.innerHTML = `
    <div class="subscription-alert">
      <div class="subscription-alert__header">
        <h3 class="subscription-alert__title">الاشتراك غير متاح للدخول</h3>
        <p class="subscription-alert__subtitle">يجب تفعيل الاشتراك أو تجديده قبل المتابعة إلى النظام.</p>
      </div>

      <div class="subscription-alert__grid">
        <div class="subscription-alert__item">
          <span class="subscription-alert__label">حالة الاشتراك</span>
          <strong class="subscription-alert__value">${escapeHtml(status)}</strong>
        </div>
        <div class="subscription-alert__item">
          <span class="subscription-alert__label">الخطة الحالية</span>
          <strong class="subscription-alert__value">${escapeHtml(plan)}</strong>
        </div>
        <div class="subscription-alert__item">
          <span class="subscription-alert__label">نهاية الاشتراك</span>
          <strong class="subscription-alert__value">${escapeHtml(endDate)}</strong>
        </div>
      </div>

      <button class="btn btn--primary btn--lg subscription-alert__button" id="renewSubscriptionBtn" type="button">
        تجديد الاشتراك
      </button>
    </div>
  `;

  const renewBtn = document.getElementById("renewSubscriptionBtn");
  if (renewBtn) {
    renewBtn.addEventListener("click", handleRenewSubscription);
  }
}

async function renewMySubscription(planId) {
  const user = await getCurrentSessionUser();

  const nextEnd = new Date();
  nextEnd.setMonth(nextEnd.getMonth() + 1);

  const { data: existingSubscription, error: fetchError } = await supabaseClient
    .from("subscriptions")
    .select("id,plan_id")
    .eq("user_id", user.id)
    .maybeSingle();

  if (fetchError) throw fetchError;

  if (existingSubscription?.id) {
    const { error: updateError } = await supabaseClient
      .from("subscriptions")
      .update({
        plan_id: planId || existingSubscription.plan_id || "starter",
        status: "active",
        current_period_end: nextEnd.toISOString()
      })
      .eq("id", existingSubscription.id);

    if (updateError) throw updateError;
  } else {
    const { error: insertError } = await supabaseClient
      .from("subscriptions")
      .insert({
        user_id: user.id,
        plan_id: planId || "starter",
        status: "active",
        current_period_end: nextEnd.toISOString()
      });

    if (insertError) throw insertError;
  }

  return {
    status: "active",
    plan_id: planId || existingSubscription?.plan_id || "starter",
    current_period_end: nextEnd.toISOString()
  };
}

function saveUserSubscriptionLocally(userName, sub) {
  localStorage.setItem("basira_user_name", userName);
  localStorage.setItem("basira_subscription_plan", sub.plan_id || "");
  localStorage.setItem("basira_subscription_status", sub.status || "");
  localStorage.setItem("basira_subscription_end", sub.current_period_end || "");
}

async function completeLoginSuccess(userName, sub) {
  saveUserSubscriptionLocally(userName, sub);

  setFlash("تم تسجيل الدخول بنجاح", `أهلًا ${userName}، تم التحقق من اشتراكك بنجاح.`);

  const popup = document.getElementById("loginSuccessPopup");
  const popupText = document.getElementById("loginSuccessPopupText");
  if (popup && popupText) {
    popupText.textContent = `أهلًا ${userName}، تم تسجيل الدخول بنجاح وسيتم تحويلك الآن إلى الصفحة التجريبية.`;
    popup.classList.add("show");
  }

  showNote("loginMessage", "ok", "تم تسجيل الدخول بنجاح. سيتم تحويلك الآن.");
  hideSubscriptionNotice();

  setTimeout(() => {
    window.location.href = "home-test.html";
  }, 1500);
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

    showNote("registerMessage", "ok", "تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.");

    const popup = document.getElementById("successPopup");
    const popupText = document.getElementById("successPopupText");
    if (popup && popupText) {
      popupText.textContent = `أهلًا ${fullName}، تم إنشاء الحساب بنجاح وسيتم تحويلك الآن إلى صفحة تسجيل الدخول.`;
      popup.classList.add("show");
    }

    setTimeout(() => {
      window.location.href = "login.html";
    }, 1800);
  } catch (err) {
    showNote("registerMessage", "err", err.message || "حدث خطأ أثناء إنشاء الحساب.");
  }
}

async function handleLoginForm(event) {
  event.preventDefault();

  const email = document.getElementById("email")?.value.trim() || "";
  const password = document.getElementById("password")?.value || "";

  hideSubscriptionNotice();
  showNote("loginMessage", "ok", "جارٍ التحقق من الحساب والاشتراك...");

  try {
    const result = await signInUser(email, password);

    await ensureMyProfileAndSubscription();

    const profile = await getMyProfile();
    const subscription = await getMySubscription();
    const check = isSubscriptionValid(subscription);

    const userName =
      result?.user?.user_metadata?.full_name ||
      profile?.full_name ||
      email;

    const planId =
      subscription?.plan_id ||
      profile?.selected_plan_id ||
      result?.user?.user_metadata?.selected_plan_id ||
      "";

    if (!check.ok) {
      pendingLoginContext = {
        userName,
        planId
      };

      showNote("loginMessage", "err", check.message);
      showSubscriptionNotice({
        statusText: check.stateLabel,
        planId,
        endDateText: formatDate(subscription?.current_period_end)
      });
      return;
    }

    await completeLoginSuccess(userName, {
      plan_id: planId,
      status: subscription.status,
      current_period_end: subscription.current_period_end
    });
  } catch (err) {
    pendingLoginContext = null;
    hideSubscriptionNotice();
    showNote("loginMessage", "err", err.message || "حدث خطأ أثناء تسجيل الدخول.");
  }
}

async function handleRenewSubscription() {
  const button = document.getElementById("renewSubscriptionBtn");
  if (button) {
    button.disabled = true;
    button.textContent = "جارٍ تحديث الاشتراك...";
  }

  try {
    const renewedSubscription = await renewMySubscription(pendingLoginContext?.planId);
    const userName = pendingLoginContext?.userName || localStorage.getItem("basira_user_name") || "المستخدم";

    showNote("loginMessage", "ok", "تم تجديد الاشتراك بنجاح. سيتم إكمال تسجيل الدخول الآن.");

    await completeLoginSuccess(userName, renewedSubscription);
  } catch (err) {
    showNote("loginMessage", "err", err.message || "تعذر تجديد الاشتراك.");
    if (button) {
      button.disabled = false;
      button.textContent = "تجديد الاشتراك";
    }
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