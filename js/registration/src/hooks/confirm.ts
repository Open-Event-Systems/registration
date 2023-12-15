import { useLocation, useNavigate } from "#src/hooks/location"
import { observable, runInAction } from "mobx"
import { createContext, useContext } from "react"

declare module "#src/hooks/location" {
  interface LocationState {
    showConfirm?: boolean
  }
}

type Confirmation = {
  title: string
  message: string
  confirm: () => void
  cancel: () => void
}

export type ConfirmFunc = (title?: string, message?: string) => Promise<boolean>

export const ConfirmContext = createContext(
  observable.box<Confirmation | null>(null),
)

export const useConfirm = (): ConfirmFunc => {
  const loc = useLocation()
  const navigate = useNavigate()
  const ctx = useContext(ConfirmContext)

  const confirm = (title = "Confirm", message = "Are you sure?") => {
    const promise = new Promise<boolean>((resolve) => {
      const confirmation: Confirmation = {
        title,
        message,
        confirm() {
          resolve(true)
        },
        cancel() {
          resolve(false)
        },
      }

      runInAction(() => {
        ctx.set(confirmation)
      })
      navigate(loc, { state: { ...loc.state, showConfirm: true } })
    })
    return promise
  }

  return confirm
}
