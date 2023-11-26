import { ElementType, ReactNode } from "react"
import { Outlet } from "react-router-dom"

export const LayoutRoute = ({
  Layout,
}: {
  Layout: ElementType<{ children: ReactNode }>
}) => {
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}
