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
