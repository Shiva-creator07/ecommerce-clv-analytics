
## Data Setup

This project uses the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle. Raw CSVs are not committed to this repo.

To download the data yourself:

```bash
pip install kaggle
# place your kaggle.json API token in ~/.kaggle/kaggle.json
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```
