"""
GSTCalculator — Indian Goods & Services Tax.

The rule:
    - If customer_state == seller_state (or seller_state is "")  =>  intra-state
        -> charge CGST + SGST (split equally, e.g. 9% + 9% = 18%)
    - Else  =>  inter-state
        -> charge IGST (e.g. 18%)

Customers without a state code default to IGST (safe choice).
"""

from decimal import Decimal

from billing_engine.money import Money
from billing_engine.taxes.base import TaxCalculator, TaxContext, TaxBreakdown


class GSTCalculator(TaxCalculator):
    def __init__(self, cgst: Decimal, sgst: Decimal, igst: Decimal) -> None:
        if cgst + sgst != igst:
         raise ValueError("cgst + sgst must equal igst")

        self.cgst = cgst
        self.sgst = sgst
        self.igst = igst

    def apply(self, taxable: Money, context: TaxContext) -> TaxBreakdown:
        intra = bool(context.customer_state) and (
        context.customer_state == context.seller_state
    )
        if intra:
            cgst_tax = taxable * self.cgst
            sgst_tax = taxable * self.sgst

            return TaxBreakdown(
            [
                ("CGST", cgst_tax),
                ("SGST", sgst_tax),
            ],
            cgst_tax + sgst_tax,
        )

        igst_tax = taxable * self.igst

        return TaxBreakdown(
            [("IGST", igst_tax)],
            igst_tax,
    )

     