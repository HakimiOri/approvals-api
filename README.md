# Approvals API Utility

---

This repository contains a FastAPI-based API and a Python script for querying ERC20 token approvals on Ethereum addresses.

## Table of Contents
- [API Overview](#api-overview)
- [Running the API](#running-the-api)
- [API Endpoint](#api-endpoint)
- [Attachments](#attachments)
- [Running `my_approvals.py` Script](#running-my_approvalspy-script)
- [Example Requests](#example-requests)

---

## API Overview

The Approvals API provides a REST endpoint to fetch the latest ERC20 token approvals for one or more Ethereum addresses. Optionally, it can also return the current USD price for each token.

### Prerequisites
- **Infura API Key:** Obtain an API key from [Infura](https://infura.io/).
- **Python 3:** Ensure Python 3 is installed on your system.

---

## Running the API

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
2. **Set your Infura API key as an environment variable:**
   ```
   export INFURA_API_KEY="YOUR_INFURA_API_KEY"
   ```
3. **Start the API server:**
   ```
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

---

## API Endpoint

### `POST /get_approvals`
Fetch the latest ERC20 approvals for a list of addresses.

- **Request Body:**
  ```json
  {
    "addresses": ["0x...", "0x..."],
    "include_prices": true // Optional, set to true to include token prices
  }
  ```
- **Response Example:**
  ```json
  {
    "approvalsByAddress": {
      "0x...": [
        {
          "token": "SLP",
          "spender": "0x...",
          "amount": "4000",
          "price_usd": 0.123 // Only if include_prices=true
        }
      ]
    }
  }
  ```
- **Error Handling:** Returns HTTP 500 with error details on failure.

## Example Requests

You can test the API using the included `test_main.http` file.

---

## Attachments

* `erc20_transfer_approval_overview.txt`: An overview document explaining ERC20 Token Standard `approval`, `transfer`, and `transferFrom` functions.
* `my_approvals.py`: A Python script that fetches and displays all past ERC20 token approvals for a specified public address.

---

## Running `my_approvals.py` Script

The `my_approvals.py` script allows you to fetch and display all past ERC20 token approvals for a given Ethereum address from the command line.

### Prerequisites
- **Infura API Key:** Obtain an API key from [Infura](https://infura.io/).
- **Python 3:** Ensure Python 3 is installed on your system.

### Installation
Before running the script, set your Infura API key as an environment variable:

```
export INFURA_API_KEY="YOUR_INFURA_API_KEY"
# Replace "YOUR_INFURA_API_KEY" with your actual Infura API key.
```

### Usage
Run the script from your terminal:

```
python ./attachments/my_approvals.py --address <PUBLIC_ADDRESS>
# Replace <PUBLIC_ADDRESS> with the blockchain address you want to query.
```

### Example
```
python ./attachments/my_approvals.py --address 0x28C6c06298d514Db089934071355E5743bf21d60
```

### Sample Output
```
Fetching latest approvals:
Approval on SLP for 4,000 to 0x64192819Ac13Ef72bF6b5AE239AC672B43a9AF08
Approval on GALA for 0 to 0x956AAE9c8267390A036a6D41b3dE7E1e2044230e
... (more approvals)
```

### Additional Options
For more information on command-line arguments, use the --help flag:

```bash
python ./attachments/my_approvals.py --help
```

---
