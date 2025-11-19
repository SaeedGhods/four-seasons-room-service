# Four Seasons Room Service Phone Agent

A voice-enabled phone agent for Four Seasons Toronto room service that helps guests inquire about menu items and place orders over the phone.

## Features

- **Voice Interaction**: Natural speech-to-speech conversation using Twilio
- **Menu Inquiry**: Guests can ask about menu items, categories, prices, and descriptions
- **Order Taking**: Ability to add items to cart and place orders
- **Smart Search**: Search menu items by name or description
- **Order Management**: Review orders and calculate totals with service charges

## Setup

### Prerequisites

- Python 3.8+
- Twilio account with a phone number (already configured: +18566991536)
- OpenAI API key (optional, for advanced conversation handling)
- GitHub account (for deployment)
- Render account (free tier available at https://render.com)

### Installation

1. Clone or navigate to this directory:
```bash
cd "Phone Agent"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Twilio credentials in `.env`:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)

### Deployment to Production (Recommended)

**Quick Start:**
1. Run the setup script: `./setup_github.sh`
2. Create a GitHub repository
3. Push your code to GitHub
4. Deploy to Render (see `DEPLOYMENT.md` for detailed instructions)

**Detailed deployment guide:** See `DEPLOYMENT.md`

### Running Locally (Development)

1. Start the Flask server:
```bash
source venv/bin/activate
python app.py
```

2. The server will run on http://localhost:5000

**Note:** For local testing with Twilio, you'll need to use ngrok or deploy to Render. Production deployment is recommended.

## Usage

### Menu Queries

Guests can ask:
- "What's on the menu?"
- "Do you have burgers?"
- "What salads do you have?"
- "How much is the salmon?"
- "Tell me about your pasta options"

### Ordering

Guests can:
- "I'd like to order the d|Burger"
- "Add a Caesar salad to my order"
- "What did I order?" (review order)
- "Place my order" (checkout)

### Order Details

- All prices are in Canadian dollars
- 20% service charge is automatically added
- $6 delivery fee applies to all orders
- Orders are estimated to arrive in 30-45 minutes

## Menu Categories

The agent has access to the complete Four Seasons Toronto in-room dining menu:

- **To Share**: Appetizers and sharing plates
- **Soups and Salads**: Various soups and salad options
- **Enhancements**: Add-ons for salads and dishes
- **Sandwiches**: Burger and sandwich options
- **Entrées**: Main course dishes
- **Sides**: Side dish options
- **Pasta**: Pasta dishes
- **Dessert**: Dessert options

## Architecture

- `app.py`: Flask application handling Twilio webhooks
- `agent.py`: Core conversation logic and order management
- `menu_data.py`: Menu data structure and search functions

## Development

### Testing Locally

You can test the agent logic without making phone calls:

```python
from agent import RoomServiceAgent

agent = RoomServiceAgent()
response = agent.process_message("test_call_123", "What's on the menu?")
print(response)
```

### Customization

- Modify `menu_data.py` to update menu items
- Adjust conversation logic in `agent.py`
- Customize voice settings in `app.py` (currently using "alice" voice)

## Notes

- The agent uses OpenAI GPT-4 for handling complex queries
- Conversation history is maintained per call session
- Orders are stored in memory (consider database for production)
- Service charges and delivery fees are automatically calculated

## Production Considerations

For production deployment:
- Use a proper database for order storage
- Implement authentication and security
- Add logging and monitoring
- Set up proper error handling
- Consider using Twilio's recording features for quality assurance
- Implement order fulfillment integration with kitchen systems


