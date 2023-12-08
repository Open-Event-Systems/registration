import { SignInOptionsOption } from "#src/features/auth/components/options/SignInOptionsMenu"
import { useAuthAPI, useSignInState } from "#src/features/auth/hooks"
import {
  getPlatformWebAuthnDetails,
  getSavedWebAuthnCredentialId,
} from "#src/features/auth/webauthn"
import { startAuthentication } from "@simplewebauthn/browser"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { TokenEndpointResponse } from "oauth4webapi"
import { useState } from "react"

export const WebAuthnSignInOption = () => {
  const details = getPlatformWebAuthnDetails(window.navigator.userAgent)
  const Icon = details.icon

  const api = useAuthAPI()
  const state = useSignInState()
  const credentialId = getSavedWebAuthnCredentialId() ?? ""

  const [error, setError] = useState<string | null>(null)
  const client = useQueryClient()
  const webAuthnChallenge = useQuery({
    ...api.readWebAuthnAuthenticationChallenge(credentialId),
    initialData: { challenge: "", options: {} },
    initialDataUpdatedAt: 0,
    enabled: !!credentialId,
  })
  const completeAuthn = useMutation(
    api.completeWebAuthnAuthentication(webAuthnChallenge.data),
  )

  const hasError = !!error || completeAuthn.isError
  const errorMessage = error || completeAuthn.error?.message

  return (
    <SignInOptionsOption
      leftSection={<Icon />}
      label={details.name}
      active
      color={hasError ? "red" : undefined}
      description={hasError ? errorMessage : details.description}
      onClick={() => {
        completeAuthn.reset()
        setError(null)
        if (!webAuthnChallenge.isSuccess) {
          return
        }

        startAuthentication(webAuthnChallenge.data.options)
          .then((res: unknown) => {
            if (!res) {
              console.error("WebAuthn authentication failed")
              setError("Sign in failed")
              client.invalidateQueries({
                queryKey:
                  api.readWebAuthnAuthenticationChallenge(credentialId)
                    .queryKey,
              })
              return null
            }
            return completeAuthn.mutateAsync(JSON.stringify(res))
          })
          .then((token: TokenEndpointResponse) => {
            state.completeSignIn(token)
          })
          .catch((err: Error) => {
            console.error("WebAuthn authentication failed", err)
            client.invalidateQueries({
              queryKey:
                api.readWebAuthnAuthenticationChallenge(credentialId).queryKey,
            })
            setError("Sign in failed")
          })
      }}
    />
  )
}
