import json

# Load JSON data from both files (line-delimited JSON)
def load_json_lines(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]

product_data = {item["id"]: item for item in load_json_lines("product_data_info.json")}
crawl_data = load_json_lines("crawl_data_info.json")

# Merge data based on `id`
merged_data = []
for item in crawl_data:
    product_id = item.get("id")
    if product_id in product_data:
        merged_item = {**product_data[product_id], **item}  # Merge dictionaries
        merged_data.append(merged_item)
    else:
        print(f"Missing ID {product_id} in product_data_info.json")

# Print merged data count
print(f"Total merged records: {len(merged_data)}")

with open("product_data_merge.json", "w", encoding="utf-8") as file:
    for item in merged_data:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")