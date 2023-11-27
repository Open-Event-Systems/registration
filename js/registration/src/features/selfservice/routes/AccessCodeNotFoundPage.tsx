import { Subtitle, Title } from "#src/components"
import { Text } from "@mantine/core"

export const AccessCodeNotFoundPage = () => (
  <Title title="Access Code Not Found">
    <Subtitle subtitle="">
      <Text component="p">
        The access code was not found. It may be invalid or expired.
      </Text>
    </Subtitle>
  </Title>
)
