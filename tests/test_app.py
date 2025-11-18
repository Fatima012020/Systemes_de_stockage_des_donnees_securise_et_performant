from app import (
    format_row,
    make_batches,
    validate_headers,
    validate_content,
)

def test_format_row_trim():
    row = {"name": " Fatou ", "age": "25"}
    new_row = format_row(row)
    assert new_row["name"] == "Fatou"

def test_make_batches_size():
    rows = [{"i": i} for i in range(10)]
    batches = make_batches(rows, batch_size=3)
    assert len(batches) == 4
    assert len(batches[0]) == 3

def test_validate_headers_ok():
    rows = [{"col1": "a", "col2": "b"}]
    validate_headers(rows, ["col1", "col2"])

def test_validate_headers_missing():
    rows = [{"col1": "a"}]
    try:
        validate_headers(rows, ["col1", "col2"])
    except ValueError as e:
        assert "Colonnes manquantes" in str(e)
    else:
        assert False, "devait lever une erreur si une colonne manque"

def test_validate_content_ok():
    rows = [{"id": "1", "age": "25"}]
    # là on sait qu'il y a un id, donc ça ne doit pas lever
    validate_content(rows, strict_id=True)

def test_validate_content_id_manquant():
    # CAS RÉEL ACTUEL : ton CSV ne contient pas de colonne d'identifiant connue
    rows = [{"age": "25", "gender": "F"}]
    # ton code actuel affiche juste un warning et laisse passer
    validate_content(rows, strict_id=False)
    assert True  # on valide que ça ne lève pas
