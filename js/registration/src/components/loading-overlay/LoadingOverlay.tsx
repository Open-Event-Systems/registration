import {
  Center,
  Loader,
  Overlay,
  OverlayProps,
  useMantineTheme,
  useProps,
} from "@mantine/core"
import clsx from "clsx"
import { makeAutoObservable } from "mobx"
import { observer } from "mobx-react-lite"
import { createContext, useContext, useLayoutEffect } from "react"

const loadingContext = makeAutoObservable({
  value: 0,
  increment() {
    this.value += 1
  },
  decrement() {
    this.value -= 1
  },
})

export const LoadingContext = createContext(loadingContext)

export type LoadingOverlayProps = OverlayProps

/**
 * Overlay that covers the screen while loading.
 */
export const LoadingOverlay = observer((props: LoadingOverlayProps) => {
  const { className, ...other } = useProps("LoadingOverlay", {}, props)

  const theme = useMantineTheme()

  const context = useContext(LoadingContext)

  const opened = context.value > 0

  // TODO: transition

  if (!opened) {
    return null
  }

  return (
    <Overlay
      className={clsx("LoadingOverlay-root", className)}
      fixed
      backgroundOpacity={1}
      color={theme.white}
      {...other}
    >
      <Center className="LoadingOverlay-center">
        <Loader type="dots" />
      </Center>
    </Overlay>
  )
})

LoadingOverlay.displayName = "LoadingOverlay"

/**
 * Component that shows the loading overlay when rendered.
 */
export const ShowLoadingOverlay = () => {
  const context = useContext(LoadingContext)

  useLayoutEffect(() => {
    context.increment()
    return () => context.decrement()
  }, [])

  return null
}
