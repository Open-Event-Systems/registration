import { createAccount } from "#src/features/auth/api.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { SignInState } from "#src/features/auth/types/SignInOptions.js"

/**
 * Perform guest sign-in. There's no actual component rendered.
 */
export const createGuestSignIn = async (state: SignInState): Promise<null> => {
  const result = await createAccount(state.wretch)
  const authInfo = AuthInfo.createFromResponse(result)
  state.handleComplete(authInfo)
  return null
}
