import { LoadValue, Loader, createLoader } from "#src/features/loader"
import { observer } from "mobx-react-lite"
import { ReactNode, Suspense, useMemo } from "react"

export type LoaderComponentProps<T> = {
  value: LoadValue<T>
  fallback?: ReactNode
  children?: ReactNode | ((value: T) => ReactNode)
}

export const Await = <T,>(props: LoaderComponentProps<T>) => {
  const { value, fallback, children } = props
  const loader = useMemo(() => createLoader(value as Promise<T>), [value])

  return (
    <Suspense fallback={fallback}>
      <AwaitSuspender loader={loader}>{children}</AwaitSuspender>
    </Suspense>
  )
}

const AwaitSuspender = observer(
  <T,>({
    loader,
    children,
  }: {
    loader: Loader<T>
    children?: ReactNode | ((value: T) => ReactNode)
  }) => {
    if (typeof children == "function") {
      return children(loader.value)
    } else if (loader.ready) {
      return children
    } else {
      throw loader
    }
  },
)

AwaitSuspender.displayName = "AwaitSuspender"
