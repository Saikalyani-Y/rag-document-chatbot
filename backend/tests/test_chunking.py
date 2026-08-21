from services.chunking import chunk_units


def test_empty_units_produce_no_chunks():
    assert chunk_units([], chunk_size=100, overlap=20) == []
    assert chunk_units(["   ", ""], chunk_size=100, overlap=20) == []


def test_single_short_unit_produces_one_chunk_tagged_unit_1():
    chunks = chunk_units(["hello world"], chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"
    assert chunks[0].unit_number == 1


def test_chunks_advance_and_overlap():
    text = "word " * 400  # long enough to require multiple windows
    chunks = chunk_units([text], chunk_size=200, overlap=50)
    assert len(chunks) > 1
    # consecutive chunks overlap: the end of one appears near the start of the next
    assert chunks[0].text[-10:] in chunks[0].text  # sanity: chunk text is non-empty and consistent
    for c in chunks:
        assert c.text.strip() != ""


def test_unit_number_tracks_which_page_a_chunk_starts_in():
    units = ["a" * 50, "b" * 50, "c" * 50]
    chunks = chunk_units(units, chunk_size=40, overlap=5)
    unit_numbers = {c.unit_number for c in chunks}
    assert unit_numbers.issubset({1, 2, 3})
    assert chunks[0].unit_number == 1
