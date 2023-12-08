import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog"
import { WebAuthnOptionsMenu } from "#src/features/auth/components/options/WebAuthnOptionsMenu"
import {
  SignInStateContext,
  SignInStep,
  createSignIn,
} from "#src/features/auth/hooks"
import { AuthStore } from "#src/features/auth/stores/AuthStore"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Skeleton, Stack, useProps } from "@mantine/core"
import clsx from "clsx"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"
import { Wretch } from "wretch"

declare module "#src/hooks/location" {
  interface LocationState {
    signInOption?: string
  }
}

export type SignInDialogProps = Omit<
  ModalDialogProps,
  "fullScreen" | "onClose" | "onSelect"
>

/**
 * Sign in dialog component.
 */
export const SignInDialog = (props: SignInDialogProps) => {
  const { className, classNames, title, children, ...other } = useProps(
    "SignInDialog",
    {
      title: "Sign In",
    },
    props,
  )

  return (
    <ModalDialog
      className={clsx("SignInDialog-root", className)}
      title={title}
      classNames={{
        ...classNames,
        content: clsx("SignInDialog-content", classNames?.content),
        body: clsx("SignInDialog-body", classNames?.body),
      }}
      closeOnClickOutside={false}
      hideCloseButton
      onClose={() => null}
      centered
      {...other}
    >
      {children}
    </ModalDialog>
  )
}

export type SignInDialogManagerProps = {
  authStore: AuthStore
  wretch: Wretch
  children?: ReactNode
}

SignInDialog.Manager = observer((props: SignInDialogManagerProps) => {
  const { authStore, children } = props

  // show when auth setup finishes and there is no auth info
  const show = authStore.ready && !authStore.authInfo

  const state = createSignIn()

  let usePadding = false
  let content = <SignInDialog.Placeholder />

  if (state.step == SignInStep.signIn) {
    if (state.signInComponent) {
      const Component = state.signInComponent
      content = <Component />
      usePadding = true
    } else if (state.signInOptions) {
      content = (
        <>
          {state.signInOptions.map(([id, Component]) => (
            <Component key={id} />
          ))}
        </>
      )
    }
  } else if (state.step == SignInStep.webAuthn) {
    content = <WebAuthnOptionsMenu.Manager />
  }

  return (
    <SignInStateContext.Provider value={state}>
      {children}
      <SignInDialog
        opened={show}
        loading={state.updating}
        classNames={{
          body: clsx({ "SignInDialog-padding": usePadding }),
        }}
      >
        {content}
      </SignInDialog>
    </SignInStateContext.Provider>
  )
})

SignInDialog.Manager.displayName = "SigninDialog.Manager"

SignInDialog.Placeholder = () => (
  <Stack>
    <Skeleton h="2.25rem" />
    <Skeleton h="2.25rem" />
  </Stack>
)
