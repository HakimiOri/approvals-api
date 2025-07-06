Markdown

# Approvals API Utility

---

This repository contains 

## Attachments

* `erc20_transfer_approval_overview.txt`: An overview document explaining ERC20 Token Standard `approval`, `transfer`, and `transferFrom` functions.
* `my_approvals.py`: A Python script that fetches and displays all past ERC20 token approvals for a specified public address.

## Getting Started

To run the `my_approvals.py` script, you'll need an Infura API key.

### Prerequisites

* **Infura API Key:** Obtain an API key from [Infura](https://infura.io/).
* **Python 3:** Ensure Python 3 is installed on your system.

### Installation

Before running the script, set your Infura API key as an environment variable:

```
export INFURA_API_KEY="YOUR_INFURA_API_KEY"
Replace "YOUR_INFURA_API_KEY" with your actual Infura API key.
```

### Usage
Run the my_approvals.py script from your terminal:

```
python ./attachments/my_approvals.py --address <PUBLIC_ADDRESS>
Replace <PUBLIC_ADDRESS> with the blockchain address you want to query.
```
### Example
Here's an example of how to run the script and its expected output:

```Bash
python ./attachments/my_approvals.py --address 0x28C6c06298d514Db089934071355E5743bf21d60
```

### Sample Output:
```Bash
Fetching latest approvals:
Approval on SLP for 4,000 to 0x64192819Ac13Ef72bF6b5AE239AC672B43a9AF08
Approval on GALA for 0 to 0x956AAE9c8267390A036a6D41b3dE7E1e2044230e
Approval on SHIB for 0 to 0x956AAE9c8267390A036a6D41b3dE7E1e2044230e
Approval on APE for 0 to 0x956AAE9c8267390A036a6D41b3dE7E1e2044230e
Approval on SHIB for 0 to 0x825f275cFD2CDED7671dcCAF88265F6b86FF8888
Approval on SHIB for 0 to 0xfdd294C02CAc9F8206Ad3c8d7A674c84dbDc865a
Approval on SHIB for 0 to 0x8d835e8C672acC0BE26824F3FeeC203D9100e42A
Approval on SHIB for 0 to 0xcC53a5249e46B43925E79c075b43bFF2B0Df4A06
Approval on SHIB for 0 to 0x249fCC09862a1E8b1Cb960AEb47e5DB0d7874146
Approval on MATIC for 0 to 0x825f275cFD2CDED7671dcCAF88265F6b86FF8888
Approval on MEMES for 0 to 0x405f91EeD369aac25c3Dd7c9281BEeCEBC792628
Approval on MessiPeme for 0 to 0x132247c5Da548a07e3ae7Eb6dB60fB27a50AED8D
Approval on SUSHIBOT for 38,394,952,058,636 to 0xe98242ef4c30073f7E342eE78fcD33b3bCf887Aa
```

### Additional Options
For more information on command-line arguments, use the --help flag:

```Bash
python ./attachments/my_approvals.py --help
```