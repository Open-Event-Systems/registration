import { ComponentType } from "react"

export interface WebAuthnChallenge {
  challenge: string
  options: Record<string, unknown>
}

export interface WebAuthnChallengeResult {
  challenge: string
  result: string
  email_token?: string | null
}

export type PlatformWebAuthnDetails = {
  name: string
  description: string
  emailName: string
  emailDescription: string
  emailSkip: string
  icon: ComponentType
}
