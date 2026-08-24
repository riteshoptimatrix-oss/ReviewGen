from bs4 import BeautifulSoup
from app.services.structured_data_extractor import StructuredDataExtractor

def test_extract_json_ld_single():
    html = """
    <script type="application/ld+json">
    {
      "@type": "LocalBusiness",
      "name": "ABC Tech",
      "telephone": "123-456-7890",
      "url": "https://abctech.com",
      "address": "123 Main St"
    }
    </script>
    """
    soup = BeautifulSoup(html, "lxml")
    data = StructuredDataExtractor.extract(soup)
    assert data["business_name"] == "ABC Tech"
    assert data["phone"] == "123-456-7890"
    assert data["website"] == "https://abctech.com"
    assert data["address"] == "123 Main St"

def test_extract_json_ld_graph():
    html = """
    <script type="application/ld+json">
    {
      "@graph": [
        {
          "@type": "Organization",
          "name": "Wrong Org"
        },
        {
          "@type": "Restaurant",
          "name": "Good Eats",
          "aggregateRating": {
             "ratingValue": "4.5",
             "reviewCount": "100"
          }
        }
      ]
    }
    </script>
    """
    soup = BeautifulSoup(html, "lxml")
    data = StructuredDataExtractor.extract(soup)
    assert data["business_name"] == "Good Eats"
    assert data["raw_category"] == "Restaurant"
    assert data["rating"] == 4.5
    assert data["review_count"] == 100

def test_malformed_json_ld():
    html = """
    <script type="application/ld+json">
    { malformed json
    </script>
    """
    soup = BeautifulSoup(html, "lxml")
    data = StructuredDataExtractor.extract(soup)
    assert data == {}
