from app.services.business_extractor import BusinessExtractor

def test_business_extractor_priority():
    html = """
    <script type="application/ld+json">
    {
      "@type": "LocalBusiness",
      "name": "JSON Name"
    }
    </script>
    <meta property="og:title" content="Meta Name" />
    <h1>Embedded Name</h1>
    """
    data = BusinessExtractor.extract(html, "http://input", "http://final")
    
    assert data.business_name == "JSON Name"
    assert data.input_url == "http://input"
    assert data.final_url == "http://final"

def test_business_extractor_fallback():
    html = """
    <meta property="og:title" content="Meta Name" />
    <h1 class="fontHeadlineLarge">Embedded Name</h1>
    <button jsaction="pane.rating.category">Coffee Shop</button>
    """
    data = BusinessExtractor.extract(html, "http://input", "http://final")
    
    assert data.business_name == "Meta Name"
    assert data.raw_category == "Coffee Shop"
