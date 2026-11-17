#!/bin/zsh
cd "${0:A:h}"
echo "collect start $(date +%T)"
python3 collect.py
echo "reed start $(date +%T)"
python3 reed.py reed.json food:food-sales food:food-account-manager food:food-business-development-manager food:fmcg-sales food:fmcg-account-manager food:drinks-sales food:foodservice-sales food:food-key-account-manager food:food-sales-executive food:wine-sales food:beverage-sales food:food-territory-manager food:hospitality-sales food:national-account-manager-food buyer:food-buyer buyer:buyer buyer:assistant-buyer buyer:junior-buyer buyer:purchasing buyer:category-manager buyer:procurement-food buyer:buying other:account-manager other:key-account-manager other:business-development-manager other:sales-account-manager other:field-sales other:area-sales-manager other:territory-manager other:national-account-manager other:sales-executive
echo "food2 start $(date +%T)"
python3 extra.py food2.json "Bidfood" "Brakes" "Booker" "Sysco" "Lactalis" "Arla" "Muller" "Yeo Valley" "Thatchers" "Cotswold Fayre" "Diverse Fine Food" "Fine Cheese" "Clifton Coffee" "Butcombe" "St Austell Brewery" "Heineken" "Carlsberg" "Molson Coors" "Diageo" "Coca-Cola Europacific" "Britvic" "PepsiCo" "Nestle" "Premier Foods" "Warburtons" "Pukka" "Matthew Clark" "speciality food" "FMCG sales" "food service" "brewery sales" "wine sales" "coffee sales" "confectionery" "food buyer" "drinks buyer" "assistant buyer" "category buyer" "purchasing manager" > /dev/null
echo "details start $(date +%T)"
python3 details.py | tail -1
echo "SWEEP DONE $(date +%T)"
