import requests
import urllib.parse
import re

# Ссылки на внешние сабки, откуда качаем новые конфиги
SUBSCRIPTIONS = [
    "https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://raw.githack.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS_mobile.txt",
    "https://raw.githack.com/igareck/vpn-configs-for-russia/main/BLACK_SS%2BAll_RUS.txt"
]

# Жесткие маркеры из твоего файла sub.txt (они всегда на своих местах)
MARKER_NORMAL = "socks://0g==@1488.88.88.88:443#Обычные сервера⬇️"
MARKER_WHITE  = "socks://0g==@52.52.52.52:443#Белые списки⬇️"

# Реальные белые SNI для РФ
# Реальные белые SNI для РФ
WHITE_SNI_KEYWORDS = [
    "gosuslugi", "gov", "mos", "nalog", "pfr", "zakupki", "digital",
    "yandex", "ya", "vk", "mail", "ok", "rambler",
    "sber", "sberbank", "vtb", "tinkoff", "t-bank", "tbank", "alfabank", "alfa", "raiffeisen", 
    "rshb", "gazprombank", "gpb", "nspk", "mir", "cbr",
    "mts", "megafon", "beeline", "tele2", "rt", "rostelecom", "domru",
    "ru-central", "yandexcloud", "vkcloud", "selectel", "beget", "reg", "nic", "cloud",
    "ozon", "wildberries", "avito", "lamoda", "sbermegamarket", "aliexpress", "magnit", "5ka",
    "rutube", "kinopoisk", "ivi", "okko", "vkvideo", "dzen", "tass", "ria", "rbc",
    "uchebnik", "sdamgia", "foxford", "skyeng", "geekbrains", "skillbox",
    "max"
]

# Твоя полная база стран
COUNTRY_BASE = {
    "afghanistan": ("🇦🇫", "Afghanistan"), "albania": ("🇦🇱", "Albania"), "algeria": ("🇩🇿", "Algeria"),
    "andorra": ("🇦🇩", "Andorra"), "angola": ("🇦🇴", "Angola"), "argentina": ("🇦🇷", "Argentina"),
    "armenia": ("🇦🇲", "Armenia"), "australia": ("🇦🇺", "Australia"), "austria": ("🇦🇹", "Austria"),
    "azerbaijan": ("🇦🇿", "Azerbaijan"), "bahamas": ("🇧🇸", "Bahamas"), "bahrain": ("🇧🇭", "Bahrain"),
    "bangladesh": ("🇧🇩", "Bangladesh"), "belarus": ("🇧🇾", "Belarus"), "belgium": ("🇧🇪", "Belgium"),
    "bolivia": ("🇧🇴", "Bolivia"), "bosnia": ("🇧🇦", "Bosnia"), "brazil": ("🇧🇷", "Brazil"),
    "bulgaria": ("🇧🇬", "Bulgaria"), "cambodia": ("🇰🇭", "Cambodia"), "cameroon": ("🇨🇲", "Cameroon"),
    "canada": ("🇨🇦", "Canada"), "chile": ("🇨🇱", "Chile"), "china": ("🇨🇳", "China"),
    "colombia": ("🇨🇴", "Colombia"), "costa rica": ("🇨🇷", "Costa Rica"), "croatia": ("🇭🇷", "Croatia"),
    "cuba": ("🇨🇺", "Cuba"), "cyprus": ("🇨🇾", "Cyprus"), "czechia": ("🇨🇿", "Czechia"),
    "czech": ("🇨🇿", "Czech Republic"), "denmark": ("🇩🇰", "Denmark"), "dominican": ("🇩🇴", "Dominican Republic"),
    "ecuador": ("🇪🇨", "Ecuador"), "egypt": ("🇪🇬", "Egypt"), "estonia": ("🇪🇪", "Estonia"),
    "ethiopia": ("🇪🇹", "Ethiopia"), "finland": ("🇫🇮", "Finland"), "france": ("🇫🇷", "France"),
    "georgia": ("🇬🇪", "Georgia"), "germany": ("🇩🇪", "Germany"), "ghana": ("🇬🇭", "Ghana"),
    "greece": ("🇬🇷", "Greece"), "guatemala": ("🇬🇹", "Guatemala"), "honduras": ("🇭🇳", "Honduras"),
    "hong kong": ("🇭🇰", "Hong Kong"), "hungary": ("🇭🇺", "Hungary"), "iceland": ("🇮🇸", "Iceland"),
    "india": ("🇮🇳", "India"), "indonesia": ("🇮🇩", "Indonesia"), "iran": ("🇮🇷", "Iran"),
    "iraq": ("🇮🇶", "Iraq"), "ireland": ("🇮🇪", "Ireland"), "israel": ("🇮🇱", "Israel"),
    "italy": ("🇮🇹", "Italy"), "jamaica": ("🇯🇲", "Jamaica"), "japan": ("🇯🇵", "Japan"),
    "jordan": ("🇯🇴", "Jordan"), "kazakhstan": ("🇰🇿", "Kazakhstan"), "kenya": ("🇰🇪", "Kenya"),
    "korea": ("🇰🇷", "South Korea"), "kuwait": ("🇰🇼", "Kuwait"), "kyrgyzstan": ("🇰🇬", "Kyrgyzstan"),
    "laos": ("🇱🇦", "Laos"), "latvia": ("🇱🇻", "Latvia"), "lebanon": ("🇱🇧", "Lebanon"),
    "libya": ("🇱🇾", "Libya"), "liechtenstein": ("🇱🇮", "Liechtenstein"), "lithuania": ("🇱🇹", "Lithuania"),
    "luxembourg": ("🇱🇺", "Luxembourg"), "madagascar": ("🇲🇬", "Madagascar"), "malaysia": ("🇲🇾", "Malaysia"),
    "maldives": ("🇲🇻", "Maldives"), "malta": ("🇲🇹", "Malta"), "mexico": ("🇲🇽", "Mexico"),
    "moldova": ("🇲🇩", "Moldova"), "monaco": ("🇲🇨", "Monaco"), "mongolia": ("🇲🇳", "Mongolia"),
    "montenegro": ("🇲🇪", "Montenegro"), "morocco": ("🇲🇦", "Morocco"), "myanmar": ("🇲🇲", "Myanmar"),
    "nepal": ("🇳🇵", "Nepal"), "netherlands": ("🇳🇱", "Netherlands"), "new zealand": ("🇳🇿", "New Zealand"),
    "nicaragua": ("🇳🇮", "Nicaragua"), "nigeria": ("🇳🇬", "Nigeria"), "norway": ("🇳🇴", "Norway"),
    "oman": ("🇴🇲", "Oman"), "pakistan": ("🇵🇰", "Pakistan"), "panama": ("🇵🇦", "Panama"),
    "paraguay": ("🇵🇾", "Paraguay"), "peru": ("🇵🇪", "Peru"), "philippines": ("🇵🇭", "Philippines"),
    "poland": ("🇵🇱", "Poland"), "portugal": ("🇵🇹", "Portugal"), "qatar": ("🇶🇦", "Qatar"),
    "romania": ("🇷🇴", "Romania"), "russia": ("🇷🇺", "Russia"), "saudi arabia": ("🇸🇦", "Saudi Arabia"),
    "serbia": ("🇷🇸", "Serbia"), "singapore": ("🇸🇬", "Singapore"), "slovakia": ("🇸🇰", "Slovakia"),
    "slovenia": ("🇸🇮", "Slovenia"), "south africa": ("🇿🇦", "South Africa"), "spain": ("🇪🇸", "Spain"),
    "sri lanka": ("🇱🇰", "Sri Lanka"), "sudan": ("🇸🇩", "Sudan"), "sweden": ("🇸🇪", "Sweden"),
    "switzerland": ("🇨🇭", "Switzerland"), "syria": ("🇸🇾", "Syria"), "taiwan": ("🇹🇼", "Taiwan"),
    "tajikistan": ("🇹🇯", "Tajikistan"), "tanzania": ("🇹🇿", "Tanzania"), "thailand": ("🇹🇭", "Thailand"),
    "tunisia": ("🇹🇳", "Tunisia"), "turkey": ("🇹🇷", "Turkey"), "turkmenistan": ("🇹🇲", "Turkmenistan"),
    "uae": ("🇦🇪", "UAE"), "ukraine": ("🇺🇦", "Ukraine"), "united kingdom": ("🇬🇧", "United Kingdom"),
    "uk": ("🇬🇧", "UK"), "usa": ("🇺🇸", "USA"), "united states": ("🇺🇸", "United States"),
    "uzbekistan": ("🇺🇿", "Uzbekistan"), "venezuela": ("🇻🇪", "Venezuela"), "vietnam": ("🇻🇳", "Vietnam"),
    "yemen": ("🇾🇪", "Yemen"), "zambia": ("🇿🇲", "Zambia"), "zimbabwe": ("🇿🇼", "Zimbabwe")
}

def get_sni_from_config(config_str):
    """Извлекает SNI из параметров конфигурации"""
    try:
        if "?" in config_str:
            query_part = config_str.split("?")[1].split("#")[0]
            params = urllib.parse.parse_qs(query_part)
            if "sni" in params: return params["sni"][0].lower()
            if "peer" in params: return params["peer"][0].lower()
    except:
        pass
    return ""

def process_config_line(line):
    """Ищет страну в названии конфига по базе COUNTRY_BASE и форматирует её"""
    if "#" not in line:
        return line
        
    base_part, name_part = line.split("#", 1)
    name_part_lower = name_part.lower()
    
    # Пропускаем наши маркеры-заголовки
    if "обычные сервера" in name_part_lower or "белые списки" in name_part_lower:
        return line

    # Проходим по твоей базе стран
    for country_key, (flag, std_name) in COUNTRY_BASE.items():
        if re.search(r'\b' + re.escape(country_key) + r'\b', name_part_lower):
            # Удаляем старое упоминание страны, чтобы имя не дублировалось
            cleaned_name = re.sub(r'\b' + re.escape(country_key) + r'\b', '', name_part, flags=re.IGNORECASE).strip()
            cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
            
            if cleaned_name:
                new_name = f"{cleaned_name} {flag} {std_name}"
            else:
                new_name = f"{flag} {std_name}"
                
            return f"{base_part}#{new_name}"
            
    return line

def parse_and_build_sub():
    normal_servers = []
    white_list_servers = []

    print("🚀 Скачиваю новые конфиги и запускаю фильтрацию по базе стран...")

    for url in SUBSCRIPTIONS:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200: continue
                
            for line in response.text.splitlines():
                line = line.strip()
                if not line: continue
                
                # Защита: не трогаем и не дублируем наши маркерные IP
                if "1488.88.88.88" in line or "52.52.52.52" in line or "⬇️" in line:
                    continue
                
                # Проверяем, что это валидный конфиг
                if not any(p in line.lower() for p in ["vless://", "ss://", "vmess://", "trojan://"]):
                    continue

                # Форматируем название страны (добавляем флаг)
                line = process_config_line(line)

                # Сортируем в зависимости от SNI
                sni = get_sni_from_config(line)
                is_white = any(keyword in sni for keyword in WHITE_SNI_KEYWORDS)
                
                if is_white:
                    white_list_servers.append(line)
                else:
                    normal_servers.append(line)
        except Exception as e:
            print(f"Ошибка при обработке источника {url}: {e}")

    # Перезаписываем sub.txt строго по структуре твоего GitHub
    with open("sub.txt", "w", encoding="utf-8") as f:
        # Строка 1: Маркер обычных серверов
        f.write(MARKER_NORMAL + "\n")
        for cfg in normal_servers:
            f.write(cfg + "\n")
            
        # Пустые строки между блоками
        f.write("\n\n")
        
        # Строка 5: Маркер белых списков
        f.write(MARKER_WHITE + "\n")
        for cfg in white_list_servers:
            f.write(cfg + "\n")

    print("\n📊 Сборка sub.txt завершена!")
    print(f"📍 Обычных серверов записано: {len(normal_servers)} шт.")
    print(f"📍 Серверов в белом списке: {len(white_list_servers)} шт.")

if __name__ == "__main__":
    parse_and_build_sub()
