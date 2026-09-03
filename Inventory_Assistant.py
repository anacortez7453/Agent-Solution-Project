#import packages
import os
import pandas as pd 
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek

#Loading the envrionment variables 
load_dotenv()

#Tool Num1
#Would get the stock levels, reorder thresholds, and costs for specific product ID.
@tool
def get_product_info(product_id: str) -> str:
    """Retrieves stock levels, reorder thresholds, and costs for a specifc product ID. The input should be a product ID like 'SK-100'."""
    df = pd.read_csv("products.csv")
    product = df[df['product_id']==product_id.upper()]

    if product.empty:
        return f"No product found with ID {product_id}."
    return product.to_string(index=False)

#Tool Num2
#Scan inventory and returns list of all products wher equantity on hand less than or equal to reorder threshold
@tool
def list_low_stock_items() -> str:
    """Scans inventory and returns a list of all products wher stock is at or below the reorder threshold."""
    df = pd.read_csv("products.csv")
    low_stock = df[df['quantity_on_hand'] <= df['reorder_threshold']]

    if low_stock.empty:
        return "All items are currently at healthy stock levels."
    return low_stock[['product_id', 'name', 'quantity_on_hand', 'reorder_threshold']].to_string(index=False)

#High Risk
#Initiates a purchase fromt the vendor
#The human in the loop
@tool
def request_order(product_id: str, quantity: int) -> str:
    """Initiates a formal purchase from the vendor. This is a high-risk action requiring human approval."""
    confirm = input(f"CONFIRMATION REQUIRED: Reorder {quantity} units of {product_id}? (y/n): ")
    if confirm.lower() == 'y':
        return f"REORDER SUCCESSFUL: Ordered {quantity} units of {product_id}."
    return "REORDER CANCELLED: Human approval was not granted."

#Starts the DeepSeek model
#Set to 0 fro consistency
model = ChatDeepSeek(
    model="deepseek-v4-flash",
    temperature=0 
)

#Define prompt for agent tone/behavior
system_prompt = (
    "You are a helpful Inventory Assistant for a retail buisness."
    "Your goal is to help the user manage stock levels using the provided tools."
    "When asked about low stock, check the inventory first."
    "Use the request_reorder tool immediately when a specific request is made."
)

#Factory call, binding the model and toiols to a runnable agent loo[]
agent =  create_agent(
    model,
    tools=[get_product_info, list_low_stock_items, request_order],
    system_prompt=system_prompt
)

#Define query, forces agent to use tools
user_input = "The inventory shows SK-102 is low. Call the request_order tool IMMEDIATELY to order 20 more. Do not ask for confirmation in the chat, just execute the tool."

#Agent loop
print("Agent is thinking...")
result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})

#The required logging that inspects the message history for tool usage
#log-> when agent decides to call tool, data returned from csv to agent, log final response of agent
print("\n---AGENT EXECUTION LOG---")
for message in result["messages"]:
    if getattr(message, "tool_calls", None):
        for tc in message.tool_calls:
            print(f"[Tool call] {tc['name']} with args: {tc['args']}")
    elif message.__class__.__name__ == "ToolMessage":
        print(f"[Tool Result] {message.content}")
    elif message.type == "ai":
        print (f"\nFinal Response: {message.content}")