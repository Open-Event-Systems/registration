import { LoadValue, LoadingState, createLoader } from "#src/features/loader"
import { observer } from "mobx-react-lite"
import { ReactNode, useLayoutEffect, useMemo } from "react"

export type LoaderComponentProps<T> = {
  value: LoadValue<T>
  fallback?: ReactNode
  children?: ReactNode | ((value: T) => ReactNode)
}

export const Await = observer(<T,>(props: LoaderComponentProps<T>) => {
  const { value, fallback, children } = props
  const loader = useMemo(() => createLoader(value as Promise<T>), [value])

  useLayoutEffect(() => {
    loader.load()
  }, [loader])

  let content
  switch (loader.state) {
    default:
    case LoadingState.notLoading:
    case LoadingState.loading:
      content = fallback
      break
    case LoadingState.resolved:
    case LoadingState.rejected:
      if (typeof children == "function") {
        content = children(loader.value)
      } else {
        content = children
      }
  }

  return content
})

Await.displayName = "Await"
