import json
import re

def clean_text_final(text):
    """
    Membersihkan hasil akhir teks pertanyaan/jawaban.
    Menghapus tag HTML tersisa, spasi ganda, dan karakter aneh.
    """
    if not isinstance(text, str):
        return ""
    
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    
    text = re.sub(r'<[^>]+>', ' ', text)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    text = re.sub(r'^[0-9a-zA-Z]{1,2}[\.\)]\s+', '', text)
    
    return text

def is_valid_question(text):
    """
    Validasi apakah string ini benar-benar pertanyaan.
    """
    text = clean_text_final(text)
    if len(text) < 5: return False 
    
    question_words = [
        "apa", "apakah", "bagaimana", "bagaimanakah", 
        "siapa", "siapakah", "kapan", "dimana", "kemana", "darimana",
        "mengapa", "kenapa", "berapa", 
        "syarat", "dasar hukum", "ketentuan", "prosedur", "langkah"
    ]
    
    text_lower = text.lower()
    
    if text.endswith('?'):
        return True
        
    first_words = " ".join(text_lower.split()[:3])
    if any(q in first_words for q in question_words):
        return True
        
    return False

def extract_faq(item):
    """
    Fungsi utama untuk membedah satu row data.
    """
    original_topic = clean_text_final(item.get('question', ''))
    raw_answer = item.get('answer_text', '')
    
    extracted_results = []
    
    # --- METODE 1: Split by HTML Tags (Strong/Bold/Heading) ---
    # Logika: Teks di dalam <strong> biasanya adalah sub-judul/pertanyaan
    # Kita cari pola: <strong>ISI_TEKS</strong> diikuti oleh JAWABAN
    
    # Regex ini mencari blok bold, lalu menangkap teks setelahnya sampai ketemu bold berikutnya
    # Pattern penjelasan:
    # (<(strong|b|h\d)>.*?<\/\2>)  -> Group 1: Tag pembuka + Isi (Pertanyaan) + Tag penutup
    # (.*?)                        -> Group 3: Isi Jawaban (non-greedy)
    # (?=<(strong|b|h\d)>|$)       -> Lookahead: Berhenti saat ketemu tag baru atau akhir string
    
    pattern_html = re.compile(r'(<(strong|b|h\d)[^>]*>.*?<\/\2>)(.*?)(?=(<(strong|b|h\d)[^>]*>.*?<\/\2>)|$)', re.DOTALL | re.IGNORECASE)
    
    matches_html = pattern_html.findall(raw_answer)
    
    if matches_html:
        for match in matches_html:
            q_raw = match[0] 
            a_raw = match[2] 
            
            q_clean = clean_text_final(q_raw)
            a_clean = clean_text_final(a_raw)
            
            if is_valid_question(q_clean) and a_clean:
                full_question = f"{original_topic} - {q_clean}"
                extracted_results.append({
                    "question": full_question,
                    "answer": a_clean
                })
            elif a_clean: 
      
                pass

    if not extracted_results:

        clean_raw = re.sub(r'<[^>]+>', ' ', raw_answer) # Hapus tag
        clean_raw = re.sub(r'\s+', ' ', clean_raw).strip() # Rapikan spasi
        
        q_starters = "Apa|Apakah|Bagaimana|Siapa|Kapan|Dimana|Mengapa|Kenapa|Berapa|Syarat|Dasar Hukum|Prosedur"

        
        pattern_text = re.compile(
            r'(?P<q>\b(?:' + q_starters + r')\b.*?\?)(?P<a>.*?(?=\b(?:' + q_starters + r')\b.*?\?|$))',
            re.IGNORECASE
        )
        
        matches_text = list(pattern_text.finditer(clean_raw))
        
        if matches_text:
            for m in matches_text:
                q_txt = clean_text_final(m.group('q'))
                a_txt = clean_text_final(m.group('a'))
                
                if q_txt and a_txt:
                    full_question = f"{original_topic} - {q_txt}"
                    extracted_results.append({
                        "question": full_question,
                        "answer": a_txt
                    })
    
    if not extracted_results:
        final_answer = clean_text_final(raw_answer)
        if final_answer:
            extracted_results.append({
                "question": original_topic,
                "answer": final_answer
            })
            
    return extracted_results

def process_json(input_file, output_file):
    print(f"Membaca file: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Jumlah data asli: {len(data)}")
        
        final_data = []
        for item in data:
            results = extract_faq(item)
            final_data.extend(results)
            
        print(f"Jumlah data setelah dipecah: {len(final_data)}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        print(f"Selesai! Hasil disimpan di: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_filename = 'filtered_pdf_without_nullpdf.json' 
    output_filename = 'faq_pajak_final.json'
    
    process_json(input_filename, output_filename)