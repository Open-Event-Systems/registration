import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { SigninOptionsMenu } from "#src/features/auth/components/SigninOptionsMenu.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import { SignInStore } from "#src/features/auth/stores/SignInStore.js"
import { SignInOptions } from "#src/features/auth/types/SignInOptions.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import {
  DefaultProps,
  Selectors,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ReactNode, useEffect } from "react"
import { Wretch } from "wretch"

declare module "#src/hooks/location.js" {
  interface LocationState {
    signInOption?: keyof SignInOptions
  }
}

const useStyles = createStyles({
  root: {},
  body: {
    padding: "0 0 8px 0",
  },
  content: {},
})

export type SigninDialogProps = Omit<
  ModalDialogProps,
  "styles" | "fullScreen" | "onClose" | "onSelect"
> &
  DefaultProps<Selectors<typeof useStyles>>

/**
 * Sign in dialog component.
 */
export const SigninDialog = (props: SigninDialogProps) => {
  const { className, classNames, styles, unstyled, title, children, ...other } =
    useComponentDefaultProps(
      "SigninDialog",
      {
        title: "Sign In",
      },
      props
    )

  const { classes, cx } = useStyles(undefined, {
    name: "SigninDialog",
    classNames,
    styles,
    unstyled,
  })

  return (
    <ModalDialog
      className={cx(classes.root, className)}
      title={title}
      classNames={{
        content: classes.content,
        body: classes.body,
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

export type SigninDialogManagerProps = {
  authStore: AuthStore
  wretch: Wretch
  children?: ReactNode
}

SigninDialog.Manager = observer((props: SigninDialogManagerProps) => {
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
            navigate(-1)
          }
        })
      } else {
        state.selectedOptionRender = null
      }
    }),
    [signInOption]
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
      <SigninOptionsMenu
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
      <SigninDialog opened={show} loading={loading && show}>
        {content}
      </SigninDialog>
    </>
  )
})

SigninDialog.Manager.displayName = "SigninDialog.Manager"
