import { CheckoutState } from "#src/features/checkout/CheckoutState.js"
import { PaymentServiceID } from "#src/features/checkout/types/Checkout.js"
import { Loader } from "#src/util/loader.js"
import {
  Alert,
  Button,
  LoadingOverlay,
  LoadingOverlayProps,
  Text,
  Title,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { ReactNode, useEffect } from "react"

export const CheckoutComplete = ({ onClose }: { onClose?: () => void }) => {
  return (
    <>
      <Text component="p">Your order is complete.</Text>
      <Button onClick={onClose}>Close</Button>
    </>
  )
}

export const CheckoutError = ({ children }: { children?: ReactNode }) => {
  return (
    <Alert title="Error" color="red">
      {children}
    </Alert>
  )
}

const formatError = (err: unknown) => {
  if (err && typeof err == "object" && err instanceof Error) {
    return err.message
  } else if (err && typeof err == "object" && "detail" in err) {
    return `${err.detail}`
  } else {
    return `${err}`
  }
}

export type CheckoutContainerProps<ID extends PaymentServiceID> = {
  state: Loader<CheckoutState<ID>>
  LoadingOverlayProps?: Partial<LoadingOverlayProps>
  onClose?: () => void
}

/**
 * Displays the checkout component, error message, complete message, and/or loading overlay.
 */
export const CheckoutContainer = observer(
  <ID extends PaymentServiceID>(props: CheckoutContainerProps<ID>) => {
    const { state, LoadingOverlayProps, onClose } = props

    // load state and component on render
    useEffect(() => {
      const statePromise = state.load()
      statePromise.then((res) => {
        return res.component.load()
      })

      // cancel checkout on unmount
      return () => {
        statePromise.then((state) => {
          if (!state.complete) {
            state.cancel().catch(() => null)
          }
        })
      }
    }, [state])

    const showLoading =
      !state.checkLoaded() ||
      state.value.loading ||
      !state.value.component.checkLoaded()

    let content
    if (state.value?.complete) {
      content = <CheckoutComplete onClose={onClose} />
    } else if (
      state.checkLoaded() &&
      !state.value.complete &&
      state.value.component.checkLoaded()
    ) {
      const Component = state.value.component.value
      content = <Component state={state.value} />
    }

    return (
      <>
        {content}
        {state.value?.error != null ? (
          <CheckoutError>{formatError(state.value.error)}</CheckoutError>
        ) : undefined}
        <LoadingOverlay {...LoadingOverlayProps} visible={showLoading} />
      </>
    )
  }
)

CheckoutContainer.displayName = "CheckoutContainer"
