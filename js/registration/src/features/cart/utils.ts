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
