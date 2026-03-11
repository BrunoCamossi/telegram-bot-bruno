from flask import Flask, request, jsonify
import requests
import anthropic
import os
import traceback

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8230619479:AAFfI3YSBUBx-4xOpoEiaCLDnwUrXLxE8xo')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

SYSTEM_PROMPT = 'Voce e o assistente pessoal do Bruno Camossi via Telegram. Bruno e empreendedor com startups: Focos Biblia e outras. Usa Claude/Cowork para produtividade e automacao. Fale sempre em portugues brasileiro. Seja direto, inteligente e parceiro. Respostas concisas. /status = bot ativo via webhook | /ajuda = lista capacidades'

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
        print(f'send_message status: {r.status_code}')
    except Exception as e:
        print(f'send_message error: {e}')

def send_typing(chat_id):
    try:
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction',
                      json={'chat_id': chat_id, 'action': 'typing'}, timeout=5)
    except:
        pass

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print(f'Received: {data}')
    except Exception as e:
        print(f'JSON parse error: {e}')
        return jsonify({'ok': True})

    if not data or 'message' not in data:
        return jsonify({'ok': True})

    message = data['message']
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if not chat_id or not text:
        return jsonify({'ok': True})

    send_typing(chat_id)

    try:
        if not ANTHROPIC_API_KEY:
            raise ValueError('ANTHROPIC_API_KEY not set')

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': text}]
        )
        reply = response.content[0].text
        print(f'Claude reply: {reply[:100]}')
        send_message(chat_id, reply)

    except Exception as e:
        print(f'ERROR: {e}')
        print(traceback.format_exc())
        send_message(chat_id, f'Erro: {str(e)[:200]}')

    return jsonify({'ok': True})

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'api_key_set': bool(ANTHROPIC_API_KEY)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
