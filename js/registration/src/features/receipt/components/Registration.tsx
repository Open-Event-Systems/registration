import { ReceiptCode } from "#src/features/receipt/components/Code"
import clsx from "clsx"
import { ComponentPropsWithoutRef } from "react"

export type ReceiptRegistrationProps = {
  name?: string
  receiptUrl?: string
} & ComponentPropsWithoutRef<"tbody">

export const ReceiptRegistration = (props: ReceiptRegistrationProps) => {
  const { name, receiptUrl, className, children, ...other } = props

  return (
    <tbody className={clsx("ReceiptRegistration-root", className)} {...other}>
      <tr className="ReceiptRegistration-row">
        <td className="ReceiptRegistration-name" colSpan={3}>
          {name || "Registration"}
        </td>
      </tr>
      {receiptUrl && (
        <tr className="ReceiptRegistration-row">
          <td className="ReceiptRegistration-code" colSpan={3}>
            <ReceiptCode receiptUrl={receiptUrl} />
          </td>
        </tr>
      )}
      {children}
    </tbody>
  )
}
