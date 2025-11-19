"""
Four Seasons Room Service Phone Agent
Handles conversations about menu items and takes orders
"""

import os
from typing import Dict, List, Optional
from menu_data import MENU_CATEGORIES, search_menu, get_category_items, SERVICE_CHARGE_PERCENT, DELIVERY_FEE
from openai import OpenAI

class RoomServiceAgent:
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key" else None
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
    
    def process_message(self, call_sid: str, user_message: str) -> str:
        """Process user message and generate response"""
        # Store user message
        if call_sid not in self.conversation_history:
            self.conversation_history[call_sid] = []
            self.active_orders[call_sid] = []
        
        self.conversation_history[call_sid].append({
            "role": "user",
            "content": user_message
        })
        
        # Check for menu queries
        message_lower = user_message.lower()
        
        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            response = "Hello! Welcome to Four Seasons Toronto room service. I'm here to help you with our menu and take your order. How can I assist you today?"
        
        # Menu categories request
        elif any(word in message_lower for word in ["menu", "what do you have", "what's available", "options", "categories"]):
            response = self.get_menu_summary()
            response += " What would you like to know more about?"
        
        # Search for specific items
        elif any(word in message_lower for word in ["search", "find", "looking for", "have", "do you have"]):
            # Extract search terms
            search_terms = user_message
            for word in ["search", "find", "looking for", "have", "do you have", "i want", "i'd like"]:
                search_terms = search_terms.replace(word, "").strip()
            
            if search_terms:
                items = search_menu(search_terms)
                response = self.format_item_response(items)
            else:
                response = "What item would you like to search for?"
        
        # Category-specific queries
        elif any(word in message_lower for word in ["appetizer", "starter", "share", "soup", "salad", "sandwich", "entree", "main", "pasta", "dessert", "side"]):
            category_map = {
                "appetizer": "to_share",
                "starter": "to_share",
                "share": "to_share",
                "soup": "soups_salads",
                "salad": "soups_salads",
                "sandwich": "sandwiches",
                "entree": "entrees",
                "main": "entrees",
                "pasta": "pasta",
                "dessert": "dessert",
                "side": "sides"
            }
            
            category_key = None
            for keyword, key in category_map.items():
                if keyword in message_lower:
                    category_key = key
                    break
            
            if category_key:
                items = MENU_CATEGORIES[category_key]["items"]
                category_name = MENU_CATEGORIES[category_key]["name"]
                response = f"Here are our {category_name} options:\n"
                for item in items[:5]:  # Limit to 5 for voice
                    response += f"{item['name']} - {item['price']} dollars. "
                if len(items) > 5:
                    response += f"We have {len(items) - 5} more items in this category."
            else:
                response = "Which category would you like to explore?"
        
        # Price queries
        elif any(word in message_lower for word in ["price", "cost", "how much", "dollar"]):
            # Try to extract item name
            items = search_menu(user_message)
            if items:
                response = self.format_item_response(items)
            else:
                response = "Which item would you like to know the price for?"
        
        # Order taking
        elif any(word in message_lower for word in ["order", "i'll take", "i want", "i'd like", "add", "get me"]):
            # Extract item name from order
            order_terms = user_message
            for word in ["order", "i'll take", "i want", "i'd like", "add", "get me", "please"]:
                order_terms = order_terms.replace(word, "").strip()
            
            items = search_menu(order_terms)
            if items:
                # Add first matching item to order
                item = items[0]
                order_item = {
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": 1
                }
                self.active_orders[call_sid].append(order_item)
                response = f"Great! I've added {item['name']} to your order. That's {item['price']} dollars. Would you like to add anything else?"
            else:
                response = "I couldn't find that item. Could you please specify which item you'd like to order?"
        
        # Order review
        elif any(word in message_lower for word in ["review", "what did i order", "my order", "order summary"]):
            order = self.active_orders.get(call_sid, [])
            if order:
                response = "Here's your current order:\n"
                total = 0
                for item in order:
                    response += f"{item['name']} - {item['price']} dollars. "
                    total += item['price']
                response += f"\nSubtotal: {total} dollars. "
                service_charge = total * (SERVICE_CHARGE_PERCENT / 100)
                final_total = total + service_charge + DELIVERY_FEE
                response += f"With a {SERVICE_CHARGE_PERCENT} percent service charge and {DELIVERY_FEE} dollar delivery fee, your total is {final_total:.2f} dollars."
            else:
                response = "You don't have any items in your order yet. What would you like to order?"
        
        # Checkout/Place order
        elif any(word in message_lower for word in ["place order", "checkout", "complete", "finish", "that's all", "done"]):
            order = self.active_orders.get(call_sid, [])
            if order:
                total = sum(item['price'] for item in order)
                service_charge = total * (SERVICE_CHARGE_PERCENT / 100)
                final_total = total + service_charge + DELIVERY_FEE
                response = f"Perfect! Your order has been placed. Your total is {final_total:.2f} Canadian dollars, including service charge and delivery fee. Your order will arrive in approximately 30 to 45 minutes. Thank you for choosing Four Seasons room service!"
                # Clear order after placement
                self.active_orders[call_sid] = []
            else:
                response = "You don't have any items in your order yet. What would you like to order?"
        
        # Use AI for more complex queries
        else:
            # Use OpenAI for natural conversation
            context = self.get_conversation_context(call_sid)
            menu_info = self.get_menu_summary()
            
            prompt = f"""You are a friendly and professional room service agent for Four Seasons Hotel Toronto. 
You help guests with menu inquiries and take orders over the phone.

Menu Information:
{menu_info}

Recent conversation:
{context}

User said: {user_message}

Respond naturally and helpfully. If they're asking about menu items, provide specific information. 
If they want to order, help them add items. Keep responses concise for phone conversation (2-3 sentences max).
Be warm, professional, and helpful."""

            if self.openai_client:
                try:
                    completion = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a professional room service agent for Four Seasons Hotel Toronto."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    response = completion.choices[0].message.content.strip()
                except Exception as e:
                    response = "I'm here to help with our menu. Would you like to hear about our categories or search for a specific item?"
            else:
                response = "I'm here to help with our menu. Would you like to hear about our categories or search for a specific item?"
        
        # Store agent response
        self.conversation_history[call_sid].append({
            "role": "assistant",
            "content": response
        })
        
        return response


