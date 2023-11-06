import { LoadingContext } from "#src/components"
import { Loader, createLoader } from "#src/util/loader.js"
import { useCallback, useContext, useState } from "react"

/**
 * Hook to create a {@link Loader} and keep it in component state.
 */
export const useLoader = <T>(
  loadFunc: () => Promise<T>,
  initialValue?: T,
): Loader<T> => {
  const [loader] = useState(() => createLoader(loadFunc, initialValue))
  return loader
}

type ShowLoadingFunc = <T>(promise: Promise<T>) => Promise<T>

/**
 * Get a function to set the loading state while a promise executes.
 * @returns
 */
export const useShowLoading = (): ShowLoadingFunc => {
  const context = useContext(LoadingContext)
  const showLoading = useCallback(
    async <T>(promise: Promise<T>) => {
      context.increment()
      try {
        const res = await promise
        context.decrement()
        return res
      } catch (err) {
        context.decrement()
        throw err
      }
    },
    [context],
  )

  return showLoading
}
