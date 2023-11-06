import { SignInDialog } from "#src/features/auth/components/dialog/SigninDialog"
import { SignInOptionsMenu } from "#src/features/auth/components/options/SignInOptionsMenu"
import { getPlatformWebAuthnDetails } from "#src/features/auth/components/signin/WebAuthn.js"
import { Meta, StoryObj } from "@storybook/react"
import { IconUserOff } from "@tabler/icons-react"
import { IconAt } from "@tabler/icons-react"
import { useEffect, useState } from "react"

import "../options/SignInOptionsMenu.module.css"
import "../signin/EmailAuth.module.css"
import "./SigninDialog.module.css"

const webAuthnDetails = getPlatformWebAuthnDetails("")
const iOSWebAuthnDetails = getPlatformWebAuthnDetails("iPhone")
const androidWebAuthnDetails = getPlatformWebAuthnDetails("Android")
const windowsWebAuthnDetails = getPlatformWebAuthnDetails("Windows NT")

export default {
  component: SignInDialog,
  args: {
    opened: true,
  },
  parameters: {
    layout: "fullscreen",
  },
} as Meta<typeof SignInDialog>

export const Default: StoryObj<typeof SignInDialog> = {
  render(args) {
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      window.setTimeout(() => setLoading(false), 500)
    }, [])

    const onSelect = () => {
      if (loading) {
        return
      }

      setLoading(true)
      window.setTimeout(() => {
        setLoading(false)
      }, 500)
    }

    return (
      <SignInDialog {...args} loading={loading}>
        <SignInOptionsMenu
          options={[
            {
              id: "email",
              icon: IconAt,
              name: "Sign in with email",
              description: "Use your email address to sign in",
              getRender: async () => () => null,
            },
            {
              id: "platformWebAuthn",
              icon: webAuthnDetails.icon,
              name: webAuthnDetails.name,
              description: webAuthnDetails.description,
              getRender: async () => () => null,
            },
            {
              id: "guest",
              icon: IconUserOff,
              name: "Continue as guest",
              description: "You might not be able to make changes later",
              getRender: async () => () => null,
            },
          ]}
          onSelect={onSelect}
        />
      </SignInDialog>
    )
  },
}

export const iOSWebAuthn: StoryObj<typeof SignInDialog> = {
  ...Default,
  name: "iOS Web Authn",
  render(args) {
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      window.setTimeout(() => setLoading(false), 500)
    }, [])

    const onSelect = () => {
      if (loading) {
        return
      }

      setLoading(true)
      window.setTimeout(() => {
        setLoading(false)
      }, 500)
    }

    return (
      <SignInDialog {...args} loading={loading}>
        <SignInOptionsMenu
          options={[
            {
              id: "email",
              icon: IconAt,
              name: "Sign in with email",
              description: "Use your email address to sign in",
              getRender: async () => () => null,
            },
            {
              id: "platformWebAuthn",
              icon: iOSWebAuthnDetails.icon,
              name: iOSWebAuthnDetails.name,
              description: iOSWebAuthnDetails.description,
              getRender: async () => () => null,
            },
            {
              id: "guest",
              icon: IconUserOff,
              name: "Continue as guest",
              description: "You might not be able to make changes later",
              getRender: async () => () => null,
            },
          ]}
          onSelect={onSelect}
        />
      </SignInDialog>
    )
  },
}

export const AndroidWebAuthn: StoryObj<typeof SignInDialog> = {
  ...Default,
  render(args) {
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      window.setTimeout(() => setLoading(false), 500)
    }, [])

    const onSelect = () => {
      if (loading) {
        return
      }

      setLoading(true)
      window.setTimeout(() => {
        setLoading(false)
      }, 500)
    }

    return (
      <SignInDialog {...args} loading={loading}>
        <SignInOptionsMenu
          options={[
            {
              id: "email",
              icon: IconAt,
              name: "Sign in with email",
              description: "Use your email address to sign in",
              getRender: async () => () => null,
            },
            {
              id: "platformWebAuthn",
              icon: androidWebAuthnDetails.icon,
              name: androidWebAuthnDetails.name,
              description: androidWebAuthnDetails.description,
              getRender: async () => () => null,
            },
            {
              id: "guest",
              icon: IconUserOff,
              name: "Continue as guest",
              description: "You might not be able to make changes later",
              getRender: async () => () => null,
            },
          ]}
          onSelect={onSelect}
        />
      </SignInDialog>
    )
  },
}

export const WindowsWebAuthn: StoryObj<typeof SignInDialog> = {
  ...Default,
  render(args) {
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      window.setTimeout(() => setLoading(false), 500)
    }, [])

    const onSelect = () => {
      if (loading) {
        return
      }

      setLoading(true)
      window.setTimeout(() => {
        setLoading(false)
      }, 500)
    }

    return (
      <SignInDialog {...args} loading={loading}>
        <SignInOptionsMenu
          options={[
            {
              id: "email",
              icon: IconAt,
              name: "Sign in with email",
              description: "Use your email address to sign in",
              getRender: async () => () => null,
            },
            {
              id: "platformWebAuthn",
              icon: windowsWebAuthnDetails.icon,
              name: windowsWebAuthnDetails.name,
              description: windowsWebAuthnDetails.description,
              getRender: async () => () => null,
            },
            {
              id: "guest",
              icon: IconUserOff,
              name: "Continue as guest",
              description: "You might not be able to make changes later",
              getRender: async () => () => null,
            },
          ]}
          onSelect={onSelect}
        />
      </SignInDialog>
    )
  },
}
