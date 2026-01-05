const tg = window.Telegram?.WebApp;

// Элементы интерфейса
const statusEl = document.getElementById('status');
const errorLogEl = document.getElementById('error-log');
const userInfoEl = document.getElementById('user-info');

const regEl = document.getElementById('reg');
const appEl = document.getElementById('app');
const newOrderEl = document.getElementById('newOrder');
const ordersContainer = document.getElementById('orders-container');

// Кнопки
const btnRegister = document.getElementById('btnRegister');
const btnReload = document.getElementById('btnReload');
const btnNew = document.getElementById('btnNew');
const btnCreate = document.getElementById('btnCreate');
const btnCancel = document.getElementById('btnCancel');

// Показываем ошибки на экране (полезно для отладки с телефона)
function showError(msg) {
  console.error(msg);
  errorLogEl.classList.remove('hidden');
  errorLogEl.innerHTML = `<div>⚠️ ${msg}</div>` + errorLogEl.innerHTML;
}

function getAuthHeader() {
  const initData = tg?.initData || '';
  return { 'Authorization': 'tma ' + initData };
}

async function api(path, opts = {}) {
  const baseUrl = (window.BACKEND_URL || '').replace(//$/, '');
  const url = baseUrl + path;

  const headers = {
    ...(opts.headers || {}),
    ...getAuthHeader(),
    'Content-Type': 'application/json'
  };

  try {
    const res = await fetch(url, { ...opts, headers });
    const txt = await res.text();

    let data;
    try { data = JSON.parse(txt); } catch { data = { raw: txt }; }

    if (!res.ok) {
      throw new Error(data.detail || JSON.stringify(data));
    }
    return data;
  } catch (e) {
    if (String(e.message || '').includes('Failed to fetch')) {
      throw new Error('Нет связи с сервером. Сервер спит или блокирует запрос.');
    }
    throw e;
  }
}

// 1. Инициализация Telegram
try {
  tg?.ready();
  tg?.expand();

  // Debug (можно потом удалить)
  if (tg) {
    showError(`tg.version = ${tg.version || 'unknown'}`);
    showError(`isVerticalSwipesEnabled(before) = ${tg.isVerticalSwipesEnabled}`);
  }

  // Главное: запретить свайп вниз по контенту (Bot API 7.7+)
  tg?.disableVerticalSwipes?.();

  // Подтверждение при закрытии (по желанию)
  tg?.enableClosingConfirmation?.();

  if (tg) {
    showError(`isVerticalSwipesEnabled(after) = ${tg.isVerticalSwipesEnabled}`);
  }

  // Настраиваем цвета
  if (tg?.themeParams?.bg_color) {
    document.body.style.backgroundColor = tg.themeParams.bg_color;
  }
} catch (e) {
  console.error("Ошибка TG Init:", e);
}

// 3. Запуск приложения (Boot)
async function boot() {
  statusEl.textContent = 'Подключение...';
  try {
    const me = await api('/api/me');
    statusEl.classList.add('hidden');

    const roles = { 'shop': 'Магазин', 'courier': 'Курьер' };
    userInfoEl.textContent = `ID: ${me.tg_id} | ${roles[me.role] || 'Нет роли'}`;

    if (!me.role) {
      regEl.classList.remove('hidden');
      appEl.classList.add('hidden');
    } else {
      regEl.classList.add('hidden');
      appEl.classList.remove('hidden');

      if (me.role === 'shop') {
        btnNew.classList.remove('hidden');
      } else {
        btnNew.classList.add('hidden');
      }

      loadOrders();
    }
  } catch (e) {
    statusEl.textContent = 'Ошибка';
    showError(e.message);
  }
}

// 4. Загрузка списка заказов
async function loadOrders() {
  ordersContainer.innerHTML = '<div style="text-align:center; padding:10px; color:#666;">Обновление...</div>';
  try {
    const data = await api('/api/orders');
    const items = data.items || [];

    ordersContainer.innerHTML = '';

    if (items.length === 0) {
      ordersContainer.innerHTML = '<div style="text-align:center; padding:20px; color:#666;">Список пуст</div>';
      return;
    }

    items.forEach(order => {
      const el = document.createElement('div');
      el.className = 'order-item';

      let statusColor = '#888';
      if (order.status === 'new') statusColor = '#28a745';
      if (order.status === 'taken') statusColor = '#f39c12';
      if (order.status === 'done') statusColor = '#3498db';

      el.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom: 6px;">
          <span style="font-weight:bold; color:#fff;">#${order.id}</span>
          <span class="status-badge" style="color:${statusColor}; border:1px solid ${statusColor}">${order.status}</span>
        </div>
        <div style="font-size: 13px; color: #ccc;">
          <div>📍 <b>Откуда:</b> ${order.from_address}</div>
          <div>🏁 <b>Куда:</b> ${order.to_address}</div>
          <div style="margin-top:4px; color:#fff;">💰 ${order.price} сом</div>
        </div>
      `;
      ordersContainer.appendChild(el);
    });

  } catch (e) {
    ordersContainer.innerHTML = `<div style="color:#ff5555; text-align:center;">Ошибка: ${e.message}</div>`;
  }
}

// 5. Обработчики кнопок

// Регистрация
btnRegister.onclick = async () => {
  const role = document.getElementById('role').value;
  const phone = document.getElementById('phone').value.trim();

  if (!phone) {
    alert('Пожалуйста, введите номер телефона');
    return;
  }

  btnRegister.disabled = true;
  btnRegister.textContent = 'Сохранение...';

  try {
    await api('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ role, phone })
    });
    location.reload();
  } catch (e) {
    alert('Ошибка: ' + e.message);
    btnRegister.disabled = false;
    btnRegister.textContent = 'Зарегистрироваться';
  }
};

// Обновить
btnReload.onclick = () => loadOrders();

// Открыть форму создания
btnNew.onclick = () => {
  appEl.classList.add('hidden');
  newOrderEl.classList.remove('hidden');
};

// Закрыть форму создания
btnCancel.onclick = () => {
  newOrderEl.classList.add('hidden');
  appEl.classList.remove('hidden');
};

// Отправить заказ
btnCreate.onclick = async () => {
  const payload = {
    from_address: document.getElementById('from_address').value,
    shop_contact: document.getElementById('shop_contact').value,
    to_address: document.getElementById('to_address').value,
    client_name: document.getElementById('client_name').value,
    client_phone: document.getElementById('client_phone').value,
    price: parseFloat(document.getElementById('price').value || '0')
  };

  if (!payload.from_address || !payload.to_address) {
    alert('Заполните адреса!');
    return;
  }

  btnCreate.disabled = true;
  btnCreate.textContent = 'Создание...';

  try {
    await api('/api/orders', { method: 'POST', body: JSON.stringify(payload) });
    alert('Заказ создан!');

    document.querySelectorAll('#newOrder input').forEach(i => i.value = '');

    newOrderEl.classList.add('hidden');
    appEl.classList.remove('hidden');
    loadOrders();
  } catch (e) {
    alert('Ошибка: ' + e.message);
  } finally {
    btnCreate.disabled = false;
    btnCreate.textContent = 'Создать';
  }
};

// Запуск
boot();
