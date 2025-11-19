"""
Test script for the Room Service Agent
Run this to test the agent without making phone calls
"""

from agent import RoomServiceAgent

def test_agent():
    """Test the agent with various queries"""
    agent = RoomServiceAgent()
    call_sid = "test_call_001"
    
    print("=" * 60)
    print("Four Seasons Room Service Agent - Test Mode")
    print("=" * 60)
    print()
    
    # Test scenarios
    test_cases = [
        "Hello",
        "What's on the menu?",
        "Do you have burgers?",
        "What salads do you have?",
        "I'd like to order the d|Burger",
        "What did I order?",
        "How much is the salmon?",
        "Tell me about your pasta options",
        "Add a Caesar salad to my order",
        "What's my order total?",
        "Place my order"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n[Test {i}]")
        print(f"User: {query}")
        response = agent.process_message(call_sid, query)
        print(f"Agent: {response}")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_agent()


