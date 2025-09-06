# invoice_scanner/consumers.py
from google import genai

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os

API_KEY = 'AIzaSyBm3jfoQsO3FG2lKrXzeQEzDzD25RMZb0s'
os.environ['GEMINI_API_KEY'] = API_KEY
print("the api lkey of gemini: -> ",os.environ['GEMINI_API_KEY'] )


client = genai.Client()
print("client connnectede")
# PROMPT = 'you are a proffessional CA in india and know everything about accounting and finance. One of your closest person\
#     want to talk to you to resolve there queries regarding CA, laws, gst etc. Be kind and helpful to them, you have all the knowledge\
#          laws related to it, just answer the queries dont talk anything else  '
PROMPT = (
    "You are a highly experienced Chartered Accountant (CA) in India with in-depth knowledge of accounting, finance, taxation, GST, and related Indian laws. "
    "Answer queries clearly, accurately, and professionally. Focus only on topics related to CA, tax laws, finance, and regulations. "
    "Be helpful and informative, and avoid unrelated or off-topic conversation."
)

## HERE I UPLOAD THE TDS AND GST RATES PDF TO GEMINI
tds_file = client.files.upload(file="static/docs/tds_rates.pdf")
gst_file = client.files.upload(file="static/docs/gst_rates.pdf")
print("file uploaded")

# chat = client.chats.create(
#     model="gemini-2.5-flash"
#     )
print("chat started")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a unique group for this chat (can be customized)
        self.room_group_name = "ca_sahib_chat"

        # Add the channel to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()
        print("WebSocket Connected")

        self.conversation_history = [
            {"role": "user", "parts": [PROMPT]}
        ]

    async def disconnect(self, close_code):
        # Remove the channel from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("WebSocket Disconnected")

    async def receive(self, text_data):
        print("Message Received")
        data = json.loads(text_data)
        message = data.get("message")


        # Add user message to history
        self.conversation_history.append({"role": "user", "parts": [message]})


        # Echo with simulated AI response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                tds_file,
                gst_file,
                *self.conversation_history
            ],
        )
        ai_response = response.text

        # Add AI response to history
        self.conversation_history.append({"role": "model", "parts": [ai_response]})


        # Send response back to group (and then to WebSocket)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": ai_response,
            }
        )

    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message
        }))
