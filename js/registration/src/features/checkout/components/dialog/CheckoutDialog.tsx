import { Skeleton, useProps } from "@mantine/core"
import { ReactNode } from "react"

import clsx from "clsx"
import { ModalDialog, ModalDialogProps } from "#src/components"

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

CheckoutDialog.Placeholder = () => (
  <>
    <Skeleton h="2.25rem" />
    <Skeleton h="2.25rem" />
  </>
)
