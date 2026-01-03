import urllib.parse
from typing import Optional


def html_report(order_id: int, o: dict, courier_name: Optional[str] = None, include_log: bool = True) -> str:
    apt = o.get("to_apt") or "—"
    price_display = int(o.get("price") or 0)
    log_content = o.get("log") or "Лог пуст."

    def clickable(addr: str | None) -> str:
        if not addr:
            return "Н/Д"
        enc = urllib.parse.quote_plus(addr)
        return f"<a href='https://yandex.ru/maps/?text={enc}'>{addr}</a>"

    header = f"<b>ЗАКАЗ #{order_id}</b>"
    if o.get("return_for"):
        header = f"↩️ <b>ВОЗВРАТ #{o['return_for']}.{order_id}</b> (к заказу #{o['return_for']})"

    report = (
        f"{header}

"
        f"<b>Статус:</b> {str(o.get('status','')).upper()}
"
        f"<b>Цена:</b> {price_display} ₽
"
        f"<b>Курьер:</b> {courier_name or '—'}

"
        f"<b>ОТПРАВИТЕЛЬ</b>
"
        f"Адрес: {clickable(o.get('from_address'))}
"
        f"Контакт: {o.get('shop_contact','')}

"
        f"<b>ПОЛУЧАТЕЛЬ</b>
"
        f"Адрес: {clickable(o.get('to_address'))} (кв: {apt})
"
        f"Имя: {o.get('client_name','')}
"
        f"Телефон: {o.get('client_phone','')}
"
    )

    if include_log:
        report += f"
<b>ЛОГ:</b>
<pre>{log_content}</pre>"

    return report