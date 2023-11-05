import { Meta, StoryObj } from "@storybook/react"

import { AuthStoreProvider } from "#src/features/auth/providers.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import { Subtitle, Title } from "#src/components/title/Title.js"
import { SimpleLayout } from "#src/components/layout/SimpleLayout.js"

import { Text } from "@mantine/core"

import "./user-menu/UserMenu.module.css"
import "./header/Header.module.css"
import "./title-area/TitleArea.module.css"
import "./StackLayout.module.css"
import "./ContainerLayout.module.css"
import "./app-shell/AppShellLayout.module.css"

const meta: Meta<typeof SimpleLayout> = {
  component: SimpleLayout,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

const mockAuth = {
  accessToken: true,
  email: "user@example.net",
}

export const Default: StoryObj<typeof SimpleLayout> = {
  decorators: [
    (Story) => (
      <AuthStoreProvider authStore={mockAuth as unknown as AuthStore}>
        <Story />
      </AuthStoreProvider>
    ),
  ],
  render() {
    return (
      <SimpleLayout>
        <Title title="Example Page">
          <Subtitle subtitle="An example page">
            <Text component="p">Example content.</Text>
          </Subtitle>
        </Title>
      </SimpleLayout>
    )
  },
}
