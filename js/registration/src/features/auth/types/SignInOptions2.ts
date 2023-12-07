import { useAuthAPI } from "#src/features/auth/hooks"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"
import { JS_CLIENT_ID } from "#src/features/auth/stores/AuthStore"
import { useMutation } from "@tanstack/react-query"
import { ComponentType, ReactNode } from "react"

export interface SignInState {}

export interface SignInOption {
  readonly id: string
  readonly name: string
  readonly description?: string
  readonly icon?: ComponentType
  readonly highlight?: boolean

  optionRenderFunc(
    Option: (props: { onSelect: () => void }) => ReactNode,
  ): ReactNode
}

export type SignInOptionFactory = () => Promise<SignInOption>
