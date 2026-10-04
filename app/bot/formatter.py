from typing import Dict, Any

def format_telegram_report(data: Dict[str, Any]) -> str:
    plate = data.get("plate")
    vin = data.get("vin")
    summary = data.get("summary", {}) or {}

    car_name = summary.get("car_name") or "Транспортное средство"
    year = f", {summary.get('year')}" if summary.get("year") else ""
    color = f" ({summary.get('color')})" if summary.get("color") else ""

    lines = []
    lines.append(f"🚘 <b>{car_name}{year}{color}</b>")
    
    id_parts = []
    if plate: id_parts.append(f"🇰🇬 <code>{plate}</code>")
    if vin: id_parts.append(f"🔑 <code>{vin}</code>")
    lines.append(" | ".join(id_parts) + "\n")

    lines.append("<b>СВОДКА ПО РЕЕСТРАМ:</b>")

    # 1. Секция Tolom.kg (Штрафы и владение)
    tolom = data.get("tolom")
    if tolom is not None:
        if tolom.get("success"):
            fines = tolom.get("fines", {})
            f_count = fines.get("count", 0)
            f_sum = fines.get("total_sum", 0.0)

            if f_count > 0:
                lines.append(f"• <b>Штрафы ГУОБДД:</b> 🔴 {f_count} шт. на {f_sum:,.0f} сом")
                if fines.get("protocols"):
                    p0 = fines["protocols"][0]
                    lines.append(f"  └ <i>Посл.: {p0.get('title')} ({p0.get('amount_to_pay', 0):,.0f} с)</i>")
            else:
                lines.append("• <b>Штрафы ГУОБДД:</b> 🟢 Задолженностей нет")

            # Аресты
            if tolom.get("has_arrest"):
                lines.append("• <b>Обременения/Арест:</b> 🔴 <b>ЕСТЬ АРЕСТ</b>")
            else:
                lines.append("• <b>Обременения/Арест:</b> 🟢 Чисто")

            # Тонировка
            tint = tolom.get("tinting", "")
            if "Разрешение отсутствует" in tint or not tint:
                lines.append("• <b>Тонировка:</b> ⚪ Не оформлена")
            else:
                lines.append(f"• <b>Тонировка:</b> 🟢 {tint}")

            # Владельцы
            periods = tolom.get("ownership_periods", [])
            if periods:
                lines.append(f"• <b>Периодов регистрации в КР:</b> {len(periods)}")
        else:
            lines.append(f"• <b>Tolom.kg:</b> ⚪ {tolom.get('message', 'Данных не найдено')}")
    else:
        lines.append("• <b>Штрафы/Аресты (Tolom.kg):</b> ⚠️ <b>Требуется госномер</b>")

    # 2. Секция Таможня КР
    customs = data.get("customs")
    if customs is not None:
        if customs.get("found"):
            solution = customs.get("solution", "ВЫПУСК РАЗРЕШЕН")
            doc_type = customs.get("document_type", "ДТ")
            date_str = customs.get("issue_date", "")[:10] if customs.get("issue_date") else ""
            d_info = f" ({date_str})" if date_str else ""
            lines.append(f"• <b>Таможня КР:</b> 🟢 {solution}{d_info}")
        else:
            lines.append("• <b>Таможня КР:</b> ⚪ В реестре оформления не числится")
    else:
        lines.append("• <b>Таможня КР:</b> ⚠️ <b>Требуется VIN</b>")

    # 3. Секция Реестр Кореи
    korea = data.get("korea")
    if korea is not None:
        if korea.get("found"):
            mileage = korea.get("export_mileage")
            exp_date = korea.get("export_date", "")
            m_text = f", пробег {mileage}" if (mileage and mileage != "Не зафиксирован") else ""
            lines.append(f"• <b>Реестр Южной Кореи:</b> 🔵 Вывезен {exp_date}{m_text}")
        else:
            lines.append("• <b>Реестр Южной Кореи:</b> ⚪ В реестре экспорта не найден")
    else:
        lines.append("• <b>Реестр Южной Кореи:</b> ⚠️ <b>Требуется VIN</b>")

    # 4. Секция Аукционы Copart / IAAI
    auction = data.get("autopartner")
    if auction is not None:
        if auction.get("found"):
            photos_count = len(auction.get("images", []))
            odo = f", {auction.get('odometer')}" if auction.get('odometer') else ""
            lines.append(f"• <b>Аукцион США (Copart/IAAI):</b> 🟡 Найден лот (📷 {photos_count} фото{odo})")
        else:
            lines.append("• <b>Аукцион США (Copart/IAAI):</b> ⚪ В архиве торгов не найден")
    else:
        lines.append("• <b>Аукцион США (Copart/IAAI):</b> ⚠️ <b>Требуется VIN</b>")

    # Подсказка если введен только один идентификатор
    if not plate or not vin:
        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚠️ <b>ОТЧЕТ НЕПОЛНЫЙ</b>")
        if not vin:
            lines.append("<i>VIN не указан — Таможня КР, Корея и Copart пропущены.</i>")
        if not plate:
            lines.append("<i>Госномер не указан — Штрафы и аресты Tolom.kg пропущены.</i>")
        
        sample_plate = plate or "01KG555ADF"
        sample_vin = vin or "1FTEW1E55KFB29513"
        lines.append(f"\n💡 <b>Для полной проверки отправьте:</b>\n<code>{sample_plate} {sample_vin}</code>")

    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📊 <i>Подробная детализация протоколов, таможни и фото в Mini App:</i>")

    return "\n".join(lines)
