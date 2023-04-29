import logging
import os
import re
import json
import azure.functions as func
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from shared_code import blob_operation

# 定数
NEW_LINE_LINE_MESSAGE_API = '\n'
PACKET_STR_CODE = 'utf-8'
SIGNATURE_REQUEST_HEADER_NAME = 'x-line-signature'
CONTAINER_NAME_MESSAGE_MODE_TYPE = 'tsusho-bot-config'
BLOB_NAME_MESSAGE_MODE_TYPE = 'status.json'
FILE_STR_CODE_STAUS_JSON = 'utf-8'
LINE_MESSAGE_API_COUNT_KEY_STAUS_JSON = 'lineMessageAPICount'
MESSAGE_MODE_TYPE_KEY_STAUS_JSON = 'messageModeType'
MIN_MESSAGE_MODE_TYPE = 0
MAX_MESSAGE_MODE_TYPE = 1
NONE_MESSAGE_MODE_TYPE = '0'
NONE_MESSAGE_MODE_TYPE_NAME = '未選択モード'
CHATGPT_MESSAGE_MODE_TYPE = '1'
CHATGPT_MESSAGE_MODE_TYPE_NAME = 'ChatGPTモード'
# メッセージは将来的にjsonファイルで管理
INFO_001 = 'に変更されました。'
INFO_002 = 'LineMessageAPI回数:'
INFO_003 = 'モード:'
INFO_004 = '未選択'
WARNING_001 = 'モードを選択してください。'
WARNING_002 = '選択したモードはありません。選択できるモードを入力してください。'

# Azure FunctionsのApplication Settingに設定した値から取得する↓
channel_secret = os.getenv('TSUSHO_BOT_SECRET_KEY', None)
channel_access_token = os.getenv('TSUSHO_BOT_CHANEL_ACCESS_TOKEN', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # get x-line-signature header value
    signature = req.headers[SIGNATURE_REQUEST_HEADER_NAME]

    # get request body as text
    body = req.get_body().decode(PACKET_STR_CODE)
    logging.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        func.HttpResponse(status_code=400)

    return func.HttpResponse('OK')


def get_line_message_api_count():
    message_mode_type_blob_client = blob_operation.get_blob_client(CONTAINER_NAME_MESSAGE_MODE_TYPE, BLOB_NAME_MESSAGE_MODE_TYPE)
    json_dic = json.loads(message_mode_type_blob_client.download_blob().readall().decode(FILE_STR_CODE_STAUS_JSON))
    return int(json_dic[LINE_MESSAGE_API_COUNT_KEY_STAUS_JSON])


def get_message_mode_type():
    message_mode_type_blob_client = blob_operation.get_blob_client(CONTAINER_NAME_MESSAGE_MODE_TYPE, BLOB_NAME_MESSAGE_MODE_TYPE)
    json_dic = json.loads(message_mode_type_blob_client.download_blob().readall().decode(FILE_STR_CODE_STAUS_JSON))
    return json_dic[MESSAGE_MODE_TYPE_KEY_STAUS_JSON]


def get_message_mode_type_name(message_mode_type):
    message_mode_type_name = ''
    if message_mode_type == NONE_MESSAGE_MODE_TYPE:
        message_mode_type_name = NONE_MESSAGE_MODE_TYPE_NAME
    elif message_mode_type == CHATGPT_MESSAGE_MODE_TYPE:
        message_mode_type_name = CHATGPT_MESSAGE_MODE_TYPE_NAME
    return message_mode_type_name


def update_status_json(line_message_api_count, message_mode_type):
    message_mode_type_blob_client = blob_operation.get_blob_client(CONTAINER_NAME_MESSAGE_MODE_TYPE, BLOB_NAME_MESSAGE_MODE_TYPE)
    json_dic = json.loads(message_mode_type_blob_client.download_blob().readall().decode(FILE_STR_CODE_STAUS_JSON))
    json_dic[LINE_MESSAGE_API_COUNT_KEY_STAUS_JSON] = line_message_api_count
    if len(message_mode_type):
        json_dic[MESSAGE_MODE_TYPE_KEY_STAUS_JSON] = message_mode_type
    blob_operation.upload_json_blob(json_dic,CONTAINER_NAME_MESSAGE_MODE_TYPE, BLOB_NAME_MESSAGE_MODE_TYPE)
    message_mode_type_name = ''
    if message_mode_type == CHATGPT_MESSAGE_MODE_TYPE:
        message_mode_type_name = CHATGPT_MESSAGE_MODE_TYPE_NAME
    return message_mode_type_name


def crate_message_in_chatGPTAPI(rceivedMessage):
    return 'ChatGPTAPIでメッセージ作成しました。'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    received_message=event.message.text
    send_message=WARNING_001
    # モードを変更するか判定
    pattern_message_mode_type = re.compile(r"モード[0-9]{1}")
    result_matching_message_mode_type = pattern_message_mode_type.fullmatch(received_message)
    # LineMessageAPI情報を応答するか判定
    pattern_line_message_api_info_notify = re.compile(r"LB情報")
    result_matching_line_message_api_info_notify = pattern_line_message_api_info_notify.fullmatch(received_message)
    logging.debug("result_matching_message_mode_type: " + str(type(result_matching_message_mode_type)))
    updated_message_mode_type = ''
    updated_line_message_api_count = get_line_message_api_count() + 1
    # モードを変更
    if result_matching_message_mode_type:
        updated_message_mode_type = result_matching_message_mode_type.group().replace('モード', '')
        # jsonファイルを修正したとき、ソースを変更せず、制御できるようにしたい
        message_mode_type_name = get_message_mode_type_name(updated_message_mode_type)
        if len(message_mode_type_name):
            send_message = message_mode_type_name + INFO_001
        else:
            # モードにないため、初期化（この後、初期化しないと更新されてしまう）
            updated_message_mode_type = ''
            send_message = WARNING_002
    # LineMessageAPI情報作成
    elif result_matching_line_message_api_info_notify:
        now_message_mode_type_name = get_message_mode_type_name(get_message_mode_type())
        send_message = INFO_002 + str(updated_line_message_api_count) + NEW_LINE_LINE_MESSAGE_API + INFO_003 + now_message_mode_type_name
    # チャットモード
    else:
        # メッセージタイプを取得
        message_mode_type = get_message_mode_type()
        logging.debug("message_mode_type: " + message_mode_type)
        # チャットGPTモード
        if message_mode_type == CHATGPT_MESSAGE_MODE_TYPE:
            # チャットGPTAPIでメッセージ作成
            send_message = crate_message_in_chatGPTAPI(received_message)
    
    logging.debug("send_message: " + send_message)

    # status.json更新
    update_status_json(str(updated_line_message_api_count), updated_message_mode_type)

    # メッセージ応答
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=send_message)
    )
