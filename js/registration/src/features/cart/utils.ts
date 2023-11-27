import { fetchCart, fetchEmptyCart } from "#src/features/cart/api"
import { Wretch } from "wretch"
import { handleNotFound } from "#src/util/api"
import { Cart } from "#src/features/cart/types"

const COOKIE_NAME = "oes-current-cart-"

/**
 * Saves the user's current cart ID.
 *
 * This is stored as a session cookie so it will automatically be removed at the end of
 * the browsing session. localStorage would keep the data around in between sessions,
 * but sessionStorage is per-tab.
 */
export const setCurrentCartId = (eventId: string, id: string) => {
  const name = `${COOKIE_NAME}${eventId}`
  const cookieStr = `${encodeURIComponent(name)}=${encodeURIComponent(
    id,
  )}; path=/; SameSite=Strict`
  document.cookie = cookieStr
}

/**
 * Get the current cart ID, or undefined.
 */
export const getCurrentCartId = (eventId: string): string | undefined => {
  const name = `${COOKIE_NAME}${eventId}`
  const values = document.cookie
    .split(";")
    .map((e) => e.split("=", 2))
    .map((kvs) => kvs.map((e) => e.trim()))
    .filter(([k, _v]) => k == encodeURIComponent(name))
    .map(([_k, v]) => v)

  return values[0]
}

/**
 * Get the current cart, or the empty cart if the saved current cart ID cannot be found.
 * @returns A pair of the cart ID and the {@link Cart}.
 */
export const fetchCurrentOrEmptyCart = async (
  wretch: Wretch,
  eventId: string,
): Promise<readonly [string, Cart]> => {
  const currentId = getCurrentCartId()

  if (!currentId) {
    return await fetchEmptyCart(wretch, eventId)
  } else {
    const [cartId, cart] = await fetchCartOrEmpty(wretch, currentId, eventId)
    if (cartId != currentId) {
      setCurrentCartId(cartId)
    }

    return [cartId, cart]
  }
}

/**
 * Fetch the given cart ID, or the empty cart if not found.
 */
export const fetchCartOrEmpty = async (
  wretch: Wretch,
  cartId: string,
  eventId: string,
): Promise<readonly [string, Cart]> => {
  const result = await handleNotFound(fetchCart(wretch, cartId))

  if (result) {
    return [cartId, result]
  }

  return await fetchEmptyCart(wretch, eventId)
}
