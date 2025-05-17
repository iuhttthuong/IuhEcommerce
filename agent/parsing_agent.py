import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load biến môi trường từ .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ParsingAgent:
    @staticmethod
    def initiate_parsing(user_input: str) -> dict:
        functions = [
            {
                "name": "extract_product_info",
                "description": "Trích xuất thông tin sản phẩm từ văn bản khách hàng theo schema chuẩn",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Tên_sản_phẩm": {"type": "string"},
                        "Danh_mục": {"type": "string"},
                        "Thương_hiệu": {"type": "string"},
                        "Người_bán": {"type": "string"},
                        "Mô_tả_ngắn": {"type": "string"},
                        "Mô_tả_chi_tiết": {"type": "string"},
                    },
                    "required": [
                        "Tên_sản_phẩm",
                        "Danh_mục",
                        "Thương_hiệu",
                        "Người_bán",
                        "Mô_tả_ngắn",
                        "Mô_tả_chi_tiết"
                    ]
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý AI có nhiệm vụ trích xuất thông tin sản phẩm từ văn bản người dùng. "
                    "Hãy phân tích cẩn thận và điền các trường càng đầy đủ càng tốt, đúng theo schema đã định nghĩa."
                )
            },
            {
                "role": "user",
                "content": f"Hãy phân tích đoạn sau và trích xuất thông tin: {user_input}"
            }
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                functions=functions,
                function_call={"name": "extract_product_info"},
                temperature=0.2
            )

            arguments = response.choices[0].message.function_call.arguments
            result_dict = json.loads(arguments)

        except Exception as e:
            print(f"❌ Lỗi khi trích xuất JSON từ function_call: {e}")
            result_dict = {}

        return result_dict


# if __name__ == "__main__":
#     test_input = "sinh tồn trong rừng trong rúrú"
#     result = ParsingAgent.initiate_parsing(test_input)
#     print("✅ Kết quả phân tích:")
#     print(json.dumps(result, indent=2, ensure_ascii=False))
