import { ComponentType } from "react"

export const signInOptions: Record<
  string,
  () => Promise<ComponentType | null>
> = {
  guest: async () => {
    const { GuestSignInOption } = await import(
      "#src/features/auth/options/Guest"
    )
    return GuestSignInOption
  },
  email: async () => {
    const { EmailSignInOption } = await import(
      "#src/features/auth/options/Email"
    )
    return EmailSignInOption
  },
}

export const signInComponents: Record<
  string,
  (() => Promise<ComponentType | null>) | undefined
> = {
  email: async () => {
    const { EmailSignIn } = await import("#src/features/auth/options/Email")
    return EmailSignIn
  },
}
