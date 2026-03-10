from flask import Flask, request, jsonify
import requests, anthropic, os
app = Flask(__name__)
TELEGRAM_TOKEN = '8230619479:AAFfI3YSBUBx-4xOpoEiaCLDnwUrXLxE8xo'
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
SYSTEM_PROMPT = 'Voce e o assistente pessoal do Bruno Camossi via Telegram. Fale em portugues, seja parceiro e direto.'
def send_message(chat_id, text):
    requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id':chat_id,'text':text,'parse_mode':'Markdown'}, timeout=10)
def send_typing(chat_id):
    requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction', json={'chat_id':chat_id,'action':'typing'}, timeout=5)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data: return jsonify({'ok':True})
    msg = data['message']; chat_id = msg['chat']['id']; text = msg.get('text','')
    if not text: return jsonify({'ok':True})
    send_typing(chat_id)
    try:
        r = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY).messages.create(model='claude-haiku-4-5-20251001',max_tokens=1024,system=SYSTEM_PROMPT,messages=[{'role':'user','content':text}])
        send_message(chat_id, r.content[0].text)
    except Exception as e:
        send_message(chat_id, 'Erro interno.')
    return jsonify({'ok':True})
@app.route('/', methods=['GET'])
def health(): return jsonify({'status':'online'})
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
