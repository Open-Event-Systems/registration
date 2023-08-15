import {
  DefaultProps,
  LoadingOverlay,
  Modal,
  Selectors,
  createStyles,
  useComponentDefaultProps,
  useMantineTheme,
} from "@mantine/core"
import { ModalRootProps } from "@mantine/core/lib/Modal/ModalRoot/ModalRoot.js"
import { useMediaQuery } from "@mantine/hooks"
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
  Omit<ModalRootProps, "title" | "opened" | "onClose" | "styles"> &
  DefaultProps<Selectors<typeof useStyles>, ModalDialogParams>

const useStyles = createStyles((_theme, params: ModalDialogParams) => ({
  root: {},
  inner: {},
  content: {},
  header: {
    zIndex: "initial",
  },
  overlay: {},
  title: {
    fontWeight: "bold",
  },
  body: {
    padding: params.noPadding ? 0 : undefined,
  },
  close: {},
  loading: {},
}))

export const ModalDialog = (props: ModalDialogProps) => {
  const theme = useMantineTheme()

  const {
    className,
    classNames,
    styles,
    unstyled,
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
  } = useComponentDefaultProps("ModalDialog", {}, props)

  const { classes, cx } = useStyles(
    { noPadding },
    { name: "ModalDialog", classNames, styles, unstyled }
  )

  const fullScreen = propFullScreen ?? useMediaQuery(fullScreenMediaQuery)

  return (
    <Modal.Root
      className={cx(classes.root, className)}
      opened={opened}
      onClose={onClose}
      fullScreen={fullScreen}
      centered
      {...other}
    >
      <Modal.Overlay className={classes.overlay} />
      <Modal.Content className={classes.content}>
        <Modal.Header className={classes.header}>
          <Modal.Title className={classes.title}>{title}</Modal.Title>
          {!hideCloseButton && <Modal.CloseButton className={classes.close} />}
        </Modal.Header>
        <Modal.Body className={classes.body}>{children}</Modal.Body>
        <LoadingOverlay className={classes.loading} visible={!!loading} />
      </Modal.Content>
    </Modal.Root>
  )
}
