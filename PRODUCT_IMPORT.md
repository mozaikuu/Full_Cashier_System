# Product Import

The Products screen can import `.xlsx`, `.xlsm`, or `.csv` files. Use **Download Excel template** in the app to create a workbook with the correct headers and one example row.

## Required columns

Use these exact column names in the first row:

| Column     | Required | Example         | Rules                                               |
| ---------- | -------- | --------------- | --------------------------------------------------- |
| `name`     | Yes      | `Water`         | Product name                                        |
| `sku`      | No       | `WAT-001`       | Internal code; leave blank to generate one          |
| `barcode`  | No       | `6221234567890` | Barcode; leave blank to generate one                |
| `price`    | Yes      | `10.50`         | Selling price, numeric                              |
| `cost`     | No       | `7.00`          | Cost price, numeric; defaults to zero               |
| `stock`    | No       | `25`            | Opening quantity, whole number; defaults to zero    |
| `reorder`  | No       | `5`             | Low-stock threshold, whole number; defaults to zero |
| `category` | Yes      | `Drinks`        | Existing category or a new category name            |

The importer creates a category automatically when the category name does not already exist. Each valid row creates one product with one variant.

## Example CSV row

```csv
name,sku,barcode,price,cost,stock,reorder,category
Water,WAT-001,,10.50,7.00,25,5,Drinks
```

## Import behavior

- Blank rows are skipped.
- Invalid rows are reported with their row number while valid rows continue importing.
- Duplicate SKU or barcode values are reported as errors.
- Prices may contain decimals; stock and reorder must be whole numbers.
- Excel files should use the first worksheet.
- Keep the header row unchanged. Additional columns are ignored.
