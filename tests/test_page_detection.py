from bs4 import BeautifulSoup
from app.services.google_page_detector import GooglePageDetector

def test_detect_consent():
    html = '<form action="https://consent.google.com/v2/whatever"></form>'
    soup = BeautifulSoup(html, "lxml")
    assert GooglePageDetector.detect("https://consent.google.com/m", 200, html, soup) == GooglePageDetector.PAGE_TYPE_CONSENT
    assert GooglePageDetector.detect("https://google.com", 200, html, soup) == GooglePageDetector.PAGE_TYPE_CONSENT

def test_detect_challenge():
    html = '<html><head><title>Sorry!</title></head><body>google.com/sorry/index</body></html>'
    soup = BeautifulSoup(html, "lxml")
    assert GooglePageDetector.detect("https://google.com", 200, html, soup) == GooglePageDetector.PAGE_TYPE_CHALLENGE

def test_detect_maps_business():
    html = '<html></html>'
    soup = BeautifulSoup(html, "lxml")
    assert GooglePageDetector.detect("https://www.google.com/maps/place/ABC", 200, html, soup) == GooglePageDetector.PAGE_TYPE_MAPS_BUSINESS

def test_detect_error():
    html = '<html></html>'
    soup = BeautifulSoup(html, "lxml")
    assert GooglePageDetector.detect("https://google.com/maps", 404, html, soup) == GooglePageDetector.PAGE_TYPE_ERROR
