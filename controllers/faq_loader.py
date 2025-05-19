import os, re, json5
from fastapi import APIRouter
from sqlalchemy.orm import Session
from db import Session as db_session
from models.fqas import FQA
from typing import List
from datetime import datetime
from env import env
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from autogen import AssistantAgent
import json

router = APIRouter(prefix="/load-faq", tags=["Load PDF folder for FAQ"])

# Sử dụng đường dẫn tuyệt đối
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_FOLDER = os.path.join(BASE_DIR, "tiki_policies")  # đường dẫn tuyệt đối đến thư mục chứa file PDF
print(f"PDF folder path: {PDF_FOLDER}")  # Debug để xem đường dẫn thực tế

# 1. Trích xuất nội dung từ 1 file PDF
def extract_text_from_pdf_path(file_path: str) -> str:
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.strip()

# 2. Chunk văn bản
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

# 3. Gọi LLM để sinh câu hỏi - câu trả lời từ 1 chunk
def generate_faq_from_chunk(chunk: str) -> List[dict]:
    system_message = f"""Tạo các cặp câu hỏi - câu trả lời từ đoạn văn mà người dùng cung cấp bằng tiếng Việt:
    Hãy phân tích cẩn thận và trả về kết quả dưới dạng JSON, tuyệt đối không có gì khác, đặc biệt là không có dấu ngoặc kép ở đầu và cuối.:
    [{{"question": "...", "answer": "..."}}]

    """
    agent = AssistantAgent(
        name="controller",
        system_message=system_message,
        llm_config={
                "model": "llama3-70b-8192",
                "api_key": env.GROQ_API_KEY,
                "api_type": "groq",
            }
    )
    user_message = {"role": "user", "content": chunk}
    response = agent.generate_reply(
        messages=[user_message],
        function_call={"name": "extract_product"}
    )

    data = re.sub("Tiki", "IUH-Ecommerce", response["content"], flags=re.IGNORECASE)
    
    match = re.search(r'\[.*\]', data, re.DOTALL)
    
    if match:
        try:
            json_str = match.group(0)
            data = json.loads(json_str)
            print("Dữ liệu JSON được xử lý thành công")
            print(data)
        except json.JSONDecodeError as e:
            print(f"Lỗi khi giải mã JSON: {e}")
            print(f"JSON string: {json_str}")
            # Nếu JSON không hợp lệ, thử một cách khác sử dụng json5
            try:
                data = json5.loads(json_str)
                print("Xử lý thành công bằng json5")
                print(data)
            except Exception as e2:
                print(f"Lỗi khi giải mã bằng json5: {e2}")
                return []
    else:
        print("Không tìm thấy JSON.")
        return []
    
    if isinstance(data, list):
        # Validate structure of each FAQ
        valid_faqs = []
        for item in data:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                valid_faqs.append(item)
            else:
                print(f"Bỏ qua mục không hợp lệ: {item}")
        return valid_faqs
    else:
        print("Dữ liệu không phải là danh sách.")
        print(data)
        return []

# 4. Lưu kết quả vào DB
def save_faqs_to_db(faqs: List[dict]):
    with db_session() as session:
        for faq in faqs:
            # Check if required keys exist
            if "question" not in faq or "answer" not in faq:
                print(f"Bỏ qua FAQ không hợp lệ: {faq}")
                continue
                
            record = FQA(
                question=faq["question"],
                answer=faq["answer"],
                created_at=datetime.utcnow()
            )
            session.add(record)
        session.commit()

# 5. API để load toàn bộ file PDF trong thư mục
@router.post("/")
def process_pdf_folder():
    if not os.path.exists(PDF_FOLDER):
        return {"message": f"Thư mục '{PDF_FOLDER}' không tồn tại."}

    total_faqs = 0
    processed_files = 0
    failed_files = []
    
    try:
        for filename in os.listdir(PDF_FOLDER):
            if filename.lower().endswith(".pdf"):
                try:
                    print(f"Đang xử lý file: {filename}")
                    path = os.path.join(PDF_FOLDER, filename)
                    text = extract_text_from_pdf_path(path)
                    chunks = chunk_text(text)
                    
                    file_faqs = 0
                    for chunk in chunks:
                        try:
                            faqs = generate_faq_from_chunk(chunk)
                            
                            if faqs:
                                save_faqs_to_db(faqs)
                                total_faqs += len(faqs)
                                file_faqs += len(faqs)
                        except Exception as e:
                            print(f"Lỗi khi xử lý chunk từ file {filename}: {str(e)}")
                    
                    print(f"Đã tạo {file_faqs} FAQ từ file {filename}")
                    processed_files += 1
                    
                    # Chỉ xóa file nếu xử lý thành công
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"Không thể xóa file {path}: {str(e)}")
                except Exception as e:
                    print(f"Lỗi khi xử lý file {filename}: {str(e)}")
                    failed_files.append(filename)
    except Exception as e:
        print(f"Lỗi không mong muốn: {str(e)}")
        return {"message": f"Lỗi xử lý: {str(e)}", "total_files_processed": processed_files, "total_faqs": total_faqs, "failed_files": failed_files}

    return {
        "message": f"Đã xử lý thư mục PDF. Tổng số Q&A được lưu: {total_faqs}",
        "total_files_processed": processed_files,
        "failed_files": failed_files
    }

## test

if __name__ == "__main__":
    pdf_path = "tiki_policies/bookcare-la-gi.pdf"  
    text = extract_text_from_pdf_path(pdf_path)
    chunks = chunk_text(text)
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        print(chunk)
        print("-" * 20)
        faqs = generate_faq_from_chunk(chunk)
        print(f"type(faqs): {type(faqs)}")
        #
        if faqs:
            save_faqs_to_db(faqs)
            print(f"Number of FAQs generated: {len(faqs)}")
        else:
            print("No FAQs generated.")