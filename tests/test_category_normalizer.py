from app.services.category_normalizer import CategoryNormalizer

def test_exact_match():
    res = CategoryNormalizer.normalize("Software Company")
    assert res.value == "Software Company"
    assert res.confidence == 1.0

def test_synonym_match():
    res = CategoryNormalizer.normalize("coffee shop")
    assert res.value == "Cafe"
    assert res.confidence == 0.95

def test_partial_match():
    res = CategoryNormalizer.normalize("Best Italian Restaurant in town")
    assert res.value == "Restaurant"
    assert res.confidence == 0.85

def test_unknown_match():
    res = CategoryNormalizer.normalize("Quantum Physics Lab")
    assert res.value is None
    assert res.confidence == 0.0

def test_null_input():
    res = CategoryNormalizer.normalize(None)
    assert res.value is None
    assert res.confidence == 0.0
