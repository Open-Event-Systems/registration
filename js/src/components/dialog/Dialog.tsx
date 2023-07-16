import {
  DefaultProps,
  LoadingOverlay,
  LoadingOverlayProps,
  Modal,
  Selectors,
  createStyles,
  useComponentDefaultProps,
  useMantineTheme,
} from "@mantine/core"
import { ModalRootProps } from "@mantine/core/lib/Modal/ModalRoot/ModalRoot.js"
import { useMediaQuery } from "@mantine/hooks"
import { ReactNode } from "react"

export type DialogParams = {
  noPadding?: boolean
}

const useStyles = createStyles((_theme, { noPadding }: DialogParams) => ({
  overlay: {},
  content: {},
  header: {},
  body: {
    padding: noPadding ? 0 : undefined,
  },
  title: {
    fontWeight: "bold",
  },
  closeButton: {},
  loadingOverlay: {},
}))

export type DialogProps = {
  title?: ReactNode
  children?: ReactNode
  fullScreen?: boolean
  fullScreenMediaQuery?: string
  hideCloseButton?: boolean
  onClose?: () => void
  loading?: boolean
  LoadingOverlayProps?: LoadingOverlayProps
} & DialogParams &
  Omit<ModalRootProps, "styles" | "children" | "onClose"> &
  DefaultProps<Selectors<typeof useStyles>>

export const Dialog = (props: DialogProps) => {
  const {
    classNames,
    styles,
    unstyled,
    title,
    children,
    fullScreen,
    fullScreenMediaQuery,
    hideCloseButton,
    onClose,
    loading,
    LoadingOverlayProps,
    noPadding,
    ...other
  } = useComponentDefaultProps(
    "OESDialog",
    {
      centered: true,
    },
    props
  )

  const { classes } = useStyles(
    { noPadding },
    {
      name: "OESDialog",
      classNames,
      styles,
      unstyled,
    }
  )

  const theme = useMantineTheme()
  const mediaQuery =
    fullScreenMediaQuery ?? `(max-width: ${theme.breakpoints.sm})`
  const fullScreenQueryResult = useMediaQuery(mediaQuery)

  return (
    <Modal.Root
      fullScreen={fullScreen ?? fullScreenQueryResult}
      onClose={onClose ?? (() => null)}
      {...other}
    >
      <Modal.Overlay className={classes.overlay} />
      <Modal.Content className={classes.content}>
        <Modal.Header className={classes.header}>
          <Modal.Title className={classes.title}>{title}</Modal.Title>
          {!hideCloseButton && (
            <Modal.CloseButton className={classes.closeButton} />
          )}
        </Modal.Header>
        <Modal.Body className={classes.body}>
          {children}
          <LoadingOverlay
            className={classes.loadingOverlay}
            visible={!!loading}
            zIndex={1001} // just above the header
            {...LoadingOverlayProps}
          />
        </Modal.Body>
      </Modal.Content>
    </Modal.Root>
  )
}
