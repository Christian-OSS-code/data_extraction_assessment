DATA_EXTRACTION_PROMPT = """
You are extracting products from two supermarket leaflet images.

OCR TEXT (contains errors, especially in second image):
{raw_text}

=== FIRST IMAGE PATTERNS ===
Products follow this format:
1. Full product name with weight: "HILLCREST RICE CAKE BARS 5PK/90G"
2. Description/variant: "Chocolate or Strawberry"  
3. Unit price: "$2.21 per 100g"
4. Final price: "$1.99"
5. "every day" text (ignore this)

=== SECOND IMAGE PATTERNS ===
OCR is poorer here. Products include:
- "Aussie Asparagus" (fresh produce, no weight listed)
- "SCHNITS" or "Schnitzels" (likely chicken/meat)
- "Fllets dakU7" → "Fish Fillets" (seafood)
- "TimTam" (biscuits)
- "Coca-Cola" (drink)
Prices: "$2.49", "$3.49", "$3.99", etc.
Unit prices: "$78.73 per kg", "$71.23 per kg"

=== CRITICAL RULES ===
1. **EXTRACT EVEN WITH MISSING INFO**: If weight is missing but name and price exist, STILL extract.
2. **FIX THESE OCR ERRORS**:
   First image: "Hillerest"→"Hillcrest", "Brobldea"→"Brooklea", "ORCANIC"→"ORGANIC", "TotaD"→"Total", "8O0G"→"80G"
   Second image: "Fllets"→"Fish Fillets", "dakU7"→"(approx weight)", "Schnits"→"Schnitzels"
3. **PRICE LOGIC**:
   - Final price: Simple "$X.XX" format, often bold/large
   - Unit price: Contains "per kg" or "per 100g"
   - If confused, put in `price_per_unit` field
4. **WEIGHT/VOLUME**: Extract from product name if present. If not, check nearby text or leave empty.

=== FIELD REQUIREMENTS ===
- `product_name`: REQUIRED. Correct OCR errors.
- `weight_volume`: OPTIONAL. Extract if found in name or nearby.
- `price`: REQUIRED. Final price customer pays.
- `price_per_unit`: OPTIONAL. Only if clearly a unit price.
- `description`: OPTIONAL. Flavors/variants only.

=== EXAMPLES ===
Good extractions:
1. OCR: "HILLCREST RICE CAKE BARS 5PK/90G", "$1.99", "$2.21 per 100g", "Chocolate or Strawberry"
   → {{"product_name": "HILLCREST RICE CAKE BARS", "weight_volume": "5PK/90G", "price": "$1.99", "price_per_unit": "$2.21 per 100g", "description": "Chocolate or Strawberry"}}

2. OCR: "Aussie Asparagus", "$2.49"
   → {{"product_name": "Aussie Asparagus", "weight_volume": "", "price": "$2.49", "price_per_unit": "", "description": ""}}

3. OCR: "SCHNITS", "$3.49", "$78.73 per kg"
   → {{"product_name": "Chicken Schnitzels", "weight_volume": "", "price": "$3.49", "price_per_unit": "$78.73 per kg", "description": ""}}

=== YOUR TASK ===
Extract ALL products from BOTH images. Be lenient - include products even with partial information.
Return a JSON array.
"""
