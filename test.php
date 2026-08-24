<?php
require 'index.php'; // wait, index.php has lots of logic, let's just copy the function

function scrapeGoogleCategoryHack($businessName) {
    $ch = curl_init();
    $searchUrl = "https://www.google.com/search?q=" . urlencode($businessName) . "&hl=en";
    
    $headers = [
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language: en-US,en;q=0.9",
        "Sec-Ch-Ua: \"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Mobile: ?0",
        "Sec-Ch-Ua-Platform: \"Windows\"",
        "Sec-Fetch-Dest: document",
        "Sec-Fetch-Mode: navigate",
        "Sec-Fetch-Site: none",
        "Sec-Fetch-User: ?1",
        "Upgrade-Insecure-Requests: 1"
    ];

    curl_setopt($ch, CURLOPT_URL, $searchUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_ENCODING, "");
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36');
    curl_setopt($ch, CURLOPT_TIMEOUT, 6);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    
    $html = curl_exec($ch);
    curl_close($ch);
    
    if ($html) {
        $pattern1 = '/<span class="YhemCb"[^>]*>(.*?)<\/span>/i';
        if (preg_match($pattern1, $html, $matches)) {
            $scrapedText = strip_tags($matches[1]);
            $parts = explode(' in ', $scrapedText);
            return trim($parts[0]);
        }
        $pattern2 = '/data-attrid="subtitle"[^>]*>.*?<span[^>]*>(.*?)<\/span>/i';
        if (preg_match($pattern2, $html, $matches)) {
            $scrapedText = strip_tags($matches[1]);
            return trim($scrapedText);
        }
        
        $commonCats = [
            'tour operator', 'travel agency', 'software training institute', 'restaurant', 'cafe', 
            'software company'
        ];
        
        foreach ($commonCats as $cat) {
            if (preg_match("/\b" . preg_quote($cat, '/') . "\b/i", $html)) {
                return $cat;
            }
        }
    }
    return null; 
}

echo "Category: " . scrapeGoogleCategoryHack("Opti Matrix Solutions") . "\n";
