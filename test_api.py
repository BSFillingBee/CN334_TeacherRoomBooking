import os, requests
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking.settings')
django.setup()

system_instruction = '''You are an AI assistant for ECE Thammasat's room booking system.
ALWAYS return a SINGLE JSON object.
CRITICAL: You MUST ALWAYS reply in Thai language in the 'reply' field. Never reply in English.
CRITICAL: A 'Current Booking State' JSON will be provided in the user prompt. You MUST carry over ALL fields from it into your JSON response exactly as they are, unless the user explicitly updates them. Do not drop any fields.
CRITICAL: You MUST extract and include EVERY piece of booking information the user mentions (roomId/roomCode, date, start, end, attendees, purpose) in the JSON immediately.
CRITICAL: If any required booking information is missing, ask the user ONLY for the specific information that is missing in the 'reply' field. Do NOT ask for information you already have.
CRITICAL: If you have gathered ALL required booking information (room, date, start, end), your 'reply' MUST instruct the user to click the confirmation button below to complete the booking. Do NOT ask them a yes/no question.
When asked about available rooms, carefully check the Bookings context. A room is NOT available if it has a booking on the requested date that overlaps with the requested time. List ONLY the rooms that are truly free during the requested time.
Thai time hints: บ่าย 2 = 14:00, เช้า 9 = 09:00.
'''

contents = [
    {'role': 'user', 'parts': [{'text': 'อยากจองพรุ่งนี้ 930-1230'}]},
    {'role': 'model', 'parts': [{'text': '{"roomId": "", "roomCode": "", "date": "2026-05-18", "start": "09:30", "end": "12:30", "attendees": "", "purpose": "", "reply": "ต้องการจองห้องใดครับ"}'}]},
    {'role': 'user', 'parts': [{'text': 'Context: Today is 2026-05-17\nRooms: [{"id": "1", "code": "406-3", "name": "ห้องประชุม 1"}]\nBookings: []\nCurrent Booking State: {"date": "2026-05-18", "start": "09:30", "end": "12:30"}\n\nUser: มีห้องไหนบ้าง จะเอาไว้ติว'}]}
]

payload = {
    'systemInstruction': {'parts': [{'text': system_instruction}]},
    'contents': contents,
    'generationConfig': {
        'temperature': 0.2,
        'response_mime_type': 'application/json',
        'response_schema': {
            'type': 'OBJECT',
            'properties': {
                'roomId': {'type': 'STRING'}, 'roomCode': {'type': 'STRING'},
                'date': {'type': 'STRING'}, 'start': {'type': 'STRING'}, 'end': {'type': 'STRING'},
                'attendees': {'type': 'STRING'}, 'purpose': {'type': 'STRING'},
                'reply': {'type': 'STRING'}
            },
            'required': ['roomId', 'roomCode', 'date', 'start', 'end', 'attendees', 'purpose', 'reply']
        }
    }
}


def main():
    api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.AI_API_KEY}'
    resp = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
    print(resp.json()['candidates'][0]['content']['parts'][0]['text'])


if __name__ == '__main__':
    main()
