import { SigninDialog } from "#src/features/auth/components/SigninDialog.js"
import { SigninOptionsMenu } from "#src/features/auth/components/SigninOptionsMenu.js"
import {
  getPlatformWebAuthnDetails,
  signInOptions,
} from "#src/features/auth/signInOptions.js"
import { Meta, StoryObj } from "@storybook/react"
import { useEffect, useState } from "react"

const webAuthnDetails = getPlatformWebAuthnDetails("")
const iOSWebAuthnDetails = getPlatformWebAuthnDetails("iPhone")
const androidWebAuthnDetails = getPlatformWebAuthnDetails("Android")
const windowsWebAuthnDetails = getPlatformWebAuthnDetails("Windows NT")

export default {
  component: SigninDialog,
  args: {
    opened: true,
  },
  parameters: {
    layout: "fullscreen",
  },
} as Meta<typeof SigninDialog>

export const Default: StoryObj<typeof SigninDialog> = {
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
      <SigninDialog {...args} loading={loading}>
        <SigninOptionsMenu
          options={[
            signInOptions.email,
            {
              id: "platformWebAuthn",
              icon: webAuthnDetails.icon,
              name: webAuthnDetails.name,
              description: webAuthnDetails.description,
              factory: () => Promise.resolve(null),
            },
            signInOptions.guest,
          ]}
          onSelect={onSelect}
        />
      </SigninDialog>
    )
  },
}

export const iOSWebAuthn: StoryObj<typeof SigninDialog> = {
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
      <SigninDialog {...args} loading={loading}>
        <SigninOptionsMenu
          options={[
            signInOptions.email,
            {
              id: "platformWebAuthn",
              icon: iOSWebAuthnDetails.icon,
              name: iOSWebAuthnDetails.name,
              description: iOSWebAuthnDetails.description,
              factory: () => Promise.resolve(null),
            },
            signInOptions.guest,
          ]}
          onSelect={onSelect}
        />
      </SigninDialog>
    )
  },
}

export const AndroidWebAuthn: StoryObj<typeof SigninDialog> = {
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
      <SigninDialog {...args} loading={loading}>
        <SigninOptionsMenu
          options={[
            signInOptions.email,
            {
              id: "platformWebAuthn",
              icon: androidWebAuthnDetails.icon,
              name: androidWebAuthnDetails.name,
              description: androidWebAuthnDetails.description,
              factory: () => Promise.resolve(null),
            },
            signInOptions.guest,
          ]}
          onSelect={onSelect}
        />
      </SigninDialog>
    )
  },
}

export const WindowsWebAuthn: StoryObj<typeof SigninDialog> = {
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
      <SigninDialog {...args} loading={loading}>
        <SigninOptionsMenu
          options={[
            signInOptions.email,
            {
              id: "platformWebAuthn",
              icon: windowsWebAuthnDetails.icon,
              name: windowsWebAuthnDetails.name,
              description: windowsWebAuthnDetails.description,
              factory: () => Promise.resolve(null),
            },
            signInOptions.guest,
          ]}
          onSelect={onSelect}
        />
      </SigninDialog>
    )
  },
}
