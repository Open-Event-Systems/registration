import { LoadingOverlay, Skeleton, Text, useProps } from "@mantine/core"
import { ReactNode, useEffect, useRef } from "react"

import "./Checkout.module.css"
import clsx from "clsx"
import { ModalDialog, ModalDialogProps } from "#src/components"
import { CheckoutComponent } from "#src/features/checkout/components/checkout/CheckoutComponent"
import { Checkout, CheckoutState } from "#src/features/checkout/types/Checkout"
import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useLocation, useNavigate } from "#src/hooks/location"

export type CheckoutDialogProps = {
  children?: ReactNode
} & Omit<ModalDialogProps, "children">

export const CheckoutDialog = (props: CheckoutDialogProps) => {
  const { className, classNames, children, ...other } = useProps(
    "CheckoutDialog",
    {},
    props,
  )

  return (
    <ModalDialog
      title="Checkout"
      centered
      className={clsx("CheckoutDialog-root", className)}
      classNames={{
        ...classNames,
        body: clsx("CheckoutDialog-body", classNames?.body),
      }}
      {...other}
    >
      {children}
    </ModalDialog>
  )
}

CheckoutDialog.Complete = () => (
  <Text component="p">Your order is complete.</Text>
)

CheckoutDialog.Canceled = () => (
  <Text component="p">This checkout has been canceled.</Text>
)

CheckoutDialog.Error = ({ children }: { children?: string }) => (
  <Text c="red">{children}</Text>
)

CheckoutDialog.Placeholder = () => (
  <>
    <Skeleton h="2.25rem" />
    <Skeleton h="2.25rem" />
  </>
)

CheckoutDialog.Manager = (
  props: Omit<CheckoutDialogProps, "children" | "opened" | "onClose">,
) => {
  const loc = useLocation()
  const navigate = useNavigate()

  const locState = loc.state?.showCheckoutDialog

  const checkoutId = locState?.checkoutId

  const checkoutAPI = useCheckoutAPI()
  const query = useQuery({
    ...checkoutAPI.read(checkoutId ?? ""),
    enabled: !!checkoutId,
    throwOnError: false,
  })

  const prevContent = useRef<ReactNode>()
  const prevCheckout = useRef<Checkout | null>(null)

  const cancel = useMutation(
    checkoutAPI.cancel(checkoutId ?? prevCheckout.current?.id ?? ""),
  )

  const show = !!locState?.checkoutId

  useEffect(() => {
    if (!show && prevCheckout.current?.state == CheckoutState.pending) {
      cancel.mutate()
    }
  }, [show])

  let content

  if (checkoutId && query.isSuccess) {
    content = (
      <CheckoutComponent key={checkoutId} checkoutId={checkoutId}>
        {(renderProps) => {
          const { Component, ...other } = renderProps

          let content
          if (renderProps.checkout?.state == CheckoutState.complete) {
            content = <CheckoutDialog.Complete />
          } else if (renderProps.checkout?.state == CheckoutState.canceled) {
            content = <CheckoutDialog.Canceled />
          } else if (Component) {
            content = <Component {...other} />
          } else {
            content = <CheckoutDialog.Placeholder />
          }

          return (
            <>
              {content}
              {renderProps.error && (
                <CheckoutDialog.Error>{renderProps.error}</CheckoutDialog.Error>
              )}
              <LoadingOverlay visible={renderProps.isSubmitting} />
            </>
          )
        }}
      </CheckoutComponent>
    )
  } else {
    content = <CheckoutDialog.Placeholder />
  }

  if (show) {
    prevContent.current = content
    prevCheckout.current = query.data ?? null
  }

  return (
    <CheckoutDialog
      {...props}
      opened={show}
      onClose={() => {
        if (checkoutId && query.data?.state == CheckoutState.pending) {
          cancel.mutate()
        }
        navigate(-1)
      }}
    >
      {show ? content : prevContent.current}
    </CheckoutDialog>
  )
}
