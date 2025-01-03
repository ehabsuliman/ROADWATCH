from fastapi import FastAPI, Request
from pydantic import BaseModel
from catboost import CatBoostClassifier
import pandas as pd
import json
import re
from rapidfuzz import fuzz

# Initialize FastAPI app
app = FastAPI()

# Load your trained model
model = CatBoostClassifier()
model.load_model("/teamspace/studios/this_studio/ROADWATCH/Road/catboost_model_98.cbm")  # Replace with the path to your trained CatBoost model

# Define location names, close words, and open words
location_names = [
"المنشية", "يتسهار", "صرة", "زعترة", "عصيرة", "المساكن", "المربعة",
"بوابة بورين", "دير شرف", "عورتا", "بيت فوريك", "بزاريا", "شافي شمرون",
"حومش", "عناب", "الكفريات", "حجة", "وادي قانا", "بيت ليد", "كفر لاقف",
"الحمرا", "عوفرا", "ارئيل", "سلفيت", "رام الله", "نابلس", "عين سينيا",
"عطارة", "روابي", "عيون الحرامية", "ترمسعيا", "سنجل", "كركر", "بيت ايل",
"عزون", "جماعين", "كفل حارس", "مردا", "اللبن الشرقية", "بديا", "برقين",
"الزعيم", "العيزرية", "قلنديا", "جبع", "الكونتينر", "عش الغراب",
"مخماس", "جيت", "بيتا", "دير بلوط", "ياسوف", "النبي الياس", "سعير",
"حلحول", "حوارة", "راس الجورة", "عناتا", "حزما", "اماتين", "بيرزيت",
"النبي صالح", "افرات", "تقوع", "دورا", "عتصيون", "العروب", "فرش الهوى",
"حاجز النفق", "شارع بيجن", "الخليل", "واد النار", "DCO", "بيت جالا",
"اريحا", "برقة", "الغرس", "يتما", "الساوية", "يبرود", "سلواد",
"الطيبة", "النشاش", "طولكرم", "المسعودية", "بيت ايل", "جنين",
"قلقيلية", "عيلي", "كدوميم", "مخيم الجلزون", "روجيب", "شعفاط",
"الرام", "بيت لحم", "حوارة", "قبلان", "عينبوس", "بيت عور", "القرع",
"اودلا", "معالي ادوميم", "حزما", "السيلة", "نور شمس", "بلعا",
"الجفتلك", "الباذان", "البيرة", "بركان", "حبلة", "حرميش", "طوباس",
"السيلة", "افرايم", "ضواحي القدس", "القدس", "العبيدية", "بيت ساحور",
"تل الربيع", "يطا", "الظاهرية", "ترقوميا", "دير شرف", "شقبا",
"النفق", "شيلو", "عطروت", "حلميش", "المشتل", "عقربا", "قلنديا",
"سبسطية", "الفوار", "ادوميم", "العبيدية", "جين صافوت", "زواتا",
"حومش", "دير استيا", "العوجا", "بيت امر", "قباطية", "الجلزون",
"عطارة", "الخروبة", "عارورة", "الاحراش", "عصيرة الشمالية", "جيوس", "عين يبرود",
"عنبتا", "الناقورة", "الدهيشة", "بيت امرين", "قوصين", "عناتا",
"باب الزاوية", "الصيرفي", "صوريف", "ضاحية الريحان", "ابو ديس", "سالم",
"العيسوية", "بيت حنينا", "البيرة", "الاسكانات", "الزاوية", "النصارية",
"واد قانا", "المصانع", "كفر عقب", "بير زيت", "عصيرة القبلية", "الفندق"
]

close_words = [
'مغلق', 'مغلقة', 'وقوف', 'واقفه', 'سكروه', 'مسكره', 'سكر',
'مسكرين', 'متوقفه', 'اغلاق', 'اغلاقه'
]
open_words = [
'فتح', 'فاضي', 'سالك', 'سالكه', 'فاتحة', 'فاتح', 'سلك', 'فتحت',
'فاتحين', 'بمشو', 'مفتوحة', 'بسلك', 'بمشي', 'مشوا', 'فتحوها', 'سالكات', 'وسلك'
]

# Telegram Bot Token and API URL
TELEGRAM_BOT_TOKEN = "7917315228:AAFpcIq2HePtKTcCj9iMsRL978tlCdIxXlQ"  # Replace with your bot token
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = "https://your-server.com/webhook"  # Replace with your server URL

# Preprocessing and Tokenization Function
def preprocess_and_tokenize(data, location_names, close_words, open_words, similarity_threshold=80, close_threshold=80, open_threshold=80):
    def remove_emojis(text):
        if isinstance(text, str):
            return re.sub(r'[^\w\s,.!?؛:\n]', '', text)
        return text

    data['message'] = data['message'].apply(remove_emojis)
    
    def regex_tokenize_with_similarity(data, location_names, similarity_threshold, close_threshold, open_threshold):
        sentence_splitter = re.compile(r'(?<=[.!?]) +')
        word_splitter = re.compile(r'[\u0600-\u06FF]+|\d+|\w+')
        sentences_list, words_list, original_messages, word_indices, labels, similarities = [], [], [], [], [], []
        sentence_count = 1

        for index, message in data['message'].items():
            if isinstance(message, str):
                sentences = sentence_splitter.split(message.strip())
                for sentence in sentences:
                    words = word_splitter.findall(sentence)
                    i = 0
                    while i < len(words):
                        if i + 1 < len(words) and f"{words[i]} {words[i+1]}" in location_names:
                            labels.extend(["B-LOC", "I-LOC"])
                            similarities.extend([100, 100])
                            sentences_list.extend([f"Sentence: {sentence_count}"] * 2)
                            words_list.extend([words[i], words[i + 1]])
                            original_messages.extend([message] * 2)
                            word_indices.extend([i + 1, i + 2])
                            i += 2
                            continue
                        elif words[i] in location_names:
                            labels.append("B-LOC")
                            similarities.append(100)
                        else:
                            max_close_similarity = max(fuzz.ratio(words[i], word) for word in close_words)
                            if max_close_similarity >= close_threshold:
                                labels.append("B-close")
                                similarities.append(max_close_similarity)
                            else:
                                max_open_similarity = max(fuzz.ratio(words[i], word) for word in open_words)
                                if max_open_similarity >= open_threshold:
                                    labels.append("B-open")
                                    similarities.append(max_open_similarity)
                                else:
                                    max_loc_similarity = max(fuzz.ratio(words[i], loc) for loc in location_names)
                                    labels.append("B-LOC" if max_loc_similarity >= similarity_threshold else "O")
                                    similarities.append(max_loc_similarity if max_loc_similarity >= similarity_threshold else 0)

                        sentences_list.append(f"Sentence: {sentence_count}")
                        words_list.append(words[i])
                        original_messages.append(message)
                        word_indices.append(i + 1)
                        i += 1
                    sentence_count += 1

        return pd.DataFrame({
            'Sentence #': sentences_list,
            'Word': words_list,
            'Original Message': original_messages,
            'Word Index': word_indices,
            'label': labels,
            'Similarity Score': similarities
        })

    tokenized_df = regex_tokenize_with_similarity(data, location_names, similarity_threshold, close_threshold, open_threshold)
    tokenized_df['label'] = tokenized_df['label'].replace({'I-LOC': 'B-LOC', 'B-open': 'B-STATE', 'B-close': 'B-STATE'})
    return tokenized_df

# FastAPI endpoint to handle Telegram Webhook
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        # Parse incoming Telegram update
        update = await request.json()
        message_text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

        # Preprocess and tokenize the message
        data = pd.DataFrame({"message": [message_text]})
        tokenized_df = preprocess_and_tokenize(data, location_names, close_words, open_words)

        # Extract features for prediction
        features = tokenized_df.drop(columns=['label', 'Original Message', 'Sentence #'], errors='ignore')
        prediction = model.predict(features)

        # Send prediction back to Telegram
        response_message = f"Predicted condition: {prediction[0]}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": response_message})
        return {"status": "success"}

    except Exception as e:
        return {"error": str(e)}

# Set Telegram Webhook
@app.on_event("startup")
async def set_webhook():
    response = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}")
    print(f"Webhook set: {response.json()}")

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
