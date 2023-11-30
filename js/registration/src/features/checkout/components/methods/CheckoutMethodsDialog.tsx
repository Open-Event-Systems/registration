import { CheckoutMethod } from "#src/features/checkout/types/Checkout"
import {
  Button,
  LoadingOverlay,
  LoadingOverlayProps,
  useProps,
} from "@mantine/core"
import { useEffect } from "react"

import "./CheckoutMethods.module.css"
import clsx from "clsx"
import { ModalDialog, ModalDialogProps } from "#src/components"

export type CheckoutMethodsDialogProps = {
  methods?: CheckoutMethod[]
  loading?: boolean
  onSelect?: (service: string, method?: string) => void
  LoadingOverlayProps?: Partial<LoadingOverlayProps>
} & Omit<ModalDialogProps, "children" | "onSelect">

export const CheckoutMethodsDialog = (props: CheckoutMethodsDialogProps) => {
  const {
    className,
    classNames,
    methods,
    loading,
    onSelect,
    opened,
    LoadingOverlayProps,
    ...other
  } = useProps(
    "CheckoutMethodsDialog",
    {
      LoadingOverlayProps: {
        zIndex: 1000,
      },
    },
    props,
  )

  const showOptions = !loading && !!methods && methods.length != 1

  useEffect(() => {
    if (opened && !loading && !!methods && methods.length == 1) {
      // select the first option automatically if it is the only option
      onSelect && onSelect(methods[0].service, methods[0].method)
    }
  }, [opened, loading, methods])

  return (
    <ModalDialog
      title="Payment Method"
      centered
      className={clsx("CheckoutMethodsDialog-root", className)}
      classNames={{
        ...classNames,
        body: clsx("CheckoutMethodsDialog-body", classNames?.body),
      }}
      opened={opened && !!methods && methods.length > 1}
      {...other}
    >
      <Button.Group orientation="vertical">
        {showOptions &&
          methods.map((m) => (
            <Button
              key={`${m.service}-${m.method}`}
              size="md"
              variant="subtle"
              onClick={() => {
                onSelect && onSelect(m.service, m.method)
              }}
            >
              {m.name || "Checkout"}
            </Button>
          ))}
      </Button.Group>
      <LoadingOverlay {...LoadingOverlayProps} visible={!showOptions} />
    </ModalDialog>
  )
}
