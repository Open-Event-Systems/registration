import { SignInOptionsOption } from "#src/features/auth/components/options/SignInOptionsMenu"
import {
  SignInStep,
  useAuthAPI,
  useSignInState,
} from "#src/features/auth/hooks"
import { getPlatformWebAuthnDetails } from "#src/features/auth/webauthn"
import { Box } from "@mantine/core"
import { startRegistration } from "@simplewebauthn/browser"
import { IconUserOff } from "@tabler/icons-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

export type WebAuthnOptionsMenuProps = {
  onAccept?: () => void
  onCancel?: () => void
}

export const WebAuthnOptionsMenu = (props: WebAuthnOptionsMenuProps) => {
  const { onAccept, onCancel } = props
  const details = getPlatformWebAuthnDetails(window.navigator.userAgent)
  const Icon = details.icon
  return (
    <Box>
      <SignInOptionsOption
        leftSection={<Icon />}
        label={details.registerName}
        description={details.registerDescription}
        onClick={onAccept}
      />
      <SignInOptionsOption
        leftSection={<IconUserOff />}
        label="Don't stay signed in"
        onClick={onCancel}
      />
    </Box>
  )
}

const WebAuthnOptionsMenuManager = () => {
  const api = useAuthAPI()
  const client = useQueryClient()
  const state = useSignInState()

  const webAuthnRegQuery = useQuery({
    ...api.readWebAuthnRegistrationChallenge(
      state.tokenResponse?.access_token ?? "",
    ),
    enabled:
      !!state.tokenResponse?.access_token && state.step == SignInStep.webAuthn,
    initialData: { challenge: "", options: {} },
    initialDataUpdatedAt: 0,
  })

  const completeWebAuthnRegistration = useMutation(
    api.completeWebAuthnRegistration(
      state.tokenResponse?.access_token ?? "",
      webAuthnRegQuery.data,
    ),
  )

  return (
    <WebAuthnOptionsMenu
      onAccept={() => {
        if (!webAuthnRegQuery.data) {
          return
        }

        startRegistration(webAuthnRegQuery.data.options)
          .then((regResult: { id: string }) => {
            if (!regResult) {
              client.invalidateQueries({
                queryKey: api.readWebAuthnRegistrationChallenge(
                  state.tokenResponse?.access_token ?? "",
                ).queryKey,
              })
              console.error("WebAuthn registration failed")
              return null
            }
            return completeWebAuthnRegistration
              .mutateAsync(JSON.stringify(regResult))
              .then(() => regResult.id)
          })
          .then((credentialId: string | null) => {
            if (credentialId) {
              state.completeWebAuthnRegistration(credentialId)
            }
          })
          .catch((err: Error) => {
            client.invalidateQueries({
              queryKey: api.readWebAuthnRegistrationChallenge(
                state.tokenResponse?.access_token ?? "",
              ).queryKey,
            })
            console.error("WebAuthn registration failed", err)
          })
      }}
      onCancel={() => {
        state.completeWebAuthnRegistration(null)
      }}
    />
  )
}

WebAuthnOptionsMenu.Manager = WebAuthnOptionsMenuManager
