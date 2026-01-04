const tg = window.Telegram?.WebApp;
const statusEl = document.getElementById('status');
const regEl = document.getElementById('reg');
const appEl = document.getElementById('app');

const btnContact = document.getElementById('btnContact');
const btnRegister = document.getElementById('btnRegister');
const btnReload = document.getElementById('btnReload');
const btnNew = document.getElementById('btnNew');
const ordersEl = document.getElementById('orders');
const newOrderEl = document.getElementById('newOrder');
const btnCreate = document.getElementById('btnCreate');

let phoneFromContact = null;

// Сообщаем Telegram, что приложение готово
tg?.ready();
// Разворачиваем на весь экран
tg?.expand();

function authHeader() {
  const initData = tg?.initData || '';
  return { 'Authorization': 'tma ' + initData };
}

async function api(path, opts = {}) {
  // ИСПРАВЛЕНО: .replace(/\/$/, '') вместо .replace(//$/, '') - это была синтаксическая ошибка
  const baseUrl = (window.BACKEND_URL || '').replace(/\/$/, '');
  const url = baseUrl + path;
  
  const headers = { 
    ...(opts.headers || {}), 
    ...authHeader(), 
    'Content-Type': 'application/json' 
  };
  
  const res = await fetch(url, { ...opts, headers });
  const txt = await res.text();
  let data;
  try { 
    data = JSON.parse(txt); 
  } catch { 
    data = { raw: txt }; 
  }
  
  if (!res.ok) {
    throw new Error(data.detail || JSON.stringify(data));
  }
  return data;
}

async function boot() {
  if (!statusEl) return;
  statusEl.textContent = 'Проверка...';
  try {
    const me = await api('/api/me');
    statusEl.textContent = `Ваш TG_ID: ${me.tg_id}. Роль: ${me.role || 'не задана'}`;
    
    if (!me.role) {
      regEl?.classList.remove('hidden');
      appEl?.classList.add('hidden');
    } else {
      regEl?.classList.add('hidden');
      appEl?.classList.remove('hidden');
      
      if (me.role === 'shop' && btnNew) {
        btnNew.classList.remove('hidden');
      }
      await loadOrders();
    }
  } catch (e) {
    console.error(e);
    statusEl.textContent = 'Ошибка: ' + e.message;
  }
}

if (btnContact) {
  btnContact.onclick = async () => {
    // ИСПРАВЛЕНО: Метода tg.requestContact не существует в WebApp API.
    // Номер телефона можно получить только если пользователь введет его вручную,
    // либо через кнопку в самом боте (не в WebApp).
    alert('Автоматический запрос номера не поддерживается в WebApp. Пожалуйста, введите номер вручную.');
    
    // Если вы хотите использовать API буфера обмена (в новых версиях):
    /*
    if (tg.readTextFromClipboard) {
      tg.readTextFromClipboard((clipText) => {
        if (clipText && clipText.match(/^\+?\d+$/)) {
             document.getElementById('phone').value = clipText;
        }
      });
    }
    */
  };
}

if (btnRegister) {
  btnRegister.onclick = async () => {
    const roleEl = document.getElementById('role');
    const phoneEl = document.getElementById('phone');
    
    if (!roleEl || !phoneEl) return;

    const role = roleEl.value;
    const phone = (phoneFromContact || phoneEl.value || '').trim();
    
    try {
      await api('/api/auth/register', { 
        method: 'POST', 
        body: JSON.stringify({ role, phone }) 
      });
      await boot();
    } catch (e) {
      alert('Ошибка регистрации: ' + e.message);
    }
  };
}

async function loadOrders() {
  if (!ordersEl) return;
  try {
    const data = await api('/api/orders');
    // Красивый вывод JSON
    ordersEl.textContent = JSON.stringify(data.items || [], null, 2);
  } catch (e) {
    ordersEl.textContent = 'Ошибка загрузки заказов: ' + e.message;
  }
}

if (btnReload) {
  btnReload.onclick = async () => {
    try { await loadOrders(); } catch(e) { alert(e.message); }
  };
}

if (btnNew) {
  btnNew.onclick = () => {
    newOrderEl?.classList.toggle('hidden');
  };
}

if (btnCreate) {
  btnCreate.onclick = async () => {
    const fromAddr = document.getElementById('from_address')?.value;
    const shopCont = document.getElementById('shop_contact')?.value;
    const toAddr = document.getElementById('to_address')?.value;
    const clientName = document.getElementById('client_name')?.value;
    const clientPhone = document.getElementById('client_phone')?.value;
    const priceVal = document.getElementById('price')?.value;

    const payload = {
      from_address: fromAddr,
      shop_contact: shopCont,
      to_address: toAddr,
      client_name: clientName,
      client_phone: clientPhone,
      price: parseFloat(priceVal || '0')
    };
    
    try {
      const r = await api('/api/orders', { method: 'POST', body: JSON.stringify(payload) });
      alert('Создан заказ #' + r.order_id);
      
      // Скрываем форму и обновляем список
      newOrderEl?.classList.add('hidden');
      await loadOrders();
    } catch(e) {
      alert('Ошибка: ' + e.message);
    }
  };
}

// Запуск
boot();
