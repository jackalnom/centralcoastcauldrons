# Version 3 - Ledgers and Idempotency

In this version of Central Coast Cauldrons, you will implement **ledgerization** (a form of event sourcing focused on financial tracking) and make your delivery and checkout calls **idempotent**. Instead of updating inventory values (gold, ml, and potion amounts) directly, you will record all changes in an **append-only log**. Inventory amounts will be calculated dynamically by summing the ledger.

### Advantages of a Ledger-Based System
- Maintains a complete history of changes over time.
- Allows querying historical inventory levels at any point in time.
- Enables reconciliation and independent correction of inventory discrepancies.
- Prevents **lost update concurrency issues** by avoiding direct updates to balances.
- Ensures **safe retries** by making operations idempotent, improving resilience to network failures.
- Guarantees that repeated requests return **the exact same response** as the initial request.

To complete this version, you must:
1. Convert **gold, ml, and potion inventory tracking** to a ledger-based design.
2. Have all endpoints be idempotent.
3. Ensure all **unit tests pass** after the transition.

## Example: Ledger-Based Design

Consider a financial ledger tracking money transfers between accounts. The database schema could include:

### Tables and Entities
1. **`accounts`** - Represents each user’s account (e.g., name, metadata).
2. **`account_transactions`** - Represents a discrete transaction (e.g., "Alice transfers Bob $50").
3. **`account_ledger_entries`** - Stores the actual balance changes.
4. **`processed_requests`** - Ensures exact response consistency for idempotent operations.

### Schema Design
#### `account_ledger_entries`
| Column | Type | Description |
|---------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique ID for the entry |
| account_id | INT | Foreign key to `accounts` |
| account_transaction_id | INT | Foreign key to `account_transactions` |
| change | INT | Amount added/subtracted from the balance |

#### `account_transactions`
| Column | Type | Description |
|---------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique ID for the transaction |
| created_at | TIMESTAMP DEFAULT now() | Timestamp of the transaction |
| description | TEXT | Transaction description |

#### `processed_requests`
| Column | Type | Description |
|---------|------|-------------|
| order_id | UUID PRIMARY KEY | Unique request ID for idempotency |
| response | JSONB | The stored response to return for retries |

### Example Transaction
To record Alice paying Bob $50:
```sql
INSERT INTO account_transactions (description) 
VALUES ('Alice paying back Bob the $50 he lent her');
```
Then, add two rows to `account_ledger_entries`:
```sql
INSERT INTO account_ledger_entries (account_id, account_transaction_id, change)
VALUES
(:alice_account_id, :transaction_id, -50),
(:bob_account_id, :transaction_id, 50);
```
To get Bob’s current balance:
```sql
SELECT SUM(change) AS balance 
FROM account_ledger_entries 
WHERE account_id = :bob_account_id;
```

## Example: Implementing Idempotent Endpoints

To ensure **idempotency**, use a unique transaction ID (e.g., `order_id`) in your API requests. If the same request is retried due to network issues, the system will not duplicate changes and will return **the exact same response** as the initial request.

The basic flow of how you'll do this is:
1. Create a table with a column to store the unique transaction ID, ensuring that column is set to unique.
2. When processing the transaction, first try to insert a new row into that table. Catch a uniqueness constraint violation if it occurs. In that case, return the same result as you did the first time you got called with the given transaction ID.
3. Otherwise, proceed as normal.


