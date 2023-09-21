import { Container } from "@mantine/core"
import { Title as PageTitle, Subtitle } from "#src/components/title/Title.js"

export const NotFoundPage = () => {
  return (
    <Container size="md">
      <PageTitle title="Not Found">
        <Subtitle subtitle="The page was not found." />
      </PageTitle>
    </Container>
  )
}
