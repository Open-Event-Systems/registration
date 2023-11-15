import { ILoader, LoadingState } from "#src/features/loader"
import { observer } from "mobx-react-lite"
import { ElementType, ReactNode, useLayoutEffect } from "react"

export type LoaderComponentProps = {
  state?: LoadingState
  placeholder?: ReactNode
  notFound?: ReactNode
  children?: ReactNode
}

export const LoaderComponent = (props: LoaderComponentProps) => {
  const { state, placeholder, notFound, children } = props

  let content
  switch (state) {
    case LoadingState.notLoading:
    case LoadingState.loading:
      content = placeholder
      break
    case LoadingState.ready:
      content = children
      break
    case LoadingState.notFound:
      content = notFound ?? placeholder
      break
  }

  return content
}

export type ManagedLoaderComponentProps<T> = {
  placeholder?: ReactNode
  notFound?: ReactNode
  children?: ReactNode | ((value: T) => ReactNode)
  lazy?: boolean
}

export const createLoaderComponent = <T,>(
  loader: ILoader<T>,
): ElementType<ManagedLoaderComponentProps<T>> => {
  const component = observer(
    ({
      placeholder,
      notFound,
      children,
      lazy,
    }: ManagedLoaderComponentProps<T>) => {
      useLayoutEffect(() => {
        if (!lazy) {
          loader.load()
        }
      }, [])

      let content
      if (typeof children == "function") {
        if (loader.ready) {
          content = children(loader.value as T)
        }
      } else {
        content = children
      }

      return (
        <LoaderComponent
          state={loader.state}
          notFound={notFound}
          placeholder={placeholder}
        >
          {content}
        </LoaderComponent>
      )
    },
  )

  component.displayName = "ManagedLoaderComponent"

  return component
}
