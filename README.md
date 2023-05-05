# line-bot-azure-functions  
## Release Ver-1.0.1  
### ChatGPTLineBot  
### 概要  
OpenAIAPI、LINEMessageAPIを活用したChatGPTLineBot。  
### 使用技術  
* AzureFuctionsランタイムバージョン  
Linux  
4.17.3.3  
* pythonバージョン  
3.9.3  
* pythonライブラリー  
azure-functions  
azure-storage-blob  
line-bot-sdk  
openai  
### リリース事項  
* 以下、「表1-0-1-1」インターフェースを追加。  
<table>
  <tr>
    <th width="50">No</th>
    <th width="150">関数名</th>
    <th width="100">トリガー</th>
    <th width="500">説明</th>
  </tr>
  <tr>
    <td>1</td>
    <td>CreateMessageHttpTrigger</td>
    <td>HttpTrigger</td>
    <td>送信したLineメッセージから応答メッセージを作成。以下モードを追加。<br>1-ChatGPTモード(OpenAIAPIを使用し、メッセージをプロンプトとしたときの解答をLineメッセージ応答。)</td>
  </tr>
  <tr>
    <td>2</td>
    <td>CreateXLineSignatureHttpTrigger</td>
    <td>HttpTrigger</td>
    <td>LineMessageAPIで用いられるリクエストヘッダーx-line-signatureの値を作成。</td>
  </tr>
</table>

## Release Ver-1.0.2  
### 概要  
チャット履歴を保存する機能追加。  
### 使用技術  
* pythonライブラリー  
pytz  
