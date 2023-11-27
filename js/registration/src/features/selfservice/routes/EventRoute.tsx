import { ShowLoadingOverlay } from "#src/components"
import { useSelfServiceAPI } from "#src/features/selfservice/hooks"
import { useQuery } from "@tanstack/react-query"
import { Outlet, useParams } from "react-router-dom"

export const EventRoute = () => {
  const { eventId = "" } = useParams()
  const selfServiceAPI = useSelfServiceAPI()
  const query = useQuery(selfServiceAPI.readEvent(eventId))

  if (!query.isSuccess) {
    return <ShowLoadingOverlay />
  } else {
    return <Outlet />
  }
}
