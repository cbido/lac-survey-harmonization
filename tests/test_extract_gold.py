from harmonize.extract_gold_from_idb import build_gold, strip_comments

DO_FILE = """
* header comment with a /* that must not open a block
/* outer /* nested */ still a comment
gen sexo_ci=fake
*/
gen sexo_ci=sexo
clonevar upm_ci=cod_upm
generat asiste_ci=1 if e3==1   //*2017 note with /* inside
replace e6a = . if e6a == 99
gen aedu_ci = .
replace aedu_ci = e6b if inrange(e6a, 6, 7) & e3 == 1
egen auxpen=rsum(vejez invalidez), missing
gen ypen_ci=auxpen
bys folio: egen nmiembros_ch = sum(miembro), missing
gen emp_ci=(condocup_ci==1)
gen luz_ch=. // not asked this round
gen pais_c="CHL"
egen remesas_ci=rsum(remesasaux*_*), missing
gen ylm_ci = ylmpri_ci + ///
    ylmsec_ci
label var sexo_ci "Sexo del individuo"
"""


def gold():
    return {r["target_var"]: r for r in build_gold(DO_FILE, "TEST")}


def test_comments_are_removed():
    cleaned = strip_comments(DO_FILE)
    assert "fake" not in cleaned
    assert "2017" not in cleaned
    assert "gen luz_ch=." in cleaned


def test_direct_and_cloned_sources():
    g = gold()
    assert g["sexo_ci"]["source_vars"] == "sexo"
    assert g["sexo_ci"]["idb_label"] == "Sexo del individuo"
    assert g["upm_ci"]["source_vars"] == "cod_upm"
    assert g["asiste_ci"]["source_vars"] == "e3"


def test_recoded_raw_variable_stays_raw():
    assert gold()["aedu_ci"]["source_vars"] == "e3;e6a;e6b"


def test_intermediates_are_resolved():
    assert gold()["ypen_ci"]["source_vars"] == "invalidez;vejez"
    assert gold()["nmiembros_ch"]["source_vars"] == "miembro"


def test_statuses():
    g = gold()
    assert g["emp_ci"]["status"] == "derived"
    assert g["emp_ci"]["derived_from"] == "condocup_ci"
    assert g["luz_ch"]["status"] == "not_available"
    assert g["pais_c"]["status"] == "constant"
    assert g["ylm_ci"]["derived_from"] == "ylmpri_ci;ylmsec_ci"


def test_wildcards_are_not_variables():
    assert gold()["remesas_ci"]["source_vars"] == ""


def test_dictionary_filter():
    rows = {r["target_var"]: r for r in build_gold(DO_FILE, "TEST", dictionary={"vejez"})}
    assert rows["ypen_ci"]["source_vars"] == "vejez"
    assert rows["ypen_ci"]["not_in_dictionary"] == "invalidez"
