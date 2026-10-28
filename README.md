# Inventory Assistant Agent 📦🤖

## 📌 Project Overview

The Inventory Assistant is a single-agent, tool-using AI application for a retail business. A user types a plain-English request (for example, "SK-102 is low, order 20 more"), and an LLM decides which tool to call, with which arguments, to check stock levels, find low-inventory items, or place a reorder. Because reordering is a high-risk action, it is protected by a **human-in-the-loop approval step** that the model cannot bypass.

---

## 🔍 The Problem

Managing stock usually means manually looking up products, scanning for items that are running low, and placing purchase requests. This project shows how an AI agent can handle the lookup and decision steps from natural language, while a human stays in control of any action that spends money.

---

## 🏗️ How It Works

The agent is built with LangChain's `create_agent`, which binds a DeepSeek model to three tools and a system prompt.

| Tool | What it does | Risk |
|------|--------------|------|
| `get_product_info` | Returns stock level, reorder threshold, and cost for a product ID (e.g. `SK-100`) from `products.csv` | Low (read-only) |
| `list_low_stock_items` | Scans `products.csv` and returns every product where quantity on hand is at or below its reorder threshold | Low (read-only) |
| `request_order` | Initiates a purchase for a product ID and quantity | **High** (requires human approval) |

**Flow:**
1. The user's request is sent to the agent.
2. The LLM interprets the intent and chooses a tool, extracting arguments such as the product ID and quantity.
3. The tool runs. Read-only tools query the CSV with pandas.
4. For `request_order`, the terminal pauses and asks `(y/n)`. The order only goes through if the human types `y`.
5. The LLM reads the tool result and writes a final response.
6. An execution log prints each tool call, the data returned, and the final response.

---

## 🧠 Role of AI

The LLM (DeepSeek `deepseek-v4-flash`, temperature `0` for consistent behavior) is the decision-maker in the system. It:
- **Interprets** natural-language requests (no menus or hard-coded commands).
- **Selects the right tool** and extracts the arguments from the sentence.
- **Chains steps**, such as checking inventory before acting when asked about low stock.
- **Reports outcomes honestly**, including when an order is cancelled.

The data lookups and the approval gate are ordinary Python code, not AI. This is intentional: the approval check lives inside the tool, so even if a prompt tells the model to skip confirmation, the human check still happens.

---

## 🖼️ Example Run

The same request was run twice. The agent makes an identical tool call both times; only the human's answer changes the result.

**Run 1: approved (`y`)**
```
Agent is thinking...
CONFIRMATION REQUIRED: Reorder 20 units of SK-102? (y/n): y

---AGENT EXECUTION LOG---
[Tool call] request_order with args: {'product_id': 'SK-102', 'quantity': 20}
[Tool Result] REORDER SUCCESSFUL: Ordered 20 units of SK-102.

Final Response: I've placed the order for 20 units of SK-102. The reorder was successful.
```

**Run 2: declined (`n`)**
```
Agent is thinking...
CONFIRMATION REQUIRED: Reorder 20 units of SK-102? (y/n): n

---AGENT EXECUTION LOG---
[Tool call] request_order with args: {'product_id': 'SK-102', 'quantity': 20}
[Tool Result] REORDER CANCELLED: Human approval was not granted.

Final Response: The reorder for SK-102 (20 units) was cancelled - it didn't receive human approval.
```

Screenshot: [`Agent_Terminal_Response.png`](Agent_Terminal_Response.png)

> Note: the reorder is simulated. A confirmed order prints a success message but does not write to any file or external system.

---

## 🛠️ Tools & Technologies

- **Language:** Python 3
- **Agent framework:** LangChain (`create_agent`, `@tool`)
- **LLM:** DeepSeek via `langchain-deepseek`
- **Data:** pandas reading `products.csv`
- **Configuration:** `python-dotenv` (API key loaded from a `.env` file, kept out of the repo)

---

## ⚙️ Setup

1. Make sure `products.csv` is in the same folder as the script.
2. Create a `.env` file in that folder containing your API key (never share or commit it):
   ```
   DEEPSEEK_API_KEY=your_key_here
   ```
3. Create and activate a virtual environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   The prompt should now start with `(.venv)`.
4. Install the dependencies:
   ```
   pip install langchain langchain-deepseek pandas python-dotenv
   ```

## ▶️ Run

```
python3 Inventory_Assistant.py
```

The script sends a preset request to the agent, pauses for your `y`/`n` approval if an order is attempted, then prints the execution log and the agent's final response. To try other requests (for example, "Which items are low on stock?"), edit the `user_input` variable in the script.

---

## 📁 Repository Contents

- `Inventory_Assistant.py`: the agent
- `products.csv`: inventory data the tools read
- `Agent_Terminal_Response.png`: screenshot of a run
- `README` / `README.md`: documentation

Other data files in the repo (`employees.csv`, `orders.csv`, `transactions.csv`, `hr_policies.txt`, `return_policy.txt`) are not used by this agent.
