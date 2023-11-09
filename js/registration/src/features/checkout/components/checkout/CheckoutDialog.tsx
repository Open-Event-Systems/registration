import { Modal, ModalProps, Stack, useProps } from "@mantine/core"
import { ReactNode } from "react"

import "./Checkout.module.css"
import clsx from "clsx"

export type CheckoutDialogProps = {
  children?: ReactNode
} & Omit<ModalProps, "children">

export const CheckoutDialog = (props: CheckoutDialogProps) => {
  const { className, classNames, children, ...other } = useProps(
    "CheckoutDialog",
    {},
    props,
  )

  return (
    <Modal
      title="Checkout"
      centered
      className={clsx("CheckoutDialog-root", className)}
      classNames={{
        ...classNames,
        body: clsx("CheckoutDialog-body", classNames?.body),
      }}
      {...other}
    >
      <Stack>{children}</Stack>
    </Modal>
  )
}
