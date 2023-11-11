import { fetchConfig } from "#src/config/config"
import { PricingResult } from "#src/features/cart/types"
import { fetchReceipt } from "#src/features/receipt/api"
import { Receipt } from "#src/features/receipt/components/Receipt"
import { Config } from "#src/types/config"
import { Fragment, useEffect, useState } from "react"

export const ReceiptPage = () => {
  const pathParts = window.location.pathname.split("/")
  const receiptId = pathParts[pathParts.length - 1]

  const [config, setConfig] = useState<Config | null>(null)
  const [receipt, setReceipt] = useState<PricingResult | null | false>(null)

  useEffect(() => {
    if (receiptId) {
      fetchConfig().then((config) => {
        setConfig(config)
      })
    }
  }, [])

  useEffect(() => {
    if (config && receiptId) {
      fetchReceipt(config, receiptId).then((res) => {
        setReceipt(res ?? false)
      })
    }
  }, [config, receiptId])

  if (!receiptId || receipt === false) {
    return (
      <>
        <h1>Not Found</h1>
        <p>The receipt was not found.</p>
      </>
    )
  } else if (receipt == null) {
    return (
      <>
        <h1>Loading</h1>
        <p>Retrieving receipt...</p>
      </>
    )
  } else {
    return (
      <Receipt
        receiptId={receiptId}
        totalPrice={receipt.total_price}
        date={receipt.date}
      >
        {receipt.registrations.map((reg, i) => (
          <Fragment key={reg.registration_id}>
            <Receipt.Registration
              id={`r${i + 1}`}
              name={reg.name ?? undefined}
              receiptUrl={
                receipt.receipt_url
                  ? getReceiptUrl(receipt.receipt_url, i + 1)
                  : void 0
              }
            >
              {reg.line_items.map((li, i) => (
                <Receipt.LineItem
                  key={i}
                  name={li.name}
                  price={li.price}
                  description={li.description}
                >
                  {li.modifiers.map((m, i) => (
                    <Receipt.Modifier key={i} name={m.name} amount={m.amount} />
                  ))}
                </Receipt.LineItem>
              ))}
            </Receipt.Registration>
            <Receipt.Divider />
          </Fragment>
        ))}
      </Receipt>
    )
  }
}

const getReceiptUrl = (url: string, i: number) => {
  const urlObj = new URL(url, window.location.href)
  urlObj.hash = `#r${i}`
  return urlObj.toString()
}
