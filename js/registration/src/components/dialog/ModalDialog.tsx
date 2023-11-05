import {
  LoadingOverlay,
  Modal,
  ModalRootProps,
  useMantineTheme,
  useProps,
} from "@mantine/core"
import { useMediaQuery } from "@mantine/hooks"
import clsx from "clsx"
import { ReactNode } from "react"

export type ModalDialogParams = {
  noPadding?: boolean
}

export type ModalDialogProps = {
  opened?: boolean
  onClose?: () => void
  title?: ReactNode
  loading?: boolean
  hideCloseButton?: boolean
  noPadding?: boolean
  fullScreen?: boolean
  fullScreenMediaQuery?: string
} & ModalDialogParams &
  Omit<ModalRootProps, "title" | "opened" | "onClose">

export const ModalDialog = (props: ModalDialogProps) => {
  const theme = useMantineTheme()

  const {
    className,
    opened = false,
    onClose = () => void 0,
    title,
    loading,
    hideCloseButton,
    noPadding,
    fullScreen: propFullScreen,
    fullScreenMediaQuery = `(max-width: ${theme.breakpoints.sm})`,
    children,
    ...other
  } = useProps("ModalDialog", {}, props)

  const queryResult = useMediaQuery(fullScreenMediaQuery)
  const fullScreen = propFullScreen ?? queryResult

  const show = fullScreen !== undefined && opened

  return (
    <Modal.Root
      className={clsx(className, "ModalDialog-root")}
      opened={show}
      onClose={onClose}
      fullScreen={fullScreen}
      centered
      {...other}
    >
      <Modal.Overlay className="ModalDialog-overlay" />
      <Modal.Content
        classNames={{
          inner: "ModalDialog-inner",
          content: clsx("ModalDialog-content", {
            "ModalDialog-fullscreenContent": fullScreen,
          }),
        }}
      >
        <Modal.Header className="ModalDialog-header">
          <Modal.Title className="ModalDialog-title">{title}</Modal.Title>
          {!hideCloseButton && (
            <Modal.CloseButton className="ModalDialog-close" />
          )}
        </Modal.Header>
        <Modal.Body
          className={clsx("ModalDialog-body", {
            "ModalDialog-bodyNoPadding": noPadding,
          })}
        >
          {children}
        </Modal.Body>
        <LoadingOverlay
          className="ModalDialog-loadingOverlay"
          visible={!!loading}
        />
      </Modal.Content>
    </Modal.Root>
  )
}
