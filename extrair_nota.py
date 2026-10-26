import os
import base64
from importlib import import_module
import io

try:
    flask_module = import_module('flask')
except ModuleNotFoundError as exc:
    raise RuntimeError(
        'Flask is required to run this application. Install it with: pip install Flask.'
    ) from exc

Flask = flask_module.Flask
request = flask_module.request
jsonify = flask_module.jsonify

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def load_google_drive_dependencies():
    """Load optional Google Drive libraries only when Drive is used."""
    try:
        request_module = import_module('google.auth.transport.requests')
        credentials_module = import_module('google.oauth2.credentials')
        flow_module = import_module('google_auth_oauthlib.flow')
        discovery_module = import_module('googleapiclient.discovery')
        upload_module = import_module('googleapiclient.http')
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            'Google Drive dependencies are missing. Install google-auth, '
            'google-auth-oauthlib, and google-api-python-client in the active Python environment.'
        ) from exc

    return (request_module.Request, credentials_module.Credentials,
            flow_module.InstalledAppFlow, discovery_module.build,
            upload_module.MediaIoBaseUpload)

def get_drive_service():
    Request, Credentials, InstalledAppFlow, build, _ = load_google_drive_dependencies()
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_bytes, filename):
    try:
        _, _, _, _, MediaIoBaseUpload = load_google_drive_dependencies()
        service = get_drive_service()
        file_metadata = {'name': filename}
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='image/jpeg', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Arquivo enviado com sucesso para o Google Drive! ID: {file.get('id')}")
        return True
    except Exception as e:
        print(f"Erro ao enviar para o Google Drive: {e}")
        return False

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Webhook recebido da Evolution API!")
        
        message_data = data.get('data', {})
        message_base64 = message_data.get('message', {}).get('base64') or message_data.get('base64')
        
        if message_base64:
            image_bytes = base64.b64decode(message_base64)
            filename = f"recibo_{data.get('date_time', 'desconhecido')}.jpg"
            print(f"Processando imagem recebida: {filename}")
            upload_to_drive(image_bytes, filename)
        else:
            print("Mensagem recebida não contém dados em Base64 ou imagem.")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)