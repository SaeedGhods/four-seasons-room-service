"""
Four Seasons Toronto In-Room Dining Menu Data
"""

MENU_CATEGORIES = {
    "to_share": {
        "name": "To Share",
        "items": [
            {
                "name": "Truffle Fries",
                "description": "Shaved Parmesan, Truffle Aioli",
                "price": 17
            },
            {
                "name": "Steamed Edamame",
                "description": "Everything but the Bagel Spice, Lemon",
                "price": 9
            },
            {
                "name": "Pita and House Dips",
                "description": "Smoked Aubergine and Garlic, Classic Hummus, Grilled Capsicum and Feta, served with warm pita",
                "price": 26
            },
            {
                "name": "Tuna Tacos",
                "description": "Flour Tortilla, Seared Sesame Tuna, Cilantro, Jalapeño, Avocado, Red Cabbage, Mango and Chili Salsa",
                "price": 28
            },
            {
                "name": "Buffalo Chicken Wings",
                "description": "Vegetable Crudités, Ranch Dressing",
                "price": 26
            },
            {
                "name": "Caviar - Kristal",
                "description": "Traditional Accoutrements, Potato Blinis, Shallots, Chives, Crème Fraîche, Egg (30g)",
                "price": 225
            },
            {
                "name": "Caviar - Ossetra Prestige",
                "description": "Traditional Accoutrements, Potato Blinis, Shallots, Chives, Crème Fraîche, Egg (50g)",
                "price": 325
            }
        ]
    },
    "soups_salads": {
        "name": "Soups and Salads",
        "items": [
            {
                "name": "Soup of the Day",
                "description": "Please inquire",
                "price": 17
            },
            {
                "name": "Hearty Chicken Noodle",
                "description": "Carrot, Celery, Onion, Chicken, Macaroni",
                "price": 20
            },
            {
                "name": "Beetroot and Stracciatella Cheese Salad",
                "description": "Artisanal Leaf, Grapefruit, Orange, Pistachios, Local Honey, Champagne Vinaigrette",
                "price": 26
            },
            {
                "name": "Fall Salad",
                "description": "Artisanal Leaf, Squash, Apple, Pumpkin Goat Cheese, Sunflower Seeds, Cranberry, Apple Cider Dressing",
                "price": 26
            },
            {
                "name": "Classic Caesar",
                "description": "Baby Gem, Croutons, Bacon Bits, Parmigiano Reggiano",
                "price": 24
            },
            {
                "name": "Falafel",
                "description": "Cos Lettuce, Radish, Pomegranate, Parsley, Mint, Capsicum, Heirloom Tomato, Cucumber, Sumac, Treacle Dressing",
                "price": 23
            }
        ]
    },
    "enhancements": {
        "name": "Enhancements",
        "items": [
            {"name": "Avocado", "description": "", "price": 11},
            {"name": "Grilled Tofu", "description": "", "price": 12},
            {"name": "Rotisserie Chicken Breast", "description": "", "price": 15},
            {"name": "Atlantic Salmon (6 oz.)", "description": "", "price": 18},
            {"name": "Garlic Prawns", "description": "", "price": 18}
        ]
    },
    "sandwiches": {
        "name": "Sandwiches",
        "items": [
            {
                "name": "d|Burger",
                "description": "Top Sirloin, Caramelized Onions, Sautéed Mushrooms, Provolone Cheese, Tomato, Lettuce, House Sauce",
                "price": 38
            },
            {
                "name": "Grilled Chicken Club",
                "description": "Double-Smoked Bacon, Cheddar Cheese, Fried Egg, Lettuce, Tomato, Garlic Aïoli",
                "price": 35
            },
            {
                "name": "Buffalo Chicken Caesar Wrap",
                "description": "Flour Tortilla, Cos Lettuce, Parmesan, Buffalo-Tossed Breaded Chicken, Caesar Dressing",
                "price": 26
            },
            {
                "name": "Short Rib Sandwich",
                "description": "Braised Beef, Coleslaw, Smoked Barbecue Sauce, Dill Pickles",
                "price": 32
            },
            {
                "name": "Mediterranean Garden Toast",
                "description": "Courgette, Aubergine, Carrot, Red Capsicum Spread, Toasted Sourdough",
                "price": 19
            }
        ]
    },
    "entrees": {
        "name": "Entrées",
        "items": [
            {
                "name": "Herb-Crusted Beef Tenderloin (7 oz.)",
                "description": "Chive Pomme Purée, Heirloom Carrots, with Peppercorn Jus or Red Wine Jus",
                "price": 54
            },
            {
                "name": "Corn-Fed Rotisserie Chicken",
                "description": "Roasted Baby Red Potatoes, Seasonal Vegetables, Chicken Jus",
                "price": 38
            },
            {
                "name": "Grilled Maple-Glazed Salmon",
                "description": "Red Capsicum Couscous, Asparagus, Shirazi Salsa",
                "price": 40
            },
            {
                "name": "Crispy Sesame Chicken",
                "description": "Crunchy Shallots, Courgette, Red Capsicum, Peanuts, Spring Onion, Kung Pao Sauce, Steamed Jasmine Rice",
                "price": 34
            },
            {
                "name": "Salmon Poke Bowl",
                "description": "Sushi Rice, Wakame, Avocado, Edamame, Radish-Green Onion, Tofu, Tobiko, Ponzu Dressing",
                "price": 33
            }
        ]
    },
    "sides": {
        "name": "Sides",
        "items": [
            {"name": "Pomme Purée", "description": "", "price": 12},
            {"name": "Steamed Jasmine Rice", "description": "", "price": 12},
            {"name": "House Green Salad", "description": "", "price": 12},
            {"name": "Steamed Vegetables", "description": "", "price": 12},
            {"name": "French Fries", "description": "", "price": 12},
            {"name": "Truffle Fries", "description": "", "price": 14},
            {"name": "Macaroni and Cheese", "description": "", "price": 14}
        ]
    },
    "pasta": {
        "name": "Pasta",
        "items": [
            {
                "name": "Classic Bolognese",
                "description": "Rigatoni, Beef Bolognese Sauce",
                "price": 27
            },
            {
                "name": "Basil Pesto Orecchiette",
                "description": "Green Beans, Cherry Tomato, Creamy Pesto Sauce, Parmesan",
                "price": 25
            },
            {
                "name": "Pasta Al Pomodoro",
                "description": "Basil, Parmigiano Reggiano, Extra Virgin Olive Oil; Pasta options: Orecchiette, Rigatoni, or Gluten-Free",
                "price": 22
            }
        ]
    },
    "dessert": {
        "name": "Dessert",
        "items": [
            {
                "name": "Chocolate Caramel Mousse",
                "description": "Dark Chocolate Mousse, Caramel Insert, Chocolate Brownie, Cocoa Nib Crunch",
                "price": 18
            },
            {
                "name": "Raspberry-Cashew Cheesecake",
                "description": "Cashew Cheesecake, Raspberry Gel, Vanilla Shortbread",
                "price": 17
            },
            {
                "name": "Banana Pudding",
                "description": "Banana Diplomate, Vanilla Crumble, Caramelized Banana",
                "price": 18
            },
            {
                "name": "Matcha Raspberry Tiramisu",
                "description": "Matcha Mascarpone Cream, Freeze-Dried Raspberry, Lady Finger Sponge",
                "price": 18
            },
            {
                "name": "House-made Ice Cream and Sorbet",
                "description": "Two scoops",
                "price": 12
            }
        ]
    }
}

SERVICE_CHARGE_PERCENT = 20
DELIVERY_FEE = 6

def get_all_items():
    """Get all menu items flattened"""
    all_items = []
    for category in MENU_CATEGORIES.values():
        all_items.extend(category["items"])
    return all_items

def search_menu(query):
    """Search menu items by name or description"""
    query_lower = query.lower()
    results = []
    
    for category_key, category in MENU_CATEGORIES.items():
        for item in category["items"]:
            if (query_lower in item["name"].lower() or 
                query_lower in item["description"].lower()):
                results.append({
                    "category": category["name"],
                    **item
                })
    
    return results

def get_category_items(category_name):
    """Get all items in a category"""
    category_lower = category_name.lower()
    for category_key, category in MENU_CATEGORIES.items():
        if category_lower in category["name"].lower() or category_lower in category_key:
            return category["items"]
    return []


