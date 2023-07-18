import { Dialog } from "#src/components/dialog/Dialog.js"
import {
  ManagedDialog,
  ManagedDialogBaseProps,
} from "#src/components/dialog/ManagedDialog.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import {
  ComponentPropsWithoutRef,
  ComponentType,
  createElement,
  useCallback,
} from "react"

type DialogHookComponentProps = {
  onClose?: () => void
} & ManagedDialogBaseProps

type ManagedDialogComponent = ComponentType<DialogHookComponentProps>

export type DialogHookComponent<P extends DialogHookComponentProps> =
  ComponentType<P> & {
    show: () => void
    close: () => void
  }

/**
 * Use a managed dialog.
 * @param id - The dialog ID.
 * @returns A {@link Dialog} component with show and close methods.
 */
export const useDialog = <C extends ManagedDialogComponent = typeof Dialog>(
  id: string,
  component?: C
): DialogHookComponent<ComponentPropsWithoutRef<C>> => {
  const loc = useLocation()
  const navigate = useNavigate()

  const showFunc = useCallback(() => {
    if (loc.state?.showManagedDialog != id) {
      navigate(loc, { state: { ...loc.state, showManagedDialog: id } })
    }
  }, [loc, navigate])

  const closeFunc = useCallback(() => {
    if (loc.state?.showManagedDialog == id) {
      navigate(-1)
    }
  }, [loc, navigate])

  const wrapped = useCallback(
    (props: ComponentPropsWithoutRef<C>) => {
      const el = createElement(ManagedDialog<C>, {
        id: id,
        component: component,
        onClose: () => {
          navigate(-1)
        },
        ...props,
      })

      return el
    },
    [id, navigate]
  )

  return Object.assign(wrapped, { show: showFunc, close: closeFunc })
}
