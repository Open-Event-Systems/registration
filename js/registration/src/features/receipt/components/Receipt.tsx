import { Currency } from "#src/features/cart/components/cart/Currency"
import { ComponentPropsWithoutRef, Fragment, ReactNode } from "react"
import clsx from "clsx"
import { PricingResult } from "#src/features/cart/types"
import { ReceiptRegistration } from "#src/features/receipt/components/Registration"
import { ReceiptLineItem } from "#src/features/receipt/components/LineItem"
import { ReceiptModifier } from "#src/features/receipt/components/Modifier"
import dayjs from "dayjs"

export type ReceiptProps = {
  receiptId: string
  pricingResult: PricingResult
} & ComponentPropsWithoutRef<"table">

export const Receipt = (props: ReceiptProps) => {
  const { receiptId, pricingResult, ...other } = props

  return (
    <Receipt.Root
      receiptId={receiptId}
      date={pricingResult.date ? formatDate(pricingResult.date) : undefined}
      totalPrice={pricingResult.total_price}
      {...other}
    >
      {pricingResult.registrations.map((reg, i) => (
        <Fragment key={reg.registration_id}>
          <ReceiptRegistration
            id={`r${i + 1}`}
            name={reg.name ?? undefined}
            receiptUrl={
              pricingResult.receipt_url
                ? getReceiptUrl(pricingResult.receipt_url, i + 1)
                : void 0
            }
          >
            {reg.line_items.map((li, i) => (
              <ReceiptLineItem
                key={i}
                name={li.name}
                price={li.price}
                description={li.description}
              >
                {li.modifiers.map((m, i) => (
                  <ReceiptModifier key={i} name={m.name} amount={m.amount} />
                ))}
              </ReceiptLineItem>
            ))}
          </ReceiptRegistration>
          <Receipt.Divider />
        </Fragment>
      ))}
    </Receipt.Root>
  )
}

export type ReceiptRootProps = {
  receiptId: string
  date?: string
  totalPrice: number
  children?: ReactNode
} & ComponentPropsWithoutRef<"table">

const ReceiptRoot = (props: ReceiptRootProps) => {
  const { receiptId, date, totalPrice, className, children, ...other } = props

  return (
    <table className={clsx("Receipt-root", className)} {...other}>
      <thead className="Receipt-header">
        <tr className="Receipt-headerRow">
          <th scope="col" colSpan={3} className="Receipt-title">
            Receipt <span className="Receipt-id">{receiptId}</span>
          </th>
        </tr>
        {date && (
          <tr className="Receipt-headerRow">
            <th scope="col" colSpan={3} className="Receipt-date">
              {date}
            </th>
          </tr>
        )}
      </thead>
      {children}
      <tfoot className="Receipt-footer">
        <tr className="Receipt-footerRow">
          <td colSpan={2} className="Receipt-totalName">
            Total
          </td>
          <td className="Receipt-totalAmount">
            <Currency amount={totalPrice} />
          </td>
        </tr>
      </tfoot>
    </table>
  )
}

export type ReceiptDividerProps = Omit<
  ComponentPropsWithoutRef<"tbody">,
  "children"
>

const ReceiptDivider = (props: ReceiptDividerProps) => {
  const { className, ...other } = props

  return (
    <tbody className={clsx("Receipt-divider", className)} {...other}></tbody>
  )
}

Receipt.Root = ReceiptRoot
Receipt.Divider = ReceiptDivider

const getReceiptUrl = (url: string, i: number) => {
  const urlObj = new URL(url, window.location.href)
  urlObj.hash = `#r${i}`
  return urlObj.toString()
}

const formatDate = (dateStr: string): string => {
  try {
    const parsed = dayjs(dateStr)
    if (parsed.isValid()) {
      return parsed.format("YYYY-MM-DD HH:mm Z")
    } else {
      return dateStr
    }
  } catch (_) {
    return dateStr
  }
}
