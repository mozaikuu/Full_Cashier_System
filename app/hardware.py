from app.services import money, settings


class ReceiptPrinter:
    def print_sale(self, sale) -> None:
        values = settings()
        lines = [values.get("store_name", "fyonka"), values.get("store_address", "baltim"), values.get("store_phone", "")]
        if getattr(sale, "buyer_name", ""):
            lines.append(f"المشتري: {sale.buyer_name}")
        if getattr(sale, "buyer_phone", ""):
            lines.append(f"الموبايل: {sale.buyer_phone}")
        lines += ["-" * 32, "الصنف / الباركود       الكمية  الإجمالي"]
        for line in sale.lines:
            lines.append(f"{line.variant.product.name[:18]:18} {line.qty:>3} {money(line.line_total):>12}")
            lines.append(f"باركود: {line.variant.barcode}")
        lines += ["-" * 32, f"الإجمالي {money(sale.total):>20}", "نقداً", "شكراً لزيارتكم"]
        self._send("\n".join(lines) + "\n\n\x1dV\x00", values.get("receipt_printer", ""))

    def test(self) -> None:
        self._send("اختبار طابعة الإيصالات\n\n\x1dV\x00", settings().get("receipt_printer", ""))

    @staticmethod
    def _send(text: str, printer_name: str) -> None:
        # The console fallback keeps development safe when no printer is connected.
        if printer_name:
            try:
                import win32print
                handle = win32print.OpenPrinter(printer_name)
                try:
                    win32print.StartDocPrinter(handle, 1, ("Sandy Cashier", None, "RAW"))
                    win32print.StartPagePrinter(handle)
                    win32print.WritePrinter(handle, text.encode("cp1256", errors="replace"))
                    win32print.EndPagePrinter(handle)
                    win32print.EndDocPrinter(handle)
                finally:
                    win32print.ClosePrinter(handle)
                return
            except (ImportError, OSError):
                pass
        print(text)


class LabelPrinter:
    def print_label(self, variant, copies: int = 1) -> None:
        values = settings()
        copies = max(1, int(copies))
        tspl = f"SIZE 58 mm,40 mm\nGAP 2 mm,0 mm\nCLS\nTEXT 20,20,\"3\",0,1,1,\"{variant.product.name[:24]}\"\nBARCODE 20,65,\"128\",60,1,0,2,2,\"{variant.barcode}\"\nTEXT 20,140,\"3\",0,1,1,\"{money(variant.price)}\"\nPRINT {copies}\n"
        self._send(tspl, values.get("label_printer", ""))

    def test(self) -> None:
        self._send("SIZE 58 mm,40 mm\nCLS\nTEXT 20,20,\"3\",0,1,1,\"اختبار الملصق\"\nPRINT 1\n", settings().get("label_printer", ""))

    @staticmethod
    def _send(command: str, printer_name: str) -> None:
        if printer_name:
            try:
                import win32print
                handle = win32print.OpenPrinter(printer_name)
                try:
                    win32print.StartDocPrinter(handle, 1, ("Sandy Cashier Label", None, "RAW"))
                    win32print.StartPagePrinter(handle)
                    win32print.WritePrinter(handle, command.encode("cp1256", errors="replace"))
                    win32print.EndPagePrinter(handle)
                    win32print.EndDocPrinter(handle)
                finally:
                    win32print.ClosePrinter(handle)
                return
            except (ImportError, OSError):
                pass
        print(command)
