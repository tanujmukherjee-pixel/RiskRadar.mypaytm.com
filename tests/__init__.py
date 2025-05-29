import json
import time

# --- 1. Simulate Kibana Log Store ---
# In a real system, this would query Elasticsearch via Kibana's API
MOCK_KIBANA_LOGS = {
    "TXN12345": {
        "timestamp": "2025-05-29T10:00:00Z",
        "user_id": "user_A",
        "amount": 150.00,
        "status": "BLOCKED",
        "block_reason_code": "RULE_HIGH_VELOCITY",
        "message": "Transaction blocked by rule engine.",
        "details": {"ip_address": "192.168.1.100"}
    },
    "TXN67890": {
        "timestamp": "2025-05-29T10:05:00Z",
        "user_id": "user_B",
        "amount": 25.00,
        "status": "BLOCKED",
        "block_reason_code": "RULE_GEO_MISMATCH",
        "message": "Transaction blocked due to geographic mismatch.",
        "details": {"transaction_country": "USA", "card_issue_country": "IND"}
    },
    "TXN11223": {
        "timestamp": "2025-05-29T10:10:00Z",
        "user_id": "user_C",
        "amount": 5000.00,
        "status": "ALLOWED",
        "message": "Transaction successful."
    }
}

def fetch_kibana_log(transaction_id):
    """Simulates fetching a log from Kibana."""
    print(f"\n🔍 Searching Kibana for transaction ID: {transaction_id}...")
    time.sleep(0.5) # Simulate network delay
    log_entry = MOCK_KIBANA_LOGS.get(transaction_id)
    if log_entry:
        print(f"   Found log: {json.dumps(log_entry, indent=2)}")
        return log_entry
    else:
        print(f"   No log found for transaction ID: {transaction_id}")
        return None

# --- 2. Simulate "pi platform" Rule Store ---
# In a real system, this would query your "pi platform" API
MOCK_PI_PLATFORM_RULES = {
    "RULE_HIGH_VELOCITY": {
        "rule_name": "High Velocity Transaction Monitor",
        "description": "This rule blocks transactions if a user attempts more than 3 transactions within a 5-minute window from the same IP address.",
        "action": "BLOCK_TRANSACTION",
        "severity": "HIGH"
    },
    "RULE_GEO_MISMATCH": {
        "rule_name": "Geographic Location Mismatch",
        "description": "This rule flags or blocks transactions where the transaction origin country significantly differs from the card's issuing country or typical user location.",
        "action": "BLOCK_TRANSACTION",
        "severity": "MEDIUM"
    },
    "RULE_UNUSUAL_AMOUNT": {
        "rule_name": "Unusual Transaction Amount",
        "description": "This rule flags transactions that are significantly larger than the user's average transaction value.",
        "action": "REVIEW_MANUALLY",
        "severity": "MEDIUM"
    }
}

def fetch_pi_platform_rule(rule_id):
    """Simulates fetching a rule definition from the PI platform."""
    print(f"📚 Querying PI Platform for rule ID: {rule_id}...")
    time.sleep(0.3) # Simulate API call delay
    rule_details = MOCK_PI_PLATFORM_RULES.get(rule_id)
    if rule_details:
        print(f"   Found rule: {rule_details['rule_name']}")
        return rule_details
    else:
        print(f"   No rule definition found for rule ID: {rule_id}")
        return None

# --- 3. Chatbot Logic ---
def get_block_explanation(transaction_id):
    """
    Core logic to get an explanation for a blocked transaction.
    """
    log_entry = fetch_kibana_log(transaction_id)

    if not log_entry:
        return f"Sorry, I couldn't find any logs for transaction ID '{transaction_id}'."

    if log_entry.get("status") != "BLOCKED":
        return f"Transaction '{transaction_id}' was not blocked. Its status is '{log_entry.get('status')}'."

    rule_id = log_entry.get("block_reason_code")
    if not rule_id:
        return f"Transaction '{transaction_id}' was blocked, but the specific rule ID is missing in the logs. Log details: {log_entry.get('message')}"

    rule_details = fetch_pi_platform_rule(rule_id)
    if not rule_details:
        return f"Transaction '{transaction_id}' was blocked by rule ID '{rule_id}', but I couldn't find the details for this rule in the PI platform."

    explanation = f"\n--- Explanation for Transaction {transaction_id} ---"
    explanation += f"\nStatus: BLOCKED"
    explanation += f"\nTimestamp: {log_entry.get('timestamp')}"
    explanation += f"\nReason: Blocked by rule '{rule_details.get('rule_name')}' (ID: {rule_id})."
    explanation += f"\nRule Description: {rule_details.get('description')}"
    explanation += f"\nRule Action: {rule_details.get('action')}"
    explanation += f"\nLog Message: {log_entry.get('message')}"
    if log_entry.get("details"):
        explanation += f"\nAdditional Log Details: {json.dumps(log_entry.get('details'))}"
    explanation += f"\n--- End of Explanation ---\n"
    return explanation

# --- 4. Simple Command-Line Interface ---
def main():
    print("🚀 Welcome to the Risk Consult Bot (Local Demo) 🚀")
    print("I can help you understand why a transaction was blocked.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nEnter a Transaction ID to investigate: ").strip()

        if user_input.lower() == 'exit':
            print("👋 Goodbye!")
            break

        if not user_input:
            print("Please enter a transaction ID.")
            continue

        explanation = get_block_explanation(user_input)
        print(explanation)

if __name__ == "__main__":
    main()