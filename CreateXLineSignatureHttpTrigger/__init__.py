import logging
import os
import json
import hashlib
import hmac
import base64
import azure.functions as func

# 定数
PACKET_STR_CODE = 'utf-8'

channel_secret = os.getenv('TSUSHO_BOT_SECRET_KEY', None)

def create_base64_encode_digest_hmac_sh256(secret_key, payload):
    return base64.b64encode(hmac.new(secret_key, payload, hashlib.sha256).digest())


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # リクエストヘッダーはログ出力
    # 開発環境用LineBotで確認するとき、コメント解除
    # logging.info("Request header: " + json.dumps(req.headers.__dict__))
    # リクエストボディはログ出力
    req_body_bytes = req.get_body()
    logging.info("Request body: " + req_body_bytes.decode(PACKET_STR_CODE))
    # シークレットキー、データからHMAC-SHA-256アルゴリズムで作成したダイジェストをbase64エンコード
    result = create_base64_encode_digest_hmac_sh256(channel_secret.encode(), req_body_bytes).decode()
    logging.info('x-line-signature: ' + result)

    return func.HttpResponse('OK')
