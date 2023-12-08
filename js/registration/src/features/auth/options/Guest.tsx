import { useSignInState } from "#src/features/auth/hooks"
import { IconUserOff } from "@tabler/icons-react"
import { SignInOptionsOption } from "#src/features/auth/components/options/SignInOptionsMenu"

export const GuestSignInOption = () => {
  const state = useSignInState()

  return (
    <SignInOptionsOption
      label="Continue as guest"
      description="You might not be able to make changes later"
      leftSection={<IconUserOff />}
      onClick={async () => {
        const token = await state.getAccount()
        state.completeRegistration(token)
      }}
    />
  )
}
