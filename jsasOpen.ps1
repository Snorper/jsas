$urls = Import-Csv ..\results.csv | select -ExpandProperty href
foreach ($url in $urls) {Start $url}