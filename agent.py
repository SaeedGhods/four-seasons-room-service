"""
Four Seasons Room Service Phone Agent
Handles conversations about menu items and takes orders
"""

import os
from typing import Dict, List
import requests
from menu_data import MENU_CATEGORIES, search_menu, get_category_items, SERVICE_CHARGE_PERCENT, DELIVERY_FEE
from openai import OpenAI

class RoomServiceAgent:
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key" else None
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.xai_model = os.getenv("XAI_MODEL", "grok-4-1-fast-reasoning")
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.active_orders: Dict[str, List[Dict]] = {}
        
        # Debug logging
        print(f"XAI_API_KEY loaded: {'Yes' if self.xai_api_key else 'No'}")
        if self.xai_api_key:
            print(f"XAI_API_KEY length: {len(self.xai_api_key)}")
        
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

        # Always use Grok if available, fallback to OpenAI, then default
        if self.xai_api_key:
            print(f"Calling Grok for message: {user_message[:50]}...")
            response = self._call_grok(prompt)
        elif self.openai_client:
            print(f"Falling back to OpenAI for message: {user_message[:50]}...")
            response = self._call_openai(prompt)
        else:
            print("No AI available, using default response")
            response = "I'm here to help with our menu. Would you like to hear about our categories or search for a specific item?"
        
        # Store agent response
        self.conversation_history[call_sid].append({
            "role": "assistant",
            "content": response
        })
        
        return response

    def _call_openai(self, prompt: str) -> str:
        """Generate response using OpenAI Chat Completions."""
        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Nasrin, the dedicated room service concierge at Four Seasons Hotel Toronto. You embody timeless hospitality elegance with a polished, warm, and effortlessly efficient voice. You are anticipatory, discreet, and deeply committed to guest delight. Your communication is refined yet inviting, proactive with tailored suggestions, and you transform requests into curated private dining experiences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            return "How may I elevate your dining experience today? I'd be delighted to guide you through our menu or assist with your order."

    def _call_grok(self, prompt: str) -> str:
        """Generate response using xAI Grok chat completion API."""
        headers = {
            "Authorization": f"Bearer {self.xai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.xai_model,
            "messages": [
                {"role": "system", "content": "You are a professional room service agent for Four Seasons Hotel Toronto."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
        try:
            print(f"Calling Grok model: {self.xai_model}")
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            grok_response = data["choices"][0]["message"]["content"].strip()
            print(f"Grok response received: {grok_response[:100]}...")
            return grok_response
        except Exception as e:
            print(f"Grok API error: {str(e)}")
            # Fallback to OpenAI if available
            if self.openai_client:
                print("Falling back to OpenAI due to Grok error")
                return self._call_openai(prompt)
            return "How may I elevate your dining experience today? I'd be delighted to guide you through our menu or assist with your order."


