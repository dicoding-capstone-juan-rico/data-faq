import json
import re

def clean_json_data(input_file, output_file):
    try:
        # Membaca file JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_data = []

        print(f"Memproses {len(data)} data awal...")

        for item in data:
            original_question = item.get('question', '').strip()
            answer_text = item.get('answer', '').strip()

            # 1. Hapus kata "Jawab:" atau sejenisnya di awal kalimat jawaban
            # Regex ini mencari 'Jawab' diikuti titik dua (:) dan spasi di awal string
            answer_text = re.sub(r'^(?:Jawab|Jawaban|Answer)[:\s]+', '', answer_text, flags=re.IGNORECASE).strip()

            # 2. Deteksi apakah ada pola "Pertanyaan? Jawab: Jawaban" di dalam teks answer
            # Kita memisahkan teks berdasarkan kata kunci pemisah seperti "Jawab:" yang berada di tengah kalimat
            # Pola regex ini mencari pemisah "Jawab:"/"Jawaban:" yang mungkin diawali spasi/tanda baca
            segments = re.split(r'(?:\s+Jawab:|\s+Jawaban:|\s+Answer:)\s*', answer_text, flags=re.IGNORECASE)

            # Jika tidak ada pecahan (hanya 1 segmen), berarti tidak ada pertanyaan terselip
            if len(segments) == 1:
                cleaned_data.append({
                    "question": original_question,
                    "answer": segments[0].strip()
                })
            else:
                # Jika ada pecahan, berarti ada pertanyaan baru yang terselip di akhir segmen sebelumnya
                # Logikanya: Segmen 0 berisi [Jawaban 1 + Pertanyaan 2] -> Segmen 1 berisi [Jawaban 2]
                
                current_question = original_question
                
                for i, segment in enumerate(segments):
                    segment = segment.strip()
                    if not segment: continue

                    # Jika ini bukan segmen terakhir, berarti di ujung teks ini ada "Pertanyaan Berikutnya"
                    if i < len(segments) - 1:
                        # Kita cari tanda tanya (?) terakhir dan titik/tanda baca sebelumnya
                        # Pola: Mengambil teks di akhir string yang diakhiri tanda tanya (?)
                        # Regex penjelasan:
                        # (.*[\.\!\)\n]) -> Group 1: Jawaban murni (diakhiri titik, seru, atau kurung tutup)
                        # \s* -> Spasi pemisah
                        # ([^.!?\n]+\?)$ -> Group 2: Pertanyaan baru (kalimat tanpa titik di tengah, diakhiri ?)
                        
                        match = re.search(r'(.*[\.\!\)\n])\s*([^.!?\n]+\?)$', segment, flags=re.DOTALL)
                        
                        if match:
                            real_answer = match.group(1).strip()
                            next_question = match.group(2).strip()
                            
                            # Simpan pasangan saat ini
                            cleaned_data.append({
                                "question": current_question,
                                "answer": real_answer
                            })
                            
                            # Pertanyaan untuk iterasi berikutnya
                            current_question = next_question
                        else:
                            # Fallback jika pola regex tidak ketemu (misal tidak ada tanda baca jelas)
                            # Kita anggap seluruh segmen adalah jawaban untuk pertanyaan saat ini
                            cleaned_data.append({
                                "question": current_question,
                                "answer": segment
                            })
                            current_question = "Pertanyaan Lanjutan (Silakan Cek Manual)"
                    else:
                        # Segmen terakhir adalah jawaban untuk pertanyaan terakhir yang ditemukan
                        cleaned_data.append({
                            "question": current_question,
                            "answer": segment
                        })

        # Menyimpan hasil ke file baru
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        print(f"Selesai! {len(cleaned_data)} data bersih disimpan di '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# Jalankan fungsi
if __name__ == "__main__":
    # Ganti nama file sesuai kebutuhan Anda
    input_filename = 'faq_pajak_final.json' 
    output_filename = 'faq_pajak_final_v2.json'
    
    clean_json_data(input_filename, output_filename)