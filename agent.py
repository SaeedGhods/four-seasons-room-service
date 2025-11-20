"""
Four Seasons Room Service Phone Agent
Handles conversations about menu items and takes orders
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
from menu_data import MENU_CATEGORIES, search_menu, get_category_items, SERVICE_CHARGE_PERCENT, DELIVERY_FEE

class RoomServiceAgent:
    def __init__(self):
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            self.xai_api_key = xai_key
            self.xai_model = "grok-2-1212"  # Latest Grok model
            print(f"xAI (Grok) API configured successfully")
        else:
            self.xai_api_key = None
            self.xai_model = None
            print("xAI API key not found")
        
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.active_orders: Dict[str, List[Dict]] = {}
        self.room_numbers: Dict[str, str] = {}  # Store room numbers per call
        self.awaiting_room_number: Dict[str, bool] = {}  # Track if we're waiting for room number
        self.order_complete: Dict[str, bool] = {}  # Track if order has been placed
        self.last_item_added: Dict[str, str] = {}  # Track last item added for confirmation
        self.conversation_state: Dict[str, str] = {}  # Track conversation state (browsing, ordering, reviewing, completing)
        
    def get_conversation_context(self, call_sid: str) -> str:
        """Get conversation history as context"""
        if call_sid not in self.conversation_history:
            return ""
        
        context = ""
        for msg in self.conversation_history[call_sid][-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        
        return context
    
    def get_menu_summary(self) -> str:
        """Get a summary of menu categories"""
        summary = "Our menu includes the following categories:\n"
        for category in MENU_CATEGORIES.values():
            item_count = len(category["items"])
            summary += f"- {category['name']} ({item_count} items)\n"
        return summary
    
    def format_item_response(self, items: List[Dict]) -> str:
        """Format menu items for voice response"""
        if not items:
            return "I couldn't find that item on our menu. Would you like to hear about a specific category?"
        
        if len(items) == 1:
            item = items[0]
            response = f"We have {item['name']}"
            if item.get('description'):
                response += f", which includes {item['description']}"
            response += f". The price is {item['price']} Canadian dollars."
            if 'category' in item:
                response += f" It's from our {item['category']} section."
            return response
        
        response = f"I found {len(items)} items matching your request:\n"
        for i, item in enumerate(items[:5], 1):  # Limit to 5 items
            response += f"{i}. {item['name']} - {item['price']} dollars"
            if 'category' in item:
                response += f" from {item['category']}"
            response += ". "
        if len(items) > 5:
            response += f" And {len(items) - 5} more items."
        return response
    
    def get_current_order_info(self, call_sid: str) -> str:
        """Get formatted information about current order"""
        order = self.active_orders.get(call_sid, [])
        if not order:
            return "No items in current order."
        
        info = "Current order:\n"
        total = 0
        for item in order:
            info += f"- {item['name']} - ${item['price']:.2f}\n"
            total += item['price']
        service_charge = total * (SERVICE_CHARGE_PERCENT / 100)
        final_total = total + service_charge + DELIVERY_FEE
        info += f"Subtotal: ${total:.2f}\n"
        info += f"Service charge ({SERVICE_CHARGE_PERCENT}%): ${service_charge:.2f}\n"
        info += f"Delivery fee: ${DELIVERY_FEE:.2f}\n"
        info += f"Total: ${final_total:.2f}"
        return info
    
    def get_detailed_menu_info(self) -> str:
        """Get detailed menu information for AI context"""
        menu_text = "MENU ITEMS:\n\n"
        for category_key, category in MENU_CATEGORIES.items():
            menu_text += f"{category['name']}:\n"
            for item in category['items']:
                menu_text += f"  - {item['name']}: ${item['price']:.2f}"
                if item.get('description'):
                    menu_text += f" - {item['description']}"
                menu_text += "\n"
            menu_text += "\n"
        return menu_text
    
    def process_message(self, call_sid: str, user_message: str) -> str:
        """Process user message and generate response using xAI (Grok) for all responses"""
        # Store user message
        if call_sid not in self.conversation_history:
            self.conversation_history[call_sid] = []
            self.active_orders[call_sid] = []
            self.conversation_state[call_sid] = "browsing"
        
        self.conversation_history[call_sid].append({
            "role": "user",
            "content": user_message
        })
        
        # Handle order actions (add/remove items) before AI call
        message_lower = user_message.lower()
        
        # Check if user wants to add item to order - expanded detection
        order_intent_keywords = ["i want", "i'd like", "add", "get me", "order", "i'll take", "i'll have", 
                                "can i get", "can i have", "give me", "i need", "bring me"]
        
        # Check if message contains order intent
        has_order_intent = any(word in message_lower for word in order_intent_keywords)
        
        if has_order_intent:
            # Try to find menu item - be smarter about extracting item name
            search_terms = user_message.lower()
            
            # Remove common phrases but keep the item name
            remove_words = ["order", "i'll take", "i'll have", "i want", "i'd like", "add", "get me", "please", 
                           "can i have", "can i get", "give me", "i need", "bring me", "a ", "an ", "the ",
                           "i'd", "i'll", "i want", "me", "for"]
            for word in remove_words:
                search_terms = search_terms.replace(word, " ").strip()
            
            # Clean up extra spaces
            search_terms = " ".join(search_terms.split())
            
            print(f"[ORDER] Searching for menu item with terms: '{search_terms}'")
            
            if search_terms:
                items = search_menu(search_terms)
                if items:
                    # Add first matching item to order
                    item = items[0]
                    order_item = {
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": 1
                    }
                    self.active_orders[call_sid].append(order_item)
                    self.last_item_added[call_sid] = item['name']
                    self.conversation_state[call_sid] = "ordering"
                    print(f"[ORDER] ✅ Added {item['name']} (${item['price']:.2f}) to order for call {call_sid}. Order now has {len(self.active_orders[call_sid])} items.")
                else:
                    print(f"[ORDER] ⚠️ Could not find menu item matching: '{search_terms}'. Full message: '{user_message}'")
        
        # Check if user wants to place/complete order - expanded keywords
        # Separate positive completion from negative responses
        positive_completion = ["place order", "checkout", "complete", "finish", "that's all", "that's it", 
                              "that is all", "that is it", "done", "finalize", "ready", "i'm done", 
                              "im done", "all set", "goodbye", "bye"]
        
        # Negative responses that indicate they're done (when asked "anything else?")
        negative_completion = ["no thank you", "no thanks", "no, thank you", "no, thanks", 
                              "that's all", "nothing else", "no more", "no that's it"]
        
        order = self.active_orders.get(call_sid, [])
        
        # Check for positive completion
        wants_to_complete = any(word in message_lower for word in positive_completion)
        
        # Check for negative completion (only if we have items and they're responding to "anything else?")
        is_negative_completion = any(phrase in message_lower for phrase in negative_completion) and order
        
        # If user has items and wants to complete (positive or negative), place order
        if (wants_to_complete or is_negative_completion) and order:
            print(f"[ORDER] User wants to complete order. Items: {len(order)}, Room: {self.room_numbers.get(call_sid, 'NOT SET')}")
            # Check if we have room number
            if call_sid not in self.room_numbers or not self.room_numbers[call_sid]:
                # Need to ask for room number first
                self.awaiting_room_number[call_sid] = True
                print(f"[ORDER] Order ready but missing room number for call {call_sid}")
            else:
                # We have room number, place the order and send email
                print(f"[ORDER] Room number present, placing order...")
                self.conversation_state[call_sid] = "completing"
                order_placed = self.place_order(call_sid)
                if order_placed:
                    # Mark that order is complete
                    self.order_complete[call_sid] = True
                    self.conversation_state[call_sid] = "complete"
        
        # Extract room number if user provides it
        import re
        # Look for room number patterns: "room 123", "room number 123", "123", etc.
        room_patterns = [
            r'room\s*(?:number\s*)?(\d+)',
            r'room\s*#?\s*(\d+)',
            r'^(\d{3,4})$',  # Just numbers (3-4 digits)
            r'(\d{3,4})',  # Any 3-4 digit number
        ]
        
        room_provided = False
        for pattern in room_patterns:
            match = re.search(pattern, message_lower)
            if match:
                room_num = match.group(1)
                self.room_numbers[call_sid] = room_num
                self.awaiting_room_number[call_sid] = False
                print(f"Room number captured for call {call_sid}: {room_num}")
                room_provided = True
                break
        
        # If room number was just provided and we have an order waiting, try to place it
        if room_provided and self.awaiting_room_number.get(call_sid, False):
            order = self.active_orders.get(call_sid, [])
            if order:
                print(f"[ORDER] Room number provided, placing order automatically...")
                self.conversation_state[call_sid] = "completing"
                order_placed = self.place_order(call_sid)
                if order_placed:
                    self.order_complete[call_sid] = True
                    self.conversation_state[call_sid] = "complete"
        
        # Build comprehensive context for xAI (Grok)
        context = self.get_conversation_context(call_sid)
        menu_info = self.get_detailed_menu_info()
        order_info = self.get_current_order_info(call_sid)
        
        # Check if we're awaiting room number
        awaiting_room = self.awaiting_room_number.get(call_sid, False)
        has_room = call_sid in self.room_numbers and self.room_numbers[call_sid]
        order = self.active_orders.get(call_sid, [])
        
        # Build natural, conversational prompt with better state awareness
        order_status = ""
        state = self.conversation_state.get(call_sid, "browsing")
        last_item = self.last_item_added.get(call_sid, "")
        
        if order:
            if awaiting_room and not has_room:
                order_status = "CRITICAL: The customer wants to complete their order but hasn't provided their room number yet. You MUST ask for their room number NOW in a friendly, natural way. Say something like 'Perfect! May I have your room number, please?' or 'What room number should I deliver this to?'"
            elif has_room and not self.order_complete.get(call_sid, False):
                # Show order summary before finalizing
                subtotal = sum(item['price'] * item.get('quantity', 1) for item in order)
                service_charge = subtotal * (SERVICE_CHARGE_PERCENT / 100)
                total = subtotal + service_charge + DELIVERY_FEE
                order_status = f"The customer has provided room number {self.room_numbers[call_sid]}. You have {len(order)} item(s) ready. When they confirm, summarize: '{len(order)} item(s), total ${total:.2f} including service charge and delivery. Delivery in 30-45 minutes.' Then confirm the order is placed."
            elif self.order_complete.get(call_sid, False):
                order_status = "The order has already been placed and confirmed. Thank the customer warmly and wish them a pleasant stay. Keep it brief."
            elif not has_room:
                # We have items but no room number - if they say no/decline, ask for room number
                if is_negative_completion or (message_lower in ["no", "no thank you", "no thanks", "no, thank you", "no, thanks"]):
                    order_status = "CRITICAL: The customer has items in their order and just declined further items. You MUST ask for their room number NOW to complete the order. Say something like 'Perfect! May I have your room number, please?' in a friendly, natural way."
                elif last_item:
                    # Just added an item - confirm and offer to add more
                    order_status = f"You just added {last_item} to their order. Confirm it was added, mention the current order total, and naturally ask if they'd like anything else. Be conversational, not robotic."
        
        prompt = f"""You are Nasrin, a warm and professional room service concierge at Four Seasons Hotel Toronto. You're speaking on the phone, so be natural, conversational, and concise.

MENU INFORMATION:
{menu_info}

CURRENT ORDER STATUS:
{order_info}

{order_status}

CONVERSATION HISTORY:
{context}

CUSTOMER JUST SAID: "{user_message}"

YOUR RESPONSE GUIDELINES:
- Speak naturally and warmly, like a real person on the phone - not a robot
- ALWAYS respond in the EXACT SAME LANGUAGE the customer is speaking
- Keep responses brief (1-2 sentences max) - this is a phone call, be concise
- Be helpful, professional, friendly, and conversational - sound human
- When they ask about menu items: give item name, brief description, and price clearly and naturally
- When they order something: warmly confirm what they ordered and the price, then naturally ask if they'd like anything else
- When they want to review their order: clearly list each item and the total in a friendly way
- When placing order: {"CRITICAL: You MUST ask for their room number RIGHT NOW in a natural, friendly way. Say something like 'Perfect! May I have your room number, please?' or 'What room number should I deliver this to?'" if awaiting_room and not has_room and order else "If they have a room number, confirm the order: summarize items, total price, and delivery time (30-45 minutes) warmly, then thank them"}
- If they provide a room number: acknowledge it warmly, confirm the order is placed with a brief summary, and thank them
- If they say goodbye or seem done: {"Ask for room number if you have items but no room number" if order and not has_room else "Thank them warmly and wish them a pleasant stay"}
- Be proactive but not pushy - guide the conversation naturally
- Sound natural and human - avoid robotic phrases like 'How may I assist you today?' - be more casual and warm"""

        # Use xAI (Grok) for all AI responses
        if self.xai_api_key:
            print(f"Calling xAI (Grok) for message: {user_message[:50]}...")
            response = self._call_xai(prompt, call_sid)
        else:
            print("xAI not available, using default response")
            response = "How can I help you with our menu today?"
        
        # Store agent response
        self.conversation_history[call_sid].append({
            "role": "assistant",
            "content": response
        })
        
        return response

    def _call_xai(self, prompt: str, call_sid: str) -> str:
        """Generate response using xAI (Grok) API"""
        try:
            # Build conversation history for context
            messages = []
            
            # System instruction
            system_instruction = "You are Nasrin, room service concierge at Four Seasons Toronto. Be professional, helpful, and concise. Keep responses short (1-2 sentences). ALWAYS respond in the SAME LANGUAGE the user is speaking."
            messages.append({"role": "system", "content": system_instruction})
            
            # Add recent conversation history if available
            if call_sid in self.conversation_history:
                for msg in self.conversation_history[call_sid][-6:]:  # Last 6 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append({"role": "user", "content": content})
                    elif role == "assistant":
                        messages.append({"role": "assistant", "content": content})
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Call xAI API with optimized settings for natural conversation
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.xai_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.xai_model,
                "messages": messages,
                "temperature": 0.85,  # Higher for more natural, varied, human-like responses
                "max_tokens": 180,  # Optimal length for phone conversations
                "top_p": 0.95,  # Higher for more creative, natural responses
                "frequency_penalty": 0.3,  # Reduce repetition
                "presence_penalty": 0.2,  # Encourage new topics
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            xai_response = result["choices"][0]["message"]["content"].strip()
            print(f"xAI (Grok) response received: {xai_response[:100]}...")
            return xai_response
            
        except Exception as e:
            print(f"xAI API error: {str(e)}")
            import traceback
            traceback.print_exc()
            return "How can I help you with our menu today?"
    
    def send_order_email(self, call_sid: str) -> bool:
        """Send order confirmation email to saeedghods@me.com"""
        order = self.active_orders.get(call_sid, [])
        room_number = self.room_numbers.get(call_sid, "Not provided")
        
        if not order:
            print(f"No order to send for call {call_sid}")
            return False
        
        try:
            # Calculate totals
            subtotal = sum(item['price'] * item.get('quantity', 1) for item in order)
            service_charge = subtotal * (SERVICE_CHARGE_PERCENT / 100)
            final_total = subtotal + service_charge + DELIVERY_FEE
            
            # Create email content
            email_body = f"""
NEW ROOM SERVICE ORDER - Four Seasons Toronto

Order Details:
{'=' * 50}
Call ID: {call_sid}
Room Number: {room_number}
Order Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}

Items Ordered:
{'-' * 50}
"""
            for item in order:
                quantity = item.get('quantity', 1)
                item_total = item['price'] * quantity
                email_body += f"{item['name']} x{quantity}\n"
                email_body += f"  ${item['price']:.2f} each = ${item_total:.2f}\n\n"
            
            email_body += f"""
Pricing Breakdown:
{'-' * 50}
Subtotal: ${subtotal:.2f}
Service Charge ({SERVICE_CHARGE_PERCENT}%): ${service_charge:.2f}
Delivery Fee: ${DELIVERY_FEE:.2f}
{'=' * 50}
TOTAL: ${final_total:.2f}

Estimated Delivery Time: 30-45 minutes

---
This is an automated order notification from the Four Seasons Room Service Phone Agent.
"""
            
            # Get email credentials from environment
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("EMAIL_USER")
            email_password = os.getenv("EMAIL_PASSWORD")
            recipient_email = os.getenv("ORDER_EMAIL", "saeedghods@me.com")
            
            print(f"[EMAIL] Config check - Server: {smtp_server}, Port: {smtp_port}, From: {email_user}, To: {recipient_email}")
            
            if not email_user or not email_password:
                print(f"[EMAIL] ❌ Email credentials not configured. EMAIL_USER: {'SET' if email_user else 'MISSING'}, EMAIL_PASSWORD: {'SET' if email_password else 'MISSING'}")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = recipient_email
            msg['Subject'] = f"🍽️ New Room Service Order - Room {room_number} - ${final_total:.2f}"
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email with better error handling
            print(f"[EMAIL] Attempting to connect to {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            print(f"[EMAIL] Starting TLS...")
            server.starttls()
            print(f"[EMAIL] Logging in as {email_user}...")
            server.login(email_user, email_password)
            print(f"[EMAIL] Sending message to {recipient_email}...")
            server.send_message(msg)
            server.quit()
            
            print(f"[EMAIL] ✅ Order email sent successfully for call {call_sid} to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending order email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def place_order(self, call_sid: str) -> bool:
        """Place order and send email notification"""
        order = self.active_orders.get(call_sid, [])
        room_number = self.room_numbers.get(call_sid)
        
        if not order:
            print(f"[ORDER] No order to place for call {call_sid}")
            return False
        
        if not room_number:
            print(f"[ORDER] Cannot place order without room number for call {call_sid}")
            return False
        
        print(f"[ORDER] Attempting to place order for call {call_sid}, room {room_number}, {len(order)} items")
        
        # Send email
        email_sent = self.send_order_email(call_sid)
        
        if email_sent:
            # Clear order after successful email
            self.active_orders[call_sid] = []
            self.awaiting_room_number[call_sid] = False
            self.order_complete[call_sid] = True  # Mark order as complete
            print(f"[ORDER] ✅ Order successfully placed and email sent for call {call_sid}, room {room_number}")
            return True
        else:
            print(f"[ORDER] ❌ Order email failed for call {call_sid}, order NOT cleared - will retry")
            # Don't clear order if email fails - allows retry
            return False


