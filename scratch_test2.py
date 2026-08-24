from bs4 import BeautifulSoup

with open("search_result.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
for el in soup.find_all(string=lambda text: text and "Software Company" in text) or soup.find_all(string=lambda text: text and "Software" in text):
    print("Found 'Software' in:", el.parent.name, el.parent.attrs)
    print(el.strip())
