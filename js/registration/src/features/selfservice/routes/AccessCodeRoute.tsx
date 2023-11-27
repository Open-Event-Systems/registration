import { ShowLoadingOverlay } from "#src/components"
import { useSelfServiceAPI } from "#src/features/selfservice/hooks"
import { AccessCodeNotFoundPage } from "#src/features/selfservice/routes/AccessCodeNotFoundPage"
import { useQuery } from "@tanstack/react-query"
import { Outlet, useParams } from "react-router-dom"

export const AccessCodeRoute = () => {
  const { eventId = "", accessCode = "" } = useParams()
  const selfServiceAPI = useSelfServiceAPI()
  const query = useQuery(selfServiceAPI.checkAccessCode(eventId, accessCode))

  if (!query.isSuccess) {
    return <ShowLoadingOverlay />
  } else if (query.data) {
    return <Outlet />
  } else {
    return <AccessCodeNotFoundPage />
  }
}
