"""KVKK (6698 sayılı Kişisel Verilerin Korunması Kanunu) uyumluluk denetimi.

Metindeki kişisel verileri **genel** ve **özel nitelikli** kategorilere ayırır,
ilgili KVKK madde referanslarıyla birlikte bir uyumluluk raporu üretir.

Özel nitelikli kişisel veriler (Madde 6): sağlık, biyometrik, ceza mahkûmiyeti,
din/mezhep/felsefi inanç, ırk/etnik köken, sendika üyeliği. Bu veriler kural
olarak yalnızca ilgilinin **açık rızası** ile işlenebilir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from hashlib import sha256

from guardllm.config import PIIConfig
from guardllm.input.pii_scanner import PIIScanner

# --------------------------------------------------------------------------- #
# KVKK madde referansları
# --------------------------------------------------------------------------- #
ARTICLES: dict[str, str] = {
    "madde_4": "Madde 4 — Genel ilkeler (hukuka uygunluk, amaçla sınırlılık, ölçülülük)",
    "madde_5": "Madde 5 — Kişisel verilerin işlenme şartları (açık rıza veya kanuni sebep)",
    "madde_6": "Madde 6 — Özel nitelikli kişisel verilerin işlenmesi (kural olarak açık rıza)",
    "madde_12": "Madde 12 — Veri güvenliği yükümlülükleri (uygun teknik ve idari tedbirler)",
}

GENEL = "genel"
OZEL = "özel_nitelikli"


@dataclass(frozen=True)
class KVKKCategory:
    key: str
    label: str
    sensitivity: str  # GENEL | OZEL
    articles: tuple[str, ...]


# PII scanner kategorileri -> KVKK kategorisi eşlemesi (genel nitelikli).
_PII_TO_KVKK: dict[str, KVKKCategory] = {
    "tc_kimlik": KVKKCategory("tc_kimlik", "Kimlik verisi (TC Kimlik No)", GENEL, ("madde_5",)),
    "telefon": KVKKCategory("telefon", "İletişim verisi (telefon)", GENEL, ("madde_5",)),
    "email": KVKKCategory("email", "İletişim verisi (e-posta)", GENEL, ("madde_5",)),
    "iban": KVKKCategory("iban", "Finansal veri (IBAN)", GENEL, ("madde_5",)),
    "kredi_karti": KVKKCategory("kredi_karti", "Finansal veri (kredi kartı)", GENEL, ("madde_5",)),
}

# Özel nitelikli kategoriler ve tespit için anahtar-kelime kalıpları.
_SPECIAL_CATEGORIES: dict[str, KVKKCategory] = {
    "saglik": KVKKCategory("saglik", "Sağlık verisi", OZEL, ("madde_6", "madde_12")),
    "biyometrik": KVKKCategory("biyometrik", "Biyometrik veri", OZEL, ("madde_6", "madde_12")),
    "ceza_mahkumiyeti": KVKKCategory(
        "ceza_mahkumiyeti", "Ceza mahkûmiyeti ve güvenlik tedbirleri", OZEL, ("madde_6",)
    ),
    "din_inanc": KVKKCategory("din_inanc", "Din, mezhep veya felsefi inanç", OZEL, ("madde_6",)),
    "irk_etnik": KVKKCategory("irk_etnik", "Irk ve etnik köken", OZEL, ("madde_6",)),
    "sendika": KVKKCategory("sendika", "Sendika üyeliği", OZEL, ("madde_6",)),
}

_SPECIAL_PATTERNS_RAW: dict[str, str] = {
    "saglik": r"\b(hastal[ıi]k|te[şs]his|tan[ıi]s[ıi]|tedavi|ila[çc]|re[çc]ete|kan\s+grubu|"
    r"hiv|kanser|diyabet|hamile|gebe|engelli|sa[ğg]l[ıi]k\s+raporu|psikiyatri|"
    r"ameliyat|hastane\s+kayd[ıi]|kronik\s+rahats[ıi]zl[ıi]k)\b",
    "biyometrik": r"\b(parmak\s+izi|y[üu]z\s+tan[ıi]ma|retina|iris\s+taramas[ıi]|dna|"
    r"avu[çc]\s+i[çc]i|ses\s+tan[ıi]ma|biyometrik)\b",
    "ceza_mahkumiyeti": r"\b(sab[ıi]ka|mahk[uû]miyet|h[üu]k[üu]m\s+giy|ceza\s+ald[ıi]|"
    r"h[üu]k[üu]ml[üu]|adli\s+sicil|tutuklu)\b",
    "din_inanc": r"\b(dini\s+inanc|mezhebi|dini\s+g[öo]r[üu][şs]|felsefi\s+inan|"
    r"alevi|s[üu]nni|ateist)\b",
    "irk_etnik": r"\b([ıi]rk[ıi]|etnik\s+k[öo]ken|[ıi]rksal)\b",
    "sendika": r"\b(sendika\s+[üu]yeli[ğg]i|sendika\s+[üu]yesi)\b",
}
_SPECIAL_PATTERNS = {
    k: re.compile(v, re.IGNORECASE | re.UNICODE) for k, v in _SPECIAL_PATTERNS_RAW.items()
}


@dataclass
class KVKKFinding:
    category: KVKKCategory
    matches: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category.key,
            "label": self.category.label,
            "sensitivity": self.category.sensitivity,
            "articles": [ARTICLES[a] for a in self.category.articles],
            "match_count": len(self.matches),
        }


@dataclass
class ComplianceReport:
    """KVKK uyumluluk raporu."""

    text_hash: str
    findings: list[KVKKFinding]
    redacted: str
    risk_level: str  # yok | orta | yüksek
    requires_explicit_consent: bool
    recommendations: list[str]

    @property
    def compliant(self) -> bool:
        """Kişisel veri bulunmuyorsa (korunacak veri yok) uyumlu kabul edilir."""
        return len(self.findings) == 0

    @property
    def has_special_category(self) -> bool:
        return any(f.category.sensitivity == OZEL for f in self.findings)

    def to_dict(self) -> dict:
        return {
            "text_hash": self.text_hash,
            "compliant": self.compliant,
            "risk_level": self.risk_level,
            "requires_explicit_consent": self.requires_explicit_consent,
            "has_special_category": self.has_special_category,
            "findings": [f.to_dict() for f in self.findings],
            "articles_referenced": sorted(
                {ARTICLES[a] for f in self.findings for a in f.category.articles}
            ),
            "recommendations": self.recommendations,
            "redacted": self.redacted,
        }

    def to_markdown(self) -> str:
        """İnsan-okunur uyumluluk raporu (Markdown)."""
        lines = ["# KVKK Uyumluluk Raporu", ""]
        status = "✅ Uyumlu" if self.compliant else "⚠️ Dikkat gerektiriyor"
        lines += [
            f"**Durum:** {status}",
            f"**Risk seviyesi:** {self.risk_level}",
            f"**Açık rıza gerekli mi:** {'Evet' if self.requires_explicit_consent else 'Hayır'}",
            "",
        ]
        if self.findings:
            lines.append("## Tespit edilen kişisel veri kategorileri")
            lines.append("")
            lines.append("| Kategori | Nitelik | İlgili madde(ler) |")
            lines.append("|----------|---------|-------------------|")
            for f in self.findings:
                nitelik = "Özel nitelikli" if f.category.sensitivity == OZEL else "Genel"
                arts = "; ".join(a.replace("Madde", "m.").split(" — ")[0] for a in
                                 (ARTICLES[a] for a in f.category.articles))
                lines.append(f"| {f.category.label} | {nitelik} | {arts} |")
            lines.append("")
        if self.recommendations:
            lines.append("## Öneriler")
            lines.append("")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        return "\n".join(lines)


class KVKKChecker:
    """Metni KVKK kapsamında denetler ve uyumluluk raporu üretir."""

    name = "kvkk_compliance"

    def __init__(self, pii_scanner: PIIScanner | None = None):
        # Tüm genel PII kategorilerini kapsayan bir tarayıcı kullan.
        self.pii = pii_scanner or PIIScanner(
            PIIConfig(
                categories=["tc_kimlik", "telefon", "email", "iban", "kredi_karti"],
                action="mask",
            )
        )

    def check(self, text: str) -> ComplianceReport:
        text_hash = sha256((text or "").encode("utf-8")).hexdigest()[:16]
        findings: list[KVKKFinding] = []

        # 1) Genel nitelikli PII (regex + doğrulama).
        pii_result = self.pii.scan(text or "")
        detected_pii = pii_result.metadata.get("categories", []) if text else []
        for cat_key in detected_pii:
            kvkk_cat = _PII_TO_KVKK.get(cat_key)
            if kvkk_cat:
                findings.append(KVKKFinding(category=kvkk_cat, matches=[cat_key]))

        # 2) Özel nitelikli kişisel veriler (anahtar-kelime).
        for cat_key, pattern in _SPECIAL_PATTERNS.items():
            hits = pattern.findall(text or "")
            if hits:
                flat = [h if isinstance(h, str) else h[0] for h in hits]
                findings.append(
                    KVKKFinding(category=_SPECIAL_CATEGORIES[cat_key], matches=flat)
                )

        has_special = any(f.category.sensitivity == OZEL for f in findings)
        if not findings:
            risk = "yok"
        elif has_special:
            risk = "yüksek"
        else:
            risk = "orta"

        return ComplianceReport(
            text_hash=text_hash,
            findings=findings,
            redacted=pii_result.redacted or (text or ""),
            risk_level=risk,
            requires_explicit_consent=has_special,
            recommendations=self._recommendations(findings, has_special),
        )

    @staticmethod
    def _recommendations(findings: list[KVKKFinding], has_special: bool) -> list[str]:
        if not findings:
            return ["Kişisel veri tespit edilmedi; ek bir işlem gerekmiyor."]
        recs = [
            "Kişisel verileri maskeleyin/şifreleyin (Madde 12 — teknik ve idari tedbirler).",
            "İşleme için hukuki dayanak (açık rıza veya kanuni sebep) belgeleyin (Madde 5).",
            "Verileri amaçla sınırlı ve ölçülü şekilde işleyin (Madde 4).",
        ]
        if has_special:
            recs.insert(
                0,
                "ÖZEL NİTELİKLİ VERİ: Kural olarak açık rıza olmadan işlemeyin (Madde 6); "
                "ek güvenlik tedbirleri ve Kurul kararlarına uyum gereklidir.",
            )
        return recs
