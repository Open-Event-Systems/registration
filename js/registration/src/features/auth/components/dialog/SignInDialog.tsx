import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog"
import { SignInOptionsMenu } from "#src/features/auth/components/options/SignInOptionsMenu"
import { WebAuthnOptionsMenu } from "#src/features/auth/components/options/WebAuthnOptionsMenu"
import {
  SignInStateContext,
  SignInStep,
  createSignIn,
  useAuthAPI,
} from "#src/features/auth/hooks"
import { signInComponents, signInOptions } from "#src/features/auth/options"
import { AuthStore } from "#src/features/auth/stores/AuthStore"
import { SignInStore } from "#src/features/auth/stores/SignInStore"
import { SignInOptions } from "#src/features/auth/types/SignInOptions"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Box, Skeleton, Stack, useProps } from "@mantine/core"
import { useIsMutating, useMutation, useQuery } from "@tanstack/react-query"
import clsx from "clsx"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ComponentType, ReactNode, useEffect, useState } from "react"
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
  const { authStore, wretch, children } = props
  const navigate = useNavigate()
  const loc = useLocation()

  const state = useLocalObservable(() => new SignInStore(wretch, authStore))

  const signInOptionID = loc.state?.signInOption
  const signInOption = signInOptionID
    ? state.options.find((opt) => opt.id == signInOptionID)
    : undefined

  // show when auth setup finishes and there is no auth info
  const noAuth = authStore.ready && !authStore.authInfo
  const show = noAuth && state.ready
  const loading =
    state.loading || (!!signInOption && !state.selectedOptionRender)

  // load
  useEffect(() => {
    if (noAuth) {
      state.load()

      return action(() => {
        state.ready = false
      })
    }
  }, [noAuth])

  // load the selected option
  useEffect(
    action(() => {
      if (signInOption) {
        state.selectOption(signInOption).then((res) => {
          if (res == null) {
            // navigate back on error
            return state.load().then(() => navigate(-1))
          }
        })
      } else {
        state.selectedOptionRender = null
      }
    }),
    [signInOptionID],
  )

  // navigate back on complete
  useEffect(() => {
    if (!show && signInOptionID) {
      navigate(-1)
    }
  }, [show])

  let content

  if (state.selectedOptionRender) {
    content = state.selectedOptionRender({
      loading: state.loading,
      onComplete: (authInfo) => state.handleComplete(authInfo),
      setLoading: (loading) => state.setLoading(loading),
    })
  } else {
    content = (
      <SignInOptionsMenu
        options={state.options}
        onSelect={(id) => {
          navigate(loc, { state: { ...loc.state, signInOption: id } })
        }}
      />
    )
  }

  return (
    <>
      {children}
      <SignInDialog opened={show} loading={loading && show}>
        {content}
      </SignInDialog>
    </>
  )
})

SignInDialog.Manager.displayName = "SigninDialog.Manager"

SignInDialog.Manager2 = observer((props: SignInDialogManagerProps) => {
  const { authStore, children } = props
  const navigate = useNavigate()
  const loc = useLocation()

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

SignInDialog.Manager2.displayName = "SigninDialog.Manager2"

SignInDialog.Placeholder = () => (
  <Stack>
    <Skeleton h="2.25rem" />
    <Skeleton h="2.25rem" />
  </Stack>
)
