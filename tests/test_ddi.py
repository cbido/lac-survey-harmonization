from ingest.ddi_to_dictionary import parse_ddi

DDI = """<?xml version='1.0' encoding='UTF-8'?>
<codeBook xmlns="http://www.icpsr.umich.edu/DDI" version="1.2.2">
  <fileDscr ID="F1"><fileTxt><fileName>
      EH_Persona.NSDstat
  </fileName></fileTxt></fileDscr>
  <fileDscr ID="F2"><fileTxt><fileName>EH_Vivienda.NSDstat</fileName></fileTxt></fileDscr>
  <dataDscr>
    <var ID="V1" name="FOLIO" files="F1"><labl>Identificador</labl><varFormat type="character"/></var>
    <var ID="V2" name="s01a_02" files="F1" intrvl="discrete">
      <labl>
        Sexo
      </labl>
      <qstn><qstnLit>¿Es hombre
         o mujer?</qstnLit></qstn>
      <catgry><catValu>1</catValu><labl>Hombre</labl></catgry>
      <catgry><catValu>2</catValu><labl>Mujer</labl></catgry>
      <varFormat type="numeric"/>
    </var>
    <var ID="V3" name="folio" files="F2"><labl>Identificador</labl></var>
  </dataDscr>
</codeBook>"""


def test_parse_ddi(tmp_path):
    path = tmp_path / "x.xml"
    path.write_text(DDI, encoding="utf-8")
    d = parse_ddi(str(path)).set_index("variable")
    assert list(d.index) == ["folio", "s01a_02"]            # lowercased, duplicates merged
    assert d.loc["folio", "file"] == "EH_Persona;EH_Vivienda"
    assert d.loc["s01a_02", "label"] == "Sexo"
    assert d.loc["s01a_02", "question"] == "¿Es hombre o mujer?"
    assert d.loc["s01a_02", "value_labels"] == '{"1": "Hombre", "2": "Mujer"}'
    assert d.loc["s01a_02", "dtype"] == "numeric"
