import config from "#src/config/config"
import { PricingResult } from "#src/features/cart/types"
import { fetchReceipt } from "#src/features/receipt/api"
import { Receipt } from "#src/features/receipt/components/Receipt"
import { useEffect, useState } from "react"

export const ReceiptPage = () => {
  const pathParts = window.location.pathname.split("/")
  const receiptId = pathParts[pathParts.length - 1]

  const [receipt, setReceipt] = useState<PricingResult | null | false>(null)

  useEffect(() => {
    if (receiptId) {
      fetchReceipt(config, receiptId).then((res) => {
        setReceipt(res ?? false)
      })
    }
  }, [receiptId])

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
    return <Receipt receiptId={receiptId} pricingResult={receipt} />
  }
}
