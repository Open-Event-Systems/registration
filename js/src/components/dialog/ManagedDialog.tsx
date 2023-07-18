import { Dialog, DialogProps } from "#src/components/dialog/Dialog.js"
import { useLocation } from "#src/hooks/location.js"
import {
  ComponentPropsWithoutRef,
  ComponentType,
  useLayoutEffect,
  useState,
} from "react"

declare module "#src/hooks/location.js" {
  interface LocationState {
    showManagedDialog?: string
  }
}

export type ManagedDialogBaseProps = Pick<
  DialogProps,
  "id" | "opened" | "transitionProps"
>

export type ManagedDialogProps<
  C extends ComponentType<ManagedDialogBaseProps>
> = {
  id: string
  children?: never
} & Omit<ComponentPropsWithoutRef<C>, "opened" | "transitionProps">

/**
 * A dialog whose opened state is managed by location state.
 */
export const ManagedDialog = <
  C extends ComponentType<ManagedDialogBaseProps> = typeof Dialog
>(
  props: ManagedDialogProps<C> & { component?: C }
) => {
  const { component: Component = Dialog, id, children, ...other } = props

  const loc = useLocation()

  const [prevChildren, setPrevChildren] =
    useState<ManagedDialogProps<C>["children"]>()

  const show = loc.state?.showManagedDialog == id

  useLayoutEffect(() => {
    if (!show) {
      setPrevChildren(children)
    }
  }, [show])

  return (
    <Component
      {...other}
      id={id}
      opened={show}
      transitionProps={{
        onExited: () => {
          setPrevChildren(undefined)
        },
      }}
    >
      {show ? children : prevChildren}
    </Component>
  )
}

// /**
//  * A dialog whose opened state is managed by location state.
//  */
// export const ManagedDialog = <P extends ManagedDialogBaseProps = DialogProps>(
//   props: P & { component?: ComponentType<Omit<P, "component">> }
// ) => {
//   const {
//     component: Component = Dialog,
//     ...other
//   } = props

//   const {
//     id,
//     children
//   } = props

//   const loc = useLocation()

//   const [prevChildren, setPrevChildren] = useState<ReactNode>(null)

//   const show = loc.state?.showManagedDialog == id

//   useLayoutEffect(() => {
//     if (!show) {
//       setPrevChildren(children)
//     }
//   }, [show])

//   return (
//     <Component
//       {...other}
//       id={id}
//       opened={show}
//       transitionProps={{
//         onExited: () => {
//           setPrevChildren(null)
//         }
//       }}
//     >
//       {show ? children : prevChildren}
//     </Component>
//   )
// }
