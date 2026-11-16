import json

import os

from harmonize.propose_mappings import build_prompt, format_dictionary, load_env, parse_response, propose

DICTIONARY = [
    {"variable": "sexo", "label": "Sexo", "value_labels": json.dumps({"1": "Hombre", "2": "Mujer"})},
    {"variable": "edad", "label": "Edad", "value_labels": "{}", "question": "¿Cuántos años cumplidos tiene?"},
]
SCHEMA = [
    {"name": "sexo_ci", "level": "person", "domain": "demographics", "type": "int", "description": "Sex",
     "values": {1: "male", 2: "female"}},
    {"name": "edad_ci", "level": "person", "domain": "demographics", "type": "int", "description": "Age"},
    {"name": "luz_ch", "level": "household", "domain": "housing", "type": "int", "description": "Electricity"},
]


def fake_llm(system, prompt):
    assert "sexo: Sexo | 1=Hombre; 2=Mujer" in prompt
    reply = [
        {"target_var": "sexo_ci", "status": "mapped", "source_vars": ["SEXO"], "confidence": 0.97, "rationale": "r"},
        {"target_var": "edad_ci", "status": "mapped", "source_vars": ["edad_anios"], "confidence": 0.8, "rationale": "r"},
        # luz_ch left unanswered
    ]
    return "Here is the mapping:\n```json\n" + json.dumps(reply) + "\n```"


def test_prompt_contains_dictionary_and_targets():
    prompt = build_prompt(format_dictionary(DICTIONARY), SCHEMA)
    assert "edad: Edad | Q: ¿Cuántos años cumplidos tiene?" in prompt
    assert "sexo_ci (person, int): Sex | codes: 1=male; 2=female" in prompt


def test_parse_response_ignores_surrounding_text():
    assert parse_response('ok [ {"target_var": "x"} ] done') == [{"target_var": "x"}]


def test_invented_variables_are_caught():
    rows = {r["target_var"]: r for r in propose("T", DICTIONARY, SCHEMA, fake_llm, model="fake")}
    assert rows["sexo_ci"]["source_vars"] == "sexo" and rows["sexo_ci"]["status"] == "mapped"
    assert rows["edad_ci"]["invalid_sources"] == "edad_anios"
    assert rows["edad_ci"]["status"] == "no_valid_source"
    assert rows["luz_ch"]["status"] == "no_answer"
    assert all(r["review_status"] == "" for r in rows.values())


def test_load_env_reads_file_without_overriding(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comment\nTEST_KEY_A='abc'\nTEST_KEY_B=from_file\n")
    monkeypatch.delenv("TEST_KEY_A", raising=False)
    monkeypatch.setenv("TEST_KEY_B", "already_set")
    load_env(str(env))
    assert os.environ["TEST_KEY_A"] == "abc"
    assert os.environ["TEST_KEY_B"] == "already_set"
    monkeypatch.delenv("TEST_KEY_A")
