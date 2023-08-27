import { SigninDialog } from "#src/features/auth/components/SigninDialog.js"
import {
  getPlatformWebAuthnDetails,
  signInOptions,
} from "#src/features/auth/signInOptions.js"
import { SignInOptions } from "#src/features/auth/types/SignInOptions.js"
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
  args: {
    options: [
      signInOptions.email,
      {
        id: "platformWebAuthn",
        icon: webAuthnDetails.icon,
        name: webAuthnDetails.name,
        description: webAuthnDetails.description,
      },
      signInOptions.guest,
    ],
  },
  render(args) {
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      window.setTimeout(() => setLoading(false), 500)
    }, [])

    const onSelect = (id: keyof SignInOptions) => {
      if (loading) {
        return
      }

      setLoading(true)
      window.setTimeout(() => {
        setLoading(false)
        args.onSelect && args.onSelect(id)
      }, 500)
    }

    return <SigninDialog {...args} loading={loading} onSelect={onSelect} />
  },
}

export const iOSWebAuthn: StoryObj<typeof SigninDialog> = {
  ...Default,
  name: "iOS Web Authn",
  args: {
    ...Default.args,
    options: [
      signInOptions.email,
      {
        id: "platformWebAuthn",
        icon: iOSWebAuthnDetails.icon,
        name: iOSWebAuthnDetails.name,
        description: iOSWebAuthnDetails.description,
      },
      signInOptions.guest,
    ],
  },
}

export const AndroidWebAuthn: StoryObj<typeof SigninDialog> = {
  ...Default,
  args: {
    ...Default.args,
    options: [
      signInOptions.email,
      {
        id: "platformWebAuthn",
        icon: androidWebAuthnDetails.icon,
        name: androidWebAuthnDetails.name,
        description: androidWebAuthnDetails.description,
      },
      signInOptions.guest,
    ],
  },
}

export const WindowsWebAuthn: StoryObj<typeof SigninDialog> = {
  ...Default,
  args: {
    ...Default.args,
    options: [
      signInOptions.email,
      {
        id: "platformWebAuthn",
        icon: windowsWebAuthnDetails.icon,
        name: windowsWebAuthnDetails.name,
        description: windowsWebAuthnDetails.description,
      },
      signInOptions.guest,
    ],
  },
}
