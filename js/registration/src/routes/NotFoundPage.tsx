import { Text } from "@mantine/core"
import { Title as PageTitle, Subtitle } from "#src/components/title/Title"
import { useRouteError } from "react-router-dom"
import { isNotFoundError } from "#src/utils/api"

export const NotFoundPage = () => {
  return (
    <PageTitle title="Not Found">
      <Subtitle subtitle="">
        <Text component="p">The page was not found.</Text>
      </Subtitle>
    </PageTitle>
  )
}

export const NotFoundErrorBoundary = () => {
  const error = useRouteError()
  if (isNotFoundError(error)) {
    return <NotFoundPage />
  } else {
    throw error
  }
}
