import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.rag.agent.executor import AgentExecutor
from apps.rag.models import ChatHistory


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = "agent_chat"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send welcome message
        await self.send(
            text_data=json.dumps(
                {
                    "type": "system",
                    "message": "Connected to Agentic RAG System. How can I help you?",
                }
            )
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")
            user_id = text_data_json.get("user_id", "anonymous")

            if not message:
                return

            # Send user message back to confirm receipt (optional)
            await self.send(text_data=json.dumps({"type": "user_message", "message": message}))

            # Initialize Agent components
            # Note: AgentExecutor initializes everything internally
            agent = AgentExecutor()

            # Fetch history
            chat_history = await self.get_chat_history(user_id)

            # Execute agent logic (sync code needs to be wrapped)
            response = await sync_to_async(agent.run)(message, chat_history=chat_history)

            # Save chat history
            await self.save_chat_history(user_id, message, response)

            # Send agent response
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "agent_response",
                        "message": response.get("answer"),
                        "sources": response.get("sources", []),
                        "steps": response.get("steps_taken", []),
                    }
                )
            )

        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    @sync_to_async
    def save_chat_history(self, user_id, query, response):
        """Save chat interaction to database."""
        # This is a simplified history saving.
        # In a real app, you might append to an existing conversation.
        ChatHistory.objects.create(
            user=user_id,
            messages=[
                {"role": "user", "content": query},
                {"role": "assistant", "content": response.get("answer")},
            ],
        )

    @sync_to_async
    def get_chat_history(self, user_id):
        """Fetch recent chat history with this endpoint."""
        history_objs = ChatHistory.objects.filter(user=user_id).order_by("-created_at")[:5]
        chat_history = []
        for h in reversed(history_objs):
            if isinstance(h.messages, list):
                chat_history.extend(h.messages)
        return chat_history
