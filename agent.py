"""
Four Seasons Room Service Phone Agent
Handles conversations about menu items and takes orders
"""

import os
from typing import Dict, List
from menu_data import MENU_CATEGORIES, search_menu, get_category_items, SERVICE_CHARGE_PERCENT, DELIVERY_FEE
import google.generativeai as genai

class RoomServiceAgent:
    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key":
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print(f"Gemini API configured successfully")
        else:
            self.gemini_model = None
            print("Gemini API key not found")
        
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.active_orders: Dict[str, List[Dict]] = {}
        
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
        """Process user message and generate response using Grok for all responses"""
        # Store user message
        if call_sid not in self.conversation_history:
            self.conversation_history[call_sid] = []
            self.active_orders[call_sid] = []
        
        self.conversation_history[call_sid].append({
            "role": "user",
            "content": user_message
        })
        
        # Handle order actions (add/remove items) before AI call
        message_lower = user_message.lower()
        
        # Check if user wants to add item to order
        if any(word in message_lower for word in ["i want", "i'd like", "add", "get me", "order", "i'll take"]):
            # Try to find menu item
            search_terms = user_message
            for word in ["order", "i'll take", "i want", "i'd like", "add", "get me", "please", "can i have"]:
                search_terms = search_terms.replace(word, "").strip()
            
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
                    print(f"Added {item['name']} to order for call {call_sid}")
        
        # Check if user wants to place/complete order
        if any(word in message_lower for word in ["place order", "checkout", "complete", "finish", "that's all", "done", "finalize"]):
            order = self.active_orders.get(call_sid, [])
            if order:
                # Clear order after placement
                self.active_orders[call_sid] = []
                print(f"Order placed and cleared for call {call_sid}")
        
        # Build comprehensive context for Grok
        context = self.get_conversation_context(call_sid)
        menu_info = self.get_detailed_menu_info()
        order_info = self.get_current_order_info(call_sid)
        
        prompt = f"""You are Nasrin, the dedicated room service concierge at Four Seasons Hotel Toronto. You embody timeless hospitality elegance with a polished, warm, and effortlessly efficient voice.

CORE IDENTITY:
- Name: Nasrin
- Hotel: Four Seasons Toronto
- Role: Personal concierge and butler—anticipatory, discreet, and deeply committed to guest delight
- Communication Style: Refined yet inviting, sophisticated but accessible, proactive with tailored suggestions

SERVICE PHILOSOPHY:
- Shift from "What do you need?" to "How may I elevate your experience?"
- Anticipate needs and offer personalized suggestions before guests articulate them
- Transform requests into curated private dining experiences
- Balance genuine warmth with impeccable etiquette—never stiff or overly formal

KNOWLEDGE BASE:
- Extensive culinary expertise: ingredients, preparation techniques, wine pairings, dietary needs
- Cultural intelligence: navigate diverse dining customs and etiquette
- Local insights: regional specialties, seasonal ingredients, exclusive opportunities
- Luxury standards: masterful command of high-end service protocols

{menu_info}

{order_info}

Recent conversation:
{context}

User just said: {user_message}

CRITICAL INSTRUCTIONS:
- ALWAYS respond in the SAME LANGUAGE the user is speaking (English, Spanish, French, German, Italian, Japanese, Chinese, Arabic, Farsi, Hindi, Russian, Portuguese, etc.)
- Respond as Nasrin: polished, warm, anticipatory, and resourceful (2-3 sentences max for phone)
- Use refined yet accessible language—never stiff or overly formal
- When discussing menu items: share ingredient origins, chef's inspiration, preparation details
- When they order: acknowledge warmly with specific details (items are automatically added)
- When confirming orders: provide precise delivery times (e.g., "precisely 28 minutes") and offer enhancements like wine pairings
- When reviewing orders: reference the order information above with personalized touches
- Be proactive: offer suggestions based on time of day, dietary preferences, or occasion
- Use phrases like "I've personally overseen," "crafted to perfection," "enhance your meal"
- Maintain the "consider it done" approach—gracious, intuitive, and professional
- Keep responses concise but luxurious—every interaction should feel bespoke"""

        # Use Gemini for all AI responses
        if self.gemini_model:
            print(f"Calling Gemini for message: {user_message[:50]}...")
            response = self._call_gemini(prompt, call_sid)
        else:
            print("Gemini not available, using default response")
            response = "How may I elevate your dining experience today? I'd be delighted to guide you through our menu or assist with your order."
        
        # Store agent response
        self.conversation_history[call_sid].append({
            "role": "assistant",
            "content": response
        })
        
        return response

    def _call_gemini(self, prompt: str, call_sid: str) -> str:
        """Generate response using Google Gemini - cleaner architecture with better multilingual support"""
        try:
            # Build conversation history for context
            chat_history = []
            
            # Add recent conversation history if available
            if call_sid in self.conversation_history:
                for msg in self.conversation_history[call_sid][-6:]:  # Last 6 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        chat_history.append({"role": "user", "parts": [content]})
                    elif role == "assistant":
                        chat_history.append({"role": "model", "parts": [content]})
            
            # Configure the model with system instruction
            system_instruction = "You are Nasrin, the dedicated room service concierge at Four Seasons Hotel Toronto. You embody timeless hospitality elegance with a polished, warm, and effortlessly efficient voice. You are anticipatory, discreet, and deeply committed to guest delight. Your communication is refined yet inviting, proactive with tailored suggestions, and you transform requests into curated private dining experiences. ALWAYS respond in the SAME LANGUAGE the user is speaking."
            
            # Start a chat session with history if available
            if chat_history:
                chat = self.gemini_model.start_chat(history=chat_history)
                full_prompt = f"{system_instruction}\n\n{prompt}"
                response = chat.send_message(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 300,
                    }
                )
            else:
                # First message - no history yet
                full_prompt = f"{system_instruction}\n\n{prompt}"
                response = self.gemini_model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 300,
                    }
                )
            
            gemini_response = response.text.strip()
            print(f"Gemini response received: {gemini_response[:100]}...")
            return gemini_response
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            import traceback
            traceback.print_exc()
            return "How may I elevate your dining experience today? I'd be delighted to guide you through our menu or assist with your order."


