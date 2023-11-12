import { Currency } from "#src/features/cart/components/cart/Currency"
import clsx from "clsx"
import { ComponentPropsWithoutRef } from "react"

export type ReceiptLineItemProps = {
  name: string
  description?: string
  price: number
} & ComponentPropsWithoutRef<"tr">

export const ReceiptLineItem = (props: ReceiptLineItemProps) => {
  const { name, description, price, className, children, ...other } = props

  return [
    <tr
      key="name"
      className={clsx("ReceiptLineItem-nameRow", className)}
      {...other}
    >
      <td colSpan={2} className="ReceiptLineItem-name">
        {name}
      </td>
      <td className="ReceiptLineItem-amount">
        <Currency amount={price} />
      </td>
    </tr>,
    description ? (
      <tr
        key="description"
        className={clsx("ReceiptLineItem-descriptionRow", className)}
      >
        <td colSpan={2} className="ReceiptLineItem-description">
          {description}
        </td>
        <td className="ReceiptLineItem-spacer"></td>
      </tr>
    ) : null,
    children,
  ]
}
