import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["uz", "ru", "en"]
# function name -> index of the argument that holds the locale key
KEY_ARG = {"t": 1, "tr": 1, "translate": 1, "ta": 0}


def load(lang):
    return json.loads((ROOT / "locales" / f"{lang}.json").read_text(encoding="utf-8"))


def keys_used_in_code():
    used, dynamic = {}, []
    for path in ROOT.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                continue
            index = KEY_ARG.get(node.func.id)
            if index is None or len(node.args) <= index:
                continue
            arg = node.args[index]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                used.setdefault(arg.value, f"{path.name}:{node.lineno}")
            elif not (isinstance(arg, ast.Name) and arg.id == "key"):  # `key` = thin wrapper
                dynamic.append(f"{path.name}:{node.lineno}")
    return used, dynamic


def test_all_locales_have_exactly_the_same_keys():
    reference = set(load("uz"))
    for lang in LANGS:
        keys = set(load(lang))
        assert keys == reference, f"{lang}: missing {reference - keys}, extra {keys - reference}"


def test_placeholders_match_across_locales():
    def placeholders(text):
        return sorted(re.findall(r"{(\w+)}", text))

    reference = load("uz")
    for lang in LANGS:
        for key, text in load(lang).items():
            assert placeholders(text) == placeholders(reference[key]), f"{lang}.{key}"


def test_no_empty_translations():
    for lang in LANGS:
        for key, text in load(lang).items():
            assert text.strip(), f"{lang}.{key} is empty"


def test_every_key_used_in_code_exists():
    used, dynamic = keys_used_in_code()
    assert len(used) > 20, "key scan found suspiciously few keys"
    assert not dynamic, f"locale keys must be string literals so they can be checked: {dynamic}"
    for lang in LANGS:
        missing = {key: where for key, where in used.items() if key not in load(lang)}
        assert not missing, f"{lang} is missing keys used in code: {missing}"


@pytest.mark.parametrize("lang", LANGS)
def test_translate_falls_back_to_the_key(lang):
    import i18n

    assert i18n.translate(lang, "definitely_not_a_key") == "definitely_not_a_key"
    assert i18n.translate("xx", "back") == i18n.translate("uz", "back")
