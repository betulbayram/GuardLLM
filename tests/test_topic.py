from guardllm import Guard, GuardConfig
from guardllm.config import TopicConfig
from guardllm.input import TopicRestrictor


def _medical_blocklist():
    return TopicConfig(
        enabled=True,
        mode="blocklist",
        topics={
            "tıbbi_tavsiye": ["teşhis", "ilaç", "doz", "tedavi", "reçete"],
            "hukuki_tavsiye": ["dava", "avukat", "mahkeme"],
        },
        blocked=["tıbbi_tavsiye"],
    )


def test_disabled_by_default():
    r = TopicRestrictor().check("herhangi bir metin")
    assert r.safe


def test_blocklist_blocks_restricted_topic():
    r = TopicRestrictor(_medical_blocklist()).check("Bana bir ilaç dozu öner ve reçete yaz")
    assert not r.safe
    assert r.threat == "restricted_topic"
    assert "tıbbi_tavsiye" in r.metadata["topics"]


def test_blocklist_allows_unlisted_topic():
    # 'hukuki_tavsiye' is defined but not in `blocked`, so it passes.
    r = TopicRestrictor(_medical_blocklist()).check("Bir avukata dava hakkında sordum")
    assert r.safe


def test_blocklist_allows_off_topic():
    r = TopicRestrictor(_medical_blocklist()).check("Ankara'nın nüfusu kaç?")
    assert r.safe


def test_allowlist_blocks_off_topic():
    cfg = TopicConfig(
        enabled=True,
        mode="allowlist",
        topics={"bankacılık": ["hesap", "kredi", "iban", "havale", "bakiye"]},
        allowed=["bankacılık"],
    )
    tr = TopicRestrictor(cfg)
    assert tr.check("Hesap bakiyemi ve kredi durumumu öğrenebilir miyim?").safe
    off = tr.check("Bana bir kek tarifi ver")
    assert not off.safe
    assert off.threat == "off_topic"


def test_guard_wires_topic_restrictor():
    cfg = GuardConfig.default()
    cfg.input.topic_restrictor = _medical_blocklist()
    guard = Guard(cfg)
    r = guard.check_input("Hangi ilaç dozunu almalıyım?")
    assert not r.safe
    assert r.threat == "restricted_topic"


def test_word_boundary_no_false_positive():
    cfg = TopicConfig(
        enabled=True, mode="blocklist", topics={"t": ["dava"]}, blocked=["t"]
    )
    # 'davar' / 'davet' must not match 'dava'
    assert TopicRestrictor(cfg).check("Düğün daveti ve davar sürüsü").safe
