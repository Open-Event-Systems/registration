import { PricingResult } from "#src/features/cart/types"
import { Config } from "#src/types/config"

/**
 * Fetch a receipt from the server.
 * @param config - The config object.
 * @param receiptId - The receipt ID.
 * @returns A pricing result, or null if not found.
 */
export const fetchReceipt = async (
  config: Config,
  receiptId: string,
): Promise<PricingResult | null> => {
  const url = `${config.apiUrl}/receipts/${receiptId}`
  const res = await fetch(url)
  if (res.ok) {
    return await res.json()
  } else {
    return null
  }
}
