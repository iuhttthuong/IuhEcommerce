
import json


data = []
with open("data/product_data_info.json", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 5000:
            break
        try:
            data.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Lỗi ở dòng {i}: {e}")

json_data = json.dumps(data, indent=2, ensure_ascii=False)
# luu file
with open("data/product_data_info_proper.json", "w", encoding="utf-8") as f:
    f.write(json_data)
    