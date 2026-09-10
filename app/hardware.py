from app.services import money, settings


class ReceiptPrinter:
    def print_sale(self, sale) -> None:
        values = settings()
        lines = [values.get("store_name", "fyonka"), values.get("store_address", "baltim"), values.get("store_phone", ""), "-" * 32]
        for line in sale.lines:
            lines.append(f"{line.variant.product.name[:20]:20} {line.qty:>3} {money(line.line_total):>12}")
        lines += ["-" * 32, f"TOTAL {money(sale.total):>25}", "Cash", "Thank you"]
        print("\n".join(lines))


class LabelPrinter:
    def print_label(self, variant) -> None:
        print(f"LABEL | {variant.product.name[:24]} | {variant.barcode} | {money(variant.price)}")
