from guardllm.output import ToxicityFilter


def test_toxic_english_blocked():
    tox = ToxicityFilter()
    result = tox.check("You are such an idiot and a moron")
    assert not result.safe
    assert result.threat == "toxicity"


def test_toxic_turkish_blocked():
    tox = ToxicityFilter()
    result = tox.check("Sen tam bir salak ve aptalsın")
    assert not result.safe


def test_clean_text_safe():
    tox = ToxicityFilter()
    result = tox.check("Yardımınız için çok teşekkür ederim.")
    assert result.safe


def test_benign_idiom_not_flagged():
    tox = ToxicityFilter()
    result = tox.check("Bu işten siktiri çekmek istiyorum artık.")
    assert result.safe
