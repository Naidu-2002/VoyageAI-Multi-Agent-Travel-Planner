import os
import re
import certifi
import airportsdata
import unicodedata
import pycountry
import requests
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DFW")

BASE_URL = "http://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")

def _normalize_country_alias(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


COUNTRY_ALIASES = {}
for country in pycountry.countries:
    for alias in (
        country.name,
        country.alpha_2,
        country.alpha_3,
        country.numeric,
        getattr(country, "official_name", None),
        getattr(country, "common_name", None),
    ):
        if alias:
            COUNTRY_ALIASES[_normalize_country_alias(alias)] = country.alpha_2

COUNTRY_ALIASES.update(
    {
        _normalize_country_alias(alias): country_code
        for country_code, aliases in {
            "US": (
                "America",
                "U.S.",
                "U.S.A.",
                "United States of America",
                "US of A",
            ),
            "GB": (
                "Britain",
                "Great Britain",
                "UK",
                "U.K.",
                "United Kingdom",
                "United Kingdom of Great Britain and Northern Ireland",
                "England",
                "Scotland",
                "Wales",
                "Northern Ireland",
            ),
            "KR": (
                "Korea",
                "South Korea",
                "Korea South",
                "Republic of Korea",
                "ROK",
            ),
            "KP": (
                "North Korea",
                "Korea North",
                "DPRK",
                "Democratic People's Republic of Korea",
            ),
            "RU": ("Russia",),
            "AE": ("UAE", "Emirates"),
            "SA": ("KSA", "Saudi Arabia"),
            "CN": ("PRC", "People's Republic of China"),
            "CZ": ("Czech Republic",),
            "TR": ("Turkey",),
            "CI": ("Ivory Coast",),
            "CV": ("Cape Verde",),
            "MM": ("Burma",),
            "SZ": ("Swaziland",),
            "MK": ("Macedonia",),
            "NL": ("Holland",),
            "LA": ("Laos",),
            "VN": ("Vietnam",),
            "SY": ("Syria",),
            "TZ": ("Tanzania",),
            "MD": ("Moldova",),
            "BO": ("Bolivia",),
            "VE": ("Venezuela",),
            "IR": ("Iran",),
            "BN": ("Brunei",),
            "TL": ("East Timor",),
            "FM": ("Micronesia",),
            "CD": (
                "DR Congo",
                "Democratic Republic of the Congo",
                "Congo Kinshasa",
            ),
            "CG": ("Republic of the Congo", "Congo Brazzaville"),
            "PS": ("Palestine",),
            "VA": ("Vatican City",),
            "TW": ("Taiwan",),
            "MO": ("Macau",),
            "BS": ("Bahamas",),
            "GM": ("Gambia",),
        }.items()
        for alias in aliases
    }
)

COUNTRY_MAIN_AIRPORTS = {
    "AE": "DXB",
    "AF": "KBL",
    "AG": "ANU",
    "AI": "AXA",
    "AL": "TIA",
    "AM": "EVN",
    "AO": "LAD",
    "AR": "EZE",
    "AS": "PPG",
    "AT": "VIE",
    "AU": "SYD",
    "AW": "AUA",
    "AX": "MHQ",
    "AZ": "GYD",
    "BA": "SJJ",
    "BB": "BGI",
    "BD": "DAC",
    "BE": "BRU",
    "BF": "OUA",
    "BG": "SOF",
    "BH": "BAH",
    "BI": "BJM",
    "BJ": "COO",
    "BL": "SBH",
    "BM": "BDA",
    "BN": "BWN",
    "BO": "VVI",
    "BQ": "BON",
    "BR": "GRU",
    "BS": "NAS",
    "BT": "PBH",
    "BW": "GBE",
    "BY": "MSQ",
    "BZ": "BZE",
    "CA": "YYZ",
    "CC": "CCK",
    "CD": "FIH",
    "CF": "BGF",
    "CG": "BZV",
    "CH": "ZRH",
    "CI": "ABJ",
    "CK": "RAR",
    "CL": "SCL",
    "CM": "DLA",
    "CN": "PEK",
    "CO": "BOG",
    "CR": "SJO",
    "CU": "HAV",
    "CV": "SID",
    "CW": "CUR",
    "CY": "LCA",
    "CZ": "PRG",
    "DE": "FRA",
    "DJ": "JIB",
    "DK": "CPH",
    "DM": "DOM",
    "DO": "SDQ",
    "DZ": "ALG",
    "EC": "UIO",
    "EE": "TLL",
    "EG": "CAI",
    "EH": "VIL",
    "ER": "ASM",
    "ES": "MAD",
    "ET": "ADD",
    "FI": "HEL",
    "FJ": "NAN",
    "FK": "MPN",
    "FM": "PNI",
    "FO": "FAE",
    "FR": "CDG",
    "GA": "LBV",
    "GB": "LHR",
    "GD": "GND",
    "GE": "TBS",
    "GF": "CAY",
    "GG": "GCI",
    "GH": "ACC",
    "GI": "GIB",
    "GL": "GOH",
    "GM": "BJL",
    "GN": "CKY",
    "GP": "PTP",
    "GQ": "SSG",
    "GR": "ATH",
    "GT": "GUA",
    "GU": "GUM",
    "GW": "OXB",
    "GY": "GEO",
    "HK": "HKG",
    "HN": "SAP",
    "HR": "ZAG",
    "HT": "PAP",
    "HU": "BUD",
    "ID": "CGK",
    "IE": "DUB",
    "IL": "TLV",
    "IM": "IOM",
    "IN": "DEL",
    "IQ": "BGW",
    "IR": "IKA",
    "IS": "KEF",
    "IT": "FCO",
    "JE": "JER",
    "JM": "MBJ",
    "JO": "AMM",
    "JP": "HND",
    "KE": "NBO",
    "KG": "BSZ",
    "KH": "KTI",
    "KI": "TRW",
    "KM": "HAH",
    "KN": "SKB",
    "KP": "FNJ",
    "KR": "ICN",
    "KW": "KWI",
    "KY": "GCM",
    "KZ": "ALA",
    "LA": "VTE",
    "LB": "BEY",
    "LC": "UVF",
    "LK": "CMB",
    "LR": "ROB",
    "LS": "MSU",
    "LT": "VNO",
    "LU": "LUX",
    "LV": "RIX",
    "LY": "MJI",
    "MA": "CMN",
    "MD": "RMO",
    "ME": "TGD",
    "MF": "SFG",
    "MG": "TNR",
    "MH": "MAJ",
    "MK": "SKP",
    "ML": "BKO",
    "MM": "RGN",
    "MN": "UBN",
    "MO": "MFM",
    "MP": "SPN",
    "MQ": "FDF",
    "MR": "NKC",
    "MS": "MNI",
    "MT": "MLA",
    "MU": "MRU",
    "MV": "MLE",
    "MW": "LLW",
    "MX": "MEX",
    "MY": "KUL",
    "MZ": "MPM",
    "NA": "WDH",
    "NC": "NOU",
    "NE": "NIM",
    "NG": "LOS",
    "NI": "MGA",
    "NL": "AMS",
    "NO": "OSL",
    "NP": "KTM",
    "NR": "INU",
    "NU": "IUE",
    "NZ": "AKL",
    "OM": "MCT",
    "PA": "PTY",
    "PE": "LIM",
    "PF": "PPT",
    "PG": "POM",
    "PH": "MNL",
    "PK": "ISB",
    "PL": "WAW",
    "PM": "FSP",
    "PR": "SJU",
    "PT": "LIS",
    "PW": "ROR",
    "PY": "ASU",
    "QA": "DOH",
    "RE": "RUN",
    "RO": "OTP",
    "RS": "BEG",
    "RU": "SVO",
    "RW": "KGL",
    "SA": "JED",
    "SB": "HIR",
    "SC": "SEZ",
    "SD": "KRT",
    "SE": "ARN",
    "SG": "SIN",
    "SH": "HLE",
    "SI": "LJU",
    "SK": "BTS",
    "SL": "FNA",
    "SN": "DSS",
    "SO": "MGQ",
    "SR": "PBM",
    "SS": "JUB",
    "ST": "TMS",
    "SV": "SAL",
    "SX": "SXM",
    "SY": "DAM",
    "SZ": "MTS",
    "TC": "PLS",
    "TD": "NDJ",
    "TG": "LFW",
    "TH": "BKK",
    "TJ": "DYU",
    "TL": "DIL",
    "TM": "ASB",
    "TN": "TUN",
    "TO": "TBU",
    "TR": "IST",
    "TT": "POS",
    "TV": "FUN",
    "TW": "TPE",
    "TZ": "DAR",
    "UA": "KBP",
    "UG": "EBB",
    "US": "ATL",
    "UY": "MVD",
    "UZ": "TAS",
    "VC": "SVD",
    "VE": "CCS",
    "VG": "EIS",
    "VI": "STT",
    "VN": "SGN",
    "VU": "VLI",
    "WF": "WLS",
    "WS": "APW",
    "YE": "SAH",
    "YT": "DZA",
    "ZA": "JNB",
    "ZM": "LUN",
    "ZW": "HRE",
}

def _normalize_city_name(city: str) -> str:
    return re.sub(r"[^\w]+", " ", city.casefold()).strip()


# Keys are (ISO alpha-2 country code, normalized city name).
CITY_MAIN_AIRPORTS = {
    ("AE", "abu dhabi"): "AUH",
    ("AE", "dubai"): "DXB",
    ("AF", "kabul"): "KBL",
    ("AL", "tirana"): "TIA",
    ("AM", "yerevan"): "EVN",
    ("AO", "luanda"): "LAD",
    ("AR", "buenos aires"): "EZE",
    ("AT", "vienna"): "VIE",
    ("AU", "adelaide"): "ADL",
    ("AU", "brisbane"): "BNE",
    ("AU", "melbourne"): "MEL",
    ("AU", "perth"): "PER",
    ("AU", "sydney"): "SYD",
    ("AZ", "baku"): "GYD",
    ("BD", "dhaka"): "DAC",
    ("BE", "brussels"): "BRU",
    ("BG", "sofia"): "SOF",
    ("BH", "manama"): "BAH",
    ("BO", "la paz"): "LPB",
    ("BO", "santa cruz"): "VVI",
    ("BR", "sao paulo"): "GRU",
    ("BR", "são paulo"): "GRU",
    ("BR", "brasilia"): "BSB",
    ("BR", "rio de janeiro"): "GIG",
    ("BW", "gaborone"): "GBE",
    ("CA", "calgary"): "YYC",
    ("CA", "edmonton"): "YEG",
    ("CA", "montreal"): "YUL",
    ("CA", "ottawa"): "YOW",
    ("CA", "quebec city"): "YQB",
    ("CA", "toronto"): "YYZ",
    ("CA", "vancouver"): "YVR",
    ("CD", "kinshasa"): "FIH",
    ("CH", "geneva"): "GVA",
    ("CH", "zurich"): "ZRH",
    ("CI", "abidjan"): "ABJ",
    ("CL", "santiago"): "SCL",
    ("CM", "douala"): "DLA",
    ("CN", "beijing"): "PEK",
    ("CN", "shanghai"): "PVG",
    ("CO", "bogota"): "BOG",
    ("CO", "medellin"): "MDE",
    ("CZ", "prague"): "PRG",
    ("DE", "berlin"): "BER",
    ("DE", "frankfurt"): "FRA",
    ("DE", "munich"): "MUC",
    ("DK", "copenhagen"): "CPH",
    ("DZ", "algiers"): "ALG",
    ("EC", "guayaquil"): "GYE",
    ("EC", "quito"): "UIO",
    ("EE", "tallinn"): "TLL",
    ("EG", "cairo"): "CAI",
    ("ES", "barcelona"): "BCN",
    ("ES", "madrid"): "MAD",
    ("ET", "addis ababa"): "ADD",
    ("FI", "helsinki"): "HEL",
    ("FJ", "nadi"): "NAN",
    ("FR", "lyon"): "LYS",
    ("FR", "paris"): "CDG",
    ("GB", "edinburgh"): "EDI",
    ("GB", "london"): "LHR",
    ("GB", "manchester"): "MAN",
    ("GE", "tbilisi"): "TBS",
    ("GH", "accra"): "ACC",
    ("GR", "athens"): "ATH",
    ("HK", "hong kong"): "HKG",
    ("HR", "zagreb"): "ZAG",
    ("HU", "budapest"): "BUD",
    ("ID", "jakarta"): "CGK",
    ("IE", "dublin"): "DUB",
    ("IL", "tel aviv"): "TLV",
    ("IN", "ahmedabad"): "AMD",
    ("IN", "bangalore"): "BLR",
    ("IN", "bengaluru"): "BLR",
    ("IN", "chennai"): "MAA",
    ("IN", "delhi"): "DEL",
    ("IN", "hyderabad"): "HYD",
    ("IN", "kolkata"): "CCU",
    ("IN", "mumbai"): "BOM",
    ("IR", "tehran"): "IKA",
    ("IS", "reykjavik"): "KEF",
    ("IT", "milan"): "MXP",
    ("IT", "rome"): "FCO",
    ("JP", "osaka"): "KIX",
    ("JP", "tokyo"): "HND",
    ("KE", "nairobi"): "NBO",
    ("KH", "phnom penh"): "KTI",
    ("KH", "siem reap"): "SAI",
    ("KR", "seoul"): "ICN",
    ("KW", "kuwait city"): "KWI",
    ("KZ", "almaty"): "ALA",
    ("LK", "colombo"): "CMB",
    ("LU", "luxembourg"): "LUX",
    ("MA", "casablanca"): "CMN",
    ("MA", "marrakech"): "RAK",
    ("MG", "antananarivo"): "TNR",
    ("MM", "yangon"): "RGN",
    ("MN", "ulaanbaatar"): "UBN",
    ("MU", "port louis"): "MRU",
    ("MX", "cancun"): "CUN",
    ("MX", "guadalajara"): "GDL",
    ("MX", "mexico city"): "MEX",
    ("MX", "monterrey"): "MTY",
    ("MY", "kuala lumpur"): "KUL",
    ("MZ", "maputo"): "MPM",
    ("NA", "windhoek"): "WDH",
    ("NG", "lagos"): "LOS",
    ("NL", "amsterdam"): "AMS",
    ("NO", "oslo"): "OSL",
    ("NP", "kathmandu"): "KTM",
    ("NZ", "auckland"): "AKL",
    ("NZ", "wellington"): "WLG",
    ("OM", "muscat"): "MCT",
    ("PE", "lima"): "LIM",
    ("PG", "port moresby"): "POM",
    ("PH", "manila"): "MNL",
    ("PK", "islamabad"): "ISB",
    ("PK", "karachi"): "KHI",
    ("PK", "lahore"): "LHE",
    ("PL", "krakow"): "KRK",
    ("PL", "warsaw"): "WAW",
    ("PT", "lisbon"): "LIS",
    ("PT", "porto"): "OPO",
    ("PY", "asuncion"): "ASU",
    ("QA", "doha"): "DOH",
    ("RO", "bucharest"): "OTP",
    ("RS", "belgrade"): "BEG",
    ("RU", "moscow"): "SVO",
    ("RU", "saint petersburg"): "LED",
    ("RW", "kigali"): "KGL",
    ("SA", "jeddah"): "JED",
    ("SA", "riyadh"): "RUH",
    ("SE", "stockholm"): "ARN",
    ("SG", "singapore"): "SIN",
    ("SN", "dakar"): "DSS",
    ("TH", "bangkok"): "BKK",
    ("TN", "tunis"): "TUN",
    ("TO", "nuku alofa"): "TBU",
    ("TR", "istanbul"): "IST",
    ("TW", "taipei"): "TPE",
    ("TZ", "dar es salaam"): "DAR",
    ("TZ", "zanzibar"): "ZNZ",
    ("UA", "kyiv"): "KBP",
    ("UG", "kampala"): "EBB",
    ("US", "atlanta"): "ATL",
    ("US", "austin"): "AUS",
    ("US", "boston"): "BOS",
    ("US", "charlotte"): "CLT",
    ("US", "chicago"): "ORD",
    ("US", "dallas"): "DFW",
    ("US", "denton"): "DFW",
    ("US", "denver"): "DEN",
    ("US", "detroit"): "DTW",
    ("US", "honolulu"): "HNL",
    ("US", "houston"): "IAH",
    ("US", "las vegas"): "LAS",
    ("US", "los angeles"): "LAX",
    ("US", "miami"): "MIA",
    ("US", "minneapolis"): "MSP",
    ("US", "nashville"): "BNA",
    ("US", "new york"): "JFK",
    ("US", "orlando"): "MCO",
    ("US", "paris"): "DFW",
    ("US", "philadelphia"): "PHL",
    ("US", "phoenix"): "PHX",
    ("US", "san diego"): "SAN",
    ("US", "san francisco"): "SFO",
    ("US", "seattle"): "SEA",
    ("US", "washington dc"): "DCA",
    ("UY", "montevideo"): "MVD",
    ("UZ", "tashkent"): "TAS",
    ("VE", "caracas"): "CCS",
    ("VN", "hanoi"): "HAN",
    ("VN", "ho chi minh city"): "SGN",
    ("WS", "apia"): "APW",
    ("ZA", "cape town"): "CPT",
    ("ZA", "johannesburg"): "JNB",
    ("ZM", "lusaka"): "LUN",
    ("ZW", "harare"): "HRE",
}

def clean_text(text: str) -> str:
    """Clean travel-related text while preserving important information."""

    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # Step 1: Normalize text and convert to lowercase
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold().strip()

    # Step 2: Remove unnecessary special characters
    # Preserve $, numbers, hyphens, and apostrophes
    text = re.sub(r"[^\w\s$€£,.'-]", " ", text)

    # Step 3: Remove unnecessary travel-related words
    stop_words = {
        "flight", "flights",
        "ticket", "tickets",
        "trip", "travel",
        "plan", "planning",
        "booking", "book",
        "information", "info"
    }

    words = [
        word for word in text.split()
        if word not in stop_words
    ]

    # Step 4: Remove extra spaces
    return " ".join(words).strip()

def country_name_to_code(text: str) -> str | None:
    """
    Convert a country name or country mentioned in a sentence
    into its ISO 2-letter country code.

    Returns None if no country or multiple countries are found.
    """

    if not isinstance(text, str) or not text.strip():
        return None

    # Step 1: Normalize input using the same function as COUNTRY_ALIASES
    text = _normalize_country_alias(text)

    # Step 2: Check for an exact match in COUNTRY_ALIASES
    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    # Step 3: Try pycountry's built-in lookup
    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # Step 4: Search for country names inside longer sentences
    matches = set()

    for alias, code in COUNTRY_ALIASES.items():

        # Skip short aliases to avoid false matches
        if len(alias) < 4:
            continue

        # Match complete country names, not parts of other words
        pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

        if re.search(pattern, text):
            matches.add(code)

    # Step 5: Return the code if exactly one country was found
    if len(matches) == 1:
        return matches.pop()

    # Step 6: Return None if no country or multiple countries were found
    return None

def airport_country_matches(airport: dict, country_code: str) -> bool:
    """
    Check whether an airport belongs to the specified country.
    Supports country codes and full country names.
    """

    # Get the country from airport data
    airport_country = airport.get("country", "")

    # Convert airport country to a 2-letter country code
    airport_code = country_name_to_code(str(airport_country))

    # Convert the requested country to a 2-letter country code
    requested_code = country_name_to_code(country_code)

    # Compare only when both country codes are valid
    if airport_code is None or requested_code is None:
        return False

    return airport_code == requested_code

def resolve_location_to_iata(location: str) -> str | None:
    """
    Convert a city, country, airport name, or IATA code
    into a valid 3-letter airport code.

    Examples:
        Dallas     -> DFW
        Hyderabad  -> HYD
        Bangladesh -> DAC
        Japan      -> NRT (if configured as preferred)
        DAC        -> DAC
    """

    if not isinstance(location, str) or not location.strip():
        return None

    raw_location = location.strip()
    location_clean = _normalize_country_alias(raw_location)

    # Step 1: Check if the input is already an IATA code
    code = raw_location.upper()

    if re.fullmatch(r"[A-Z]{3}", code) and code in AIRPORTS:
        return code

    # Step 2: Check preferred city airports
    # Supports keys like ("US", "dallas"): "DFW"
    preferred = CITY_MAIN_AIRPORTS.get(location_clean)

    if preferred is None:
        city_matches = set()

        for key, iata in CITY_MAIN_AIRPORTS.items():

            if isinstance(key, tuple) and len(key) == 2:
                country, city = key

                if _normalize_country_alias(city) == location_clean:
                    city_matches.add(iata)

        # Use the mapping only when the city is unambiguous
        if len(city_matches) == 1:
            preferred = city_matches.pop()

    if isinstance(preferred, str):
        preferred = preferred.upper()

        if preferred in AIRPORTS:
            return preferred

    # Step 3: Search for exact city or airport name
    airport_matches = []

    for iata, airport in AIRPORTS.items():

        city = _normalize_country_alias(
            str(airport.get("city") or "")
        )

        name = _normalize_country_alias(
            str(airport.get("name") or "")
        )

        score = 0

        if city == location_clean:
            score += 100

        if name == location_clean:
            score += 100

        if score > 0:

            if "international" in name:
                score += 10

            airport_matches.append((score, iata))

    if airport_matches:
        airport_matches.sort(
            key=lambda item: (-item[0], item[1])
        )

        return airport_matches[0][1]

    # Step 4: Check whether the location is a country
    country_code = country_name_to_code(raw_location)

    if country_code:
        return get_best_airport_for_country(country_code)

    # Step 5: No airport found
    return None

def get_best_airport_for_country(country_code: str) -> str | None:
    """
    Return a preferred airport for a country.

    If no preferred airport is available, select a fallback
    airport from the airport database.
    """

    # Convert country name or code into a standard country code
    country_code = country_name_to_code(country_code)

    if not country_code:
        return None

    # Step 1: Check our preferred airport dictionary
    preferred = COUNTRY_MAIN_AIRPORTS.get(country_code)

    if preferred:
        preferred = preferred.upper()

        if preferred in AIRPORTS:
            return preferred

    # Step 2: Find other airports in the country
    candidates = []

    for iata, airport in AIRPORTS.items():

        if not iata:
            continue

        if airport_country_matches(airport, country_code):

            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            # Prefer airports with international in their name
            if "international" in name:
                score += 50
            elif "intl" in name:
                score += 40

            # Give a small preference to airports with city information
            if city:
                score += 5

            candidates.append((score, iata))

    # Step 3: Return None if no airport is found
    if not candidates:
        return None

    # Step 4: Select the highest-scoring airport
    candidates.sort(key=lambda item: (-item[0], item[1]))

    return candidates[0][1]

    """
    Convert an airport code, city, airport name, or country
    into an IATA airport code.

    Examples:
        Bangladesh -> DAC
        Japan      -> NRT
        Dhaka      -> DAC
        Tokyo      -> NRT
        DAC        -> DAC
    """

    if not isinstance(location, str) or not location.strip():
        return None

    raw_location = location.strip()
    location_clean = _normalize_country_alias(raw_location)

    # Step 1: Check if the input is already a valid IATA code
    code = raw_location.upper()

    if re.fullmatch(r"[A-Z]{3}", code) and code in AIRPORTS:
        return code

    # Step 2: Check our preferred city airports
    preferred = CITY_MAIN_AIRPORTS.get(location_clean)

    if isinstance(preferred, str):
        preferred = preferred.upper()

        if preferred in AIRPORTS:
            return preferred

    # Step 3: Search the airport database for an exact city or airport name
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = _normalize_country_alias(str(airport.get("city") or ""))
        name = _normalize_country_alias(str(airport.get("name") or ""))

        score = 0

        if city == location_clean:
            score += 100

        if name == location_clean:
            score += 100

        if score > 0:
            if "international" in name:
                score += 10

            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(key=lambda item: (-item[0], item[1]))
        return city_matches[0][1]

    # Step 4: Check whether the location is a country
    country_code = country_name_to_code(raw_location)

    if country_code:
        return get_best_airport_for_country(country_code)

    # Step 5: No matching airport found
    return None

def find_location_mentions(query: str) -> list[str]:
    """
    Find country and preferred-city names inside a travel request.
    Return unique matches in the order they appear.
    """

    if not isinstance(query, str) or not query.strip():
        return []

    text = _normalize_country_alias(query)
    matches = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        normalized_alias = _normalize_country_alias(alias)

        # Skip short aliases inside sentences to reduce false matches.
        if len(normalized_alias) < 4:
            continue

        pattern = rf"(?<!\w){re.escape(normalized_alias)}(?!\w)"

        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end(), normalized_alias))

    # Preferred city names
    for city in CITY_MAIN_AIRPORTS:
        normalized_city = _normalize_country_alias(city)

        if not normalized_city:
            continue

        pattern = rf"(?<!\w){re.escape(normalized_city)}(?!\w)"

        for match in re.finditer(pattern, text):
            matches.append((match.start(), match.end(), normalized_city))

    # Prefer longer matches when names overlap.
    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    unique_mentions = []
    seen = set()
    covered_until = -1

    for start, end, name in matches:
        if start < covered_until:
            continue

        covered_until = end

        if name not in seen:
            unique_mentions.append(name)
            seen.add(name)

    return unique_mentions

def parse_route(query: str) -> tuple[str | None, str | None]:
    """
    Extract departure and arrival IATA codes from a flight request.

    Examples:
        "DAC to NRT"             -> ("DAC", "NRT")
        "from Dallas to Tokyo"   -> ("DFW", "NRT")
        "flights from Dallas"    -> ("DFW", None)
        "flights to Japan"       -> (None, "NRT")
        "all global flights"     -> (None, None)

    Note:
        (None, None) can also mean the route could not be resolved.
        search_flights() checks for that before requesting global data.
    """

    if not isinstance(query, str) or not query.strip():
        return None, None

    q = query.strip()
    q_lower = q.casefold()

    global_patterns = [
        r"\ball countries\b",
        r"\ball country\b",
        r"\bglobal flights?\b",
        r"\ball flights?\b",
        r"\bworldwide flights?\b",
        r"\bflights? worldwide\b",
    ]

    if any(re.search(pattern, q_lower) for pattern in global_patterns):
        return None, None

    # Direct airport-code route, e.g. "DAC to NRT"
    direct_route = re.fullmatch(
        r"\s*([A-Za-z]{3})\s+(?:to|->|→)\s+([A-Za-z]{3})\s*[.!?]?\s*",
        q,
        flags=re.IGNORECASE,
    )

    if direct_route:
        dep = direct_route.group(1).upper()
        arr = direct_route.group(2).upper()

        if dep in AIRPORTS and arr in AIRPORTS:
            return dep, arr

    # Explicit route: "from Dallas to Tokyo"
    match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|during|at|by)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dep = resolve_location_to_iata(match.group(1).strip())
        arr = resolve_location_to_iata(match.group(2).strip())
        return dep, arr

    # Reverse wording: "to Tokyo from Dallas"
    match = re.search(
        r"\bto\s+(.+?)\s+from\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|during|at|by)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        arr = resolve_location_to_iata(match.group(1).strip())
        dep = resolve_location_to_iata(match.group(2).strip())
        return dep, arr

    # "Plan a Japan trip from Bangladesh"
    # The destination appears before "from".
    match = re.search(
        r"\b(?:plan|book|find)\b\s+(?:a\s+)?"
        r"(?:\d+\s*[- ]?\s*days?\s+)?"
        r"(.+?)\s+(?:trip|travel|flights?)\s+from\s+(.+?)"
        r"(?=[.!?]|$)",
        q_lower,
    )

    if match:
        destination = resolve_location_to_iata(match.group(1).strip())
        origin = resolve_location_to_iata(match.group(2).strip())

        if origin or destination:
            return origin, destination

    # Single departure: "flights from Dallas"
    match = re.search(
        r"\bfrom\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|during|at|by)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dep = resolve_location_to_iata(match.group(1).strip())
        return dep, None

    # Single destination: "flights to Japan"
    match = re.search(
        r"\bto\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|during|at|by)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        arr = resolve_location_to_iata(match.group(1).strip())
        return None, arr

    # Fallback: find locations mentioned anywhere in the request.
    mentions = find_location_mentions(q)

    if len(mentions) == 1:
        destination = resolve_location_to_iata(mentions[0])

        if destination:
            origin = DEFAULT_ORIGIN_IATA.upper()
            return origin, destination

    # Do not guess departure and arrival based on mention order.
    return None, None

def format_flight(flight: dict) -> str:
    """
    Format AviationStack flight data into readable text.
    """

    airline_data = flight.get("airline") or {}
    flight_info = flight.get("flight") or {}

    airline = airline_data.get("name") or "Unknown airline"
    flight_number = flight_info.get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}

    dep_airport = departure.get("airport") or "Unknown departure airport"
    dep_iata = departure.get("iata") or "Unknown"
    dep_terminal = departure.get("terminal") or "N/A"
    dep_gate = departure.get("gate") or "N/A"
    dep_scheduled = departure.get("scheduled") or "Unknown"
    dep_delay = departure.get("delay")

    arr_airport = arrival.get("airport") or "Unknown arrival airport"
    arr_iata = arrival.get("iata") or "Unknown"
    arr_terminal = arrival.get("terminal") or "N/A"
    arr_gate = arrival.get("gate") or "N/A"
    arr_scheduled = arrival.get("scheduled") or "Unknown"
    arr_delay = arrival.get("delay")

    dep_delay_text = (
        f"{dep_delay} minutes"
        if dep_delay is not None
        else "N/A"
    )

    arr_delay_text = (
        f"{arr_delay} minutes"
        if arr_delay is not None
        else "N/A"
    )

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()

def search_flights(query: str, limit: int = 10) -> str:
    """
    Search AviationStack for flight-status information.

    AviationStack's /flights endpoint does not provide ticket prices.
    """

    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add AVIATIONSTACK_API_KEY to your .env file."
        )

    if not isinstance(query, str) or not query.strip():
        return "Please enter a flight search request."

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        return "Flight search limit must be a positive integer."

    limit = min(limit, 100)

    dep_iata, arr_iata = parse_route(query)

    # Distinguish explicit global searches from unresolved routes.
    global_patterns = [
        r"\ball countries\b",
        r"\ball country\b",
        r"\bglobal flights?\b",
        r"\ball flights?\b",
        r"\bworldwide flights?\b",
        r"\bflights? worldwide\b",
    ]

    is_global = any(
        re.search(pattern, query.casefold())
        for pattern in global_patterns
    )

    if not dep_iata and not arr_iata and not is_global:
        return (
            "I couldn't identify the departure or destination airport.\n"
            "Please specify a clearer route, such as "
            "'flights from Dallas to Tokyo'."
        )

    params = {
        "access_key": API_KEY,
        "limit": limit,
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        return "Flight API request timed out. Please try again."

    except requests.exceptions.RequestException as error:
        return f"Flight API request failed: {error}"

    except ValueError:
        return "Flight API returned invalid JSON."

    if not isinstance(data, dict):
        return "Flight API returned an unexpected response format."

    # Handle AviationStack API errors.
    if "error" in data:
        error = data["error"]

        if isinstance(error, dict):
            code = error.get("code", "Unknown")
            message = error.get("message", "Unknown error")
        else:
            code = "Unknown"
            message = str(error)

        return (
            "Flight API error:\n"
            f"Code: {code}\n"
            f"Message: {message}"
        )

    flight_data = data.get("data", [])

    if not isinstance(flight_data, list):
        return "Flight API returned an unexpected flight data format."

    if not flight_data:
        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"
        else:
            route_text = ""

        return (
            f"No flight-status data found{route_text}.\n\n"
            "Note: AviationStack provides flight-status information, "
            "not ticket prices or bookable flight offers."
        )

    if dep_iata and arr_iata:
        route_info = f"Flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Flights to {arr_iata}"
    else:
        route_info = "Global flight information"

    formatted_flights = [
        format_flight(flight)
        for flight in flight_data[:limit]
        if isinstance(flight, dict)
    ]

    if not formatted_flights:
        return "No valid flight records were returned."

    return (
        f"{route_info}\n\n"
        + "\n\n---\n\n".join(formatted_flights)
    )

if __name__ == "__main__":

    print("TEST 1: Country to country")
    print(parse_route("from Bangladesh to Japan"))

    print("\nTEST 2: City to city")
    print(parse_route("from Dallas to Tokyo"))

    print("\nTEST 3: Direct airport codes")
    print(parse_route("DAC to NRT"))

    print("\nTEST 4: Destination only")
    print(parse_route("flights to Japan"))

    print("\nTEST 5: Global flights")
    print(parse_route("all country flight info"))

    print("\nTEST 6: Flight API")
    print(search_flights("from Bangladesh to Japan"))

